"""Module for search functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
from filters.players import PlayerIter


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def find_player_with_name(name):
	"""Returns player with name or None if not found."""
    for player in PlayerIter():
        if not player.is_fake_client():
            if name.lower() in player.name.lower():
                return player
