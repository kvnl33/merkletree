from merkle import Node, MerkleTree, _check_proof, check_proof, print_tree, fetch_children_hash, get_num_leaves
import codecs, string, random, bisect, sqlite3, os.path, requests
import numpy as np
from random import randint
from hashlib import sha256
from collections import OrderedDict

t1_root=t2_root=None
hash_function = sha256

server1 = "http://148.100.99.174:5000"
server2 = "http://148.100.4.151:5000"

def block_verifier(m1, m2):
	'''Searches for the block that is different in two servers'''
	search = []
	while True:
		r1 = requests.get(server1+"/getchildren", json={"root":m1[0], "path":search[:]})
		r2 = requests.get(server2+"/getchildren", json={"root":m2[0], "path":search[:]})
		r1 = r1.json()
		r2 = r2.json()
		(lhash_1, rhash_1, ldata_1, rdata_1) = tuple(r1["data"])
		(lhash_2, rhash_2, ldata_2, rdata_2) = tuple(r2["data"])
		# we have reached leaf level
		if ldata_1 and rdata_1:
			break
		# we have reached a leaf on one side and not the other
		elif ldata_1 and not rdata_1:
			if lhash_1 != lhash_2:
				break
		elif not ldata_1 and rdata_1:
			if rhash_1 != rhash_2:
				break
		if lhash_1 == lhash_2:
			search.append('r')
		else:
			search.append('l')

	if ldata_1 and not rdata_1:
		block_root_1 = ldata_1
		block_root_2 = ldata_2
	elif not ldata_1 and rdata_1:
		block_root_1 = rdata_1
		block_root_2 = rdata_2
	else:
		if ldata_1 == ldata_2:
			block_root_1 = rdata_1
			block_root_2 = rdata_2
		else:
			block_root_1 = ldata_1
			block_root_2 = ldata_2

	print block_root_1
	print block_root_2

	# empty the list to do a search for the transaction-level now
	search[:] = []
	while True:
		r1 = requests.get(server1+"/getchildren", json={"root":block_root_1, "path":search[:]})
		r2 = requests.get(server2+"/getchildren", json={"root":block_root_2, "path":search[:]})
		r1 = r1.json()
		r2 = r2.json()
		(lhash_1, rhash_1, ldata_1, rdata_1) = tuple(r1["data"])
		(lhash_2, rhash_2, ldata_2, rdata_2) = tuple(r2["data"])
		if ldata_1 and rdata_1:
			break
		# we have reached a leaf on one side and not the other
		elif ldata_1 and not rdata_1:
			if lhash_1 != lhash_2:
				break
		elif not ldata_1 and rdata_1:
			if rhash_1 != rhash_2:
				break
		if lhash_1 == lhash_2:
			search.append('r')
		else:
			search.append('l')
	if ldata_1 and not rdata_1:
		tx_root_1 = ldata_1
		tx_root_2 = ldata_2
	elif not ldata_1 and rdata_1:
		tx_root_1 = rdata_1
		tx_root_2 = rdata_2
	else:
		if ldata_1 == ldata_2:
			tx_root_1 = rdata_1
			tx_root_2 = rdata_2
		else:
			tx_root_1 = ldata_1
			tx_root_2 = ldata_2
	print tx_root_1
	print tx_root_2

def check_path(found_output, path_proof, top_root):
    '''This function, which is stored and run by the client, will check the Merkle proof returned
    by the server. The proof involves the following steps:
        1-  The requested output key is hashed to verify it matches the first part of the outkey proof.
        2-  The tx_merkle proof check is run.
        3-  The root of the first Merkle is hashed to verify it matches the first part of the tx proof.
        4-  The blk_merkle proof check is run.
        5-  The root of the second Merkle is hashed to verify it matches the first part of the blk proof.
        6-  The top_merkle proof is run.
        7-  Finally, the last part of the proof, which should contain the top merkle root, is verified.
    If all steps pass, then we have successfully checked that our query was returned correctly.
    If any of the checks fail, then the query was not returned correctly, and we need to run the verifier.'''
    outproof, txproof, blkproof = path_proof
    leaf_hashed, _ = outproof[0]
    if [hash_function(found_output[0]).hexdigest(),found_output[1]] == leaf_hashed:
    	if check_proof(outproof):
    		tx_hashed, _ = txproof[0]
    		outproof_merkle_root, _ = outproof[-1]
    		if [hash_function(outproof_merkle_root[0]).hexdigest(),outproof_merkle_root[1]]==tx_hashed:
    			if check_proof(txproof):
    				blk_hashed, _ = blkproof[0]
    				txproof_merkle_root, _ = txproof[-1]
    				if [hash_function(txproof_merkle_root[0]).hexdigest(), txproof_merkle_root[1]] == blk_hashed:
    					if check_proof(blkproof):
    						blkproof_merkle_root,_ = blkproof[-1]
    						if blkproof_merkle_root == list(top_root):
    							return True
    return False


def get_output(top_root, idx):
	assert top_root in [t1_root, t2_root]
	if idx <= top_root[1] and idx >= 0:
		if top_root == t1_root:
			r = requests.get(server1+"/getout", json={"idx":idx})
		else:
			r = requests.get(server2+"/getout", json={"idx":idx})
		r = r.json()
		found_output = r["found"]
		found_proof = r["proof"]
		return found_output, found_proof
	else:
		raise ValueError("Server has not reached that global index yet")

def setup():
	global t1_root, t2_root
	r1 = requests.get(server1+"/getroot")
	r1 = r1.json()
	t1_root = tuple(r1["root"])
	r2 = requests.get(server2+"/getroot")
	r2 = r2.json()
	t2_root = tuple(r2["root"])

def main():
	setup()

if __name__ == '__main__':
    main()