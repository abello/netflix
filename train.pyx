#distutils: language = c++
from cython.operator cimport dereference as deref
import numpy as np
cimport numpy as np
import time

# SO and google (and code samples) were used to hack this together

cdef int NUM_USERS = 458293

cdef int NUM_MOVIES = 17770

# SO and google (and code samples) were used to hack this together

cdef float LEARNING_RATE = 0.001

cdef int NUM_FEATURES = 40

cdef int NUM_ITERATIONS = 40


def loop(np.ndarray[np.float32_t, ndim=1] user_ofsts, np.ndarray[np.float32_t, ndim=1] movie_avgs, user_features, movie_features):
    cdef int i, f, user, j
    cdef np.ndarray[np.float32_t, ndim=1] uf, mf
    cdef np.ndarray[np.float32_t, ndim=1] compressed
    cdef np.ndarray[np.int32_t, ndim=1] users_per_movie
    cdef int movie
    cdef float user_off, movie_avg, predicted, tmp
    cdef int actual_rating
    cdef float error, uv_old
    cdef int _movies = 0
    cdef float _sum = 0
    cdef int u_bound, num_users, idx, user_idx

    compressed = np.load('compressed_arr.npy')
    users_per_movie = np.load('users_per_movie.npy')

    for i in xrange(NUM_ITERATIONS):
        start = time.time()
        for f in xrange(NUM_FEATURES):
            uf = user_features[f]
            mf = movie_features[f]
            idx = 0 # index for the compressed array

            for movie in xrange(NUM_MOVIES):
                num_users = users_per_movie[movie]
                movie_avg = movie_avgs[movie]
                u_bound = idx + num_users * 3
                for user_idx in xrange(idx, u_bound, 3):
                    user = (<int> (compressed[user_idx])) - 1 # Make zero indexed
                    actual_rating = <int> (compressed[user_idx + 1])

                    # Rating we currently have
                    predicted = compressed[user_idx + 2]

                    tmp = uf[user] * mf[movie]

                    error = LEARNING_RATE * (actual_rating - predicted)

                    uv_old = uf[user]
                    uf[user] += error * mf[movie]
                    mf[movie] += error * uv_old
                    
                    # Update cache
                    compressed[user_idx + 2] = predicted - tmp + uf[user] * mf[movie]

                idx += num_users * 3
                #_sum += time.time() - start
                #_movies += 1
        print "Finished iteration", i, time.time() - start
