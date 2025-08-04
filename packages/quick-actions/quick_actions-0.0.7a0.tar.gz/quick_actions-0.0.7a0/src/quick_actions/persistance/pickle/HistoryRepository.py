from abc import ABC, abstractmethod
from typing import List


class AbstractStateRepository(ABC):
    
    @abstractmethod
    def save_entry(entry: str):
        pass

    @abstractmethod
    def get_last_entries() -> List[str]:
        pass
