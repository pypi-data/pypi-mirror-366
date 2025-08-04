from abc import ABC, abstractmethod
from typing import Dict, Tuple
from datetime import datetime

class AbstractFrecencyRepository(ABC):
    
    @abstractmethod
    def save_frecency_store(frecency_store: Dict[str, Tuple[int, datetime]]):
        pass

    @abstractmethod
    def load_frecency_store() -> Dict[str, Tuple[int, datetime]]:
        pass
