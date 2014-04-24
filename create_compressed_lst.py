import numpy as np

if __name__ == '__main__':
    NUM_PAIRS = 98291669
    NUM_MOVIES = 17770
    NUM_USERS = 458293
    f = open('data-mu.npz', 'r')
    mu = np.load(f)
    # Get rid of the None in the beginning
    mu_dta = np.delete(mu["arr_0"], 0)
    # Count the size of the compressed array:
    arr = np.array([0 for i in xrange(3 * NUM_PAIRS)], dtype=np.float32)
    size_per_movie = np.array([0 for i in xrange(NUM_MOVIES)], dtype=np.int32)

    print NUM_MOVIES + NUM_PAIRS

    arr_idx = 0
    # Populate the arrays
    for i in xrange(NUM_MOVIES):
        movie = i
        pairs = mu_dta[i]
        size_per_movie[i] = len(pairs) / 2
        for j in xrange(0, len(pairs), 2):
            user = pairs[j]
            rating = pairs[j + 1]
            arr[arr_idx] = user
            arr[arr_idx + 1] = rating
            arr[arr_idx + 2] = 0.0 # Initial cache value
            arr_idx += 3

    print arr, NUM_MOVIES + NUM_PAIRS
    # Now save these arrays
    np.save("compressed_arr.npy", arr)
    np.save("users_per_movie.npy", size_per_movie)
