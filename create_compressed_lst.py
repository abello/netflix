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
    arr = np.array([0 for i in xrange(NUM_MOVIES + 2 * NUM_PAIRS)], dtype=np.int32)
    size_per_movie = np.array([0 for i in xrange(NUM_MOVIES)], dtype=np.int32)

    print NUM_MOVIES + NUM_PAIRS

    arr_idx = 0
    # Populate the arrays
    for i in xrange(NUM_MOVIES):
        movie = i
        pairs = mu_dta[i]
        size_per_movie[i] = len(pairs) / 2
        arr[arr_idx] = movie + 1 # make it 1-indexed like the movie
        arr_idx += 1
        for v in pairs:
            try:
                arr[arr_idx] = v
            except IndexError:
                print arr_idx
                exit() 
            arr_idx += 1

    print arr, NUM_MOVIES + NUM_PAIRS
    # Now save these arrays
    np.save("compressed_arr.npy", arr)
    np.save("users_per_movie.npy", size_per_movie)
