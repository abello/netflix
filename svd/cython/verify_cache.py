import numpy as np
from ht import cache_init, cache_get, cache_set
import math

if __name__ == '__main__':
    f = open('data.npz', 'r')
    um = np.load(f)
    um_dta = um["arr_0"]
    NUM_USERS = np.shape(um_dta)[0]

    print "Loaded from file"

    cache_init(um_dta)
    print "Initialized cache"

    for i in xrange(NUM_USERS):
        user = i
        for j in xrange(0, len(um_dta[i]), 2):
            movie = um_dta[user][j]  - 1
            rating = um_dta[i][j + 1]
            assert (abs(cache_get(movie, user) - 0.4) < 0.0001)
    print "Cache was initialized properly!"
    f.close()
