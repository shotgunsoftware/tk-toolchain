from __future__ import print_function
import os
import subprocess
import yaml

from tk_build import repo, ci
from tk_build.cmd_line_tools import tk_docs


def _print_header(text):
    print("=" * 79)
    print(text)
    print("=" * 79)


def main():

    suffix = None
    if ci.is_travis():
        suffix = os.path.expandvars(
            "travis_${TRAVIS_EVENT_TYPE}_${SHOTGUN_QT_LIBRARY}"
        )
    elif ci.is_appveyor:
        # TODO: Our builds do not run in parallel on appveyor so keep simple for now.
        suffix = "app_veyor"

    _print_header("Running tests...")

    subprocess.check_call(["pytest", "--cov"], env=env)

    repo_root = repo.find_repo_root()

    # If there is documentation, run it.
    if os.path.exists(os.path.join(repo_root, "docs")):
        print()
        _print_header("Generating documentation...")
        tk_docs.main()

    # Run any extra build comments from the .tx-build.yml file.
    tk_build_path = os.path.join(repo_root, ".tk-build.yml")
    if os.path.exists(tk_build_path):
        with open(tk_build_path, "rt") as fh:
            data = yaml.safe_load(fh)

        if suffix is not None:
            os.environ["SHOTGUN_TEST_ENTITY_SUFFIX"] = suffix

        for command in data.get("script") or []:
            print(command)
            os.system(command)


if __name__ == "__main__":
    main()
