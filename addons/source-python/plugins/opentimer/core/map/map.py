from .course import Course
from .bonus import Bonus
from .checkpoint import Checkpoint
from .segment import Segment

class Map(Segment):
	def __init__(self, tier):
		super().__init__(tier)

	def on_run_start(self, player):
		pass

	def on_run_end(self, player):
		pass

	def on_run_checkpoint(self, player, checkpoint):
		pass