from dataclasses import InitVar, dataclass
from pathlib import Path

from quick_actions import constants


@dataclass
class Persistance:
    backend: str = constants.DEFAULT_PERSISTANCE_BACKEND

    pickle_location: InitVar[str] = ""
    pickle_path: Path = None

    def __post_init__(self, pickle_location):
        self.pickle_path = Path(pickle_location).resolve()
