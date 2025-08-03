# yaapp - Yet Another Python Package
# A library bridging FastAPI and CLI interfaces

# Simple external API - just two things:
from .expose import expose
from .run import run

__version__ = "0.0.31"
__all__ = [
    "expose",  # For plugin writers: from yaapp import expose
    "run",     # For app users: from yaapp import run
]