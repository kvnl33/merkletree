import time, sys, cProfile, os
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

def main():
    if first_arg=="build":
        print "Profiling build time..."
        avg = []
        for x in range(0,10):
            print "Currently on iteration: %d"%(x+1)
            if os.path.isfile("/data/rct_output_10_23_2017.p"):
                os.remove("/data/rct_output_10_23_2017.p")
            avg.append(build_time())
        print avg
        print "Average time to build data structure for 100 trials is %.6f seconds."%(np.average(avg))

if __name__ == '__main__':
    main()