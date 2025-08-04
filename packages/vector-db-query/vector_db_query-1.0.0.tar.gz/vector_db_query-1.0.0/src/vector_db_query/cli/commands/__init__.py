"""CLI commands for Vector DB Query System."""

# Note: Some imports are conditional due to optional dependencies
__all__ = []

try:
    from .process_enhanced import process_command, detect_format
    __all__.extend(["process_command", "detect_format"])
except ImportError:
    pass

try:
    from .vector import vector
    __all__.append("vector")
except ImportError:
    pass

try:
    from .mcp import mcp_group
    __all__.append("mcp_group")
except ImportError:
    pass

try:
    from .interactive import interactive_group
    __all__.append("interactive_group")
except ImportError:
    pass

try:
    from .read import read_command
    __all__.append("read_command")
except ImportError:
    pass

try:
    from .monitor import monitor
    __all__.append("monitor")
except ImportError:
    pass

try:
    from .logging import logging
    __all__.append("logging")
except ImportError:
    pass

try:
    from .formats import formats_command
    __all__.append("formats_command")
except ImportError:
    pass

try:
    from .auth import auth
    __all__.append("auth")
except ImportError:
    pass

try:
    from .api import api
    __all__.append("api")
except ImportError:
    pass