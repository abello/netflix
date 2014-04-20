#distutils: language = c++
#from libcpp.unordered_map cimport unordered_map

# SO and google (and code samples) were used to hack this together

cdef int NUM_USERS = 458293

cdef int NUM_MOVIES = 17770



    

from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.pair cimport pair
 
cdef extern from "<unordered_map>" namespace "std":
    cdef cppclass unordered_map[T, U]:
        cppclass iterator:
            pair[T, U]& operator*() nogil
            iterator operator++() nogil
            iterator operator--() nogil
            bint operator==(iterator) nogil
            bint operator!=(iterator) nogil
        unordered_map()
        unordered_map(unordered_map&)
        U& operator[](T&) nogil
        # unordered_map& operator=(unordered_map&)
        U& at(T&) nogil
        iterator begin() nogil
        void clear() nogil
        size_t count(T&) nogil
        bint empty() nogil
        iterator end() nogil
        pair[iterator, iterator] equal_range(T&) nogil
        void erase(iterator) nogil
        void erase(iterator, iterator) nogil
        size_t erase(T&) nogil
        iterator find(T&) nogil
        pair[iterator, bint] insert(pair[T, U]) nogil
        iterator insert(iterator, pair[T, U]) nogil
        void insert(input_iterator, input_iterator)
        size_t max_size() nogil
        void rehash(size_t)
        size_t size() nogil
        void swap(unordered_map&) nogil

cdef unordered_map[int, float] cache

def cache_init(um_dta, user):
    cdef int len_user, j, u, m



    for u in xrange(NUM_USERS):
        user = um_dta[u]
        len_user = len(user)

        # All values OBO
        for j in range(0, len_user, 2):
            # movie_id
            m = user[j] - 1

            cache[u * NUM_MOVIES + m] = <float>0.4
            #cache.emplace(u * NUM_MOVIES + m, <float>0.4)
