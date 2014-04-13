import numpy as np

NUM_FEATURES = 40;

# Number of users in all.dta
NUM_USERS = 458293;

# Number of movies
NUM_MOVIES = 17770;

print("Reading from data.npz...");

f = np.load(open("data.npz", "r"));
data = f["arr_0"];

print("Finished reading from data.npz!");

user_features = [None for i in xrange(NUM_FEATURES)];

movie_features = [None for i in xrange(NUM_FEATURES)];

for f in xrange(NUM_FEATURES):
	user_features[f] = [None for i in xrange(NUM_USERS)];
	movie_features[f] = [None for i in xrange(NUM_MOVIES)];

global_avg = compute_global_avg(data);

user_offset = compute_user_offset(data, global_avg);

movie_avg = compute_movie_avg(data);

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
		user_cnt += len(user_data) / 2;
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
	user_offset = [(usr_avg[i] - global_avg) for i in xrange(NUM_USERS)];
	return user_offset;

# base value for predicted ratings
def predict_rating_uninitialized(user_offset, movie_avg, user_id, movie_id):
	return movie_avg[movie_id] + user_offset[user_id];