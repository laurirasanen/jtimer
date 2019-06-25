"""Module for parsing and holding plugin config."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
from configparser import ConfigParser

# Source.Python Imports
from cvars import ConVar

# Custom Imports
from .constants.paths import CFG_PATH

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
PARSER = ConfigParser()

CORE_CFG_FILE = CFG_PATH / "core.ini"
PARSER.read(CORE_CFG_FILE)
API_CFG = dict(PARSER.items("api"))

# validate stuff
assert "host" in API_CFG
assert "authenticate" in API_CFG

# convert to bool
try:
    API_CFG["authenticate"] = PARSER.getboolean("api", "authenticate")
except ValueError:
    API_CFG["authenticate"] = False

if API_CFG["authenticate"]:
    assert "username" in API_CFG
    assert "password" in API_CFG

# cvars
CVAR_CFG = dict(PARSER.items("cvar"))
for cvar in CVAR_CFG.keys():
    c = ConVar(cvar).set_string(CVAR_CFG[cvar])
