from typing import Dict

from quick_actions.config_processing.config_classes.Action import Action
from quick_actions.runners.CommandRunner import CommandRunner
from quick_actions.config_processing.ConfigProvider import ConfigProvider
from quick_actions import constants
from quick_actions.runners.MenuRunner import MenuRunner
from quick_actions.orderer.AbstractOrderer import AbstractOrderer
from quick_actions.orderer.FrecencyOrderer import FrecencyOrderer


class WhatToDoMenu(MenuRunner):
    def __init__(self):
        self.config_provider = ConfigProvider.get_instance()
        self.orderer: AbstractOrderer = FrecencyOrderer.get_instance()

        self.actions_by_decorated_label = self.build_menuline_dict()
        sorted_decorated_labels = self.sort_labels()

        actions_str = "\n".join(sorted_decorated_labels)

        menu_prompt = self.config_provider.general.display_settings.menu_prompt
        super().__init__(actions_str, menu_prompt)

    def sort_labels(self):
        # TODO: move into sorter class
        return sorted(
            self.actions_by_decorated_label.keys(), 
            key=lambda label: self.orderer.score_of(
                self.actions_by_decorated_label[label].id
            ),
            reverse = True
        )

    def build_menuline_dict(self) -> Dict[str, Action]:
        actions = self.config_provider.actions

        return {f'{self.style_label(x.label)} {self.style_id(x.id)} {self.style_prefix(x.prefix)} {self.style_tags(x.tags)} '.strip():x for x in actions.values()}

    def style_label(self, label):
        label_template = self.config_provider.general.display_settings.label_style
        return label_template.replace("{label}", label)

    def style_id(self, id):
        if not self.config_provider.general.display_settings.show_ids:
            return ""
        id_template = self.config_provider.general.display_settings.id_style
        return id_template.replace("{id}", id)

    def style_tags(self, tags):
        if not self.config_provider.general.display_settings.show_tags:
            return ""

        tag_template = self.config_provider.general.display_settings.tag_style
        tag_separator = self.config_provider.general.display_settings.tag_separator


        tags_decorated = [tag_template.replace("{tag}", tag) for tag in tags]
        return tag_separator.join(tags_decorated)

    def style_prefix(self, prefix):
        if not self.config_provider.general.display_settings.show_prefixes or prefix is None:
            return ""
        
        prefix_template = self.config_provider.general.display_settings.prefix_style

        return prefix_template.replace("{prefix}", prefix)

