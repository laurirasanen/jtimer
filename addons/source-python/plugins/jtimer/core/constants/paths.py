from paths import TRANSLATION_PATH as _TRANSLATION_PATH

from .info import info

__all__ = ("TRANSLATION_PATH",)

TRANSLATION_PATH = _TRANSLATION_PATH / info.name
