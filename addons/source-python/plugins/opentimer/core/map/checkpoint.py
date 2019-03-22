from ..zones.zone import Zone
import mathlib


class Checkpoint(Zone):
    def __init__(
        self, zone_id, cp_num, center=mathlib.NULL_VECTOR, extents=mathlib.NULL_VECTOR
    ):
        super().__init__(zone_id, center, extents)
        self.cp_num = cp_num
