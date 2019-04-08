"""Module for base Segments."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Custom Imports
from ..zones.zone import Zone


# =============================================================================
# >> SEGMENT CLASS
# =============================================================================
class Segment:
    """Base Segment for Maps, Courses and Bonuses"""

    def __init__(self, stier, dtier):
        """Create a new Segment."""
        self.stier = stier
        self.dtier = dtier
        self.checkpoints = []
        self.start_zone = Zone()
        self.end_zone = Zone()

    def add_checkpoint(self, checkpoint):
        """Add a checkpoint to the Segment."""
        self.checkpoints.append(checkpoint)

    def add_start_zone(self, zone):
        """Add a start zone to the Segment."""
        self.start_zone = zone

    def add_end_zone(self, zone):
        """Add a end zone to the Segment."""
        self.end_zone = zone
