from merkle import Node, MerkleTree, check_chain, check_hex_chain
import codecs

tree = MerkleTree(leaves=[('a',1), ('b',2), ('c', 3), ('d', 4), ('e', 5)])
tree.build()
k = tree.root

root = (codecs.encode(k.val, 'hex_codec'), k.idx)
print root

m = tree.get_all_hex_chains()

for chain in m:
	print chain
	print check_hex_chain(chain) == root[0]

tree.add_adjust(('f', 30))
m = tree.get_all_hex_chains()

k = tree.root
root = (codecs.encode(k.val, 'hex_codec'), k.idx)

for chain in m:
	print chain
	print check_hex_chain(chain) == root[0]

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