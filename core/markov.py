''' This file stores all the algorithms used in the processing of the underlying
Markov chains Laura uses to store and process data in. '''

import basics
import dbtools
import random
import re

def respond(fingerprint):
	# build a response text and submit the blip
	if fingerprint.state != 'building':
		return dbtools.CANCELLED
	text = ["--start*"]
	wresults = fingerprint.wordresults_set.fetch(1000)
	chrestuples = []
	for i in wresults:
		chrestuples.push((i.chain), i.result)
	while 1:
		poss= dbtools.get_possibilities(wresults, text[basics.USE_CHAIN_LENGTH:])
		picked = possibilities_pick_option(poss)
		if picked==False:
			text = ["--start*"]
		else:
			text.append(picked)
		if picked=="--end*":
			break
	dbtools.reply(fingerprint.parentprint, " ".join(text))
	dbtools.cancel(fingerprint)

def build_fingerprint(fingerprint):
	dbtools.add_counts(fingerprint, build_markov_dict(fingerprint.fulltext))

def possibilities_totalweight(poss):
	total = 0
	for i in poss: total += poss[i]
	return total

def possibilities_pick_option(poss):
	marker = possibilities_totalweight(poss)*random.random()
	for i in poss:
		marker -= poss[i]
		if marker < 0:
			return i
	return False

def build_markov_dict(text):
	''' Returns a dict where the keys are tuples that include the 
	resultant word, and the values are the counts of that event. 

	All tuples are of length basics.USE_CHAIN_LENGTH+1, though they may
	contain empty strings at the beginning for spots that would
	be prior to --start*. '''
	text = "--start* "+text+" --end*"
	text = re.sub(' +',' ',re.sub('\n+', ' --paragraph* ', text))
	splitted = text.split()
	finaldict = {}
	for i in range(1,len(splitted)):
		tup = tuple([""]*max(basics.USE_CHAIN_LENGTH-i,0)+splitted[max(i-basics.USE_CHAIN_LENGTH,0):(i+1)])
		if tup in finaldict:
			finaldict[tup] += 1
		else:
			finaldict[tup] = 1
	return finaldict
