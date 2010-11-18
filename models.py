from google.appengine.ext import db

import .

class WordChain(db.model):
	# Store 8, use 4
	# word1 is adjacent to result
	word1 = db.StringProperty(required=True)
	word2 = db.StringProperty()
	word3 = db.StringProperty()
	word4 = db.StringProperty()
	word5 = db.StringProperty()
	word6 = db.StringProperty()
	word7 = db.StringProperty()
	word8 = db.StringProperty()

class Fingerprint(db.model):
	state = enum [normal, building]
	author = string
	date = date
	parent = otherFingerprint
	refers_to = blip identifier/location

class WordResult(db.model):
	fingerprint = fingerprint
	chain = wordchain
	result = string
	count = integer


