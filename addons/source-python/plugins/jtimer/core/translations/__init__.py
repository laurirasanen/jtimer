"""Module for holding translation chat strings."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
from translations.strings import LangStrings

# Custom Imports
from ..constants.paths import TRANSLATION_PATH

# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = ("chat_strings",)

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
chat_strings = LangStrings(TRANSLATION_PATH / "chat_strings")
