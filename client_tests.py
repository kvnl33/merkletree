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

def main():
    if first_arg=="query":
        print "Testing 1000 queries..."
        for server in [server1, server2]:
            for x in range(0,500):
                passed = query_test(server)
                print passed
    else:
        print "Please provide an argument"
        
if __name__ == '__main__':
    main()