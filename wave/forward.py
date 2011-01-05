# forward
import makerobot
import models

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Forwarder(webapp.RequestHandler):
	def post(self):
		corekey = self.request.get('key')
		text = self.request.get('reply')
		parent_f = models.get_response_by_corekey(corekey).response_to
		laura = makerobot.make_authorized()
		dbw = parent_f.wavelet		
		wavelet = laura.fetch_wavelet(dbw.wave_id, wavelet_id=dbw.wavelet_id)
		for i in wavelet.blips:
			if i == parent_f.blip:
				reply = wavelet.blips[i].continue_thread()
				reply.append_markup(text)
				laura.submit(wavelet)
				models.insert(reply, False, author_override=True)
				break

def main():
	run_wsgi_app(webapp.WSGIApplication([
		('/forward', Forwarder),
		('/forward/', Forwarder)
	]))

if __name__ == '__main__':
	main()
