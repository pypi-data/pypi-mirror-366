from quick_actions.persistance.AbstractFrecencyRepository import AbstractFrecencyRepository
from quick_actions import constants
from quick_actions.persistance.pickle.PickleStore import PickleStore

from typing import Dict, Tuple
from datetime import datetime


class PickleFrecencyRepository(AbstractFrecencyRepository):
    def __init__(self):
        self.store = PickleStore.get_instance()
    
    def save_frecency_store(self, frecency_store: Dict[str, Tuple[int, datetime]]):
        self.store[constants.PICKLE_FRECENCY_STORE_KEY] = frecency_store

    def load_frecency_store(self) -> Dict[str, Tuple[int, datetime]]:
        return self.store.get(constants.PICKLE_FRECENCY_STORE_KEY, {})
