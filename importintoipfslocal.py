#!/usr/bin/python3.9

# Linux local with ipfs server daemon running
# Usage: importintoipfslocal.py Alex_cids.json
#
import os
import sys
import subprocess
import json

cwd = os.getcwd()
cmdtimeout = 300

def getcidlistfromfile(filename):
	try:
		cidlist = []
		f = open(cwd + "/" + filename)
		data = json.load(f)
		for element in data["Assets"]:
			if "config" in element:
				cidlist.append(element["config"])
			if "image" in element:
				cidlist.append(element["image"])
			if "animation" in element:
				cidlist.append(element["animation"])
		f.close()
	except Exception as e:
		print (e)

	return cidlist

def main(filename):
	cidlist = getcidlistfromfile(filename)

	i = 1
	cidcnt = len(cidlist)
	for cid in cidlist:
		print (str(i) + "/" + str(cidcnt) + ": " + cid)
		cmda = "ipfs pin add " + cid
		cmdb = "ipfs files cp /ipfs/" + cid + " /"
		try:
			result = subprocess.run(cmda.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=cmdtimeout)
			output = result.stdout.decode().strip()
			if len(output) > 0:
				print ("Out: " + output)
			error = result.stderr.decode().strip()
			if len(error) > 0:
				print ("Error: " + error)
		except subprocess.TimeoutExpired:
			print (cid + " - Command timed out")

		try:
			result = subprocess.run(cmdb.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=cmdtimeout)
			output = result.stdout.decode().strip()
			if len(output) > 0:
				print ("Out: " + output)
			error = result.stderr.decode().strip()
			if len(error) > 0:
				print ("Error: " + error)
		except subprocess.TimeoutExpired:
			print (cid + " - Command timed out")

		i = i + 1


if __name__ == "__main__":
	main(sys.argv[1:][0])


#ipfs pin add QmY8GmTNaCkb8FtV4zFPMe2zff4x27WeHSLHWsEuu8mxmz
#ipfs files cp /ipfs/QmY8GmTNaCkb8FtV4zFPMe2zff4x27WeHSLHWsEuu8mxmz /


