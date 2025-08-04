from dataclasses import dataclass, field, InitVar
from typing import List, Dict

from quick_actions.config_processing.config_classes.Launcher import Launcher
from quick_actions.config_processing.config_classes.Display import Display
from quick_actions.config_processing.config_classes.Persistance import Persistance


@dataclass
class General:
    disabled_units: List[str] | None = None

    copy_command: str = "wl-copy {text_to_copy}"

    launcher_settings: Launcher = None
    launcher: InitVar[ Dict | None] = None
    
    display_settings: Display = None
    display: InitVar[ Dict | None] = None

    persistance_settings: Persistance = None
    persistance: InitVar[ Dict | None] = None


    @staticmethod
    def __add_obj(clazz, obj):
        if obj is None:
            obj = {}

        return clazz(**obj)



    def __post_init__(self, launcher: Dict | None, display: Dict | None, persistance: Dict | None):
        self.launcher_settings = self.__add_obj(Launcher, launcher)
        self.display_settings = self.__add_obj(Display, display)
        self.persistance_settings = self.__add_obj(Persistance, persistance)



if __name__=="__main__":
    g = General()
    print(g)
