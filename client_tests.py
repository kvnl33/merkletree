import time, sys, requests, os, random, string
import monero_client as client
import monero_server as server
import numpy as np
from multiprocessing import Process

first_arg = sys.argv[1]
server1, server2 = client.server1, client.server2

def testup():
    try:
        requests.get(server2+"/getroot")
        return 1
    except:
        return 0

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def cleanup():
    if os.path.isfile("/data/rct_output_10_23_2017.p"):
        os.remove("/data/rct_output_10_23_2017.p")
    if os.path.isfile("/data/rct_output_10_23_2017.p"):
        os.remove("/data/rct_output_10_23_2017.p")
    if os.path.isfile("/data/merkle_forest"):
        os.remove("/data/merkle_forest")

def conflict_resolve():
    cleanup()
    server.read_in_blocks("rct_output_10_23_2017")
    modify = random.choice(server.utxos)
    idx = server.utxos.index(modify)
    num_outs = len(filter(lambda x: x[1] == modify[1], server.utxos))
    # modify a single output there
    server.utxos[idx] = (server.utxos[idx][0],server.utxos[idx][1],id_generator(size=64),server.utxos[idx][3])
    server.scan_over_new_blocks(server.utxos)
    pid = Process(target=server.app.run)
    pid.start()
    while True:
        if testup():
            break
    client.main()
    t1_root, t2_root = client.t1_root, client.t2_root
    client.block_verifier(t1_root, t2_root)
    print "The number of outputs in this transaction is %d" %(num_outs)
    pid.terminate()
    
def query_test(server):
    if server == server1:
        top = t1_root
    else:
        top = t2_root
    req_gidx = np.random.randint(0,top[1]+1)
    start = time.time()
    client.get_output(server, req_gidx)
    end = time.time()
    elapsed = end - start
    return elapsed

def proof_test(server):
    if server == server1:
        top = t1_root
    else:
        top = t2_root
    req_gidx = np.random.randint(0,top[1]+1)
    found_out, found_proof = client.get_output(server, req_gidx)
    start = time.time()
    client.check_path(found_out, found_proof, top)
    end = time.time()
    elapsed = end - start
    return elapsed

def main():
    if first_arg=="query":
        server2.main()
        print "Testing 1000 queries..."
        avg = []
        for server in [server1, server2]:
            for x in range(0,500):
                avg.append(query_test(server))
        print "Average query time for 1000 trials is %.6f seconds."%(np.average(avg))
    elif first_arg=="proof":
        avg = []
        print "Testing 1000 proofs..."
        for server in [server1, server2]:
            for x in range(0,500):
                avg.append(proof_test(server))
        print "Average time to check proof for 1000 trials is %.6f seconds."%(np.average(avg))
    elif first_arg=="conflict":
        avg = []
        print "Testing conflicts (this can take a while...)"
        conflict_resolve()
    else:
        print "Please provide a valid argument."
        
if __name__ == '__main__':
    main()