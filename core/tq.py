import basics
import doitlater
import models
import markov
import dbtools
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

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
		if self.request.get('A') == self.request.get('B'):
			self.response.out.write("done")
			return
		first = models.fromkey(self.request.get('A'))
		second = models.fromkey(self.request.get('B'))
		if first.state != "normal" or second.state != "normal":
			logging.info("State != normal")
			return
		firstset = dbtools.make_tupledict(first)
		secondset = dbtools.make_tupledict(second)
		self.simMatch = 0
		self.simTotal = 0
		for i in range(basics.USE_CHAIN_LENGTH):
			self.compare(firstset, secondset, i)
		dbtools.setSimilarity(first, second, float(self.simMatch)/self.simTotal)
		self.response.out.write("done")

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
	class Role:
		def __init__(self):
			self.authors = []
			self.roles = []

		def insert(self, author):
			if author in self.authors:
				role = self.authors.index(author)
			else:
				self.authors.append(author)
				role = len(self.authors)-1
			self.roles.append(role)
			return role

	def post(self):
		''' Use saved comparisons to compare chain similarity,
		then use dbtools.add_counts to merge result into
		the response fingerprint '''
		response = models.fromkey(self.request.get('response'))
		sample =   models.fromkey(self.request.get('sample'))
		if sample.state != "normal":
			return
		logging.info(response.key())
		cA = response.parentprint
		cB = sample.parentprint
		roleA = Build.Role()
		roleB = Build.Role()
		simtotal = 0
		while cA and cB:
			try:
				sim = self.findSimilarity(cA,cB)
				simvalue = sim.value*.8
				if cA.author == cB.author:
					simvalue += .1
				if roleA.insert(cA.author) == roleB.insert(cB.author):
					simvalue += .1
			except IndexError:
				if cA.key() == cB.key():
					simvalue = 1.0
				else:
					# Fail if the comparison is not ready
					logging.info("Comparison not ready")
					logging.info(cA.key())
					logging.info(cB.key())
					logging.info(cA.key() == cB.key())
					self.error(500)
					return
			simtotal += simvalue
			cA = cA.parentprint
			cB = cB.parentprint
		logging.info(response.build_count)
		response.build_count += 1
		response.build_weight += simtotal
		response.put()
		logging.info(response.build_count)
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
		if response_f.build_count < 5:
			logging.info(str(response_f.key()))
			logging.info("Not enough build_count (%d)" % response_f.build_count)
			self.error(500)
		else:
			r = markov.respond(response_f)
			if r != 1:
				logging.info("MARKOV CODE "+str(r))
				self.error(500)

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

class Purge(webapp.RequestHandler):
	def get(self):
		models.purge()
		self.response.out.write("Purge completed")

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
        ('/queue/respond', Respond),
        ('/queue/purge', Purge)
    ]))

if __name__ == '__main__':
    main()
