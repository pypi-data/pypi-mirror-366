from quick_actions.config_processing.ConfigProvider import ConfigProvider
from quick_actions.runners.CommandRunner import CommandRunner


class CopyResultDispatcher:
    def __init__(self, result):
        self.config_provider = ConfigProvider.get_instance()

        copy_command_template = self.config_provider.general.copy_command
        command = copy_command_template.replace("{text_to_copy}", result)

        CommandRunner(command, capture_output=False)
