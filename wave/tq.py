import makerobot
import doitlater
import models
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

def load_wavelet(wave_id, wavelet_id):
	robot = makerobot.make_authorized()
	return robot.fetch_wavelet(wave_id, wavelet_id=wavelet_id)

def load_wavelet_key(key):
	dbw = models.get(key)
	return dbw, load_wavelet(dbw.wave_id, dbw.wavelet_id)

class Load(webapp.RequestHandler):
	def post(self):
		key = self.request.get('key')
		self.dbw, fullwavelet = load_wavelet_key(key)
		logging.info(str(len(fullwavelet.blips))+" blips")
		self.thread(fullwavelet.root_thread, None)

	def thread(self, thread, parent):
		cparent = parent
		for blip in thread.blips:
			f = models.finger_blip(blip, 
				cparent, 
				wavelet=self.dbw)
			doitlater.insert(f)
			for rt in blip.reply_threads:
				self.thread(rt, f)
			cparent = f

class Scan(webapp.RequestHandler):
	def get(self):
		freeze = models.Wavelet.all().fetch(1)[0]
		wavelet = load_wavelet(freeze.wave_id, freeze.wavelet_id)
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
		''' Get a specific fingerprint by key, and insert it'''
		# get blip key
		key = self.request.get('key')
		f = models.get(key)
		models.insert(f, False)

class Purge(webapp.RequestHandler):
	def get(self):
		doitlater.purge()

	def post(self):
		models.purge()

def main():
    run_wsgi_app(webapp.WSGIApplication([
        ('/queue/load-wavelet', Load),
        ('/queue/insert-blip', Insert),
        ('/queue/scan', Scan),
        ('/queue/purge', Purge)
    ]))

if __name__ == '__main__':
    main()

