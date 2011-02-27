def sanitize(string):
	split = string.splitlines()
	rsplit = []
	for i in split:
		if i != "":
			rsplit += i
	string = " --paragraph* ".join(rsplit)
	return " ".join(['--start*']+string.split()+['--end*'])
