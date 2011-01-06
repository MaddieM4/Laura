# models
import logging
import makerobot
import urllib
from django.utils import simplejson as json

from google.appengine.ext import db
from google.appengine.api import urlfetch
from waveapi import wavelet as apiwavelet

class Wavelet(db.Model):
	wave_id = db.StringProperty()
	wavelet_id = db.StringProperty()
	activated = db.BooleanProperty(default=True)

class Fingerprint(db.Model):
	corekey = db.StringProperty()
	wavelet = db.ReferenceProperty(Wavelet)
	blip = db.StringProperty()
	parentblip = db.SelfReferenceProperty()
	fulltext = db.TextProperty()
	creator = db.EmailProperty()

class ResponsePending(db.Model):
	corekey = db.StringProperty()
	response_to = db.ReferenceProperty(Fingerprint)

def purge():
	for i in [Wavelet, Fingerprint, ResponsePending]:
		for d in i:
			d.delete()

def fetch(url, payload):
	logging.info(url)
	logging.info(payload)
	return urlfetch.fetch(url, 
		payload=urllib.urlencode(payload), 
		method=urlfetch.POST, 
		headers={'Content-Type': 'application/x-www-form-urlencoded'},
		deadline=10)

class ParentNotInserted(Exception):
	def __init__(self, parent)
		Exception.__init__(self)
		self.fingerprint = parent

	def __str__(self):
		return "Parent Not Inserted: blip %s" % str(self.fingerprint.blip)

def insert(blip, respond):
	# Pull out details from blip
	id = blip.blip
	wavelet = blip.wavelet
	text = blip.fulltext
	parent = blip.parentblip

	# Check for "cheat codes"
	if "ASLAURA" in text:
		author = "laura-wavebot@appspot.com"
		text.replace("ASLAURA","")
	else:
		author = blip.creator

	putwavelet = False
	if "STARTLAURA" in text:
		wavelet.activated = True
		putwavelet = True
		text.replace("STARTLAURA","")
	if "STOPLAURA" in text:
		wavelet.activated = True
		putwavelet = True
		respond = False
		text.replace("STARTLAURA","")
	if putwavelet:
		wavelet.put()

	# Send to core
	url = "http://laura-robot.appspot.com/api/insert"
	payload = {'text':text,'author':author}
	if parent:
		if not parent.corekey:
			raise ParentNotInserted(parent.blip)
		payload['parent'] = parent.corekey
	if respond:
		payload['responseurl']='http://laura-wavebot.appspot.com/forward'
	result = fetch(url, payload)
	logging.info(result.content)
	rdict = json.loads(result.content)
	# Insert into DB
	blip.corekey = rdict['inserted']
	if respond:
		ResponsePending(corekey = rdict['response'],
			response_to = blip).put()
	# cancel any responses to parent
	if parent:
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

def getWavelet(wave, wavelet):
	''' Finds a Wavelet with the ID information given, or creates one
	with no value set to jsoncontent.'''
	try:
		return Wavelet.all().filter('wave_id =',wave).filter(
			'wavelet_id',wavelet).fetch(1)[0]
	except IndexError:
		w = Wavelet(wave_id=wave, wavelet_id=wavelet)
		w.put()
		return w

def get_response_by_corekey(corekey):
	try:
		return ResponsePending.all().filter('corekey =',corekey).fetch(1)[0]
	except IndexError:
		return None

def finger_blip(blip, parent, wavelet=None):
	f = Fingerprint()

	f.blip = blip.blip_id
	if parent:
		f.parentblip = parent
	if wavelet:
		f.wavelet = wavelet
	elif parent and parent.wavelet:
		f.wavelet = parent.wavelet
	f.fulltext = blip.text.strip()
	f.creator = blip.creator
	f.put()
	return f

def load_wavelet(wave_id, wavelet_id):
	robot = makerobot.make_authorized()
	return robot.fetch_wavelet(wave_id, wavelet_id=wavelet_id)

def load_wavelet_key(key):
	dbw = models.get(key)
	return dbw, load_wavelet(dbw.wave_id, dbw.wavelet_id)

