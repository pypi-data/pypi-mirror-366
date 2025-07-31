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
from __future__ import annotations
from typing import Callable

from robo_orchard_lab.pipeline.hooks.mixin import (
    HookContext,
    PipelineHookArgs,
    PipelineHooks,
    PipelineHooksConfig,
)

__all__ = ["ValidationHook", "ValidationHookConfig"]


class ValidationHook(PipelineHooks):
    """A hook for evaluating the model during training.

    This hook allows for evaluation at specified intervals during training,
    either at the end of each step or at the end of each epoch.


    Args:
        eval_callback (Callable[[], None]): A callback function to be called
            for evaluation. This function should not take no argument and
            should not return any values. A common use case is to pass a
            closure that performs the evaluation.
        step_eval_freq (int | None): The frequency of evaluation in terms of
            steps. If specified, the evaluation will be performed every
            `step_eval_freq` steps.
        epoch_eval_freq (int | None): The frequency of evaluation in terms of
            epochs. If specified, the evaluation will be performed every
            `epoch_eval_freq` epochs.

    """

    def __init__(
        self,
        cfg: ValidationHookConfig,
    ):
        super().__init__()
        self.eval_callback = cfg.eval_callback
        self.step_eval_freq = cfg.step_eval_freq
        self.epoch_eval_freq = cfg.epoch_eval_freq

        if cfg.epoch_eval_freq is not None:
            self.register_hook(
                "on_epoch",
                HookContext.from_callable(
                    after=self._on_epoch_end, before=None
                ),
            )
        if cfg.step_eval_freq is not None:
            self.register_hook(
                "on_step",
                HookContext.from_callable(
                    after=self._on_step_end, before=None
                ),
            )

    def _on_step_end(
        self,
        hook_args: PipelineHookArgs,
    ) -> None:
        """Called at the end of each step.

        This method checks if evaluation is needed based on the current step
        and calls the evaluation callback if necessary.

        Args:
            hook_args (PipelineHookArgs): The current training progress state.
        """
        if self.need_eval(hook_args):
            self.eval_callback()

    def _on_epoch_end(
        self,
        hook_args: PipelineHookArgs,
    ) -> None:
        """Called at the end of each epoch.

        This method checks if evaluation is needed based on the current epoch
        and calls the evaluation callback if necessary.

        Args:
            hook_args (PipelineHookArgs): The current training progress state.
        """
        if self.need_eval(hook_args):
            self.eval_callback()

    def need_eval(
        self,
        hook_args: PipelineHookArgs,
    ) -> bool:
        """Checks if evaluation is needed based on the current state.

        This method will return True if the current step or epoch matches the
        specified evaluation frequencies. If both step_eval_freq and
        epoch_eval_freq are None, return False.

        Args:
            progress_state (PipelineHookArgs): The current training
                progress state.

        Returns:
            bool: True if evaluation is needed, False otherwise.
        """
        if (
            self.step_eval_freq is not None
            and (hook_args.global_step_id + 1) % self.step_eval_freq == 0
        ):
            return True
        if (
            self.epoch_eval_freq is not None
            and (hook_args.epoch_id + 1) % self.epoch_eval_freq == 0
        ):
            return True

        return False


class ValidationHookConfig(PipelineHooksConfig[ValidationHook]):
    """Configuration class for ValidationHook."""

    class_type: type[ValidationHook] = ValidationHook

    eval_callback: Callable[[], None]
    """A callback function to be called for evaluation. This function should
    not take no argument and should not return any values. A common use case
    is to pass a closure that performs the evaluation.
    """
    step_eval_freq: int | None = None
    """The frequency of evaluation in terms of  steps. If specified,
    the evaluation will be performed every `step_eval_freq` steps."""
    epoch_eval_freq: int | None = None
    """The frequency of evaluation in terms of epochs. If specified, the
    evaluation will be performed every `epoch_eval_freq` epochs."""

    def __post_init__(self):
        if self.step_eval_freq is None and self.epoch_eval_freq is None:
            raise ValueError(
                "Either `step_eval_freq` or `epoch_eval_freq` "
                "must be specified."
            )
        if self.step_eval_freq is not None and self.step_eval_freq < 1:
            raise ValueError(
                "step_eval_freq = {} < 1 is not allowed".format(
                    self.step_eval_freq
                )
            )
        if self.epoch_eval_freq is not None and self.epoch_eval_freq < 1:
            raise ValueError(
                "epoch_eval_freq = {} < 1 is not allowed".format(
                    self.epoch_eval_freq
                )
            )
