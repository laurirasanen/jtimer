"""Maps plugin name as a subdirectory to paths.
i.e. 	   /resource/source-python/translations/jtimer/chat_strings.ini
instead of /resource/source-python/translations/chat_strings.ini"""

from paths import TRANSLATION_PATH as _TRANSLATION_PATH, CFG_PATH as _CFG_PATH

from .info import info

__all__ = ("TRANSLATION_PATH", "CFG_PATH")

TRANSLATION_PATH = _TRANSLATION_PATH / info.name
CFG_PATH = _CFG_PATH / info.name
