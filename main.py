import logging

from waveapi import events
from waveapi import robot
from waveapi import appengine_robot_runner

import markov
import dbtools

def OnWaveletSelfAdded(event, wavelet):
	# Add all blips in wave to fingerprint database
	for i in wavelet.blips:
		dbtools.analyze_blip(i)

def OnBlipSubmitted(properties, wavelet):
	# Add new blip to database and set up to reply to it
	blip = wavelet.GetBlipById(properties['blipId'])
	dbtools.start_reply(blip)

if __name__ == '__main__':
	laura = robot.Robot('Laura the Robot',
		image_url='http://laura-robot.appspot.com/static/icon.png',
		profile_url='http://code.google.com/apis/wave/')

	laura.register_handler(events.WaveletSelfAdded, OnWaveletSelfAdded)
	laura.register_handler(events.BlipSubmitted, OnBlipSubmitted)
	appengine_robot_runner.run(laura)
