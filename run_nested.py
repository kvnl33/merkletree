from merkle import Node, MerkleTree, _check_proof, check_proof
from collections import OrderedDict
import codecs, string, random
import numpy as np
from random import randint
from hashlib import sha256

global_idx = 0
hash_function = sha256

blocks = OrderedDict()
block_headers = OrderedDict()

class Block(object):
    """Each node has, as attributes, references to left (l) and right (r) child nodes, parent (p),
    and sibling (sib) node. It can also be aware of whether it is on the left or right hand side (side).
    data is hashed automatically by default, but does not have to be, if prehashed param is set to True.
    """
    # The leaf node in here can be the block, and whatever is inside are the output keys generated
    __slots__ = ['block_hash', 'transactions']
    def __init__(self):
        self.block_hash=None
        self.transactions=[]

class Transaction(object):
    """Each node has, as attributes, references to left (l) and right (r) child nodes, parent (p),
    and sibling (sib) node. It can also be aware of whether it is on the left or right hand side (side).
    data is hashed automatically by default, but does not have to be, if prehashed param is set to True.
    """
    # The leaf node in here can be the block, and whatever is inside are the output keys generated
    __slots__ = ['tx_hash', 'outputs']
    def __init__(self):
        self.tx_hash=None
        self.outputs=[]

    def generate(self):
        self.tx_hash = id_generator(size=32)
        cap = np.random.randint(10)
        for x in range(0,cap):
            global global_idx
            self.outputs.append((id_generator(size=11),global_idx))
            global_idx+=1


def find_nearest_above(my_array, target):
	return min(filter(lambda y: y >= target,my_array))

#	random string generator for our blocks, this will emulate the outputs in our transaction
#	this is used for testsing purposes only
#random string generator for our blocks 
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

#	for printing the tree
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

#	process a transaction and transform it into a Merkle tree
#	The root of the Merkle tree will contain the greatest global index value
def tx_to_merkle(transaction):
    leaves = id_generator()
    print leaves
    newtree = MerkleTree(leaves=leaves)
    newtree.build()
    k = newtree.root
    root = (codecs.encode(k.val, 'hex_codec'), k.idx)
    return newtree, root

# 	Add a block into the global Merkle tree, let this use random data first 
def block_to_merkle(blk):
    tx_leaves = []
    if isinstance(blk, Block):
        for tx in blk.transactions:
            print tx.outputs
            tx_to_merkle(leaves=tx.outputs)
    else:
        raise TypeError("Input must be a block!")

# used for testing, we randomly generate a block with transactions in it
def add_block():
    newblk = Block()
    newblk.block_hash = id_generator(size=10)
    cap = np.random.randint(10)
    for x in range(0,cap):
        newtx = Transaction()
        newtx.generate()
        newblk.transactions.append(newtx)
    return newblk



