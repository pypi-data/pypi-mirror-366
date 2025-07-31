from __future__ import annotations

import os
import shlex

from ..base_rule import BaseRule, ExecWork
from ..config import RuleConfig


class Rule(BaseRule):
    work_cls = ExecWork

    def __init__(self, rule_config: RuleConfig) -> None:
        super().__init__(rule_config)
        if rule_config.command:
            if isinstance(rule_config.command, str):
                self.command_parts = shlex.split(rule_config.command)
            else:
                self.command_parts = rule_config.command
        else:
            assert rule_config.data
            self.command_parts = ["/bin/bash", "-c", rule_config.data.strip(), "placeholder"]

        # TODO
        self.command_env = os.environ.copy()

    def prepare(self) -> None:
        pass
