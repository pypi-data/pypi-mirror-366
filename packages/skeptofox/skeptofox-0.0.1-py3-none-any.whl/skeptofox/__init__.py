# skeptofox/__init__.py

import warnings
from importlib.metadata import version, PackageNotFoundError
from packaging.version import Version # Import the Version class

try:
    __version__ = version("skeptofox")
except PackageNotFoundError:
    __version__ = "0.0.0"

class SkeptofoxDevelopmentWarning(UserWarning):
    """Custom warning for the development phase of the skeptofox package."""
    pass

# Correctly compare versions using the Version class
if Version(__version__) < Version("0.1.1"):
    warnings.warn(
        (
            f"You are using skeptofox version {__version__}. "
            "This is a pre-release version for setup and testing only. "
            "Functional features will be available from version 0.1.1 onwards."
        ),
        SkeptofoxDevelopmentWarning,
        stacklevel=2,
    )