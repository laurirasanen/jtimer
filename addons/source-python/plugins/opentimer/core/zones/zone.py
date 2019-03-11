import mathlib
import math

class Zone():
    def __init__(self, zone_id, center=mathlib.NULL_VECTOR, extents=mathlib.NULL_VECTOR):
        self.center = center
        self.extents = extents      

    def is_overlapping(self, other_center, other_extents):
        """AABB-AABB test
        (check if distance between centers is less than extents of both objects)"""
        x = abs(self.center[0] - other_center[0]) <= (self.extents[0] + other_extents[0]);
        y = abs(self.center[1] - other_center[1]) <= (self.extents[1] + other_extents[1]);
        z = abs(self.center[2] - other_center[2]) <= (self.extents[2] + other_extents[2]);
     
        return x and y and z