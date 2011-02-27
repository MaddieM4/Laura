from waveapi import robot

def make():
	return robot.Robot('Laura the Robot',
		image_url='http://laura-wavebot.appspot.com/static/icon.png',
		profile_url='http://code.google.com/apis/wave/')

def authorize(robot):
	robot.setup_oauth(
		'147574063686',
		'XruAeiKIi51GgiWbG1VVbVgq',
		server_rpc_base="http://www-opensocial.googleusercontent.com/api/rpc"
		)

def make_authorized():
	r = make()
	authorize(r)
	return r
