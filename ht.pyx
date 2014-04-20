#distutils: language = c++
#from libcpp.unordered_map cimport unordered_map

# SO and google (and code samples) were used to hack this together

cdef int NUM_USERS = 458293

cdef int NUM_MOVIES = 17770

cdef unordered_map[int, float] *cache


    

from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.pair cimport pair
 
cdef extern from "<unordered_map>" namespace "stl":
    cdef cppclass unordered_map[int, float]: # K: key_type, T: mapped_type
        cppclass iterator:
            pair& operator*()
            bint operator==(iterator)
            bint operator!=(iterator)
        unordered_map()
        bint empty()
        size_t size()
        iterator begin()
        iterator end()
        pair emplace(K, T)
        iterator find(K)
        void clear()
        size_t count(K)
        T& operator[](K)
 

cdef unordered_map[int, float] *cache = new unordered_map[int, float]()


def cache_init(um_dta, user):
    cdef int len_user, j, u, m

    cache = new unordered_map[int, float]()


    for u in xrange(NUM_USERS):
        user = um_dta[u]
        len_user = len(user)

        # All values OBO
        for j in range(0, len_user, 2):
            # movie_id
            m = user[j] - 1

            #cache[u * NUM_MOVIES + m] = <float>0.4
            cache.emplace(u * NUM_MOVIES + m, <float>0.4)
