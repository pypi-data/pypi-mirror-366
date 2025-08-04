from abc import ABC, abstractmethod

class AbstractOrderer(ABC):
    @abstractmethod
    def score_of(self, key: str) -> float:
        pass

    @abstractmethod
    def pump_item(self, key: str):
        pass
