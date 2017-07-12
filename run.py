from merkle import Node, MerkleTree, check_chain, check_hex_chain
import codecs

tree = MerkleTree(leaves=[('s',234), ('b',2), ('e', 3)])
tree.build()
k = tree.root

if k:
	print "HELLO"
	print "Merkle Root:" + codecs.encode(k.val, 'hex_codec')
	print k.idx 

m = tree.get_all_hex_chains()
print m

