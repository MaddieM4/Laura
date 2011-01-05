import makerobot
import doitlater
import models
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Load(webapp.RequestHandler):
	def post(self):
		# get freeze key
		key = self.request.get('key')
		freeze = models.get(key)
		# load from server
		laura = makerobot.make_authorized()
		fullwavelet = laura.fetch_wavelet(freeze.wave_id,wavelet_id=freeze.wavelet_id)
		logging.info(str(len(fullwavelet.blips))+" blips")
		# save JSON to freeze
		logging.info(fullwavelet)
		freeze = models.storeWavelet(fullwavelet)
		doitlater.process_wavelet(freeze)

class Process(webapp.RequestHandler):
	def post(self):
		# get freeze key
		key = self.request.get('key')
		freeze = models.get(key)
		wavelet = models.getWaveletFromFreeze(freeze)
		for i in wavelet.blips:
			doitlater.insert_blip(freeze,i)

class Scan(webapp.RequestHandler):
	def get(self):
		freeze = models.DBWavelet.all().fetch(1)[0]
		wavelet = models.getWaveletFromFreeze(freeze)
		self.analyze(wavelet)
		self.analyze(wavelet.root_thread)
		for i in wavelet.blips:
			self.analyze(wavelet.blips[i])

	def analyze(self, object):
		self.response.out.write(str(type(object))+"\n")
		for slot in dir(object):
			self.response.out.write("%s:\t%s\n" % (slot,
				str(getattr(object,slot)) ))

class Insert(webapp.RequestHandler):
	def post(self):
		''' Unpack a freeze, find a specific blip, and insert it'''
		# get freeze key
		key = self.request.get('wavelet')
		blipid = self.request.get('blip_id')
		freeze = models.get(key)
		wavelet = models.getWaveletFromFreeze(freeze)
		for i in wavelet.blips:
			if i == blipid:
				models.insert(wavelet.blips[i], False)
				return

def main():
    run_wsgi_app(webapp.WSGIApplication([
        ('/queue/load-wavelet', Load),
        ('/queue/process-wavelet', Process),
        ('/queue/insert-blip', Insert),
        ('/queue/scan', Scan)
    ]))

if __name__ == '__main__':
    main()

