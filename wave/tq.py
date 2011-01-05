import doitlater
import models

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
		freeze = models.storeWavelet(fullwavelet)
		doitlater.process_wavelet(freeze)

class Process(webapp.RequestHandler):
	def post(self):
		# get freeze key
		key = self.request.get('key')
		freeze = models.get(key)
		wavelet = models.getWaveletFromFreeze(freeze)
		for i in wavelet.blips
			doitlater.insert_blip(freeze,i)

class Insert(webapp.RequestHandler):
	def post(self):
		''' Unpack a freeze, find a specific blip, and insert it'''
		# get freeze key
		key = self.request.get('wavelet')
		blipid = self.request.get('blip_id')
		freeze = models.get(key)
		wavelet = models.getWaveletFromFreeze(freeze)
		for i in wavelet.blips
			if i == blipid:
				models.insert(wavelet.blips[i], False)
				return

def main():
    run_wsgi_app(webapp.WSGIApplication([
        ('/queue/load-wavelet', Load),
        ('/queue/process-wavelet', Process),
        ('/queue/insert-blip', Insert)
    ]))

if __name__ == '__main__':
    main()

