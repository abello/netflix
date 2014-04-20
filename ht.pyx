#distutils: language = c++
from libcpp.unordered_map cimport unordered_map
from libc.stdlib cimport malloc, free
from cython.operator cimport dereference as deref

# SO and google (and code samples) were used to hack this together

cdef int NUM_USERS = 458293

cdef int NUM_MOVIES = 17770

# Struct elem that is gonna be stored on each hashtable entry
# TODO: See if we can make this a bitfield
#cdef packed struct s_elem:
#    unsigned short cache
#    unsigned char rating
#ctypedef s_elem elem

# TODO: Use reserve?
# TODO: Set load factors
cdef unordered_map[unsigned int, unsigned int] cache

def cache_init(um_dta):
    cdef int len_user, j, u, m
    cdef unsigned short c, r
    #cdef elem *e

    for u in xrange(NUM_USERS):
        user = um_dta[u]
        len_user = len(user)

        # All values OBO
        for j in xrange(0, len_user, 2):
            #e = <elem *> malloc(sizeof(elem))

            # movie_id
            m = user[j] - 1
            c = <unsigned short> 400
            r = <unsigned short> user[j+1]

            cache[u * NUM_MOVIES + m] = <unsigned int> ((c<<16) | (r & 0xffff))

def cache_get(unsigned int movie, unsigned int user):
    #return cache[user * NUM_MOVIES + movie].cache / 100.0
    return 1

def cache_set(unsigned int movie, unsigned int user, double val):
    #cache[user * NUM_MOVIES + movie].cache = <unsigned short> (val * 100)
    return 1

def ratings_get(unsigned int movie, unsigned int user):
    #return cache[user * NUM_MOVIES + movie].rating
    return 1

def ratings_set(unsigned int movie, unsigned int user, unsigned char val):
    return 1
    #cache[user * NUM_MOVIES + movie].rating = val

def store_shorts(unsigned short high, unsigned short low):
    return (high << 16) | (low & 0xffff)

def get_low(unsigned int num):
    return num & 0xffff

#420
def get_high(unsigned int num):
    return (num >> 16) & 0xffff

