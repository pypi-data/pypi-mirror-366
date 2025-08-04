from typing import Dict
import pickle

from quick_actions.config_processing.ConfigProvider import ConfigProvider 
from quick_actions.persistance.AbstractBaseRepository import AbstractBaseRepository


class PickleStore(AbstractBaseRepository):
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


    def __init__(self):
        self.config_provider = ConfigProvider.get_instance()

        self.pickle_path = self.config_provider.general.persistance_settings.pickle_path

        self.store: Dict[str, object] = {}

        self.load_store()

    def load_store(self):
        if self.pickle_path.exists():
            with open(self.pickle_path, "rb") as fd:
                self.store = pickle.load(fd)
        else:
            # self.pickle_path.touch()
            self.store = {}

    def flush_all(self):
        print("now flushing: ", self.store)
        with open(self.pickle_path, "wb") as fd:
            pickle.dump(self.store, fd)


    def __getitem__(self, key: str):
        return self.get(key)
    
    def get(self, key: str, default=None):
        return self.store.get(key, default)

    def __setitem__(self, key: str, value):
        self.store[key] = value

    def __repr__(self):
        return repr(self.store)

    def __str__(self):
        return str(self.store)