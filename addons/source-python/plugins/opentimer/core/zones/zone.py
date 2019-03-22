import mathlib
import math
from engines.server import server
from mathlib import Vector
from effects import box
from filters.recipients import RecipientFilter
from engines.precache import Model

model = Model("sprites/laser.vmt")


class Zone:
    def __init__(self, center=mathlib.NULL_VECTOR, extents=mathlib.NULL_VECTOR):
        self.center = center
        # half-widths
        self.extents = extents
        # opposite corners
        self.bounds = (self.center - self.extents, self.center + self.extents)

    def is_overlapping(self, other_center, other_extents):
        """AABB-AABB test
        (check if distance between centers is less than extents of both objects)"""
        x = abs(self.center[0] - other_center[0]) <= (
            self.extents[0] + other_extents[0]
        )
        y = abs(self.center[1] - other_center[1]) <= (
            self.extents[1] + other_extents[1]
        )
        z = abs(self.center[2] - other_center[2]) <= (
            self.extents[2] + other_extents[2]
        )

        return x and y and z

    def time_to_zone_edge(self, other_center, other_extents, velocity, position_delta):
        """sub-tick time until player bounding box will leave the zone"""

        # max distance travelled in a tick ( sqrt(sqrt(3500^2 + 3500^2) + 3500^2) )
        dist = 91

        if position_delta > dist:
            # player moved more than max velocity, assume teleported
            return 1.0

        # https://gamedev.stackexchange.com/a/18459

        # get closest corner to zone
        corner = self.closest_corner(other_center, other_extents)

        # get normalized direction of player velocity
        direction = Vector.normalized(velocity)

        # for some reason using mathlib.NULL_VECTOR here for dirfrac
        # causes corner vector to get all messed up,
        # i guess mathlib.NULL_VECTOR somehow refers to the same instance

        dirfrac = [0.0, 0.0, 0.0]
        for i in range(0, 3):
            if direction[i] == 0.0:
                dirfrac[i] = float("inf")
            else:
                dirfrac[i] = 1.0 / direction[i]

        # t1, t3, t5
        vt0 = [0.0, 0.0, 0.0]
        for i in range(0, 3):
            vt0[i] = (self.bounds[0][i] - corner[i]) * dirfrac[i]

        # t2, t4, t6
        vt1 = [0.0, 0.0, 0.0]
        for i in range(0, 3):
            vt1[i] = (self.bounds[1][i] - corner[i]) * dirfrac[i]

        # tmin is negative if we're leaving a zone, use abs
        tmin = abs(
            max(max(min(vt0[0], vt1[0]), min(vt0[1], vt1[1])), min(vt0[2], vt1[2]))
        )
        tmax = min(min(max(vt0[0], vt1[0]), max(vt0[1], vt1[1])), max(vt0[2], vt1[2]))

        # if tmax < 0, the whole AABB is behind us,
        # meaning we've already entered/left the zone.
        # this shouldn't happen unless you call this function wrong
        # (not using player values from the tick before zone triggering)
        # we're not going to return negative values though because
        # it MIGHT give players an advantage if they lag or if the server lags.
        if tmax < 0:
            dist = tmax
        else:
            dist = min(tmin, tmax)

        # fraction of ticks to zone edge
        time = dist / (velocity.length * server.tick_interval)
        print(f"tmax: {tmax}, tmin: {tmin}, dist: {dist}, time: {time}")

        # clamp between 0 and 1
        return max(0, min(time, 1))

    def closest_corner(self, other_center, other_extents):
        """get closest corner of other box to ours"""
        corner = mathlib.NULL_VECTOR

        for i in range(0, 3):
            if self.center[i] < other_center[i]:
                corner[i] = other_center[i] - other_extents[i]
            else:
                corner[i] = other_center[i] + other_extents[i]

        return corner

    def move_side(self, axis, end, direction, units):
        """move one of the 6 sides of the zone bounding box inwards or outwards.
        axis = the axis to move on {0, 1, 2}
        end = corner of the bounds to move {0, 1}
        direction = direction of movement on the axis {int}
        units = amount of units to move {int}"""
        if end not in (0, 1):
            end = 0

        if axis not in (0, 1, 2):
            axis = 0

        if direction not in (-1, 1):
            direction = -1

        units = int(round(units))

        self.bounds[end][axis] += direction * units
        self.center = self.bounds[0] + self.bounds[1] / 2
        self.extents = self.bounds[1] - self.center

    def draw(self):
        box(
            RecipientFilter(),
            self.bounds[0],
            self.bounds[1],
            alpha=255,
            blue=0,
            green=255,
            red=0,
            amplitude=0,
            end_width=5,
            life_time=1,
            start_width=5,
            fade_length=0,
            flags=0,
            frame_rate=255,
            halo=model,
            model=model,
            start_frame=0,
        )
