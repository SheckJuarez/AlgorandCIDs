#!/usr/bin/python3.9
#
#Usage: rightclicksaveass.py {assetid} {outputfilename}
#
import sys
import os
import urllib.request
from bs4 import BeautifulSoup
import subprocess
import requests
import re
import json
import base64

from algosdk.v2client import indexer, algod
from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn, AssetFreezeTxn, wait_for_confirmation
from algosdk import account, mnemonic
from algosdk import transaction

tmpfiles = []

cwd = os.getcwd()
cmdtimeout = 300

MAINNET_NODE_API = "https://mainnet-api.algonode.cloud"
MAINNET_INDEXER_API = "https://mainnet-idx.algonode.cloud"
requesttimeout = 300


def getextension(contenttype):
	resp = "unknown"
	if contenttype == "image/png":
		resp = "png"
	if contenttype == "image/jpg":
		resp = "jpg"
	if contenttype == "image/jpeg":
		resp = "jpg"
	if contenttype == "image/gif":
		resp = "gif"
	if contenttype == "application/json":
		resp = "json"
	if contenttype == "image/webp":
		resp = "webp"
	if contenttype == "video/mp4":
		resp = "mp4"
	if contenttype == "video/quicktime":
		resp = "mov"
	if contenttype == "model/gltf-binary":
		resp = "glb"

	return resp

def download_image_from_ipfs(cid_link, output_filename):
	contenttype = "unknown"
	try:
		response = requests.get(f"https://ipfs.io/ipfs/{cid_link}", timeout = (3, 300))
		if "Content-Type" in response.headers:
			contenttype = response.headers["Content-Type"]
		response.raise_for_status()  # Raise an exception for non-2xx status codes
	except requests.exceptions.RequestException as e:
		print(f"Error: {e}")
		return
	cid = "unknown"
	if contenttype == "application/json":
		jsoncontent = response.json()
		if "image" in jsoncontent:
			cid = jsoncontent["image"].split("/")[len(jsoncontent["image"].split("/")) - 1]
			download_image_from_ipfs(cid, output_filename)
		if "animation_url" in jsoncontent:
			cid = jsoncontent["animation_url"].split("/")[len(jsoncontent["animation_url"].split("/")) - 1]
			download_image_from_ipfs(cid, output_filename)

	else:
		filename = output_filename + "." + getextension(contenttype)
		if not os.path.exists(filename):
			with open(filename, "wb") as file:
				file.write(response.content)
				print ("Saved " + filename)


def getcidfromurl(url):
	resp = None
	cid = url.split("/")[len(url.split("/")) - 1].split("#")[0].split("?")[0].strip()
#	if "{" not in cid and ".png" not in cid and ".json" not in cid and len(cid) > 0:
	if ".png" in cid:
		if url.split("/")[len(url.split("/")) - 2] == "images":
			cid = url.split("/")[len(url.split("/")) - 3] + "/" + url.split("/")[len(url.split("/")) - 2] + "/" + url.split("/")[len(url.split("/")) - 1].split("#")[0].split("?")[0].strip() 
		else:
			cid = url.split("/")[len(url.split("/")) - 2] + "/" + url.split("/")[len(url.split("/")) - 1].split("#")[0].split("?")[0].strip() 
	if "{" not in cid and ".json" not in cid and len(cid) > 0:
		resp = cid
	return resp

def cleanfilename(filename):
	resp = ""

	pattern = r'[\\/:\*\?"<>\|]'
	resp = re.sub(pattern, '', filename).replace(" ", "_")

	return resp


def getassetconfig(indexer_client, assetid):
	holder = None
	next_token = None
	config = ""
	lastconfig = None
	while True:
		try:

			payload = indexer_client.search_transactions(asset_id=assetid, txn_type="acfg", next_page=next_token)
			note = ""
			if len(payload["transactions"]) > 0:
				lastconfig = payload["transactions"][len(payload["transactions"])-1]
				if "note" in lastconfig:
					try:
						note = ""
						note = json.loads(base64.b64decode(lastconfig["note"]).decode('utf-8'))
					except ValueError as e:
						pass
                                        #print ("#" + str(assetid) + "#" + str(note))
					config = note

			next_token = payload.get('next-token', None)
			if next_token is None:
				break

		except Exception as e:
			print (e)

	#print(json.dumps(lastconfig, indent=4))
	return config

def main(assetid, outfilename):
	idx_client = indexer.IndexerClient(indexer_token="", indexer_address=MAINNET_INDEXER_API)
	config = getassetconfig(idx_client, assetid)
	cid = getcidfromurl(config["external_link"])

	download_image_from_ipfs(cid, outfilename)



if __name__ == "__main__":
        main(sys.argv[1:][0], sys.argv[1:][1])
