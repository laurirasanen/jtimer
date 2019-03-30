from ..zones.zone import Zone
import mathlib


class Checkpoint(Zone):
    def __init__(
        self, index, p1=mathlib.NULL_VECTOR, p2=mathlib.NULL_VECTOR, orientation=0
    ):
        super().__init__(p1, p2, orientation)
        self.index = index
