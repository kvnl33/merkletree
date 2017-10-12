from merkle import Node, MerkleTree, _check_proof, check_proof
from collections import OrderedDict
import codecs, string, random
from random import randint
from hashlib import sha256

global_idx = 0
hash_function = sha256

blocks = OrderedDict()
block_headers = OrderedDict()

def find_nearest_above(my_array, target):
	return min(filter(lambda y: y >= target,my_array))

#	random string generator for our blocks, this will emulate the outputs in our transaction
#	this is used for testsing purposes only
def id_generator(size=6, chars=string.ascii_uppercase + string.digits, num_req=1):
	global global_idx
	return [(''.join(random.choice(chars) for _ in range(size)), global_idx) for global_idx in range(global_idx+1, global_idx+num_req)]

#for printing the tree
def print_tree(root):
	nodes = []
	nodes.append(root)
	while nodes:
		ntp = nodes.pop(0)
		if ntp.l:
			nodes.append(ntp.l)
		if ntp.r:
			nodes.append(ntp.r)
		print ntp

#	Add a transaction, which will be represented by a Merkle Tree
#	The root of the Merkle tree will contain the greatest global index value
def add_transaction(num_outs):
	leaves = id_generator(num_req=num_outs)
	newtree = MerkleTree(leaves=leaves)
	newtree.build()
	k = newtree.root
	root = (codecs.encode(k.val, 'hex_codec'), k.idx)

	return newtree, root


# 	Add a block into the global Merkle tree, this 
def add_block():
	x=0

