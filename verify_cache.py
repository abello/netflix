import numpy as np
from ht import cache_init, cache_get, cache_set, ratings_get, ratings_set

if __name__ == '__main__':
    f = open('data.npz', 'r')
    um = np.load(f)
    um_dta = um["arr_0"]
    cache_init(um_dta)
    NUM_USERS = np.shape(um_dta)[0]
    for i in xrange(NUM_USERS):
        user = i
        for j in xrange(0, len(um_dta[i]), 2):
            movie = um_dta[j] - 1
            rating = um_dta[i][j + 1]
            assert (rating == ratings_get(movie, user))
            assert (cache_get(movie, user) == 0.4)
    print "Cache was initialized properly!"
    f.close()
