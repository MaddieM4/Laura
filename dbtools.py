import models
import doitlater
import .
from waveapi import robot

CANCELLED = -2

def fingerprint_state(fingerprint):
	return fingerprint.state

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
		else
			results[word] = i.count
	return results

def add_counts(fingerprint, tupledict):
	for i in tupledict:
		# find or create chain
		wchainsGQL = models.WordChain.all()
		for x in range(USE_CHAIN_LENGTH):
			wchainsGQL.filter('word'+str(x+1)+' =',
				i[USE_CHAIN_LENGTH+1-x])
		wchains = wchainsGQL.fetch(1)
		if wchains == []:
			chain = models.WordChain()
			chain.word1 = i[3]
			chain.word2 = i[2]
			chain.word3 = i[1]
			chain.word4 = i[0]
			chain.put()
		else:
			chain = wchains[0]
		# Now we need to find or create the counter
		counter = models.WordResult.all().filter(
			'fingerprint =',fingerprint
			).filter('chain =',chain
			).filter('result =',i[USE_CHAIN_LENGTH]).fetch(1)
		if counter = []:
			counter = models.WordResult()
			counter.fingerprint = fingerprint
			counter.chain=chain
			counter.result = i[USE_CHAIN_LENGTH]
		else:
			counter = counter[0]
		# Increment and save
		counter.count += 1
		counter.put()

def match(wchain, matchagainst):
	l = len(matchagainst)
	wres = [wchain.word4,
		wchain.word3,
		wchain.word2,
		wchain.word1]
	if wres[-l:] == list(matchagainst):
		return True
	else
		return False

def reply(fingerprint, text):
	authorize()
	wavelet = robot.fetch_wavelet(fingerprint.wave_id,fingerprint.wavelet_id)
	for i in wavelet.blips:
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
	doitlater.build_response(f)
	doitlater.respond(f)

def start_fingerprint(blip):
	if blip.is_root():
		parent_fingerprint = None
	else:
		parent_fingerprint = models.Fingerprint.all().filter(
			wave = blip.wave_id,
			wavelet = blip.wavelet_id,
			blip = blip.parent_blip_id).fetch(limit=1)[0]

	return models.Fingerprint(
		state="normal",
		author = blip.creator,
		parent = parent_fingerprint,
		fulltext = blip.text,
		wave = blip.wave_id,
		wavelet = blip.wavelet_id,
		blip = blip.blip_id
	).put()
