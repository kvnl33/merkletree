from merkle import Node, MerkleTree, check_chain, check_hex_chain
from collections import OrderedDict
import codecs, string, random
from random import randint

blocks = []
block_headers = []

def find_nearest_above(my_array, target):
	return min(filter(lambda y: y >= target,my_array))

#random string generator for our blocks 
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def main():
	for i in range(0,100,5):
		outputs = []
		for j in range(0,5):
			outkey = id_generator()
			output = (outkey,i+j)
			outputs.append(output)
		newtree = MerkleTree(leaves=outputs)
		newtree.build()
		k = newtree.root
		root = (codecs.encode(k.val, 'hex_codec'), k.idx)
		blocks.append(newtree)
		block_headers.append(root)





tree = MerkleTree(leaves=[	('3475190c7d74e9317683784fbd4acbb65dcddad2f1451f3cb202c32ab8f7bc49', 1), 
							('c88bc6945b71287cc4c26f60ed944dac07dbc86a2d3c493f0ecbb9cd1629f9c5', 2), 
							('9563534da2c04ce6812a72fb320cf69d1e4dd74515ac955265d7c8c1c37da600', 3), 
							('f6e15d94bbe86a92c4bc2331c98ac8868e0be246242b76445eea1e5cf7993483', 4), 
							('bde35c12ec670136ede10de8a9ee02753da029e02e39b86244d191ee41455970', 5)])



tree.build()
k = tree.root

root = (codecs.encode(k.val, 'hex_codec'), k.idx)
print root

m = tree.get_all_hex_chains()

for chain in m:
	print chain
	print check_hex_chain(chain) == root[0]

tree.add_adjust(('5e47412218f25a770d7bacf5a509c783c2791b9cfd75e7e405bfcd6ceb3a17ab', 9))
m = tree.get_all_hex_chains()

k = tree.root
root = (codecs.encode(k.val, 'hex_codec'), k.idx)

for chain in m:
	print chain
	print check_hex_chain(chain) == root[0]

print root

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

for leaf in tree.leaves:
	print leaf.data