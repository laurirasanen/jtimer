import json

from .constants.paths import CFG_PATH

CORE_CFG_FILE = CFG_PATH / "core.json"
CORE_CFG = None

with CORE_CFG_FILE.open("r") as file:
    CORE_CFG = json.load(file)

API_CFG = CORE_CFG["api"]
