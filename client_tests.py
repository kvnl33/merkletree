import time, sys
import monero_client as client
import numpy as np
client.main()

first_arg = sys.argv[1]

t1_root, t2_root = client.t1_root, client.t2_root
server1, server2 = client.server1, client.server2

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
    else:
        print "Please provide a valid argument."
        
if __name__ == '__main__':
    main()