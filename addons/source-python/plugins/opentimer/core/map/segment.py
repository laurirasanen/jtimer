from ..zones.zone import Zone
from .checkpoint import Checkpoint

class Segment():
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

	def on_run_start(self, player):
		pass

	def on_run_end(self, player):
		pass

	def on_run_checkpoint(self, player, checkpoint):
		pass