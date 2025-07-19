import toml
import pathlib

# Read version from pyproject.toml
_pyproject = toml.load(pathlib.Path(__file__).parent.parent.parent / "pyproject.toml")
__version__ = _pyproject["project"]["version"]
