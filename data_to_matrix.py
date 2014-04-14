from scipy import sparse
import numpy as np

# Number of users in all.dta
NUM_USERS = 458293

# Number of movies
NUM_MOVIES = 17770

f = np.load(open("data.npz", "r"))
data = f["arr_0"]
print "data loaded"

mat = sparse.lil_matrix((NUM_USERS, NUM_MOVIES),  dtype=np.int8);
for usr in xrange(NUM_USERS):
	for i in xrange(len(data[usr]) / 2):
		mat[usr, data[usr][i * 2] - 1] = data[usr][i * 2 + 1]
	if usr % 10000 == 0:
		print(usr);



print("DONE");
# np.savez(open("mat.npz", "w"), mat)
