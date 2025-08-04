from quick_actions.config_processing.ConfigProvider import ConfigProvider
from quick_actions.persistance.pickle.PickleFactory import PickleFactory
from quick_actions.persistance.AbstractFactory import AbstractFactory

from typing import Self
from pathlib import Path


class PersistanceFactory:
    instance = None

    @classmethod
    def get_instance(cls) -> Self:
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


    def __init__(self):
        self.config_provider = ConfigProvider.get_instance()

    def get_factory(self) -> AbstractFactory:
        match self.config_provider.general.persistance_settings.backend:
            case "pickle":
                return PickleFactory()
            case _:
                print("[WARNING]: unkown backend, using pickle")
                return PickleFactory()
