import basics
import models
import doitlater
from waveapi import robot

CANCELLED = -2

def fingerprint_state(fingerprint):
	return fingerprint.state

def cancel(fingerprint):
	fingerprint.state = "cancelled"

def get_possibilities(wresults, preceding_words):
	''' Returns a one-level dict where keys are string-form 
	possibilities and the values are the weights.
	'''
	wresults_filtered = []
	for i in wresults:
		if match(i.chain,preceding_words):
			wresults_filtered=i
	results = {}
	for i in wresults_filtered:
		word = i.result
		if word in results:
			results[word] += i.count
		else:
			results[word] = i.count
	return results

def add_counts(fingerprint, tupledict):
	''' Takes a dict in the same format as returned by 
	markov.build_markov_dict, that is, tuples locked at length
	basics.USE_CHAIN_LENGTH+1, where the last item is the result, and
	the preceding items are (possibly blank) words leading up to it.'''
	for i in tupledict:
		# find or create chain
		wchainsGQL = models.WordChain.all()
		for x in range(basics.USE_CHAIN_LENGTH):
			wchainsGQL.filter('word'+str(x+1)+' =',
				i[basics.USE_CHAIN_LENGTH-1-x])
		wchains = wchainsGQL.fetch(1)
		if wchains == []:
			chain = models.WordChain(
				word1=i[3],
				word2=i[2],
				word3=i[1],
				word4=i[0]
				)
			chain.put()
		else:
			chain = wchains[0]
		# Now we need to find or create the counter
		counter = models.WordResult.all().filter(
			'fingerprint =',fingerprint
			).filter('chain =',chain
			).filter('result =',i[basics.USE_CHAIN_LENGTH]).fetch(1)
		if counter == []:
			counter = models.WordResult(
				fingerprint = fingerprint,
				chain = chain,
				result = i[basics.USE_CHAIN_LENGTH],
				count = 0
				)
		else:
			counter = counter[0]
		# Increment and save
		counter.count += 1
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
		key = (chain.word4,
			chain.word3,
			chain.word2,
			chain.word1,
			r.result)
		tupledict[key] = r.count
	return tupledict

def match(wchain, matchagainst):
	l = len(matchagainst)
	wres = [wchain.word4,
		wchain.word3,
		wchain.word2,
		wchain.word1]
	if wres[-l:] == list(matchagainst):
		return True
	else:
		return False

def reply(fingerprint, text):
	basics.authorize()
	wavelet = robot.fetch_wavelet(fingerprint.wave_id,fingerprint.wavelet_id)
	for i in wavelet.root_thread.blips:
		if i.blip_id==fingerprint.blip:
			i.reply().GetDocument.SetText(text)
			break
	wavelet.submit()

def get_text(fingerprint):
	return fingerprint.fulltext

def analyze_blip(blip):
	f = start_fingerprint(blip)
	# Defer to task queue function for actual analysis
	doitlater.markovify(f)
	return f

def start_reply(blip):
	f = analyze_blip(blip)
	doitlater.compare(f)
	response = start_response_fingerprint(f)
	doitlater.build_response(response)
	doitlater.respond(response)

def start_response_fingerprint(fingerprint):
	child = models.Fingerprint(
		state = "building",
		author = "laura-wavebot@appspot.com",
		parentprint = fingerprint,
		build_count = 0,
		build_weight = 0
	)
	child.put()
	return child

def start_fingerprint(blip):
	if blip.is_root():
		parent_fingerprint = None
	else:
		parent_fingerprint = models.Fingerprint.all().filter(
			wave = blip.wave_id,
			wavelet = blip.wavelet_id,
			blip = blip.parent_blip_id).fetch(limit=1)[0]

	f = models.Fingerprint(
		state="normal",
		author = blip.creator,
		parentprint = parent_fingerprint,
		fulltext = blip.text,
		wave = blip.wave_id,
		wavelet = blip.wavelet_id,
		blip = blip.blip_id
	)
	f.put()
	return f

def setSimilarity(A,B,amount):
	simA = models.Similarity(fingerprintA=A,fingerprintB=B,value=amount)
	simB = models.Similarity(fingerprintA=B,fingerprintB=A,value=amount)
	simA.put()
	simB.put()
