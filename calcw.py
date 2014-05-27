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


    # ======================================================================


    # Create function's data
    _f_20_1 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_20_2 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_50_1 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_100_1 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_100_2 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_GC_07 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_GC_13 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_GC_29 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_PP_50_30_NA = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_PP_50_8 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_PP_100_8 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_PP_200_8 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_PP_300_8 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)

    _f_PPD_50_8 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_PPD_100_8 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_PPD_300_8 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)

    _f_PPD_300_2 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)

    _f_RBM_200_181 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_RBM_200_240 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_RBM_200_349 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_RBM_400_394 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_RBM_200_422 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)
    _f_RBM_400_389 = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)


    _f_KNN = np.array([0 for i in xrange(PROBE_SIZE)], dtype=np.float32)

#     f5 =  open("results/probe-F=5-E=20,20-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5")
#     f10 = open("results/probe-F=10-E=10,10-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5")

    f20_1 =  open("results/pre_blending/probe-F=20-E=80,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
    f20_2 = open("results/pre_blending/probe-F=20-E=80,180-k=0.02-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
    f50_1 =  open("results/pre_blending/probe-F=50-E=120,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
    f100_1 = open("results/pre_blending/probe-F=100-E=120,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
    f100_2 = open("results/pre_blending/probe-F=100-E=120,180-k=0.02-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
    f_GC_07 = open("results/pre_blending/probe-GC-0.07", "r")
    f_GC_13 = open("results/pre_blending/probe-GC-0.13", "r")
    f_GC_29 = open("results/pre_blending/probe-GC-0.29", "r")
    f_PP_50_30_NA = open("results/pre_blending/probe-F=50-LRT_mb0.003-LAM_mb=0-LRT_ub=0.012-LAM_ub=0.03-LRT_mf=0.011-LAM_mf=0.006-LRT_uf=0.006-LAM_uf0.08-LRT_mw=0.001-LAM_mw=0.03-NBINS=5-NA", "r")
    f_PP_50_8 = open("results/pre_blending/probe-F=50-LRT_mb0.003-LAM_mb=0-LRT_ub=0.012-LAM_ub=0.03-LRT_mf=0.011-LAM_mf=0.006-LRT_uf=0.006-LAM_uf0.08-LRT_mw=0.001-LAM_mw=0.03-NBINS=5", "r")
    f_PP_100_8 = open("results/pre_blending/probe7-F=100-LRT_mb0.003-LAM_mb=0-LRT_ub=0.012-LAM_ub=0.03-LRT_mf=0.011-LAM_mf=0.006-LRT_uf=0.006-LAM_uf0.08-LRT_mw=0.001-LAM_mw=0.03-NBINS=5", "r")
    f_PP_200_8 = open("results/pre_blending/probe7-F=200-LRT_mb0.003-LAM_mb=0-LRT_ub=0.012-LAM_ub=0.03-LRT_mf=0.011-LAM_mf=0.006-LRT_uf=0.006-LAM_uf0.08-LRT_mw=0.001-LAM_mw=0.03-NBINS=5", "r")
    f_PP_300_8 = open("results/pre_blending/probe7-F=300-NR=98291669-NB=5", "r")

    # Step decay
    f_PPD_50_8 = open("results/pre_blending/probe17-F=50--NR=98291669-NBINS=5-SD", "r")

    # This should be 16 instead of 7, but for some reason 7 performs better
    f_PPD_100_8 = open("results/pre_blending/probe16-F=100-NR=98291669-NB=5-SD", "r")
    f_PPD_300_8 = open("results/pre_blending/probe14-F=300-NR=98291669-NB=5-SD", "r")
    f_PPD_300_2 = open("results/pre_blending/probe19-F=300-NR=98291669-NB=5-SD-TBS", "r")


    # RBMs
    f_RBM_200_181 = open("results/pre_blending/probe-rbm-200-181", "r")
    f_RBM_200_240 = open("results/pre_blending/probe-rbm-200-240", "r")
    f_RBM_200_349 = open("results/pre_blending/probe-rbm-200-349", "r")
    f_RBM_400_394 = open("results/pre_blending/probe-rbm-400-394", "r")
    f_RBM_200_422 = open("results/pre_blending/probe-rbm-200-422", "r")
    f_RBM_400_389 = open("results/pre_blending/probe-rbm-400-389", "r")

    f_KNN = open("results/pre_blending/probe-KNN-", "r")

    for i in xrange(PROBE_SIZE):
        _f_20_1[i] = float(f20_1.readline().rstrip())
        _f_20_2[i] = float(f20_2.readline().rstrip())
        _f_50_1[i] = float(f50_1.readline().rstrip())
        _f_100_1[i] = float(f100_1.readline().rstrip())
        _f_100_2[i] = float(f100_2.readline().rstrip())
        _f_GC_07[i] = float(f_GC_07.readline().rstrip())
        _f_GC_13[i] = float(f_GC_13.readline().rstrip())
        _f_GC_29[i] = float(f_GC_29.readline().rstrip())
        _f_PP_50_30_NA[i] = float(f_PP_50_30_NA.readline().rstrip())
        _f_PP_50_8[i] = float(f_PP_50_8.readline().rstrip())
        _f_PP_100_8[i] = float(f_PP_100_8.readline().rstrip())
        _f_PP_200_8[i] = float(f_PP_200_8.readline().rstrip())
        _f_PP_300_8[i] = float(f_PP_300_8.readline().rstrip())

        _f_PPD_50_8[i] = float(f_PPD_50_8.readline().rstrip())
        _f_PPD_100_8[i] = float(f_PPD_100_8.readline().rstrip())
        _f_PPD_300_8[i] = float(f_PPD_300_8.readline().rstrip())
        _f_PPD_300_2[i] = float(f_PPD_300_2.readline().rstrip())


        _f_RBM_200_181[i] = float(f_RBM_200_181.readline().rstrip())
        _f_RBM_200_240[i] = float(f_RBM_200_240.readline().rstrip())
        _f_RBM_200_349[i] = float(f_RBM_200_349.readline().rstrip())
        _f_RBM_400_394[i] = float(f_RBM_400_394.readline().rstrip())
        _f_RBM_200_422[i] = float(f_RBM_200_422.readline().rstrip())
        _f_RBM_400_389[i] = float(f_RBM_400_389.readline().rstrip())

        _f_KNN[i] = float(f_KNN.readline().rstrip())

    #
    # NOTE: *TRIPLE* check these settings. As this code is really messy, it's easy to 
    # miss stuff out
    #

    f20_1.close()
    f20_2.close()
    f50_1.close()
    f100_1.close()
    f100_2.close()
    f_GC_07.close()
    f_GC_13.close()
    f_GC_29.close()
    f_PP_50_30_NA.close()
    f_PP_50_8.close()
    f_PP_100_8.close()
    f_PP_200_8.close()
    f_PP_300_8.close()

    f_PPD_50_8.close()
    f_PPD_100_8.close()
    f_PPD_300_8.close()
    f_PPD_300_2.close()

    f_RBM_200_181.close()
    f_RBM_200_240.close()
    f_RBM_200_349.close()
    f_RBM_400_394.close()
    f_RBM_200_422.close()
    f_RBM_400_389.close()

    f_KNN.close()



    def f_20_1(x):
        return _f_20_1[x]

    def f_20_2(x):
        return _f_20_2[x]

    def f_50_1(x):
        return _f_50_1[x]

    def f_100_1(x):
        return _f_100_1[x]

    def f_100_2(x):
        return _f_100_2[x]

    def f_GC_07(x):
        return _f_GC_07[x]

    def f_GC_13(x):
        return _f_GC_13[x]

    def f_GC_29(x):
        return _f_GC_29[x]

    def f_PP_50_30_NA(x):
        return _f_PP_50_30_NA[x]

    def f_PP_50_8(x):
        return _f_PP_50_8[x]

    def f_PP_100_8(x):
        return _f_PP_100_8[x]

    def f_PP_200_8(x):
        return _f_PP_200_8[x]

    def f_PP_300_8(x):
        return _f_PP_300_8[x]

    

    def f_PPD_50_8(x):
        return _f_PPD_50_8[x]

    def f_PPD_100_8(x):
        return _f_PPD_100_8[x]

    def f_PPD_300_8(x):
        return _f_PPD_300_8[x]

    def f_PPD_300_2(x):
        return _f_PPD_300_2[x]






    # TODO: Not being used; remove in future
    def f_RBM_200_181(x):
        return _f_RBM_200_181[x]

    def f_RBM_200_240(x):
        return _f_RBM_200_240[x]

    def f_RBM_200_349(x):
        return _f_RBM_200_349[x]

    def f_RBM_400_394(x):
        return _f_RBM_400_394[x]

    def f_RBM_200_422(x):
        return _f_RBM_200_422[x]
    
    # Not using
    def f_RBM_400_389(x):
        return _f_RBM_400_389[x]


    def f_KNN(x):
        return _f_KNN[x]



    funcs = [f_20_1, f_20_2, f_50_1, f_100_1, f_100_2, f_GC_07, f_GC_13, f_GC_29, f_PP_50_30_NA, f_PP_50_8, f_PP_100_8, f_PP_200_8, f_PP_300_8, f_PPD_50_8, f_PPD_100_8, f_PPD_300_8, f_PPD_300_2, f_RBM_200_240, f_RBM_200_349, f_RBM_400_394, f_RBM_200_422, f_KNN]

    blender(blend_dta, funcs)
    
    

if __name__ == '__main__':
    main()
