"""Maps plugin name as a subdirectory to paths.
i.e. 	   /resource/source-python/translations/jtimer/chat_strings.ini
instead of /resource/source-python/translations/chat_strings.ini"""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
from paths import TRANSLATION_PATH as _TRANSLATION_PATH, CFG_PATH as _CFG_PATH

# Custom Imports
from .info import info

# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("TRANSLATION_PATH", "CFG_PATH")

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
TRANSLATION_PATH = _TRANSLATION_PATH / info.name
CFG_PATH = _CFG_PATH / info.name
