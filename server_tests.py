import time, sys, cProfile, os, shelve
import numpy as np
import monero_server as server

first_arg = sys.argv[1]

def build_time():
    start = time.time()
    server.read_in_blocks("rct_output_10_23_2017")
    server.scan_over_new_blocks(server.utxos)
    end = time.time()
    elapsed = end - start
    return elapsed

def add_adjust():
    server.main()
    print "Profiling adding to the top Merkle tree..."
    avg = []
    for x in range(0,100):
        start = time.time()
        server.update_test()
        end = time.time()
        elapsed = end-start
        avg.append(elapsed)
    return np.average(avg)

def main():
    if first_arg=="build":
        print "Profiling build time..."
        avg = []
        for x in range(0,10):
            print "Currently on iteration: %d"%(x+1)
            if os.path.isfile("/data/rct_output_10_23_2017.p"):
                os.remove("/data/rct_output_10_23_2017.p")
            if os.path.isfile("/data/merkle_forest"):
                os.remove("/data/merkle_forest")
                server.merkle_forest = shelve.open("/data/merkle_forest", protocol=-1)
            avg.append(build_time())
        print avg
        print "Average time to build data structure for 100 trials is %.6f seconds."%(np.average(avg))
    elif first_arg=="add":
        print "Average time to add to the top Merkle tree is %.6f seconds."%(add_adjust())

if __name__ == '__main__':
    main()