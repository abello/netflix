import numpy as np

NUM_FEATURES = 40;

# Number of users in all.dta
NUM_USERS = 100;#458293;

# Number of movies
NUM_MOVIES = 17770;

NUM_ITERATIONS = 10;

LEARNING_RATE = 0.001;


def compute_global_avg(data):
	print("Computing the global average...");

	tot_cnt = 0;
	tot_sum = 0;

	for user_data in data:
		tot_cnt += len(user_data) / 2;
		
		for i in xrange(len(user_data) / 2):
			tot_sum += user_data[2 * i + 1];

	print("Finished computing the global average!");
	return tot_sum;


def compute_user_avg(data):
	print("Computing the user averages...");

	user_avg = [None for i in xrange(NUM_USERS)];

	for u in xrange(NUM_USERS):
		user_cnt = len(data[u]) / 2;
		user_sum = 0;
		
		for i in xrange(len(data[u]) / 2):
			user_sum += data[u][2 * i + 1];

		user_avg[u] = user_sum / user_cnt;

	print("Finished computing the user averages!");
	return user_avg;

# CAUTION! INDICES SHIFTED BY 1
def compute_movie_avg(data):
	print("Computing the movie averages...");

	movie_avg = [None for i in xrange(NUM_MOVIES)];
	movie_cnt = [0 for i in xrange(NUM_MOVIES)];
	movie_sum = [0 for i in xrange(NUM_MOVIES)];

	for u in xrange(NUM_USERS):
		for i in xrange(len(data[u]) / 2):
			movie_no = data[u][2 * i] - 1; # shift by 1!
			movie_cnt[movie_no] += 1;
			movie_sum[movie_no] += data[u][2 * i + 1];

	for m in xrange(NUM_MOVIES):
		movie_avg[m] = movie_sum[m] / movie_cnt[m];

	print("Finished computing the movie averages!");
	return movie_avg;

def compute_user_offset(data, global_avg):
	user_avg = compute_user_avg(data);
	user_offset = [(user_avg[i] - global_avg) for i in xrange(NUM_USERS)];
	return user_offset;

def improved_movie_avg(data, global_avg, K = 25):
	print("Computing the movie averages (improved)...");

	movie_avg = [None for i in xrange(NUM_MOVIES)];
	movie_cnt = [K * global_avg for i in xrange(NUM_MOVIES)];
	movie_sum = [K for i in xrange(NUM_MOVIES)];

	for u in xrange(NUM_USERS):
		for i in xrange(len(data[u]) / 2):
			movie_no = data[u][2 * i] - 1; # shift by 1!
			movie_cnt[movie_no] += 1;
			movie_sum[movie_no] += data[u][2 * i + 1];

	for m in xrange(NUM_MOVIES):
		movie_avg[m] = movie_sum[m] / movie_cnt[m];

	print("Finished computing the movie averages!");
	return movie_avg;


# base value for predicted ratings
def predict_rating_uninitialized(user_offset, movie_avg, user_id, movie_id):
	return movie_avg[movie_id] + user_offset[user_id];

def predict_rating(user_features, movie_features, user_offset, movie_avg, user_id, movie_id, rating_initialized):
	if not rating_initialized:
		return predict_rating_uninitialized(user_offset, movie_avg, user_id, movie_id);
	else:
		tot_sum = 0;
		for f in xrange(NUM_FEATURES):
			tot_sum += user_features[f][user_id] * movie_features[f][movie_id];
		return tot_sum;

def train(user_features, movie_features, f, user_offset, movie_avg, user_id, movie_id, rating_initialized, actual_rating, learning_rate):
	error = learning_rate * (actual_rating - predict_rating(user_features, movie_features, user_offset, movie_avg, user_id, movie_id, rating_initialized));
	uv_old = user_features[f][user_id];
	user_features[f][user_id] += error * movie_features[f][movie_id];
	movie_features[f][movie_id] += error * uv_old;
	return;




print("Reading from data.npz...");

f = np.load(open("data.npz", "r"));
data = f["arr_0"];

print("Finished reading from data.npz!");

user_features = [None for i in xrange(NUM_FEATURES)];

movie_features = [None for i in xrange(NUM_FEATURES)];

for f in xrange(NUM_FEATURES):
	user_features[f] = [0.1 for i in xrange(NUM_USERS)];
	movie_features[f] = [0.1 for i in xrange(NUM_MOVIES)];

global_avg = compute_global_avg(data);

user_offset = compute_user_offset(data, global_avg);

# Uncomment for raw movie average
# movie_avg = compute_movie_avg(data, global_avg);
# Use predict_rating_uninitialized(user_offset, movie_avg, user_id, movie_id):
# to get Version 1

better_movie_avg = improved_movie_avg(data, global_avg);
# Use predict_rating_uninitialized(user_offset, better_movie_avg, user_id, movie_id):
# to get version 2

rating_initialized = false;

for i in xrange(NUM_ITERATIONS):
	for f in xrange(NUM_FEATURES):
		for u in xrange(NUM_USERS):
			for i in xrange(len(data[u]) / 2):
				train(user_features, movie_features, f, user_offset, better_movie_avg, u, data[u][2 * i] - 1, rating_initialized, data[u][2 * i + 1], LEARNING_RATE);
	rating_initialized = true;

# Learning is done at this point.
# use predict_rating to predict ratings