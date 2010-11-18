import logging

from waveapi import events
from waveapi import robot
from waveapi import appengine_robot_runner

def authorize():
	robot.setup_oauth(
		269341747276,
		'TLICc/8M9DzMOBRyzar+EfEZ',
		server_rpc_base="http://www-opensocial.googleusercontent.com/api/rpc"
		)

def OnWaveletSelfAdded(event, wavelet):
	# Add all blips in wave to fingerprint database
	pass

def OnBlipSubmitted(event, wavelet):
	# Add new blip to database
	# Connect fingerprint to all previous fingerprints
	# Build response fingerprint
	# Use response fingerprint to reply
	pass

if __name__ == '__main__':
	laura = robot.Robot('Laura the Robot',
		image_url='http://laura-robot.appspot.com/static/icon.png',
		profile_url='http://code.google.com/apis/wave/')

	laura.register_handler(events.WaveletSelfAdded, OnWaveletSelfAdded)
	laura.register_handler(events.BlipSubmitted, OnBlipSubmitted)
	appengine_robot_runner.run(laura)
