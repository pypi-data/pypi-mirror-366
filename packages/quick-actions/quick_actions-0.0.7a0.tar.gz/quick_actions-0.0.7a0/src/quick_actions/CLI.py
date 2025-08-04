import argparse
from pathlib import Path
import sys

from quick_actions.config_processing.ConfigProvider import ConfigProvider
from quick_actions.WhatToDoMenu import WhatToDoMenu
from quick_actions.dispatcher.ActionDispatcher import ActionDispatcher
from quick_actions.persistance.PersistenceFactory import PersistanceFactory


class CLI():
    def __init__(self):
        self.parser = self.define_config_parser()
        self.args = self.parser.parse_args()

    def run(self):

        config_path = Path(self.args.config)

        if config_path.is_dir():
            config_provider = ConfigProvider.get_instance(config_path)
            what_todo_menu = WhatToDoMenu()

            ActionDispatcher(what_todo_menu.menu_output, what_todo_menu.actions_by_decorated_label)

            PersistanceFactory.get_instance().get_factory().get_base_repository().flush_all()
        else:
            print(f"Please consider adding an existing config folder! The default is {ConfigProvider.get_default_config_path()}", file=sys.stderr)

    @classmethod
    def define_config_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            # prog="keylightctl",
            description="Create menus using dmenu-like applications, configured in toml.",
            epilog = "feel free to contribute :)",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        default_config_path = ConfigProvider.get_default_config_path()

        parser.add_argument("-C", "--config", 
                help="path to the config folder where the actions are defined", 
                default=str(default_config_path),
                )
        
        return parser


def main():
    CLI().run()