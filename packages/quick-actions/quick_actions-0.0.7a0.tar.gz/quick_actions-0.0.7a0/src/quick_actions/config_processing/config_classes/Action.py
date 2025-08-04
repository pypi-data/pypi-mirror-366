from dataclasses import dataclass
from typing import Dict
from pathlib import Path
from quick_actions import constants
from quick_actions.exception.InvalidConfigException import InvalidConfigException 
import copy


@dataclass
class Action:
    id: str
    label: str
    exec: str | None = None
    script: Path | str | None = None
    sleep_before: float | int | None = None
    search_tags: str | None = None
    prefix: str | None = None
    populate_options: str | None = ""
    show_response: bool = False
    copy: bool = False

    use_shell: bool = True
    capture_output: bool = True

    @staticmethod
    def is_action(action_candidate):
        # print(action_candidate)
        if (not isinstance(action_candidate, dict)) or action_candidate.get("label") is None:
            return False
        if action_candidate.get(constants.INLINE_SCRIPT_PREFIX) == None and \
            action_candidate.get(constants.SCRIPT_PREFIX) == None:
            # TODO: use proper warning log
            print(f"[WARNING]: Action '{action_candidate["label"]}' has no command")
        return True

    def __post_init__(self):
        # FIXME: refactor and create more warnings and validations, this should be a validation
        if (not self.capture_output) and self.show_response:
            raise InvalidConfigException(f"[WARNING]: Action '{self.label}' has capture_output=False, but show_response=True")


    @property
    def tags(self):
        if self.search_tags is None:
            return []
        return self.search_tags.strip().split(",")

    def with_arguments(self, arguments):
        new_action = copy.copy(self)

        if self.script is not None:
            new_action.script = None
            new_action.exec = str(self.script) + " " + f'"{arguments}"'
        elif self.exec is not None:
            new_action.exec += " " + f'"{arguments}"'
        return new_action
