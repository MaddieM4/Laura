from google.appengine.ext import db

class WordChain(db.Model):
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

class Fingerprint(db.Model):
	state = db.StringProperty(required=True, 
		choices = set(['normal', 'building', 'cancelled']))
	author = db.EmailProperty(required=True)
	date = db.DateTimeProperty(auto_now_add=True)
	parentprint = db.SelfReferenceProperty()
	fulltext = db.TextProperty()
	wave = db.StringProperty()
	wavelet = db.StringProperty()
	blip = db.StringProperty()
	build_count = db.IntegerProperty()
	build_weight= db.FloatProperty()

class WordResult(db.Model):
	fingerprint = db.ReferenceProperty(Fingerprint, required=True)
	chain = db.ReferenceProperty(WordChain, required=True)
	result = db.StringProperty(required=True)
	count = db.IntegerProperty(required=True)

class Similarity(db.Model):
	fingerprintA = db.ReferenceProperty(Fingerprint, required=True, 
		collection_name="SimilarityA")
	fingerprintB = db.ReferenceProperty(Fingerprint, required=True,
		collection_name="SimilarityB")
	value = db.FloatProperty(required=True)

def fromkey(keystring):
	return db.get(db.Key(keystring))
