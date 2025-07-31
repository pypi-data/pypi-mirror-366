# Project RoboOrchard
#
# Copyright (c) 2024-2025 Horizon Robotics. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

from dataclasses import dataclass
from typing import Any, Iterable

import torch
from accelerate import Accelerator
from accelerate.logging import get_logger
from accelerate.optimizer import AcceleratedOptimizer
from accelerate.scheduler import AcceleratedScheduler
from robo_orchard_core.utils.config import Config
from torch.utils.data import DataLoader

from robo_orchard_lab.pipeline.batch_processor.mixin import BatchProcessorMixin
from robo_orchard_lab.pipeline.hooks.grad_clip import (
    GradientClippingHookConfig,
)
from robo_orchard_lab.pipeline.hooks.mixin import (
    PipelineHookArgs,
    PipelineHooks,
    PipelineHooksConfig,
)
from robo_orchard_lab.pipeline.hooks.optimizer import OptimizerHookConfig
from robo_orchard_lab.pipeline.hooks.validation import ValidationHookConfig
from robo_orchard_lab.utils.huggingface import (
    AcceleratorState,
    accelerator_load_state,
)

logger = get_logger(__name__)

__all__ = [
    "HookBasedTrainer",
    "ResumeCheckpointConfig",
    "GradientClippingHookConfig",
    "ValidationHookConfig",
    "PipelineHookOrConfigType",
]


@dataclass
class TrainerProgressState(AcceleratorState):
    """A data class for storing the state of the training progress.

    This class is designed to be used with the Trainer class to keep track
    of the current epoch, step, and other relevant information during the
    training process.
    """

    epoch_id: int = 0
    """The current epoch. Starts from 0."""
    step_id: int = 0
    """The current step. Starts from 0."""
    global_step_id: int = 0
    """The total number of steps taken across all epochs. Starts from 0."""

    def update_step(self) -> None:
        """Increments the step and global_step by 1."""
        self.step_id += 1
        self.global_step_id += 1

    def update_epoch(self) -> None:
        """Increments the epoch by 1 and resets the step to 0."""
        self.epoch_id += 1
        self.step_id = 0

    def is_training_end(
        self, max_step: int | None, max_epoch: int | None
    ) -> bool:
        """Checks if the training loop should end based on the current state.

        This method will return True if the current step or epoch exceeds the
        specified maximum values. If both max_step and max_epoch are None,
        return False.

        Args:
            max_step (int|None): The maximum number of steps allowed.
            max_epoch (int|None): The maximum number of epochs allowed.

        Returns:
            bool: True if the training loop should end, False otherwise.
        """
        if max_step is not None and self.global_step_id >= max_step:
            return True
        if max_epoch is not None and self.epoch_id >= max_epoch:
            return True
        return False

    def sync_pipeline_hook_arg(self, hook_args: PipelineHookArgs) -> None:
        """Synchronizes the training state with the provided hook arguments.

        The hook arguments are updated with the current epoch, step, and
        global_step.

        Args:
            hook_args (PipelineHookArgs): The hook arguments to synchronize
            with.
        """
        hook_args.epoch_id = self.epoch_id
        hook_args.step_id = self.step_id
        hook_args.global_step_id = self.global_step_id


class ResumeCheckpointConfig(Config):
    """A configuration class for resuming from checkpoints."""

    resume_from: str
    """The directory containing the checkpoints."""
    cache_dir: str | None = None
    """The directory to cache the checkpoints if from a remote path."""

    safe_serialization: bool = True
    """Whether to use safe serialization when loading the state.

    This is used when input_dir is a remote path. The names of checkpoint
    files depend on whether `safe_serialization` is set to `True` or
    `False`. Users should ensure that the checkpoint files in the
    remote directory are compatible with the specified `safe_serialization`
    option.

    """

    def load_state(self, accelerator: Accelerator, **kwargs) -> None:
        """Loads the state of the accelerator from a checkpoint.

        Args:
            accelerator (Accelerator): The `Accelerator` instance to load the
                state into.
        """
        accelerator_load_state(
            accelerator=accelerator,
            input_dir=self.resume_from,
            cache_dir=self.cache_dir,
            safe_serialization=self.safe_serialization,
            **kwargs,
        )


