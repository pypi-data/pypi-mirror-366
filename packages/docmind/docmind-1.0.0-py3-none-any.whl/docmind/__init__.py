"""DocMind: AI-optimized document converter for technical documents."""

__version__ = "1.0.0"
__author__ = "Mount"
__email__ = "simon@mount.agency"

from .converter import DocMind
from .config import DocMindConfig, load_config, get_preset_config

__all__ = ["DocMind", "DocMindConfig", "load_config", "get_preset_config"]