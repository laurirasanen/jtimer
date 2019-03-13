from ..zones.zone import Zone
from .checkpoint import Checkpoint

class Course():
	def __init__(self, tier):
		super().__init__(tier)

	def on_run_start(self, player):
		pass

	def on_run_end(self, player):
		pass

	def on_run_checkpoint(self, player, checkpoint):
		pass