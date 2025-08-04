from quick_actions.persistance.AbstractStateRepository import AbstractStateRepository
from quick_actions.persistance.pickle.PickleStore import PickleStore
from quick_actions import constants


class PickleStateRepository(AbstractStateRepository):
    def __init__(self):
        self.store = PickleStore.get_instance()

    def _store_key_(key: str) -> str:
        return constants.PICKLE_STATE_KEY_TEMPLATE.replace("{key}", key)

    def save_state(key: str, state: object):
        self.store[self._store_key_(key)] = state

    def get_state(key: str) -> object:
        return self.store[self._store_key_(key)]
