import numpy as np
from SVD import compute_user_avg, compute_movie_avg

if __name__ == '__main__':
    f = np.load(open("data.npz", "r"))
    data = f["arr_0"]
    usr_avg = compute_user_avg(data)
    mv_avg = compute_movie_avg(data)
    output = open('output.dta', 'w+')
    with open('qual.dta', 'r') as qual:
        for line in qual:
            user_id, movie_id, time = [int(v) for v in line.split()]
            user_rating = usr_avg[user_id - 1]
            movie_rating = usr_avg[movie_id - 1]
            rating = (user_rating + movie_rating) / 2.0
            output.write(str(rating) + "\n")
