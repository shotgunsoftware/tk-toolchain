import os
import subprocess

from tk_build import repo
from tk_build.cmd_line_tools import tk_docs
from tk_build.cmd_line_tools import tk_flake8


def main():

    subprocess.check_call(["pytest", "--cov"])

    # If there is documentation, run it.
    if os.path.exists(os.path.join(repo.find_repo_root(), "docs")):
        tk_docs.main()

    tk_flake8.main()


if __name__ == "__main__":
    main()
