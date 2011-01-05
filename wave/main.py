import makerobot
import models
import doitlater
import logging

from waveapi import events
from waveapi import appengine_robot_runner

def OnWaveletSelfAdded(event, wavelet):
	# Add all blips in wave to fingerprint database
	doitlater.load_wavelet(wavelet.wave_id, wavelet.wavelet_id)
#	for i in fullwavelet.blips:
#		models.insert(fullwavelet.blips[i], False)

def OnBlipSubmitted(event, wavelet):
	# Add new blip to database and set up to reply to it
	models.insert(event.blip, True)

if __name__ == '__main__':
	laura = makerobot.make()
	laura.register_handler(events.WaveletSelfAdded, OnWaveletSelfAdded)
	laura.register_handler(events.BlipSubmitted, OnBlipSubmitted,
		context = [events.Context.PARENT, events.Context.SELF])
	appengine_robot_runner.run(laura)
