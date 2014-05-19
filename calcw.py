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
    for f in xrange(len(funcs)):
        err = 0.0
        for i in xrange(PROBE_SIZE):
            err += (X[i][f] - blend_dta[i])**2

        print "RMSE for :", funcs[f].__name__, str(sqrt(err/PROBE_SIZE))



    err = 0.0
    for i in xrange(PROBE_SIZE):
        b = 0
        for f in xrange(len(funcs)):
            b += w[f][0] * X[i][f]
        err += (b - blend_dta[i])**2

    print "======================"
    print "RMSE after blending:", str(sqrt(err/PROBE_SIZE))
        

    # Print weights
    for i in xrange(len(funcs)):
        print "w" + funcs[i].__name__ + " = " +  str(w[i][0])


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
    _f_20_1 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_20_2 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_50_1 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_100_1 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_100_2 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_GC_07 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)

#     f5 =  open("results/probe-F=5-E=20,20-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5")
#     f10 = open("results/probe-F=10-E=10,10-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5")

    f20_1 =  open("results/pre_blending/probe-F=20-E=80,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
    f20_2 = open("results/pre_blending/probe-F=20-E=80,180-k=0.02-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
    f50_1 =  open("results/pre_blending/probe-F=50-E=120,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
    f100_1 = open("results/pre_blending/probe-F=100-E=120,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
    f100_2 = open("results/pre_blending/probe-F=100-E=120,180-k=0.02-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
    f_GC_07 = open("results/pre_blending/probe-GC-0.07", "r")

    for i in xrange(PROBE_SIZE):
        _f_20_1[i] = float(f20_1.readline().rstrip())
        _f_20_2[i] = float(f20_2.readline().rstrip())
        _f_50_1[i] = float(f50_1.readline().rstrip())
        _f_100_1[i] = float(f100_1.readline().rstrip())
        _f_100_2[i] = float(f100_2.readline().rstrip())
        _f_GC_07[i] = float(f_GC_07.readline().rstrip())

    f20_1.close()
    f20_2.close()
    f50_1.close()
    f100_1.close()
    f100_2.close()
    f_GC_07.close()


    def f_20_1(x):
        return _f_20_1[x]

    def f_20_2(x):
        return _f_20_2[x]

    def f_50_1(x):
        return _f_50_1[x]

    def f_100_1(x):
        return _f_100_1[x]

    def f_100_2(x):
        return _f_100_1[x]

    def f_GC_07(x):
        return _f_GC_07[x]

    funcs = [f_20_1, f_20_2, f_50_1, f_100_1, f_100_2, f_GC_07]

    blender(blend_dta, funcs)
    
    

if __name__ == '__main__':
    main()
