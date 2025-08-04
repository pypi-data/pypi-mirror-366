import os
from glob import glob
from typing import List

_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))


def resource_filenames() -> List[str]:
    files = glob(os.path.join(_SCRIPT_DIR, "*.*"))
    files = [filename for filename in files if filename != __file__]
    return files
