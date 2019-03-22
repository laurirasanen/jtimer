from ..zones.zone import Zone


class Segment:
    def __init__(self, tier):
        self.tier = tier
        self.checkpoints = []
        self.start_zone = Zone()
        self.end_zone = Zone()

    def add_checkpoint(self, checkpoint):
        self.checkpoints.append(checkpoint)

    def add_start_zone(self, zone):
        self.start_zone = zone

    def add_end_zone(self, zone):
        self.end_zone = zone
