from abc import ABC, abstractmethod


class AbstractBaseRepository(ABC):
    @abstractmethod
    def flush_all(self):
        pass