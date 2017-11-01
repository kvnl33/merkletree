from merkle import Node, MerkleTree, _check_proof, check_proof, print_tree
import codecs, string, random, bisect, sqlite3
import numpy as np
from random import randint
from hashlib import sha256
import os.path
import cPickle as pickle
from collections import OrderedDict

t1=t2=t1_root=t2_root = None
merkle_forest = OrderedDict()

def block_verifier(m1, m2):
	'''Searches for the block that is different in two servers'''
	search = []
	while True:
		(lhash_1, rhash_1, ldata_1, rdata_1) = fetch_children_hash(path=search[:])
		(lhash_2, rhash_2, ldata_2, rdata_2) = fetch_children_hash(path=search[:])
		if ldata_1 or rdata_1:
			break
		if lhash1 == lhash_2:
			search.append('r')
		else:
			search.append('l')
	if ldata_1==ldata_2:
		block_root_1 = rdata_1
		block_root_2 = rdata_2
	else:
		block_root_1 = ldata_1
		block_root_2 = ldata_2

	# empty the list to do a search for the transaction-level now
	search[:] = []
	while True:
		(lhash_1, rhash_1, ldata_1, rdata_1) = fetch_children_hash(forest[block_root_1], path=search[:])
		(lhash_2, rhash_2, ldata_2, rdata_2) = fetch_children_hash(forest[block_root_2], path=search[:])
		if ldata_1 or rdata_1:
			break
		if lhash1 == lhash_2:
			search.append('r')
		else:
			search.append('l')
	if ldata_1==ldata_2:
		tx_root_1 = rdata_1
		tx_root_2 = rdata_2
	else:
		tx_root_1 = ldata_1
		tx_root_2 = ldata_2



def setup():
	leaf1 = [('5L6MXERSD1', 12),
	('aaaa', 44),
	('JJ37EKAMFW', 82),
	('YNHD2KBPMV', 130),
	('ORVRGN1H91', 153),
	('N9G7HRLAK0', 203),
	('17032RG0Y5', 237),
	('HY5AP0VUZB', 268),
	('2HOPM7EM2S', 344),
	('JMERH7P0F6', 352),
	('KK4LVZ4YU0', 379),
	('A523CJ0WHF', 397),
	('PZJWTB9I1V', 427),
	('3S5FF3SVRZ', 458),
	('S60R926WB1', 477),
	('9F9YEFQQGF', 484),
	('RUSV9ABHI0', 530),
	('PARIJP7EFN', 556),
	('PLUQBUPWEO', 603),
	('5LTSRTWU5H', 673),
	('5ZIJQNSL0M', 720),
	('A87CRINO12', 740),
	('IE4A07QBIG', 789),
	('UKEM8ELQYM', 838),
	('SNYLMZPN6G', 853),
	('MSOYUCXY2D', 875),
	('XXFJQKEFNE', 913),
	('D233U6MA0S', 946),
	('QN1XP0VV8G', 982),
	('NKEG1HUUKH', 1028)]

	leaf2 = [('5L6MXERSD1', 12),
	('RQ5GI2TKQV', 44),
	('JJ37EKAMFW', 82),
	('YNHD2KBPMV', 130),
	('ORVRGN1H91', 153),
	('N9G7HRLAK0', 203),
	('17032RG0Y5', 237),
	('HY5AP0VUZB', 268),
	('2HOPM7EM2S', 344),
	('JMERH7P0F6', 352),
	('KK4LVZ4YU0', 379),
	('A523CJ0WHF', 397),
	('PZJWTB9I1V', 427),
	('3S5FF3SVRZ', 458),
	('S60R926WB1', 477),
	('9F9YEFQQGF', 484),
	('RUSV9ABHI0', 530),
	('PARIJP7EFN', 556),
	('PLUQBUPWEO', 603),
	('5LTSRTWU5H', 673),
	('5ZIJQNSL0M', 720),
	('A87CRINO12', 740),
	('IE4A07QBIG', 789),
	('UKEM8ELQYM', 838),
	('SNYLMZPN6G', 853),
	('MSOYUCXY2D', 875),
	('XXFJQKEFNE', 913),
	('D233U6MA0S', 946),
	('QN1XP0VV8G', 982),
	('NKEG1HUUKH', 1028)]

	global t1, t2
	t1 = MerkleTree(leaves=leaf1)
	t1.build()
	t2 = MerkleTree(leaves=leaf2)
	t2.build()
	merkle_forest[codecs.encode(t1.root.val, 'hex_codec')] = t1
	merkle_forest[codecs.encode(t2.root.val, 'hex_codec')] = t2
	global t1_root, t2_root
	t1_root = (codecs.encode(t1.root.val, 'hex_codec'), t1.root.idx)
	t2_root = (codecs.encode(t2.root.val, 'hex_codec'), t2.root.idx)

def main():
	setup()
	block_verifier(t1_root, t2_root)

if __name__ == '__main__':
    main()