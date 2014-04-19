import numpy as np

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

K = 25

TRAINING_STARTED = False

# User features and movie features globals
# TODO: Numpy arrays?
user_features = [None for i in xrange(NUM_FEATURES)]

movie_features = [None for i in xrange(NUM_FEATURES)]


# Initializes the feature vectors
def init_features(user_features, movie_features):
    # TODO: Numpy arrays?
    for f in xrange(NUM_FEATURES):
        user_features[f] = np.array([0.1 for i in xrange(NUM_USERS)])
        movie_features[f] = np.array([0.1 for i in xrange(NUM_MOVIES)])

# Takes either mu or um numpy array (from data.npz or data-mu.npz), returns a
# list of lists, index being movie/user index, value being movie avg or user 
# average rating.
def compute_avg(np_arr, improved=False):
    height = np.shape(np_arr)[0]
    avg_arr = [0 for i in xrange(height)]
    if not improved:
        for i in xrange(height):
                avg_arr[i] = sum(np_arr[i][1::2]) / float(len(np_arr[i][1::2]))
    else:
        for i in xrange(height):
                avg_arr[i] = (GLOBAL_AVG * K + sum(np_arr[i][1::2])) / (K + len(np_arr[i][1::2]))

    return avg_arr

def compute_user_offset(movie_avg):
    user_off = [0 for i in xrange(NUM_USERS)]
    for i in xrange(NUM_USERS):
        user = um_dta[i]
        ratings = []
        for j in xrange(0, len(user), 2):
            movie_id = user[j]
            user_rating = user[j + 1]
            actual_rating = movie_avg[movie_id - 1]
            diff = user_rating - actual_rating

            # TODO: Get rid of append
            ratings.append(diff)
        user_off[i] = sum(ratings) / float(len(ratings))
    return user_off

# Returns the rating for this (movie, user) pair
# TODO: Check this
def get_rating(movie, user):
    return data[user][2 * (movie - 1) + 1]


# Initialize the cache to baseline rating
def cache_init():
    for u in xrange(NUM_USERS):
        rng = len(um_dta[u])/2
        for i in xrange(rng):
            movie = um_dta[u][2*i]
            cache[(movie, user)] = movie_avgs[movie - 1] + user_ofsts[u]

# This version should be used only TRAINING_STARTED is false, i.e. in the 
# first iteration
# Should be inlined
# def predict_rating_t_0(movie, user, movie_avg, user_off):
#     return movie_avg[movie - 1] + user_off[user - 1]


# (Training version) 
# Should be inlined
def predict_rating_t(movie, user, movie_avg, user_off):
    return cache[(user, movie)]


# Train! Super critical sector, needs to be heavily optimized.
def train(movie, user, f):
    user_off = usr_ofsts[user]
    movie_avg = movie_avgs[movie]

    # Rating we currently have
    predicted = predict_rating_t(movie, user, movie_avg, user_off)

    tmp = user_features[f][user] * movie_features[f][movie_id]
    actual_rating = get_rating(movie, user)

    error = LEARNING_RATE * (actual_rating - predicted)

    uv_old = user_features[f][user]
    user_features[f][user] += error * movie_features[f][movie_id]
    movie_features[f][movie] += error * uv_old
    
    # Update cache
    cache[(user_id, movie_id)] = cache[(user_id, movie_id)] - tmp + user_features[f][user_id] * movie_features[f][movie_id]


        
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

    global NUM_USERS
    global NUM_MOVIES

    global movie_avgs
    global user_ofsts

    NUM_USERS = np.shape(um_dta)[0]
    NUM_MOVIES = np.shape(mu_dta)[0]

    print "Loaded from files"

    # Calculate movie averages
    movie_avgs = compute_avg(mu_dta, True)
    print "Calculated movie averages"

    # Calculate the user offset array, usign the movie_avgs array
    user_ofsts = compute_user_offset(movie_avgs)
    print "Initialized user offsets"

    # Initialize cache
    cache_init()
    print "Initialized cache"

    init_features()
    print "Initialized features"

    # Shouldn't need this after this point
    del mu_dta

    for i in xrange(NUM_ITERATIONS):
        for f in xrange(NUM_FEATURES):
            for u in xrange(NUM_USERS):
                for j in xrange(len(data[u]) / 2):
                    movie = data[u][2 * j] - 1
                    train(movie, u, f)
        print "Finished iteration %d", i

if __name__ == "__main__":
    main()



