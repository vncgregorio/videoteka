"""Version information for Videoteka."""

__version__ = "1.2.2"
__version_info__ = (1, 2, 2)

# Version components
MAJOR = 1
MINOR = 2
PATCH = 1

def get_version():
    """Get the version string."""
    return __version__

def get_version_info():
    """Get the version tuple."""
    return __version_info__
