from abc import ABC, abstractmethod

from quick_actions.persistance.AbstractStateRepository import AbstractStateRepository
from quick_actions.persistance.AbstractFrecencyRepository import AbstractFrecencyRepository
from quick_actions.persistance.AbstractBaseRepository import AbstractBaseRepository


class AbstractFactory(ABC):
    @abstractmethod
    def get_base_repository(self) -> AbstractBaseRepository:
        pass

    @abstractmethod
    def get_state_repository(self) -> AbstractStateRepository:
        pass

    @abstractmethod
    def get_frecency_repository(self) -> AbstractFrecencyRepository:
        pass
