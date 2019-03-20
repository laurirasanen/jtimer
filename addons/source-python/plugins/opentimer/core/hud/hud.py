from players.helpers import index_from_userid
from messages import HintText
from engines.server import server
from ..players import state

def draw_timer(player):
	text = None

	if player.state.timer_mode == state.Timer_Mode.MAP:
		if player.state.map_state == state.Run_State.START:
			text = HintText('map start')
		elif player.state.map_state == state.Run_State.RUN:
			text = HintText(f'map time: {server.tick - player.state.map[1]}')
		elif player.state.map_state == state.Run_State.END:
			text = HintText(f'map end, time: {player.state.map[2] - player.state.map[1]}')

	elif player.state.timer_mode == state.Timer_Mode.COURSE:
		if player.state.course_state == state.Run_State.START:
			text = HintText('course start')
		elif player.state.course_state == state.Run_State.RUN:
			text = HintText(f'course time: {server.tick - player.state.courses[0][1]}')
		elif player.state.course_state == state.Run_State.END:
			text = HintText(f'course end, time: {player.state.courses[0][2] - player.state.courses[0][1]}')

	elif player.state.timer_mode == state.Timer_Mode.BONUS:
		if player.state.bonus_state == state.Run_State.START:
			text = HintText('bonus start')
		elif player.state.bonus_state == state.Run_State.RUN:
			text = HintText(f'bonus time: {server.tick - player.state.bonus[1]}')
		elif player.state.bonus_state == state.Run_State.END:
			text = HintText(f'bonus end, time: {player.state.bonus[2] - player.state.bonus[1]}')

	else:
		text = HintText('timer disabled')

	# draw
	if text != None:
		text.send(index_from_userid(player.userid))