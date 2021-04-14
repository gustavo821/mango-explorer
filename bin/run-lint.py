#!/usr/bin/env python3

import os
import sys

from pathlib import Path
from os.path import isfile, join

# Get the full path to this script.
script_path = Path(os.path.realpath(__file__))

# The parent of the script is the bin directory, the parent of that is the
# notebook directory. It's this notebook directory we want.
notebook_directory = script_path.parent.parent
print(f"Linting notebook files in: {notebook_directory}")

# But we want to lint every notebook just to make sure the code in it is OK.
all_notebook_files = [f for f in os.listdir(notebook_directory) if isfile(
    notebook_directory / f) and f.endswith(".ipynb")]

all_notebook_files.sort()

try:
    # Now lint each notebook in turn.
    for notebook_name in all_notebook_files:
        print(f"Linting {notebook_name}...", flush=True)
        command = f'nblint --linter pyflakes {notebook_name} | grep -v -E "Code Cell [0-9]+ that starts with" | grep -v "may be undefined" | grep -v "projectsetup" | grep -v "unable to detect undefined names" | sed "/^[[:space:]]*$/d"'
        os.system(command)
except Exception as ex:
    print(f"Caught exception: {ex}")

tmpfile = notebook_directory / "tmp.py"
if os.path.exists(tmpfile):
    os.unlink(tmpfile)

print("All linting complete.")
