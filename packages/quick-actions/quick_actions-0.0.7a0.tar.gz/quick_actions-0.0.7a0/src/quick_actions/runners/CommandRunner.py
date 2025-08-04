import subprocess
from typing import Dict
import os
from string import Template


class CommandRunner:
    def __init__(self, command: str, envs: Dict = None, print_err: bool = True, shell:bool=True, capture_output:bool=True, timeout: int = 100):
        if envs is not None:
            default_env = os.environ.copy()

            envs={name:os.path.expandvars(value) for name,value in envs.items() }
            envs.update(**default_env)

        self.process = subprocess.run(command, shell=shell, encoding='utf-8', env=envs,
            capture_output = capture_output,
            timeout=timeout
            )

        print(self.output)

        if print_err:
            print(f"{command}: {self.error}")

    @property
    def returncode(self):
        return self.process.returncode

    @property
    def output(self):
        return self.process.stdout

    @property
    def error(self):
        return self.process.stderr

    @staticmethod
    def expand_envs(envs, value):
        print(envs, value)
        # FIXME: disgusting spaghetti
        all_env = {
            **envs,
            **os.environ
        }
        return Template(value).safe_substitute(all_env) 
