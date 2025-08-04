from queue import Queue
from pathlib import Path
from typing import Dict

from quick_actions.config_processing.config_classes.Action import Action 
from quick_actions import constants 
from quick_actions.exception.InvalidConfigException import InvalidConfigException  


class ActionProcessor:

    @classmethod
    def get_prefixes(cls, actions):
        prefixes = {}
        # TODO: pirorized prefixes
        for action in actions.values():
            if action.prefix is not None:
                prefixes[action.prefix] = action
        return prefixes

    @classmethod
    def flat_actions(cls, actions):
        queue = Queue()
        queue.put(("", actions))
        flattened = {}
        envs = {}
        display_prefixes = {}
        while not queue.empty():
            # extract env vars
            prefix, subactions = queue.get()
            if subactions.get("env"):
                envs[prefix] = subactions["env"]
                del subactions["env"]
            
            # extract display prefixes (strings prefixed to every command in scope)
            if subactions.get("display_prefix"):
                display_prefixes[prefix] = subactions["display_prefix"]
                del subactions["display_prefix"]

            

            for name, action_candidate in subactions.items():
                if prefix: 
                    new_prefix = f"{prefix}.{name}"
                else:
                    new_prefix = name
                if Action.is_action(action_candidate):
                    try:
                        flattened[new_prefix] = Action(id=new_prefix, **action_candidate)
                    except TypeError as exc:
                        raise InvalidConfigException(f"Unkown action scoped setting in {new_prefix}") from exc

                elif isinstance(action_candidate, dict):
                    queue.put(
                        (new_prefix, action_candidate)
                    )
                else:
                    # TODO: custom exceptions
                    raise InvalidConfigException(f"Unkown action {new_prefix}: {action_candidate}.")

        # concat with display prefixes
        for prefix, dprefix in display_prefixes.items():
            for action in flattened.values():
                if action.id.startswith(prefix):
                    action.label = dprefix + action.label

        return flattened, envs


    @staticmethod
    def expand_relative_paths(base: Path, config_part: Dict):
        queue = Queue()
        queue.put(config_part)

        while not queue.empty():
            current = queue.get()

            if Action.is_action(current):
                for keyword in constants.ACTION_KEYWORDS_TO_RESOLVE_RELATIVE_PATHS:
                    if (sc := current.get(keyword)) is not None:
                        sc_path = Path(sc)
                        if not sc_path.is_absolute():
                            current[keyword] = (base / sc_path).resolve()
            else:
                for value in current.values():
                    if isinstance(value, dict):
                        queue.put(value)