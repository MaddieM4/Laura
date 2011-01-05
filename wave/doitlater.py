import models

from google.appengine.api.labs import taskqueue

def load_wavelet(wave_id, wavelet_id):
	''' Load a wavelet from the Google Wave server and into cold storage,
	then start a process-wavelet task.'''
	proc_db("load-wavelet",models.getDBWavelet(wave_id,wavelet_id))

def process_wavelet(dbw):
	''' Start an insert-blip task for every blip in the freeze '''
	proc_db("process-wavelet",dbw)

def insert_blip(dbw, id):
	''' Takes a freeze and a blip ID '''
	add_task("insert-blip", {
		'wavelet':str(dbobj.key()),
		'blip_id':id
	})

def proc_db(queue_name, dbobj):
	add_task(queue_name, {'key':str(dbobj.key())})

def add_task(name, payload):
	taskqueue.add(url = "/queue/"+name,
		queue_name = name,
		params = payload)
