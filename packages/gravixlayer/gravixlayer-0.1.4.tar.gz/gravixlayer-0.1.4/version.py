"""Version information for GravixLayer SDK"""

__version__ = "0.1.11"
__version_info__ = tuple(int(x) for x in __version__.split('.'))

# Version history
VERSION_HISTORY = {
    "0.1.0": "Initial release with OpenAI compatibility",
    "0.1.1": "Fixed URL endpoint routing for chat completions",
    # Add future versions here
    "0.1.1": "Initial",
    "0.1.2": "Initial",
    "0.1.3": "Initial",
    "0.1.4": "Initial",
    "0.1.5": "Initial",
    "0.1.6": "Fixed",
    "0.1.7": "Fixed API endpoint routing",
    "0.1.8": "Fixed",
    "0.1.9": "Test",
    "0.1.10": "Test",
    "0.1.11": "Test",
}

def get_version_info():
    """Get current version information"""
    return {
        "version": __version__,
        "version_info": __version_info__,
        "description": VERSION_HISTORY.get(__version__, "No description available")
    }
