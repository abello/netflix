#distutils: language = c++
from libcpp.unordered_map cimport unordered_map
from libc.stdlib cimport malloc, free
from cython.operator cimport dereference as deref

# SO and google (and code samples) were used to hack this together

cdef int NUM_USERS = 458293

cdef int NUM_MOVIES = 17770

# Struct elem that is gonna be stored on each hashtable entry
# TODO: See if we can make this a bitfield
cdef struct s_elem:
    unsigned short cache
    unsigned short rating
ctypedef s_elem elem

# TODO: Use reserve?
# TODO: Set load factors
cdef unordered_map[unsigned int, elem] cache

def cache_init(um_dta):
    cdef int len_user, j, u, m
    cdef elem *e

    for u in xrange(NUM_USERS):
        user = um_dta[u]
        len_user = len(user)

        # All values OBO
        for j in range(0, len_user, 2):
            e = <elem *> malloc(sizeof(elem))
            
            # movie_id
            m = user[j] - 1

            cache[u * NUM_MOVIES + m] = deref(e)
            #cache.emplace(u * NUM_MOVIES + m, <float>0.4)

def cache_get(unsigned int movie, unsigned int user):
    return cache[user * NUM_MOVIES + movie].cache / 100.0

def cache_set(unsigned int movie, unsigned int user, double val):
    cache[user * NUM_MOVIES + movie].cache = <unsigned short> (val * 100)

def ratings_get(unsigned int movie, unsigned int user):
    return cache[user * NUM_MOVIES + movie].rating / 100.0

def ratings_set(unsigned int movie, unsigned int user, double val):
    cache[user * NUM_MOVIES + movie].rating = <unsigned short> (val * 100)
