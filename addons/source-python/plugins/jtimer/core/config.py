from configparser import ConfigParser

from .constants.paths import CFG_PATH

parser = ConfigParser()

CORE_CFG_FILE = CFG_PATH / "core.ini"
parser.read(CORE_CFG_FILE)
API_CFG = dict(parser.items("api"))

# validate stuff
assert "host" in API_CFG
assert "upload" in API_CFG
if API_CFG["upload"]:
	assert "username" in API_CFG
	assert "password" in API_CFG