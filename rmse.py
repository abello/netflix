import numpy as np
import math

# Load probe
f = np.load(open("probe.npz", "r"))
probe = r["arr_0"]

# Prepend dummy to align index with uid
probe.insert(0, None)


# Load results
f = np.load(open("result.npz", "r"))
result = r["arr_0"]

mse = 0.0
num = 0

for user in range(1, len(result)):
    arr = result[user]

    for i in range(len(arr)):
        movie = arr[i]
        rating = arr[i+1]
        
        mse += (rating - result[user][movie]
        num += 1

mse = mse / num

print math.sqrt(mse)


