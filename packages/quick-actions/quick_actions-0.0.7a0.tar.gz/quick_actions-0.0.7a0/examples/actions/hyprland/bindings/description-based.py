#!/usr/bin/env python

import subprocess
import json
from pprint import pprint

command = "hyprctl binds -j"

process = subprocess.run(command, shell=True, encoding='utf-8', capture_output = True)

output = json.loads(process.stdout)

only_with_description = [ bind for bind in output if bind["has_description"]]

pprint(only_with_description)


# TODO: generate submanu based on script providing label and action pairs
