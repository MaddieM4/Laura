import urllib
import logging
import basics
import models
import doitlater

from google.appengine.api import urlfetch

CANCELLED = -2

def cancel(fingerprint):
	fingerprint.state = "cancelled"

def get_possibilities(chainresults, preceding_words):
	''' Returns a one-level dict where keys are string-form 
	possibilities and the values are the weights.
	'''
	results = {}
	logging.info("GETTING POSS: "+str(preceding_words))
	for i in chainresults:
		if match(i[0],preceding_words):
			word = i[1]
			if word in results:
				results[word] += i[2]
			else:
				results[word] = i[2]
	logging.info(results)
	return results

def add_counts(fingerprint, tupledict):
	''' Takes a dict in the same format as returned by 
	markov.build_markov_dict, that is, tuples locked at length
	basics.USE_CHAIN_LENGTH+1, where the last item is the result, and
	the preceding items are (possibly blank) words leading up to it.'''
	for i in tupledict:
		# find or create chain
		chain = models.getChain(list(i[:-1]))
		# Now we need to find or create the counter
		counter = models.WordResult.all().filter(
			'fingerprint =',fingerprint
			).filter('chain =',chain
			).filter('result =',i[basics.USE_CHAIN_LENGTH]).fetch(1)
		if len(counter) == 0:
			counter = models.WordResult(
				fingerprint = fingerprint,
				chain = chain,
				result = i[basics.USE_CHAIN_LENGTH],
				count = float(0)
				)
		else:
			counter = counter[0]
		# Increment and save
		counter.count += float(1)
		counter.put()

def fuse(f_from, f_into, amount):
	t = make_tupledict(f_from)
	for x in t:
		t[x] *= amount
	add_counts(f_into, t)

def make_tupledict(fingerprint):
	tupledict = {}
	for r in fingerprint.wordresult_set:
		chain = r.chain
		key = tuple(chain.words[-basics.USE_CHAIN_LENGTH:]+[r.result])
		tupledict[key] = r.count
	return tupledict

def match(wchain, matchagainst):
	if wchain.words[-len(matchagainst):] == list(matchagainst):
		return True
	else:
		return False

def reply(fingerprint, text):
	# send POST request to fingerprint.resp_url
	payload = urllib.urlencode({
		"key":str(fingerprint.key()),
		"reply":text
	})
	urlfetch.fetch(url=fingerprint.resp_url, 
		payload=payload,
		method=urlfetch.POST,
		headers={'Content-Type':'application/x-www-form-urlencoded'})
	cancel(fingerprint)

def start_response_fingerprint(fingerprint, url):
	logging.info(url)
	logging.info(type(url))
	logging.info(models.Fingerprint.resp_url)
	target = models.Fingerprint.all().filter('state =','normal').count()

	f = models.Fingerprint(
		state = "building",
		author = "laura-robot@appspot.com",
		parentprint = fingerprint,
		resp_url = url,
		build_count = 0,
		build_weight = 0.0,
		build_count_target = target
	)
	f.put()
	doitlater.build_response(f)
	doitlater.respond(f)
	return f

def start_fingerprint(text, creator, parentkey):
	f = models.Fingerprint(
		state="normal",
		author = creator,
		parentprint = models.fromkey(parentkey),
		fulltext = text
	)
	f.put()
	doitlater.markovify(f)
	doitlater.compare(f)
	return f

def setSimilarity(A,B,amount):
	simA = models.Similarity(fingerprintA=A,fingerprintB=B,value=amount)
	simB = models.Similarity(fingerprintA=B,fingerprintB=A,value=amount)
	simA.put()
	simB.put()
