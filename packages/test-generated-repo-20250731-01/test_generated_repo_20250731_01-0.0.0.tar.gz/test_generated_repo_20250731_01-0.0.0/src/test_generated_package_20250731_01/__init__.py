"""test_generated_repo_20250731_01 package."""

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    # Python < 3.8 fallback - not covered in standard test suite
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("test_generated_repo_20250731_01")
except PackageNotFoundError:  # pragma: no cover
    # Package not installed, fallback to development version
    # This path is handled by the build and install process
    __version__ = "dev"

__all__ = ["__version__"]
