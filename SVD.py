import numpy as np
import sys
from line_profiler import LineProfiler


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

# END profiling stuff

NUM_FEATURES = 40;

# Number of users in all.dta
NUM_USERS = 100;#458293;

# Number of movies
NUM_MOVIES = 17770;

# Number of desired iterations
NUM_ITERATIONS = 3;

# Learning rate
LEARNING_RATE = 0.001;


# Compute the global average
def compute_global_avg(data):
    sys.stderr.write("Computing the global average...\n");

#DEBUG CODE
    cnt = 1;
#DEBUG CODE END

    tot_cnt = 0;
    tot_sum = 0;

    for user_data in data:
        tot_cnt += len(user_data) / 2;
        
        for i in xrange(len(user_data) / 2):
            tot_sum += user_data[2 * i + 1];
        #DEBUG CODE
        cnt += 1;
        if (cnt == NUM_USERS):
            break;
        #DEBUG CODE END

    sys.stderr.write("Finished computing the global average!\n");
    return float(tot_sum) / float(tot_cnt);

# Compute the user averages
def compute_user_avg(data):
    sys.stderr.write("Computing the user averages...\n");

    user_avg = np.array([0.0 for i in xrange(NUM_USERS)]);

    for u in xrange(NUM_USERS):
        user_cnt = len(data[u]) / 2;
        user_sum = 0;
        
        for i in xrange(len(data[u]) / 2):
            user_sum += data[u][2 * i + 1];

        user_avg[u] = float(user_sum) / float(user_cnt);

    sys.stderr.write("Finished computing the user averages!\n");
    return user_avg;

# Compute the movie averages
# CAUTION! INDICES SHIFTED BY 1
def compute_movie_avg(data):
    sys.stderr.write("Computing the movie averages...\n");

    movie_avg = np.array([0.0 for i in xrange(NUM_MOVIES)]);
    movie_cnt = [0 for i in xrange(NUM_MOVIES)];
    movie_sum = [0 for i in xrange(NUM_MOVIES)];

    for u in xrange(NUM_USERS):
        for i in xrange(len(data[u]) / 2):
            movie_no = data[u][2 * i] - 1; # shift by 1!
            movie_cnt[movie_no] += 1;
            movie_sum[movie_no] += data[u][2 * i + 1];

    for m in xrange(NUM_MOVIES):
        #DEBUG CODE
        if (movie_cnt[m] == 0):
            movie_avg[m] = 2.5;
            continue;
        #DEBUG CODE END
        movie_avg[m] = float(movie_sum[m]) / float(movie_cnt[m]);

    sys.stderr.write("Finished computing the movie averages!\n");
    return movie_avg;

# Compute difference between the user average and the global average
def compute_user_offset(data, global_avg):
    user_avg = compute_user_avg(data);
    user_offset = np.array([(user_avg[i] - global_avg) for i in xrange(NUM_USERS)]);
    return user_offset;

# Computes the movie average with weight K on global average
def improved_movie_avg(data, global_avg, K = 25):
    sys.stderr.write("Computing the movie averages (improved)...\n");

    movie_avg = np.array([0.0 for i in xrange(NUM_MOVIES)]);
    movie_cnt = [K for i in xrange(NUM_MOVIES)];
    movie_sum = [K * global_avg for i in xrange(NUM_MOVIES)];

    for u in xrange(NUM_USERS):
        for i in xrange(len(data[u]) / 2):
            movie_no = data[u][2 * i] - 1; # shift by 1!
            movie_cnt[movie_no] += 1;
            movie_sum[movie_no] += data[u][2 * i + 1];

    for m in xrange(NUM_MOVIES):
        movie_avg[m] = float(movie_sum[m]) / float(movie_cnt[m]);

    sys.stderr.write("Finished computing the movie averages!\n");
    return movie_avg;


# base value for predicted ratings
# @do_profile(follow=[get_number])
def predict_rating_uninitialized(user_offset, movie_avg, user_id, movie_id):
    return movie_avg[movie_id] + user_offset[user_id];

# Predict rating given the specified inputs
def predict_rating(user_features, movie_features, user_offset, movie_avg, user_id, movie_id, rating_initialized):
    if not rating_initialized:
        return predict_rating_uninitialized(user_offset, movie_avg, user_id, movie_id);
    else:
        tot_sum = 0;
        for f in xrange(NUM_FEATURES):
            tot_sum += user_features[f][user_id] * movie_features[f][movie_id];
        return tot_sum;

# Actually do the training!
# @do_profile(follow=[get_number])
def train(user_features, movie_features, f, user_offset, movie_avg, user_id, movie_id, rating_initialized, actual_rating, learning_rate):
    predicted = predict_rating(user_features, movie_features, user_offset, movie_avg, user_id, movie_id, rating_initialized);
    error = learning_rate * (actual_rating - predicted)
    uv_old = user_features[f][user_id];
    user_features[f][user_id] += error * movie_features[f][movie_id];
    movie_features[f][movie_id] += error * uv_old;
    return;


def main():
    print("Reading from data.npz...");

    f = np.load(open("data.npz", "r"));
    data = f["arr_0"];

    print("Finished reading from data.npz!");

    user_features = [None for i in xrange(NUM_FEATURES)];

#     user_features = [np.array([0.1 for i in xrange(NUM_USERS)]) for j in xrange(NUM_FEATURES)];
# 
#     movie_features = [np.array([0.1 for i in xrange(NUM_MOVIES)]) for j in xrange(NUM_FEATURES)];

    movie_features = np.array([None for i in xrange(NUM_FEATURES)]);

    for f in xrange(NUM_FEATURES):
        user_features[f] = [0.1 for i in xrange(NUM_USERS)];
        movie_features[f] = [0.1 for i in xrange(NUM_MOVIES)];

    global_avg = compute_global_avg(data);
    print global_avg;


    user_offset = compute_user_offset(data, global_avg);

    # Uncomment for raw movie average
    movie_avg = compute_movie_avg(data);
    # Use predict_rating_uninitialized(user_offset, movie_avg, user_id, movie_id):
    # to get Version 1

    better_movie_avg = improved_movie_avg(data, global_avg);
    # Use predict_rating_uninitialized(user_offset, better_movie_avg, user_id, movie_id):
    # to get version 2

    rating_initialized = False;

    for i in xrange(NUM_ITERATIONS):
        for f in xrange(NUM_FEATURES):
            for u in xrange(NUM_USERS):
                for i in xrange(len(data[u]) / 2):
                    train(user_features, movie_features, f, user_offset, movie_avg, u, data[u][2 * i] - 1, rating_initialized, data[u][2 * i + 1], LEARNING_RATE);
        rating_initialized = True;
        print("Iteration " + str(i) + " completed!");


    # Learning is done at this point.
    # use predict_rating to predict ratings
    # Such as:
    # print predict_rating(user_features, movie_features, user_offset, better_movie_avg, 10, 10, rating_initialized);

    # for i in range(NUM_USERS):
    #     for m in range(NUM_MOVIES):
    #         print i+1, m+1, predict_rating(user_features, movie_features, user_offset, better_movie_avg, i, m, rating_initialized)



if __name__ == "__main__":
    main()
