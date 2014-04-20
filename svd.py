import numpy as np
import sys


# Dunny declarations, just for globals 

# Number of users in all.dta
NUM_USERS = 458293

# Number of movies
NUM_MOVIES = 17770

movie_avgs = 0
user_ofsts = 0

# Profiling stuff from https://zapier.com/engineering/profiling-python-boss/

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



NUM_FEATURES = 40

NUM_ITERATIONS = 3

# TODO: Average of what?
GLOBAL_AVG = 3.512599976023349

cache = [None for i in xrange(NUM_USERS)]

K = 25

TRAINING_STARTED = False

# User features and movie features globals
user_features = [None for i in xrange(NUM_FEATURES)]

movie_features = [None for i in xrange(NUM_FEATURES)]


# Initializes the feature vectors
def init_features():
    global user_features
    global movie_features

    for f in xrange(NUM_FEATURES):
        user_features[f] = np.array([0.1 for i in xrange(NUM_USERS)], dtype=np.float16)
        movie_features[f] = np.array([0.1 for i in xrange(NUM_MOVIES)], dtype=np.float16)

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

# Returns the rating for this (movie, user) pair
# Both movie and user are OBO
def get_rating(movie, user):
    tmp = data[user]
    for i in xrange(0, len(tmp), 2):
        if (tmp[i] - 1) == movie:
            return tmp[i + 1]
    print "Invalid get_rating. Exiting.", user, movie
    sys.exit()

def cache_init():
    for i in xrange(NUM_USERS):
        user = um_dta[i]
        # convert to float16 array:
        user_float = np.array(user, dtype=np.float16)
        # Initialize the cache for every movie to 0.4
        for j in xrange(1, len(user_float), 2):
            user_float[j] = 0.4
        cache[i] = user_float

def cache_set(movie_id, user_id, val):
    user = cache[user_id]
    for i in xrange(0, len(user), 2):
        if (user[i] - 1) == movie_id:
            user[i + 1] = val
            break
    print "Invalid cache set. Exiting.", user_id, movie_id
    sys.exit()

def cache_get(movie_id, user_id):
    user = cache[user_id]
    for i in xrange(0, len(user), 2):
        if (user[i] - 1) == movie_id:
            return user[i + 1]
    print "Invalid cache set. Exiting.", user_id, movie_id
    sys.exit()

# This version should be used only TRAINING_STARTED is false, i.e. in the 
# first iteration
# Should be inlined
# def predict_rating_t_0(movie, user, movie_avg, user_off):
#     return movie_avg[movie - 1] + user_off[user - 1]


# (Training version) 
# Should be inlined
# Takes OBO user_id and movie_id
def predict_rating_t(movie, user):
    return cache_get(movie, user)


# Train! Super critical sector, needs to be heavily optimized.
# Takes the OBO user_id and movie_id
# TODO: The Thikonov regularization stuff
def train(movie, user, f):
    user_off = user_ofsts[user]
    movie_avg = movie_avgs[movie]

    # Rating we currently have
    predicted = predict_rating_t(movie, user)

    tmp = user_features[f][user] * movie_features[f][movie]
    actual_rating = get_rating(movie, user)

    error = LEARNING_RATE * (actual_rating - predicted)

    uv_old = user_features[f][user]
    user_features[f][user] += error * movie_features[f][movie]
    movie_features[f][movie] += error * uv_old
    
    # Update cache
    cache_set(movie, user, cache_get(user, movie) - tmp + user_features[f][user] * movie_features[f][movie])


        
# Cythonize this so it unrolls loops and stuff
def main():
    pass

if __name__ == "__main__":
    f1, f2 = open('data.npz', 'r'), open('data-mu.npz', 'r')
    um = np.load(f1)
    global um_dta
    um_dta = um["arr_0"]
    f1.close()
#     mu = np.load(f2)
#     global mu_dta
#     mu_dta = mu["arr_0"]
#     f2.close()

    print "Loaded from files"


#     movie_avgs = compute_avg(mu_dta, True)
    movie_avgs = np.load(open("movie_avgs", "r"))
    # Shouldn't need this after this point
    print "Loaded movie averages"

#     user_ofsts = compute_user_offset(movie_avgs)
    user_ofsts = np.load(open("user_ofsts", "r")) 
    print "Loaded user offsets"

    # Initialize cache
    cache_init()
    print "Initialized cache"

    init_features()
    print "Initialized features"


    data = um_dta

    for i in xrange(NUM_ITERATIONS):
        for f in xrange(NUM_FEATURES):
            for u in xrange(NUM_USERS):
                for j in xrange(len(data[u]) / 2):
                    movie = data[u][2 * j] - 1
                    train(movie, u, f)
        print "Finished iteration %d", i



