import time
import monero_client as client
import numpy as np
client.main()

t1_root, t2_root = client.t1_root, client.t2_root
server1, server2 = client.server1, client.server2

def query_test():
    req_gidx = np.random.randint(0,t1_root[1]+1)
    start = time.time()
    client.get_output(server1, req_gidx)
    end = time.time()
    elapsed = end - start
    return elapsed

def main():
    for x in range(0,10):
        passed = query_test()
        print passed