PipelineHookOrConfigType = PipelineHooksConfig | PipelineHooks


class HookBasedTrainer:
    """A trainer class that uses hooks to manage the training process.

    The data loader, model, optimizer, and learning rate scheduler are
    prepared using the `Accelerator` instance, which provides
    distributed training capabilities. The `PipelineHooks` are used to
    manage the training process, allowing for custom hooks to be defined
    for various stages of the training loop.

    The whole training process with hooks is as follows:

    .. code-block:: text

        with on_loop:
            with on_epoch:
                for batch in dataloader:
                    with on_step:
                        with on_batch:
                            batch_processor(...)
                            ...

                        update step id
            update epoch id


    Note:
        The trainer will register the following default hooks in order:

        - `GradientClippingHook`: This hook is responsible for clipping
            the gradients to prevent exploding gradients. It will be
            registered if the `grad_clip` argument is provided.

        - `OptimizerHook`: This hook is responsible for performing the
            optimization step and updating the learning rate scheduler.

        - `ValidationHook`: This hook is responsible for performing
            validation during training. It will call the evaluation
            callback function at the specified frequency. It will be
            registered if the `validation` argument is provided.

    Args:
        accelerator (Accelerator): The `Accelerator` instance managing
            distributed training.
        model (torch.nn.Module): The model to be trained.
        dataloader (DataLoader | Iterable): The data loader for feeding
            batches to the model during training.
        batch_processor (BatchProcessorMixin): The batch processor
            responsible for processing the batches and backpropagating
            the loss.
        optimizer (torch.optim.Optimizer): The optimizer used during
            training.
        lr_scheduler (torch.optim.lr_scheduler.LRScheduler): The learning
            rate scheduler used during training.
        hooks (PipelineHooks | Iterable[PipelineHooks]): The hooks to be
            used during training. These hooks can be used to customize
            various stages of the training process.
        max_step (int | None): The maximum number of steps for
            training. Either `max_step` or `max_epoch` must be specified.
        max_epoch (int | None): The maximum number of epochs for
            training. Either `max_step` or `max_epoch` must be specified.
        grad_clip (GradClipConfig | None): The gradient clipping
            configuration.
        validation (ValidationConfig | None): The validation
            configuration. If not specified, no validation will be
            performed.
        resume_from (ResumeCheckpointConfig | None): The configuration
            for resuming from checkpoints. If not specified, training
            will start from scratch.
    """

    def __init__(
        self,
        accelerator: Accelerator,
        model: torch.nn.Module,
        dataloader: DataLoader | Iterable,
        batch_processor: BatchProcessorMixin,
        optimizer: torch.optim.Optimizer,
        lr_scheduler: torch.optim.lr_scheduler.LRScheduler,
        hooks: PipelineHookOrConfigType | Iterable[PipelineHookOrConfigType],
        max_step: int | None = None,
        max_epoch: int | None = None,
        grad_clip: GradientClippingHookConfig | None = None,
        validation: ValidationHookConfig | None = None,
        resume_from: ResumeCheckpointConfig | None = None,
    ):
        if max_step is None and max_epoch is None:
            raise ValueError(
                "Either `max_step` or `max_epoch` must be specified."
            )
        if max_step is not None and max_step < 1:
            raise ValueError(
                "max_step = {} < 1 is not allowed".format(max_step)
            )
        if max_epoch is not None and max_epoch < 1:
            raise ValueError(
                "max_epoch = {} < 1 is not allowed".format(max_epoch)
            )

        self.accelerator = accelerator
        user_hooks = PipelineHooks.from_hooks(hooks)
        self.max_step = max_step
        self.max_epoch = max_epoch

        # prepare using accelerator
        self.model: torch.nn.Module = accelerator.prepare(model)
        self.dataloader: DataLoader = accelerator.prepare(dataloader)
        self.optimizer: AcceleratedOptimizer = accelerator.prepare(optimizer)
        self.lr_scheduler: AcceleratedScheduler = accelerator.prepare(
            lr_scheduler
        )
        self.trainer_progress_state = TrainerProgressState()
        accelerator.register_for_checkpointing(self.trainer_progress_state)

        self.batch_processor = batch_processor

        self.hooks = PipelineHooks()
        # register default hooks: grad_clip, optimizer, validation
        if grad_clip is not None:
            self.hooks += grad_clip()

        self.hooks += OptimizerHookConfig()()
        if validation is not None:
            self.hooks += validation()

        # register user hooks
        self.hooks += user_hooks

        self._start_epoch = 0
        self._start_step = 0

        if resume_from is not None:
            logger.info(f"Resume from: {resume_from}", main_process_only=True)
            resume_from.load_state(accelerator=self.accelerator)
            self._start_epoch = self.trainer_progress_state.epoch_id
            self._start_step = self.trainer_progress_state.step_id

    def _get_hook_args(self, **kwargs) -> PipelineHookArgs:
        """Get Hook args.

        Creates and returns a HookArgs object with current training state
        and additional arguments.

        Args:
            **kwargs: Additional arguments to include in the HookArgs object.

        Returns:
            PipelineHookArgs: An object containing the current training state
                and additional arguments.
        """
        hookargs = PipelineHookArgs(
            accelerator=self.accelerator,
            max_step=self.max_step,
            max_epoch=self.max_epoch,
            epoch_id=self.trainer_progress_state.epoch_id,
            step_id=self.trainer_progress_state.step_id,
            global_step_id=self.trainer_progress_state.global_step_id,
            dataloader=self.dataloader,
            optimizer=self.optimizer,
            lr_scheduler=self.lr_scheduler,
            start_epoch=self._start_epoch,
            start_step=self._start_step,
        )
        for k, v in kwargs.items():
            setattr(hookargs, k, v)
        return hookargs

    def __call__(self):
        logger.info(
            "\n" + "=" * 50 + "BEGIN TRAINING" + "=" * 50,
            main_process_only=True,
        )
        logger.info(
            f"Start training loop from epoch {self._start_epoch} "
            f"and step {self._start_step}",
            main_process_only=True,
        )
        end_loop_flag = False
        self.model.train()

        def step(
            batch: Any,
            batch_processor: BatchProcessorMixin,
        ):
            with self.hooks.begin(
                "on_step", self._get_hook_args()
            ) as on_step_hook_args:
                with self.hooks.begin(
                    "on_batch", self._get_hook_args(batch=batch)
                ) as on_batch_hook_args:
                    batch_processor(
                        pipeline_hooks=self.hooks,
                        on_batch_hook_args=on_batch_hook_args,
                        model=self.model,
                    )
                    # update module_output to on_step_hook_args
                    on_step_hook_args.model_outputs = (
                        on_batch_hook_args.model_outputs
                    )
                    on_step_hook_args.reduce_loss = (
                        on_batch_hook_args.reduce_loss
                    )

        with self.hooks.begin(
            "on_loop", self._get_hook_args()
        ) as on_loop_hook_args:
            while not end_loop_flag:
                # TODO: Synchronize end_loop_flag when different
                # processes have different batch numbers. !
                #
                # In some cases, the dataloader may not have the same
                # number of batches when dataset is split into
                # different processes.
                #
                # If the dataloader has a different number of batches,
                # the training loop may hang or produce unexpected results.
                #
                # Consider using Accelerator.join_uneven_inputs?
                #
                with self.hooks.begin(
                    "on_epoch", self._get_hook_args()
                ) as on_epoch_hook_args:
                    for _i, batch in enumerate(self.dataloader):
                        # TODO: Support Accelerator.accumulate?
                        step(batch=batch, batch_processor=self.batch_processor)
                        self.trainer_progress_state.update_step()
                        self.trainer_progress_state.sync_pipeline_hook_arg(
                            on_epoch_hook_args
                        )
                        if self.trainer_progress_state.is_training_end(
                            max_step=self.max_step, max_epoch=self.max_epoch
                        ):
                            end_loop_flag = True
                            break

                self.trainer_progress_state.update_epoch()
                self.trainer_progress_state.sync_pipeline_hook_arg(
                    on_loop_hook_args
                )
                if self.trainer_progress_state.is_training_end(
                    max_step=self.max_step, max_epoch=self.max_epoch
                ):
                    end_loop_flag = True

        logger.info(
            "\n" + "=" * 50 + "FINISH TRAINING" + "=" * 50,
            main_process_only=True,
        )
