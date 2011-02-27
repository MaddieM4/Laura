def sanitize(string):
	split = string.splitlines()
	rsplit = []
	for i in split:
		if i != "":
			rsplit.append(i)
	string = " --paragraph* ".join(rsplit)
	return " ".join(['--start*']+string.split()+['--end*'])

def output(string):
	string = string.replace("--start* ","")
	string = string.replace("--paragraph* ","")
	string = string.replace(" --end*","")
	return string
