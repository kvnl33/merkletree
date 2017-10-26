from merkle import Node, MerkleTree, _check_proof, check_proof, print_tree
from collections import OrderedDict
import codecs, string, random, bisect
import numpy as np
from random import randint
from hashlib import sha256

global_idx = 0
hash_function = sha256

testblocks = []

tx_dict = OrderedDict()
blocks = OrderedDict()

# client side will keep the root hashes of the transactions
block_root_hash = OrderedDict()
tx_root_hash = OrderedDict()

top_root = None
top_merkle = None

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
        cap = np.random.randint(10)+1
        for x in range(0,cap):
            global global_idx
            self.outputs.append((id_generator(size=11),global_idx))
            global_idx+=1

def find_ge(my_array, target):
    '''Find smallest item greater-than or equal to key.
    Raise ValueError if no such item exists.
    If multiple keys are equal, return the leftmost.

    '''
    fst, snd = zip(*my_array)
    i = bisect.bisect_left(snd, target)
    if i == len(snd):
        raise ValueError('No item found with key at or above: %r' % (target,))
    return my_array[i], i

def find_nearest_above(my_array, target):
	return min(filter(lambda y: y >= target,my_array))

#	random string generator for our blocks, this will emulate the outputs in our transaction
#	this is used for testsing purposes only
#random string generator for our blocks 
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

#	process a transaction and transform it into a Merkle tree
#	The root of the Merkle tree will contain the greatest global index value
def tx_to_merkle(tx):
    new_t = MerkleTree(leaves=tx.outputs)
    # build the tree
    new_t.build()
    return new_t

# 	Add a block into the global Merkle tree, let this use random data first 
def block_to_merkle(blk):
    tx_leaves = []
    if isinstance(blk, Block):
        for tx in blk.transactions:
            newtree = tx_to_merkle(tx)
            k = newtree.root
            tx_dict[tx.tx_hash] = newtree
            tx_root_hash[tx.tx_hash] = codecs.encode(k.val, 'hex_codec')
            tx_leaves.append((tx.tx_hash,k.idx))

        blk_merkle_tree = MerkleTree(leaves=tx_leaves)
        blk_merkle_tree.build()
        blk_root = blk_merkle_tree.root
        blocks[blk.block_hash] = blk_merkle_tree
        block_root_hash[blk.block_hash] = codecs.encode(blk_root.val, 'hex_codec')

        return (blk.block_hash,blk_root.idx)
    else:
        raise TypeError("Input must be a block!")

# codecs.encode(k.val, 'hex_codec')

# used for testing, we randomly generate a block with transactions in it
def add_block():
    newblk = Block()
    newblk.block_hash = id_generator(size=10)
    cap = np.random.randint(10)+1
    for x in range(0,cap):
        newtx = Transaction()
        newtx.generate()
        newblk.transactions.append(newtx)
    return newblk

def generate_blocks():
    limit = np.random.randint(100)+1
    for x in range(0,limit):
        newblk = add_block()
        testblocks.append(newblk)

def scan_over():
    top_merkle_leaves=[]
    while testblocks:
        top_merkle_leaves.append(block_to_merkle(testblocks.pop(0)))
    top_merkle = MerkleTree(leaves = top_merkle_leaves)
    top_merkle.build()
    return top_merkle

# when there is a new block, process the block to a Merkle tree and add to the main tree
# return the 
def scan_new_block(tm, blk):
    new_entry = block_to_merkle(blk)
    if isinstance(tm, MerkleTree):
        tm.add_adjust(new_entry)
    else:
        raise TypeError("Argument must be a Merkle Tree!")

def main():
    generate_blocks()
    global top_merkle
    top_merkle = scan_over()
    # client will have access to the top_root, which it will store
    global top_root
    top_root = (codecs.encode(top_merkle.root.val, 'hex_codec'), top_merkle.root.idx)
    print top_root
    
    req_gidx = np.random.randint(top_root[1])+1
    print req_gidx

    found_block, blk_idx = find_ge([(leaf.data,leaf.idx) for leaf in top_merkle.leaves], req_gidx)
    # write proof for block here
    blk_proof = top_merkle.get_proof(blk_idx)
    if check_proof(blk_proof) == top_root[0]:
        print "Passed top check"

    block_merkle = blocks[found_block[0]]
    found_tx, tx_idx = find_ge([(leaf.data,leaf.idx) for leaf in block_merkle.leaves], req_gidx)

    # write proof for transaction over here
    tx_proof = block_merkle.get_proof(tx_idx)
    if check_proof(tx_proof) == block_root_hash[found_block[0]]:
        print "Passed block Check"

    tx_merkle = tx_dict[found_tx[0]]
    found_output, output_idx = find_ge([(leaf.data,leaf.idx) for leaf in tx_merkle.leaves], req_gidx)

    out_proof = tx_merkle.get_proof(output_idx)
    if check_proof(out_proof) == tx_root_hash[found_tx[0]]:
        print "Passed Tx check"

    # add more blocks, test if add_adjust works
    for r in range(0,10):
        generate_blocks()
        while testblocks:
            scan_new_block(top_merkle, testblocks.pop(0))

    top_root = (codecs.encode(top_merkle.root.val, 'hex_codec'), top_merkle.root.idx)
    print top_root

    req_gidx = np.random.randint(top_root[1])+1
    print req_gidx

    found_block, blk_idx = find_ge([(leaf.data,leaf.idx) for leaf in top_merkle.leaves], req_gidx)
    # write proof for block here
    blk_proof = top_merkle.get_proof(blk_idx)
    if check_proof(blk_proof) == top_root[0]:
        print "Passed top check"

    block_merkle = blocks[found_block[0]]
    found_tx, tx_idx = find_ge([(leaf.data,leaf.idx) for leaf in block_merkle.leaves], req_gidx)

    # write proof for transaction over here
    tx_proof = block_merkle.get_proof(tx_idx)
    if check_proof(tx_proof) == block_root_hash[found_block[0]]:
        print "Passed block Check"

    tx_merkle = tx_dict[found_tx[0]]
    found_output, output_idx = find_ge([(leaf.data,leaf.idx) for leaf in tx_merkle.leaves], req_gidx)

    out_proof = tx_merkle.get_proof(output_idx)
    if check_proof(out_proof) == tx_root_hash[found_tx[0]]:
        print "Passed Tx check"

    print_tree(top_merkle)
    

if __name__ == '__main__':
    main()




