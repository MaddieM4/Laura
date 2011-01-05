# forward
import makerobot
import models

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Forwarder(webapp.RequestHandler):
	def post(self):
		corekey = self.request.get('key')
		text = self.request.get('reply')
		parent_f = models.get(corekey).response_to
		laura = makerobot.make_authorized()		
		wavelet = laura.fetch_wavelet(parent_f.wave, wavelet_id=parent_f.wavelet)
		for i in wavelet.blips:
			if i.blip_id == parent_f.blip:
				models.insert(i.reply(text), False)
				break

def main():
run_wsgi_app(webapp.WSGIApplication([
        ('/forward', Forwarder),
        ('/forward/', Forwarder),
    ]))

if __name__ == '__main__':
    main()
