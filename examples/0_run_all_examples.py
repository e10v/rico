"""Run all the example scripts.

Removes all HTML files before running the scripts.
"""

import os
import subprocess


EXAMPLES_DIR = "examples"


if __name__ == "__main__":
    for file in os.listdir(EXAMPLES_DIR):
        if file.endswith(".html"):
            os.remove(os.path.join(EXAMPLES_DIR, file))

    for file in os.listdir(EXAMPLES_DIR):
        if file.endswith(".py") and not file.startswith("0_"):
            subprocess.run(["python", os.path.join(EXAMPLES_DIR, file)])
