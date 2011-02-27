def sanitize(string):
	split = string.splitlines()
	rsplit = []
	for i in split:
		if i != "":
			rsplit.append(i)
	string = " --paragraph* ".join(rsplit)
	return " ".join(['--start*']+string.split()+['--end*'])


def sanitized_already(string):
	return sanitize(output(string)) == string

def filter(string):
	if sanitized_already(string):
		return string
	else:
		return sanitize(string)

def output(string):
	string = string.replace("--start* ","")
	string = string.replace("--paragraph* ","")
	string = string.replace(" --end*","")
	return string
