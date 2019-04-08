"""Module for checkpoints."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
import mathlib

# Custom Imports
from ..zones.zone import Zone


# =============================================================================
# >> CHECKPOINT CLASS
# =============================================================================
class Checkpoint(Zone):
    def __init__(
        self, index, p1=mathlib.NULL_VECTOR, p2=mathlib.NULL_VECTOR, orientation=0
    ):
        """Create a new checkpoint."""
        super().__init__(p1, p2, orientation)
        self.index = index
