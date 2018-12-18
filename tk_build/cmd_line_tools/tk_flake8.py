"""
usage: tk-flake8 [--diff=<commit-branch-tag>] [--] [<flake8-args>...]

Runs flake8 against the source code. If the flake8 configuration file contains diffcompare=True
then validation will be run only on lines modified from the origin/master branch.

Arguments <flake8-args> passed after -- will be passed to flake8 directly. tk-flake8 will take care
of passing down --diff and the diff when required.

Options:
 --diff commit-branch-tag -d commit-branch-tag      Run Flake8 against another branch. Defaults to origin/master
""" # noqa

import sys
import subprocess
from docopt import docopt


from tk_build import ci, github, repo


def tk_flake8(commit=None, flake8_args=None):
    flake8_args = flake8_args or []

    # If the user didn't pass in a commit.
    if commit is None:
        # TODO: This should probably be read from a configuration file
        # in case we're working for a long time against
        # a branch other than origin/master.
        # "origin/master"
        commit = "origin/master"
        # When we're in a CI environment, we want to diff against
        # what the a request is using as the base for the diff.
        if ci.is_in_ci_environment():
            # FIXME: Possible parameter injection?
            subprocess.check_call(["git", "fetch", "origin", "master"])

    flake8_cmd = ["flake8"]
    if commit is not None:
        # TODO: We could do so much better here and ask for a diff against only
        # the files that flake8 will be validating. For now we'll diff the
        # entire repo, which shouldn't take long anyway.
        flake8_stdin = subprocess.check_output(
            ["git", "diff", commit, "--", repo.find_repo_root()]
        )
        flake8_cmd.append("--diff")
    else:
        flake8_stdin = ""

    flake8_cmd.extend(flake8_args)

    # Redirect the output of STDERR into STDOUT and send the diff to flake8.
    proc = subprocess.Popen(
        flake8_cmd,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    stdout, _ = proc.communicate(flake8_stdin)
    if stdout:
        print(stdout)
    sys.exit(proc.returncode)


def main():
    arguments = docopt(__doc__, version="0.0.1")
    tk_flake8(arguments["--diff"], arguments["<flake8-args>"])


if __name__ == "__main__":
    main()
