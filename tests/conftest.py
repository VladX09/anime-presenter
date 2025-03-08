import pathlib
from distutils.dir_util import copy_tree

import pytest


@pytest.fixture
def resources(tmp_path: pathlib.Path) -> pathlib.Path:
    tmp_path = tmp_path / "resources"
    resources_src = pathlib.Path(__file__).parent / "resources"
    copy_tree(src=resources_src, dst=tmp_path)

    return tmp_path
