import makerobot
import doitlater
import models
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Load(webapp.RequestHandler):
	def post(self):
		key = self.request.get('key')
		self.dbw, fullwavelet = models.load_wavelet_key(key)
		logging.info(str(len(fullwavelet.blips))+" blips")
		self.thread(fullwavelet.root_thread, None)

	def thread(self, thread, parent):
		cparent = parent
		for blip in thread.blips:
			f = models.finger_blip(blip, 
				cparent, 
				wavelet=self.dbw)
			if cparent == None:
				# root blip
				doitlater.insert_blip(f)
			for rt in blip.reply_threads:
				self.thread(rt, f)
			cparent = f

class Find(webapp.RequestHandler):
	def post(self):
		key = self.request.get('wavelet')
		self.blip_id = self.request.get('blip_id')
		self.dbw, fullwavelet = models.load_wavelet_key(key)
		parent_id = self.thread(fullwavelet.root_thread, None)
		if not parent_id:
			logging.info("Hopeless case, parent no longer exists")
		if parent_id == "root":
			parent_id = None
		parent = models.Fingerprint.all().filter('wavelet =',
			self.dbw).filter('blip =',parent_id).fetch(1)[0]
		blip = fullwavelet.blips[self.blip_id]
		f = models.finger_blip(blip, parent, wavelet=self.dbw)
		models.insert(f, True)

	def thread(self, thread, parent):
		cparent = parent
		for blip in thread.blips:
			if blip.blip_id == self.blip_id:
				if cparent:
					return cparent.blip_id
				else:
					return "root"
			for rt in blip.reply_threads:
				threadresult = self.thread(rt, blip)
				if threadresult:
					return threadresult
			cparent = blip
		return None

class Insert(webapp.RequestHandler):
	def post(self):
		''' Get a specific fingerprint by key, and insert it'''
		# get blip key
		key = self.request.get('key')
		f = models.get(key)
		models.insert(f, False)
		for i in f.fingerprint_set:
			# process children
			doitlater.insert_blip(i)

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

class Purge(webapp.RequestHandler):
	def get(self):
		doitlater.purge()
		self.response.out.write("purge initiated")

	def post(self):
		models.purge()

def main():
    run_wsgi_app(webapp.WSGIApplication([
        ('/queue/load-wavelet', Load),
        ('/queue/insert-blip', Insert),
        ('/queue/find-blip', Find),
        ('/queue/scan', Scan),
        ('/queue/purge', Purge)
    ]))

if __name__ == '__main__':
    main()

