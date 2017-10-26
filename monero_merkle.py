from merkle import Node, MerkleTree, _check_proof, check_proof, print_tree
from collections import OrderedDict
import codecs, string, random, bisect, sqlite3
import numpy as np
from random import randint
from hashlib import sha256
import os.path

hash_function = sha256

utxos = []

tx_dict = OrderedDict()
blocks = OrderedDict()

# client side will keep the root hashes of the transactions
block_root_hash = OrderedDict()
tx_root_hash = OrderedDict()

top_root = None
top_merkle = None

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

def read_in_blocks():
    '''Read in the blocks from the database containing all the RingCT outputs
    It will be in the format of a tuple
    '''
    if os.path.isfile("rct_output_10_23_2017.npz"):
        npzfile = np.load("rct_output_10_23_2017.npz")
        fetched = npzfile["fetched"]
    else:
        conn = sqlite3.connect('/home/yorozuya/rct_output_10_23_2017.db')
        c_1 = conn.cursor()
        c_1.execute('''SELECT block_hash, tx_hash, outkey, idx FROM out_table ORDER BY idx LIMIT 1000000''')
        fetched = c_1.fetchall()
        fetched = np.asarray(fetched)
        outfile = "rct_output_10_23_2017"
        np.savez(outfile, fetched = fetched)
    global utxos
    utxos = fetched.tolist()

def block_to_merkle(block_outkeys):
    block_merkle_leaves=[]
    block_hash = block_outkeys[0][0]
    assert all(item[0] == block_hash for item in block_outkeys)
    while block_outkeys:
        curr_tx_hash = block_outkeys[0][1]
        tx_outkeys = []
        while block_outkeys[0][1] == curr_tx_hash:
            tx_outkeys.append(block_outkeys.pop(0))
            if not block_outkeys:
                break
        block_merkle_leaves.append(tx_to_merkle(tx_outkeys))
    block_merkle = MerkleTree(leaves=block_merkle_leaves)
    block_merkle.build()
    blocks[block_hash] = block_merkle
    block_root_hash[block_hash] = codecs.encode(block_merkle.root.val, 'hex_codec')
    return (block_hash, block_merkle.root.idx)

def tx_to_merkle(tx_outkeys):
    tx_hash = tx_outkeys[0][1]
    assert all(item[1] == tx_hash for item in tx_outkeys)
    tx_merkle_leaves = [(item[2], item[3]) for item in tx_outkeys]
    tx_merkle = MerkleTree(leaves=tx_merkle_leaves)
    tx_merkle.build()
    tx_dict[tx_hash] = tx_merkle
    tx_root_hash[tx_hash] = codecs.encode(tx_merkle.root.val, 'hex_codec')
    return (tx_hash, tx_merkle.root.idx)

def scan_over_new_blocks():
    '''Scan over the utxos, distinguishing new blocks
    We will use block hash to distinguish new blocks'''
    top_merkle_leaves=[]
    while utxos:
        curr_block_hash = utxos[0][0]
        block_outkeys = []
        while utxos[0][0] == curr_block_hash:
            block_outkeys.append(utxos.pop(0))
            if not utxos:
                break
        top_merkle_leaves.append(block_to_merkle(block_outkeys))
    global top_merkle
    top_merkle = MerkleTree(leaves = top_merkle_leaves)
    top_merkle.build()
    global top_root
    top_root = (codecs.encode(top_merkle.root.val, 'hex_codec'), top_merkle.root.idx)

def main():
    read_in_blocks()
    scan_over_new_blocks()

    req_gidx = np.random.randint(top_root[1])+1
    print req_gidx

    found_block, blk_idx = find_ge([(leaf.data, leaf.idx) for leaf in top_merkle.leaves], req_gidx)
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

    # # add more blocks, test if add_adjust works
    # for r in range(0,10):
    #     generate_blocks()
    #     while testblocks:
    #         scan_new_block(top_merkle, testblocks.pop(0))

    # top_root = (codecs.encode(top_merkle.root.val, 'hex_codec'), top_merkle.root.idx)
    # print top_root

    # req_gidx = np.random.randint(top_root[1])+1
    # print req_gidx

    # found_block, blk_idx = find_ge([(leaf.data,leaf.idx) for leaf in top_merkle.leaves], req_gidx)
    # # write proof for block here
    # blk_proof = top_merkle.get_proof(blk_idx)
    # if check_proof(blk_proof) == top_root[0]:
    #     print "Passed top check"

    # block_merkle = blocks[found_block[0]]
    # found_tx, tx_idx = find_ge([(leaf.data,leaf.idx) for leaf in block_merkle.leaves], req_gidx)

    # # write proof for transaction over here
    # tx_proof = block_merkle.get_proof(tx_idx)
    # if check_proof(tx_proof) == block_root_hash[found_block[0]]:
    #     print "Passed block Check"

    # tx_merkle = tx_dict[found_tx[0]]
    # found_output, output_idx = find_ge([(leaf.data,leaf.idx) for leaf in tx_merkle.leaves], req_gidx)

    # out_proof = tx_merkle.get_proof(output_idx)
    # if check_proof(out_proof) == tx_root_hash[found_tx[0]]:
    #     print "Passed Tx check"

    # print_tree(top_merkle)
    

if __name__ == '__main__':
    main()




