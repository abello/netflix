#distutils: language = c++
from libcpp.unordered_map cimport unordered_map

# SO and google (and code samples) were used to hack this together

cdef int NUM_USERS = 458293

cdef int NUM_MOVIES = 17770

# TODO: Use reserve?
# TODO: Set load factors
cdef unordered_map[unsigned int, float] cache
cdef unordered_map[unsigned int, float] ratings

def cache_init(um_dta):
    cdef int len_user, j, u, m

    for u in xrange(NUM_USERS):
        user = um_dta[u]
        len_user = len(user)

        # All values OBO
        for j in range(0, len_user, 2):
            # movie_id
            m = user[j] - 1

            cache[u * NUM_MOVIES + m] = <float>40
            #cache.emplace(u * NUM_MOVIES + m, <float>0.4)

def cache_get(unsigned int movie, unsigned int user):
    return cache[user * NUM_MOVIES + movie]

def cache_set(unsigned int movie, unsigned int user, double val):
    cache[user * NUM_MOVIES + movie] = (float) (val * 100)



def ratings_init(um_dta):
    cdef int len_user, j, u, m

    for u in xrange(NUM_USERS):
        user = um_dta[u]
        len_user = len(user)

        # All values OBO
        for j in range(0, len_user, 2):
            # movie_id
            m = user[j] - 1

            cache[u * NUM_MOVIES + m] = <float>user[j+1]
            #cache.emplace(u * NUM_MOVIES + m, <float>0.4)

def ratings_get(unsigned int movie, unsigned int user):
    return ratings[user * NUM_MOVIES + movie]

def ratings_set(unsigned int movie, unsigned int user, double val):
    ratings[user * NUM_MOVIES + movie] = (float) (val * 100)
