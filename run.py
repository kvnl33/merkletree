from merkle import Node, MerkleTree, _check_proof, check_proof
from collections import OrderedDict
import codecs, string, random
from random import randint
from hashlib import sha256

hash_function = sha256

blocks = OrderedDict()
block_headers = OrderedDict()

def find_nearest_above(my_array, target):
	return min(filter(lambda y: y >= target,my_array))

#random string generator for our blocks 
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

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

def main():
	for i in range(0,1000,5):
		# generate a block
		


		outputs = []
		for j in range(0,5):
			outkey = id_generator()
			output = (outkey,i+j)
			outputs.append(output)



		newtree = MerkleTree(leaves=outputs)
		newtree.build()
		k = newtree.root
		root = (codecs.encode(k.val, 'hex_codec'), k.idx)
		blocks[k.idx] = newtree
		block_headers[k.idx] = root






	block_headers_keys = block_headers.keys()
	blocks_keys = blocks.keys()

	#Run a test 100 times
	correct = incorrect = 0
	for _ in range(0,100):

		c = randint(0,999)
		#The client will make a request using c, and collect the ground truth

		d = find_nearest_above(block_headers_keys, c)
		truth = block_headers[d]

		e = find_nearest_above(blocks_keys, c)
		tree = blocks[e]
		
		avail = [leaf.idx for leaf in tree.leaves]
		chosen = avail.index(e)







		proof = tree.get_proof(chosen)

		data = tree.leaves[chosen].data
		print "Chosen index: " + str(c) + ', Returned data: ' + str(data) 

		#check if the data returned is hashed to the first element in the proof
		if hash_function(data).hexdigest() == proof[0][0][0]:

			#check the Merkle proof
			if check_proof(proof) == truth[0]:
				correct += 1
			else:
				incorrect += 1
		else:
			incorrect += 1

	total = correct + incorrect
	print "Number Correct: " + str(correct) + '/' + str(total)
	print "Number Incorrect: " + str(incorrect) + '/' + str(total)

if __name__ == '__main__':
	main()

