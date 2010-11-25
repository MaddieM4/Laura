import basics
import doitlater
import models
import markov
import dbtools
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from waveapi import robot

class Markovify(webapp.RequestHandler):
	def post(self):
		''' Add a fingerprint to the database '''
		logging.info("A")
		fingerprint = models.fromkey(self.request.get('key'))
		logging.info("B")
		markov.build_fingerprint(fingerprint)
		logging.info("C")
		self.response.out.write("done")

class Compare(webapp.RequestHandler):
	def post(self):
		''' Compare two already-markovized fingerprints. Produce
		2 models.Similarity objects, sacrificing storage space
		for CPU speed. '''
		first = models.fromkey(self.request.get('A'))
		second = models.fromkey(self.request.get('B'))
		firstset = dbtools.make_tupledict(first)
		secondset = dbtools.make_tupledict(second)
		self.simMatch = 0
		self.simTotal = 0
		for i in range(basics.USE_CHAIN_LENGTH):
			self.compare(firstset, secondset, i)
		dbtools.setSimilarity(first, second, self.simMatch/self.simTotal)
		self.response.out.write("")

	def compare(self, td1, td2, level):
		comp1 = self.compile(td1, level)
		comp2 = self.compile(td2, level)
		for i in comp1:
			if i in comp2:
				self.yes()
				if comp1[i] == comp2[i]:
					self.yes()
				else:
					self.no()
			else:
				self.no()
		for i in comp2:
			# matches have already been scored
			if not i in comp1:
				self.no()

	def compile(self, td, level):
		res = {}
		for i in td:
			t = self.trim(i, level)
			if t in res:
				res[t] += td[i]
			else:
				res[t] = td[i]
		return res

	def trim(self, tup, level):
		return tup[-(level+1):]

	def yes(self):
		self.simMatch += 1
		self.simTotal += 1
	def no(self):
		self.simTotal += 1

class Build(webapp.RequestHandler):
	def post(self):
		''' Use saved comparisons to compare chain similarity,
		then use dbtools.add_counts to merge result into
		the response fingerprint '''
		response = models.fromkey(self.request.get('response'))
		sample =   models.fromkey(self.request.get('sample'))
		cA = response.parentprint
		cB = sample.parentprint
		simtotal = 0
		while cA and cB:
			sim = self.findSimilarity(cA,cB)
			# Fail if the comparison is not ready
			if not sim.value: self.error(500)
			simtotal += sim.value
			cA = cA.parentprint
			cB = cB.parentprint
		dbtools.fuse(sample, response, simtotal)

	def findSimilarity(self, fA, fB):
		query = models.Similarity.all()
		query.filter("fingerprintA =",fA)
		query.filter("fingerprintB =",fB)
		return query.fetch(1)[0]

class Respond(webapp.RequestHandler):
	def post(self):
		''' Use a built response fingerprint to create a response
		string, then use it to actually respond.'''
		response_f = models.fromkey(self.request.get('key'))
		markov.respond(response_f)

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

def expand(target, offset, callback):
	fingers = models.Fingerprint.all().order('date').fetch(50,int(offset))
	for finger in fingers:
		callback(target,str(finger.key()))

def main():
    run_wsgi_app(webapp.WSGIApplication([
        ('/queue/markovify-fingerprint', Markovify),
        ('/queue/compare-fingerprint', Compare),
        ('/queue/compare-fingerprint-E50', Compare_Expand),
        ('/queue/build-response', Build),
        ('/queue/build-response-E50', Build_Expand),
        ('/queue/respond', Respond)
    ]))

if __name__ == '__main__':
    main()
