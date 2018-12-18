import os
import subprocess

from tk_build import ci
from tk_build.cmd_line_tools import tk_docs


def main():

    subprocess.check_call(["pytest", "--cov"])

    # If there is documentation, run it.
    if os.path.exists(os.path.join(ci.get_cloned_folder_root(), "docs")):
        tk_docs.main()


if __name__ == "__main__":
    main()
