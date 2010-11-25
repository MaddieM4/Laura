import logging

from waveapi import events
from waveapi import robot
from waveapi import ops
from waveapi import appengine_robot_runner

def OnWaveletSelfAdded(event, wavelet):
	# Add all blips in wave to fingerprint database
	import dbtools
	fullwavelet = ops.OperationQueue().robot_fetch_wave(wavelet.wave_id, wavelet.wavelet_id)
	logging.info(str(len(fullwavelet.blips))+" blips")
	for i in fullwavelet.blips:
		dbtools.analyze_blip(fullwavelet.blips[i])

def OnBlipSubmitted(event, wavelet):
	# Add new blip to database and set up to reply to it
	import dbtools
	blip = event.blip
	dbtools.start_reply(blip)

if __name__ == '__main__':
	laura = robot.Robot('Laura the Robot',
		image_url='http://laura-robot.appspot.com/static/icon.png',
		profile_url='http://code.google.com/apis/wave/')

	laura.register_handler(events.WaveletSelfAdded, OnWaveletSelfAdded)
	laura.register_handler(events.BlipSubmitted, OnBlipSubmitted,
		context = [events.Context.PARENT, events.Context.SELF])
	appengine_robot_runner.run(laura)
