from abc import ABC, abstractmethod

class AbstractStateRepository(ABC):
    
    @abstractmethod
    def save_state(key: str, state: object):
        pass

    @abstractmethod
    def get_state(key: str) -> object:
        pass