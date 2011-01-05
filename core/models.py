import md5
from google.appengine.ext import db

class WordChain(db.Model):
	# Store 8, use 4
	# words are in same order as src text
	words = db.StringListProperty(required=True)

class Fingerprint(db.Model):
	state = db.StringProperty(required=True, 
		choices = set(['normal', 'building', 'cancelled']))
	author = db.EmailProperty(required=True)
	date = db.DateTimeProperty(auto_now_add=True)
	parentprint = db.SelfReferenceProperty()
	fulltext = db.TextProperty()
	resp_url = db.LinkProperty()
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
	try:
		return db.get(db.Key(keystring))
	except:
		return None

def getChain(wlist):
	return WordChain.get_or_insert(getChainKeystring(wlist),words=wlist)

def getChainKeystring(wlist):
	letters = ""
	for i in wlist:
		if len(i) > 0:
			letters += i[0]
		else:
			letters += "~"
	return letters + md5.new("".join(wlist)).hexdigest()[:10]

def purge():
	for m in [WordChain, WordResult, Similarity, Fingerprint]:
		for i in m.all(keys_only=True):
			i.delete()
