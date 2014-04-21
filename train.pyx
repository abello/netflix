#distutils: language = c
# cython: profile=True
from cython.operator cimport dereference as deref
import numpy as np
cimport numpy as np
from ht import cache_get, cache_set
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
    cdef np.ndarray[np.int32_t, ndim=1] compressed, users_per_movie
    cdef int movie
    cdef float user_off, movie_avg, predicted, tmp
    cdef int actual_rating
    cdef float error, uv_old
    cdef int len_data_user
    cdef int _movies = 0
    cdef float _sum = 0

    compressed = np.load('compressed_arr.npy')
    users_per_movie = np.load('users_per_movie.npy')

    for i in xrange(NUM_ITERATIONS):
        for f in xrange(NUM_FEATURES):
            uf = user_features[f]
            mf = movie_features[f]
            idx = 0 # index for the compressed array

            for movie in xrange(NUM_MOVIES):
                start = time.time()
                num_users = users_per_movie[movie]
                movie_avg = movie_avgs[movie]
                for user_idx in xrange(idx, idx + num_users * 2, 2):
                    user = compressed[user_idx] - 1 # Make zero indexed
                    actual_rating = compressed[user_idx + 1]

                    # Rating we currently have
                    predicted = cache_get(movie, user)

                    tmp = uf[user] * mf[movie]

                    error = LEARNING_RATE * (actual_rating - predicted)

                    uv_old = uf[user]
                    uf[user] += error * mf[movie]
                    mf[movie] += error * uv_old
                    
                    # Update cache
                    cache_set(movie, user, cache_get(movie, user) - tmp + uf[user] * mf[movie])

                idx += num_users * 2
                _sum += time.time() - start
                _movies += 1
                if (user % 1000) == 0:
                    print "avg for 1000 movies", _sum/_movies
                    _sum = 0
                    _movies =0
        print "Finished iteration %d", i
