import mathlib
import math
from mathlib import Vector

class Zone():
    def __init__(self, center=mathlib.NULL_VECTOR, extents=mathlib.NULL_VECTOR):
        self.center = center
        # half-widths
        self.extents = extents
        # opposite corners
        self.bounds = (self.center - self.extents, self.center + self.extents)

    def is_overlapping(self, other_center, other_extents):
        """AABB-AABB test
        (check if distance between centers is less than extents of both objects)"""
        x = abs(self.center[0] - other_center[0]) <= (self.extents[0] + other_extents[0]);
        y = abs(self.center[1] - other_center[1]) <= (self.extents[1] + other_extents[1]);
        z = abs(self.center[2] - other_center[2]) <= (self.extents[2] + other_extents[2]);
     
        return x and y and z

    def time_to_zone_edge(self, other_center, other_extents, velocity):
        """sub-tick time until player bounding box will leave the zone"""
        # get closest corner to zone
        corner = self.closest_corner(other_center, other_extents)

        # https://gamedev.stackexchange.com/a/18459
        direction = Vector.normalized(velocity)
        dirfrac = mathlib.NULL_VECTOR
        for i in range(0, 3):
            dirfrac[i] = 1.0 / direction[i]
        # t1, t3, t5
        vt0 = (self.bounds[0] - corner)*dirfrac
        # t2, t4, t6
        vt1 = (self.bounds[1] - corner)*dirfrac

        tmin = max(max(min(vt0[0], vt1[0]), min(vt0[1], vt1[1])), min(vt0[2], vt1[2]))
        tmax = min(min(max(vt0[0], vt1[0]), max(vt0[1], vt1[1])), max(vt0[2], vt1[2]))

        # max distance travelled in a tick ( sqrt(sqrt(3500^2 + 3500^2) + 3500^2) )
        t = 91

        # if tmax < 0, ray is intersecting AABB, but the whole AABB is behind us
        if tmax < 0:
            t = tmax

        # if tmin > tmax, ray doesn't intersect AABB
        # this shouldn't happen if we are about to exit or enter it...
        # this function should only be run after the fact, 
        # using player values from the previous tick
        if tmin > tmax:
            t = tmax

        t = tmin

        # fraction of ticks to zone edge
        time = t / velocity.length

        # clamp between 0 and 1
        return max(0, min(time, 1))

    def closest_corner(self, other_center, other_extents):
        """get closest corner of other box to ours"""
        corner = mathlib.NULL_VECTOR

        for i in range(0, 3):
            if self.center[i] - other_center[i] > 0:
                corner[i] = other_center[i] + other_extents[i]
            else:
                corner[i] = other_center[i] - other_extents[i]

        return corner

    def move_side(self, axis, end, direction, units):
        """move one of the 6 sides of the zone bounding box inwards or outwards.
        axis = the axis to move on {0, 1, 2}
        end = corner of the bounds to move {0, 1}
        direction = direction of movement on the axis {int}
        units = amount of units to move {int}"""
        if end not in (0, 1):
            end = 0

        if axis not in (0,1,2):
            axis = 0

        if direction not in (-1, 1):
            direction = -1

        units = int(round(units))

        self.bounds[end][axis] += direction * units
        self.center = self.bounds[0] + self.bounds[1] / 2
        self.extents = self.bounds[1] - self.center