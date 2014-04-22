import numpy as np
import sys
import traceback
from line_profiler import LineProfiler
import time
from scipy.sparse import coo_matrix, csr_matrix
import cPickle as cp
from train import loop, predict


# Dunny declarations, just for globals 

# Number of users in all.dta
NUM_USERS = 458293

# Number of movies
NUM_MOVIES = 17770

# Number of (user, movie) pairs (ie ratings)
# TODO: Verify this
NUM_PAIRS = 98291669


# LEARNING_RATE = 0.001
# 
# HAS TO BE CHANGED IN BOTH TRAIN AND SVD
NUM_FEATURES = 10

movie_avgs = 0
user_ofsts = 0

uf = None
mf = None

# Profiling stuff from https://zapier.com/engineering/profiling-python-boss/
def timef(f):
    def f_timer(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        print f.__name__, 'took', end - start, 'time'
        return result
    return f_timer

def do_profile(follow=[]):
    def inner(func):
        def profiled_func(*args, **kwargs):
           try:
               profiler = LineProfiler()
               profiler.add_function(func)
               for f in follow:
                   profiler.add_function(f)
               profiler.enable_by_count()
               return func(*args, **kwargs)
           finally:
               profiler.print_stats()
        return profiled_func
    return inner

def get_number():
    for x in xrange(5000000):
        yield x

# EDN profiling stuff



# TODO: Average of what?
GLOBAL_AVG = 3.512599976023349

cache = {}
ratings = {}

K = 25

TRAINING_STARTED = False


# Initializes the feature vectors
def init_features():
    global uf
    global mf
    uf = np.array([0.2738612 for i in xrange(NUM_USERS * NUM_FEATURES)], dtype=np.float32)
    mf = np.array([0.2738612  for i in xrange(NUM_MOVIES * NUM_FEATURES)], dtype=np.float32)

# Takes either mu or um numpy array (from data.npz or data-mu.npz), returns a
# list of lists, index being movie/user index, value being movie avg or user 
# average rating.
def compute_avg(np_arr, improved=False):
    height = np.shape(np_arr)[0] - 1
    avg_arr = [0 for i in xrange(height)]
    if not improved:
        for i in xrange(height):
            avg_arr[i] = sum(np_arr[i+1][1::2]) / float(len(np_arr[i+1][1::2]))
    else:
        for i in xrange(height):
            avg_arr[i] = (GLOBAL_AVG * K + sum(np_arr[i+1][1::2])) / (K + len(np_arr[i+1][1::2]))

    return avg_arr

def compute_user_offset(movie_avg):
    result = np.array([0 for i in xrange(NUM_USERS)], dtype=np.float16)
    for i in xrange(NUM_USERS):
        c = 0
        user = um_dta[i]
        len_user = len(user)
        ratings = [0 for k in xrange(0, len_user, 2)]
        for j in xrange(0, len_user, 2):
            movie_id = user[j]
            user_rating = user[j + 1]
            actual_rating = movie_avg[movie_id - 1]
            diff = user_rating - actual_rating

            ratings[c] = diff
            c += 1
        result[i] = sum(ratings) / float(len_user/2)
    return result



def output():
    output = open('output.dta', 'w+')
    with open('qual.dta', 'r') as qual:
        for line in qual:
            user_id, movie_id, time = [int(v) for v in line.split()]
            output.write(str(predict(movie_id - 1, user_id - 1)) + "\n")
        

if __name__ == "__main__":
#     f1 = open('data.npz', 'r')
#     um = np.load(f1)
#     global um_dta
#     um_dta = um["arr_0"]
#     f1.close()
# 
#     print "Loaded from files"


#     movie_avgs = compute_avg(mu_dta, True)
    movie_avgs = np.load(open("movie_avgs", "r"))
    movie_avgs = np.array(movie_avgs, dtype=np.float32)
    # Shouldn't need this after this point
    print "Loaded movie averages"

#     user_ofsts = compute_user_offset(movie_avgs)
    user_ofsts = np.load(open("user_ofsts", "r")) 
    user_ofsts = np.array(user_ofsts, dtype=np.float32)
    print "Loaded user offsets"


    # Initialize cache
#     cache = cp.load(open("cache", "r"))
    #cache_init(um_dta) 
#     print "Initialized cache"


    # Initialize ratings
#     ratings = cp.load(open("ratings", "r"))
#     ratings_init()
#     print "Loaded ratings"

    init_features()
    print "Initialized features"

#     data = um_dta
#     del data
#     del um_dta

    print "Starting training..."
    loop(user_ofsts, movie_avgs, uf, mf)
    print "Training finished"


