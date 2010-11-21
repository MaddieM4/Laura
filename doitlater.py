import models
from google.appengine.api.labs import taskqueue

def markovify(fingerprint):
	proc_db("markovify-fingerprint", fingerprint)

def respond(fingerprint):
	proc_db("respond", fingerprint)

def compareE50_expand(fpkeyA, fpkeyB):
	add_task('compare-fingerprint',{'A':fpkeyA,'B':fpkeyB})

def buildE50_expand(response, sample):
	add_task('build-response',{'response':response,'sample':sample})

def compare(fingerprint):
	E50('compare-fingerprint-E50',models.Fingerprint,fingerprint)

def build_response(fingerprint):
	E50('build-response-E50',models.Fingerprint,fingerprint)

def E50(queue_name,model,target):
	count = model.all(keys_only=True).count()
	runs = count // 50
	if count % 50 != 0:
		runs += 1
	for i in range(runs):
		add_task(queue_name, {
			'key': getkey(target),
			'offset': i*50
			})

def proc_db(queue,obj):
	add_task(queue, {'key':getkey(obj)})

def getkey(dbobj):
	return str(dbobj.key())

def add_task(queue_name, payload):
	taskqueue.add(url="/tasks/"+queue_name, 
		queue_name=queue_name, 
		params=payload)
