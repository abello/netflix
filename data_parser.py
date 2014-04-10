import numpy as np

# Number of users in all.dta
NUM_USERS = 458293

# Number of movies
NUM_MOVIES = 17770

# Open files using a large buffer
alldata = open("um/all.dta", "r", buffering=(2<<26))
index = open("um/all.idx", "r", buffering=(2<<26))

# Raw data. A list of numpy arrays containing (movie, rating) pairs
raw = [None for i in range(NUM_USERS + 1)]

while True:
    data = alldata.readline()
    idx = index.readline()

    if data == "":
        break

    # convert data into a list of ints => [user, movie, date, rating]
    data = data.split()

    data = [int(i) for i in data]

    if data[0] % 10000 == 0:
        print data[0]

    idx = int(idx)

    # If it corresponds to the training set
    if idx in [1, 2, 3]:

        # If we already have this user, add (movie, rating) tuple to array
        if raw[data[0]] != None:
            raw[data[0]] = np.append(raw[data[0]], (data[1], data[3]))

        # Else create array
        else:
            raw[data[0]] = np.array((data[1], data[3]), dtype=np.int16)
        

