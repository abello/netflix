#distutils: language = c
cimport cython
from cython.operator cimport dereference as deref
import numpy as np
cimport numpy as np
import time
from random import random
import sys

# SO and google (and code samples) were used to hack cython together

cdef int NUM_USERS = 458293

cdef int NUM_MOVIES = 17770

cdef float LEARNING_RATE = 0.01

# HAS TO BE CHANGED IN BOTH TRAIN AND SVD
cdef int NUM_FEATURES = 5

<<<<<<< HEAD
cdef int NUM_ITERATIONS = 5 
=======
cdef int NUM_ITERATIONS = 40
>>>>>>> 2e9b9195a0bec2fe81955ebfad24927191895151

# Regularization parameter, as in TD article
cdef float K = 0.015


# @cython.boundscheck(False)
# @cython.wraparound(False)
# @cython.nonecheck(False)
# @cython.overflowcheck(False)
def loop(np.ndarray[np.float32_t, ndim=1] user_ofsts, np.ndarray[np.float32_t, ndim=1] movie_avgs, np.ndarray[np.float32_t, ndim=1] uf, np.ndarray[np.float32_t, ndim=1] mf):
    cdef int i, f, user, j
    cdef np.ndarray[np.float32_t, ndim=1] compressed
    cdef np.ndarray[np.int32_t, ndim=1] users_per_movie
    cdef int movie
    cdef float user_off, movie_avg, predicted, tmp, rating
    cdef int actual_rating
    cdef float error, uv_old, mv_old
    cdef int _movies = 0
    cdef float _sum = 0
    cdef int u_bound, num_users, idx, user_idx
    
    # Cache update stuff
    cdef int _i
    cdef float _result

    compressed = np.load('compressed_arr.npy')
    users_per_movie = np.load('users_per_movie.npy')

    # Train all features one by one, for NUM_ITERATIONS each.

    for f in xrange(NUM_FEATURES):
        start = time.time()
        for i in xrange(NUM_ITERATIONS):
            idx = 0 # index for the compressed array

            for movie in xrange(NUM_MOVIES):
                num_users = users_per_movie[movie]
#                movie_avg = movie_avgs[movie]
                u_bound = idx + num_users * 3
                
                for user_idx in xrange(idx, u_bound, 3):
                    # 0-indexed user id
                    user = (<int> (compressed[user_idx])) - 1 # Make zero indexed

                    # Actual rating from the data set (fixed)
                    actual_rating = <int> (compressed[user_idx + 1])

                    # Rating we currently have
                    predicted = compressed[user_idx + 2]
                    #if (predicted <= 0):
                    #    predicted = 1.0

                    # Old values we have for the movie and user features
                    uv_old = uf[user * NUM_FEATURES + f]
                    mv_old = mf[movie * NUM_FEATURES + f]

                    predicted += uv_old * mv_old + (NUM_FEATURES - f - 1) * (0.1 * 0.1) 
                    print (NUM_FEATURES - f - 1) * (0.1 * 0.1)
                    if predicted > 5.0:
                        predicted = 5.0
                    if predicted < 1.0:
                        predicted = 1.0

                    error = (<float> actual_rating) - predicted

#                     tmp = uv_old * mv_old

#                     uf[user] += error * mv_old
#                     mf[movie] += error * uv_old

                    # Cross train, as in TD article
                    uf[user * NUM_FEATURES + f] += LEARNING_RATE * (error * mv_old - K * uv_old)
                    mf[movie * NUM_FEATURES + f] += LEARNING_RATE * (error * uv_old - K * mv_old)

                    # Update cache
                    # compressed[user_idx + 2] = predicted - tmp + uf[user] * mf[movie]

#                     rating = predicted - tmp + (uv_old + error * mv_old) * (mv_old + error * uv_old)




                idx += num_users * 3
                #_sum += time.time() - start
                #_movies += 1

        # Finished training feature here, update cache (using the TD article approach)
        for movie in xrange(NUM_MOVIES):
            idx = 0
            num_users = users_per_movie[movie]
            u_bound = idx + num_users * 3
            for user_idx in xrange(idx, u_bound, 3):
                # 0-indexed user id
                user = (<int> (compressed[user_idx])) - 1 # Make zero indexed

                # Update cache
                _result = compressed[user_idx + 2] 

                #if _result <= 0.0:
                #    _result = 1.0
                _result += uf[user * NUM_FEATURES + f] * mf[movie * NUM_FEATURES + f]
                    
                if _result > 5.0:
                    _result = 5.0
                elif _result < 1.0:
                    _result = 1.0
                    
                compressed[user_idx + 2] = _result

            idx += num_users * 3
                        


        print "Finished iteration", i, " in", int(time.time() - start), "seconds"


# Gets OBO ids
# @cython.boundscheck(False)
# @cython.wraparound(False)
# @cython.nonecheck(False)
# @cython.overflowcheck(False)
cpdef float predict(int movie, int user, np.ndarray[np.float32_t, ndim=1] uf, np.ndarray[np.float32_t, ndim=1] mf):
    cdef int i
    cdef float result = 0.0

    for i in range(NUM_FEATURES):
        result += uf[user * NUM_FEATURES + i] * mf[movie * NUM_FEATURES + i]

    # The below adjustment was made after consulting: http://www.timelydevelopment.com/demos/NetflixPrize.aspx
    if result > 5.0:
        result = 5.0
    elif result < 1.0:
        result = 1.0

    return result
