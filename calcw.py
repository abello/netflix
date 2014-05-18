import numpy as np
from math import sqrt
# Useful: arxiv.org/pdf/0911.0460.pdf

PROBE = "processed_data/probe.dta"
PROBE_SIZE = 1374739

# Pass in all learned prediction functions, and the data used for blending 
# (in numpy array format). All prediction functions passed to this function 
# should be of the format g(idx corresponding to (user_id, movie_id)) = rating. 
def blender(blend_dta, *funcs):
    funcs = funcs[0] # Unpack tuple

    X = np.ndarray(shape=(np.shape(blend_dta)[0], len(funcs)))
    y = np.ndarray(shape=(np.shape(blend_dta)[0], 1))

    # Initialize X
    for i in xrange(np.shape(blend_dta)[0]):
        row = blend_dta[i]
        y[i][0] = row
        for j in xrange(len(funcs)):
            X[i][j] = funcs[j](i)
    
    # Calculate w[i][0]
    # inv of X (this step might take a while...)
    X_pinv = np.linalg.pinv(X)
    w = np.dot(X_pinv, y)

    # Create returned function
#     def blended(user_id, movie_id):
#         summed = 0
#         for i in xrange(len(funcs)):
#             summed += w[i][0] * funcs[i](user_id, movie_id)
#     return blended


    # Calculate RMSE-s
    err = 0.0
    for i in xrange(PROBE_SIZE):
        err += (X[i][0] - blend_dta[i])**2

    print "RMSE for 1:", str(sqrt(err/PROBE_SIZE))

    err = 0.0
    for i in xrange(PROBE_SIZE):
        err += (X[i][1] - blend_dta[i])**2

    print "RMSE for 2:", str(sqrt(err/PROBE_SIZE))


    err = 0.0
    for i in xrange(PROBE_SIZE):
        err += (w[0][0] * X[i][0] + w[1][0] * X[i][1] - blend_dta[i])**2

    print "RMSE for after blending:", str(sqrt(err/PROBE_SIZE))
        

    # Print weights
    for i in xrange(len(funcs)):
        print funcs[i].__name__, w[i][0]


def main():
    probe = open(PROBE, "r")
    blend_dta = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.uint8)
    i = 0

    # Load blend_dta
    for line in probe:
        l = line.split()
        rating = int(l[3].rstrip())
        blend_dta[i] = rating
        i += 1

    probe.close()

    # Create function's data
    _f_5 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_10 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)

#     f5 =  open("results/probe-F=5-E=20,20-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5")
#     f10 = open("results/probe-F=10-E=10,10-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5")

    f5 =  open("results/probe-F=5-E=20,20-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
    f10 = open("results/probe-F=10-E=15,15-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")

    for i in xrange(PROBE_SIZE):
        _f_5[i] = float(f5.readline().rstrip())
        _f_10[i] = float(f10.readline().rstrip())

    f5.close()
    f10.close()


    def f_5(x):
        return _f_5[x]

    def f_10(x):
        return _f_10[x]

    funcs = [f_5, f_10]

    blender(blend_dta, funcs)
    
    

if __name__ == '__main__':
    main()
