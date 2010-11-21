import .
import doitlater
import models
import markov

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from waveapi import robot

class Markovify(webapp.RequestHandler):
	def post(self):
		fingerprint = models.fromkey(self.request.get('key'))
		markov.build_fingerprint(fingerprint)

class Compare(webapp.RequestHandler):
	def post(self):
		''' Compare two already-markovized fingerprints '''

class Build(webapp.RequestHandler):
	def post(self):
		response = self.request.get('response')
		sample = self.request.get('sample')

class Respond(webapp.RequestHandler):
	def post(self):

class Compare_Expand(webapp.RequestHandler):
	def post(self):
		expand(self.request.get('key'),
			self.request.get('offset'),
			doitlater.compareE50_expand)

class Build_Expand(webapp.RequestHandler):
	def post(self):
		expand(self.request.get('key'),
			self.request.get('offset'),
			doitlater.buildE50_expand)

def expand(target, offset, function):
	fingers = models.Fingerprint.all().order('date').fetch(50,offset)
	for finger in fingers:
		callback(target,str(finger.key()))

def main():
    run_wsgi_app(webapp.WSGIApplication([
        ('/tasks/markovify-fingerprint', Markovify),
        ('/tasks/compare-fingerprint', Compare),
        ('/tasks/compare-fingerprint-E50', Compare_Expand),
        ('/tasks/build-response', Build),
        ('/tasks/build-response-E50', Build_Expand),
        ('/tasks/respond', Respond)
    ]))

if __name__ == '__main__':
    main()
