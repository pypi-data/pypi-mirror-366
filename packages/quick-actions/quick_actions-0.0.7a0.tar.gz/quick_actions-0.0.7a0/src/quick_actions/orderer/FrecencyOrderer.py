from typing import Dict, Tuple, Self
from datetime import datetime, timedelta
from quick_actions.persistance.PersistenceFactory import PersistanceFactory


class FrecencyOrderer:
    """Frequency + Recency"""
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


    def __init__(self):
        self.max_age = 10000 # trigger pruning when this is exceeded

        self.frecency_repo = PersistanceFactory.get_instance().get_factory().get_frecency_repository()

        self.store: Dict[str, Tuple[int, datetime]] = {}

        self.load()

    def load(self):
        self.store = self.frecency_repo.load_frecency_store()

    def persist(self):
        self.frecency_repo.save_frecency_store(self.store)

    def score_of(self, key: str) -> float:
        count, time = self.store.get(key, (0, datetime.min))
        return self.adjust_for_time(count, time)

    def pump_item(self, key: str):
        count, time = self.store.get(key, (0, datetime.now()))
        self.store[key] = (count+1, datetime.now())
        self.persist()

    def adjust_for_time(self, count, time):
        delta = datetime.now() - time

        weight = 1
        match delta:
            case d if d < timedelta(hours=1):
                weight = 4
            case d if d < timedelta(days=1):
                weight = 2
            case d if d < timedelta(weeks=1):
                weight = 0.5
            case _:
                weight = 0.25

        return count * weight
