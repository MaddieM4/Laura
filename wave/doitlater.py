import models

from google.appengine.api.labs import taskqueue

def load_wavelet(wave_id, wavelet_id):
	''' Load a wavelet from the Google Wave server and set up blip tasks'''
	wavelet = models.getWavelet(wave_id,wavelet_id)
	proc_db("load-wavelet",wavelet)

def find_blip(wave_id, wavelet_id, blip_id):
	''' Find and insert a blip by the wave, wavelet, and blip IDs '''
	wavelet = models.getWavelet(wave_id,wavelet_id)
	add_task("find-blip", {
		'wavelet':str(wavelet.key()),
		'blip_id':blip_id
	})

def insert_blip(dbw, id):
	''' Takes a freeze and a blip ID '''
	add_task("insert-blip", {
		'wavelet':str(dbw.key()),
		'blip_id':id
	})

def purge():
	add_task("purge",{})

def proc_db(queue_name, dbobj):
	add_task(queue_name, {'key':str(dbobj.key())})

def add_task(name, payload):
	taskqueue.add(url = "/queue/"+name,
		queue_name = name,
		params = payload)
