# models
import logging

import urllib
from django.utils import simplejson as json

from google.appengine.ext import db
from google.appengine.api import urlfetch
from waveapi import wavelet as apiwavelet

class DBWavelet(db.Models):
	''' A wavelet in cold storage. Never trust one of these babies to be
	100% accurate - remember, it's a snapshot, growing increasingly 
	irrelevant the longer it's in here.'''
	wave_id = db.StringProperty()
	wavelet_id = db.StringProperty()
	jsoncontent = db.TextProperty()

class Fingerprint(db.Model):
	corekey = db.StringProperty()
	wavelet = db.ReferenceProperty(DBWavelet)
	blip = db.StringProperty()
	parentblip = db.StringProperty()

class ResponsePending(db.Model):
	corekey = db.StringProperty()
	response_to = db.ReferenceProperty(Fingerprint)

def fetch(url, payload):
	logging.info(url)
	logging.info(payload)
	return urlfetch.fetch(url, 
		payload=urllib.urlencode(payload), 
		method=urlfetch.POST, 
		headers={'Content-Type': 'application/x-www-form-urlencoded'})

def insert(blip, respond):
	# Pull out details from blip
	id = blip.blip_id
	wave = blip.wave_id
	wavelet = blip.wavelet_id
	text = blip.text
	author = blip.creator
	parent = blip.parent_blip_id
	# Send to core
	url = "http://laura-robot.appspot.com/api/insert"
	payload = {'parent':parent,'text':text,'author':author}
	if respond:
		payload['responseurl']='http://laura-wavebot.appspot.com/forward'
	result = fetch(url, payload)
	rdict = json.loads(result.content)
	# Insert into DB
	f = Fingerprint(corekey = rdict['inserted'],
		wavelet = getDBWavelet(wave,wavelet),
		blip = id,
		parentblip = parent).put()
	if respond:
		ResponsePending(corekey = rdict['response'],
			response_to = f).put()
	# cancel any response to parent
	parent = Fingerprint.all().filter('blip =',parentblip).filter('wave =',wave).filter('wavelet =',wavelet).fetch(1)
	for i in parent.responsepending_set:
		cancel(i)

def cancel(response):
	# Send to core
	url = "http://laura-robot.appspot.com/api/cancel"
	payload={'key':response.corekey}
	fetch(url, payload)
	response.delete()

def get(strkey):
	return db.get(db.Key(strkey))

def getDBWavelet(wave, wavelet):
	''' Finds a DBWavelet with the ID information given, or creates one
	with no value set to jsoncontent.'''
	try:
		return DBWavelet.all().filter('wave_id =',wave).filter(
			'wavelet_id',wavelet).fetch(1)[0]
	except IndexError:
		return DBWavelet(wave_id=wave, wavelet_id=wavelet)

def storeWavelet(wavelet):
	''' Takes an API wavelet and returns a DBWavelet '''
	w = getDBWavelet(wavelet.wave_id, wavelet.wavelet_id)
	w.jsoncontent = json.dumps(w.serialize())
	w.put()
	return w

def getWavelet(wave, wavelet):
	return getWaveletFromFreeze(getDBWavelet(wave,wavelet))

def getWaveletFromFreeze(freeze):
	''' Returns an API wavelet converted from a cold-storage DBWavelet '''
	return apiwavelet.Wavelet(json=freeze.jsoncontent)
