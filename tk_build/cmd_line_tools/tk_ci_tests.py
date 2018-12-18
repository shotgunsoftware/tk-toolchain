import os
import warnings

import pytest
from pytest import PytestWarning

from tk_build import ci

from tk_build.cmd_line_tools import tk_docs


def main():

    if os.path.basename(ci.get_cloned_folder_root()) != "tk-build":
        pytest.main(["pytest", "--cov"])
    else: # If the repo we're running in the CI is us, we'll append out coverage instead.
        pytest.main()

    # If there is documentation, run it.
    if os.path.exists(os.path.join(ci.get_cloned_folder_root(), "docs")):
        tk_docs.main()


if __name__ == "__main__":
    main()
