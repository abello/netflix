import numpy as np

f1, f2 = open('data.npz', 'r'), open('data-mu.npz', 'r')
um = np.load(f1)
f1.close()
mu = np.load(f2)
f2.close()
um_dta = um["arr_0"]
mu_dta = mu["arr_0"]

NUM_USERS = np.shape(um_dta)[0]
NUM_MOVIES = np.shape(mu_dta)[0]

GLOBAL_AVG = 3.512599976023349

K = 25

TRAINING_STARTED = False

# Takes either mu or um numpy array (from data.npz or data-mu.npz), returns a
# list of lists, index being movie/user index, value being movie avg or user 
# average rating.
def compute_avg(np_arr, improved=False):
    height = np.shape(np_arr)[0]
    avg_arr = [0 for i in xrange(height)]
    for i in xrange(height):
        if !improved:
            avg_arr[i] = sum(np_arr[i][1::2]) / float(len(np_arr[i][1::2]))
        else:
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

def predict_rating(movie, user, movie_avg, user_off):
    # TODO: Get rid of branching
    if !TRAINING_STARTED:
        return movie_avg[movie - 1] + user_off[user - 1]
    else:
         
        
        
    
