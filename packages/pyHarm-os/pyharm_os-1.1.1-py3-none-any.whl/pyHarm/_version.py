from importlib.metadata import version, PackageNotFoundError
# Extract the package name from the current module's name
__distribution_name__ = "pyHarm-os"
__package_name__ = "pyHarm"
try:
    __version__ = version(__distribution_name__)
except PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"
