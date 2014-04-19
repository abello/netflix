import numpy as np


# Dunny declarations, just for globals 

NUM_USERS = 0
NUM_MOVIES = 0

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

cache = {}
cache_opt = [None for i in xrange(NUM_USERS)]

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
        user_features[f] = np.array([0.1 for i in xrange(NUM_USERS)])
        movie_features[f] = np.array([0.1 for i in xrange(NUM_MOVIES)])

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
            sum(np_arr[i+1][1::2])
            avg_arr[i] = (GLOBAL_AVG * K + sum(np_arr[i+1][1::2])) / (K + len(np_arr[i+1][1::2]))

    return avg_arr

def compute_user_offset(movie_avg):
    user_off = np.array([0 for i in xrange(NUM_USERS)], dtype=np.float16)
    for i in xrange(NUM_USERS):
        c = 0
        user = um_dta[i]
        len_user = len(user)
        ratings = [0 for i in xrange(0, len_user, 2)]
        for j in xrange(0, len_user, 2):
            movie_id = user[j]
            user_rating = user[j + 1]
            actual_rating = movie_avg[movie_id - 1]
            diff = user_rating - actual_rating

            ratings[c] = diff
            c += 1
        user_off[i] = sum(ratings) / float(len_user/2)
    return user_off

# Returns the rating for this (movie, user) pair
# TODO: Check this
def get_rating(movie, user):
    return data[user][2 * (movie - 1) + 1]


# Initialize the cache to baseline rating
# TODO: Use baseline at some point
def cache_init():
    global movie_avgs
    global user_ofsts

    movie_avgs = compute_avg(mu_dta, True)
    print "Computed movie averages"

    user_ofsts = compute_user_offset(movie_avgs)
    print "Computed user offsets"

    for u in xrange(1, NUM_USERS + 1):
        rng = len(um_dta[u])/2
        for i in xrange(rng):
            movie = um_dta[u][2*i]
#             cache[(movie, u)] = movie_avgs[movie - 1] + user_ofsts[u]
            cache[(movie, u)] = 0.4

def cache_opt_init():
    for i in xrange(NUM_USERS):
        user = um_dta[i]
        # convert to float16 array:
        user_float = np.array(user, dtype=np.float16)
        # Initialize the cache for every movie to 0.4
        for j in xrange(1, len(user_float), 2):
            user_float[j] = 0.4
        cache_opt[i] = user_float

# This version should be used only TRAINING_STARTED is false, i.e. in the 
# first iteration
# Should be inlined
# def predict_rating_t_0(movie, user, movie_avg, user_off):
#     return movie_avg[movie - 1] + user_off[user - 1]


# (Training version) 
# Should be inlined
# Takes actual user_id and movie_id
def predict_rating_t(movie, user):
    return cache[(user, movie)]


# Train! Super critical sector, needs to be heavily optimized.
# Takes the actual user_id and movie_id, no off by one crap
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
    cache[(user, movie)] = cache[(user, movie)] - tmp + user_features[f][user] * movie_features[f][movie]


        
# Cythonize this so it unrolls loops and stuff
def main():
    f1, f2 = open('data.npz', 'r'), open('data-mu.npz', 'r')
    um = np.load(f1)
    global um_dta
    um_dta = um["arr_0"]
    f1.close()
    mu = np.load(f2)
    global mu_dta
    mu_dta = mu["arr_0"]
    f2.close()


    NUM_USERS = np.shape(um_dta)[0]
    NUM_MOVIES = np.shape(mu_dta)[0]

    print "Loaded from files"

    # Initialize cache
    cache_init()
    np.save(open("movie_avgs", "w"), movie_avgs)
    np.save(open("user_avgs", "w"), user_ofsts)
    print "Initialized cache"

    init_features()
    print "Initialized features"

    # Shouldn't need this after this point
    del mu_dta

    data = um_dta

    for i in xrange(NUM_ITERATIONS):
        for f in xrange(NUM_FEATURES):
            for u in xrange(1, NUM_USERS + 1):
                for j in xrange(len(data[u]) / 2):
                    movie = data[u][2 * j] - 1
                    train(movie, u, f)
        print "Finished iteration %d", i

if __name__ == "__main__":
    main()



