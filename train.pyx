#distutils: language = c
# cython: profile=True
from cython.operator cimport dereference as deref
import numpy as np
cimport numpy as np
from ht import cache_get, cache_set, ratings_get
import time

# SO and google (and code samples) were used to hack this together

cdef int NUM_USERS = 458293

cdef int NUM_MOVIES = 17770

cdef float LEARNING_RATE = 0.001

cdef int NUM_FEATURES = 40

cdef int NUM_ITERATIONS = 3

def loop(data, np.ndarray[np.float32_t, ndim=1] user_ofsts, np.ndarray[np.float32_t, ndim=1] movie_avgs, user_features, movie_features):
    cdef int i, f, user, j
    cdef np.ndarray[np.float32_t, ndim=1] uf, mf
    cdef int movie
    cdef float user_off, movie_avg, predicted, tmp
    cdef int actual_rating
    cdef float error, uv_old
    cdef int len_data_user
    cdef int _users = 0
    cdef float _sum = 0

    for i in xrange(NUM_ITERATIONS):
        for f in xrange(NUM_FEATURES):
            uf = user_features[f]
            mf = movie_features[f]
            for user in xrange(NUM_USERS):
                start = time.time()
                len_data_user = len(data[user])/2
                user_off = user_ofsts[user]

                for j in xrange(len_data_user):
                    movie = data[user][2 * j] - 1
                    movie_avg = movie_avgs[movie]

                    # Rating we currently have
                    predicted = cache_get(movie, user)

                    tmp = uf[user] * mf[movie]
                    actual_rating = ratings_get(movie, user)

                    error = LEARNING_RATE * (actual_rating - predicted)

                    uv_old = uf[user]
                    uf[user] += error * mf[movie]
                    mf[movie] += error * uv_old
                    
                    # Update cache
                    cache_set(movie, user, cache_get(movie, user) - tmp + uf[user] * mf[movie])

                _sum += time.time() - start
                _users += 1
                if (user % 1000) == 0:
                    print "avg for 1000 users", _sum/_users
                    _sum = 0
                    _users =0
        print "Finished iteration %d", i
