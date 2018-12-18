from __future__ import print_function
import os
import subprocess

from tk_build import repo
from tk_build.cmd_line_tools import tk_docs


def _print_header(text):
    print("=" * 79)
    print(text)
    print("=" * 79)


def main():

    _print_header("Running tests...")

    subprocess.check_call(["pytest", "--cov"])

    # If there is documentation, run it.
    if os.path.exists(os.path.join(repo.find_repo_root(), "docs")):
        print()
        _print_header("Generating documentation...")
        tk_docs.main()


if __name__ == "__main__":
    main()
