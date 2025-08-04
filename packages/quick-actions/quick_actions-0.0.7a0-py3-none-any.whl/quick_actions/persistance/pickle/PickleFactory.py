from quick_actions.persistance.pickle.StateRepository import PickleStateRepository
from quick_actions.persistance.pickle.FrecencyRepository import PickleFrecencyRepository
from quick_actions.persistance.pickle.StateRepository import PickleStateRepository
from quick_actions.persistance.pickle.PickleStore import PickleStore
from quick_actions.persistance.AbstractFactory import AbstractFactory


class PickleFactory(AbstractFactory):
    def get_state_repository(self):
        return PickleStateRepository()

    def get_frecency_repository(self):
        return PickleFrecencyRepository()

    def get_base_repository(self):
        return PickleStore.get_instance()
