QUAL_SIZE = 2749898

f20_1 =  open("results/output-F=20-E=80,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f20_2 = open("results/output-F=20-E=80,180-k=0.02-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f50_1 =  open("results/output-F=50-E=120,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f100_1 = open("results/output-F=100-E=120,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f100_2 = open("results/output-F=100-E=120,180-k=0.02-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f_GC_07 = open("results/output-GC-0.07", "r")
f_GC_13 = open("results/output-GC-0.13", "r")
f_GC_29 = open("results/output-GC-0.29", "r")
f_PP_50_30_NA = open("results/output-F=50-LRT_mb0.003-LAM_mb=0-LRT_ub=0.012-LAM_ub=0.03-LRT_mf=0.011-LAM_mf=0.006-LRT_uf=0.006-LAM_uf0.08-LRT_mw=0.001-LAM_mw=0.03-NBINS=5-NA", "r")
# f_PP_50_8 = open("results/output-F=50-LRT_mb0.003-LAM_mb=0-LRT_ub=0.012-LAM_ub=0.03-LRT_mf=0.011-LAM_mf=0.006-LRT_uf=0.006-LAM_uf0.08-LRT_mw=0.001-LAM_mw=0.03-NBINS=5", "r")
f_PP_50_8 = open("results/output-F=50-LRT_mb0.003-LAM_mb=0-LRT_ub=0.012-LAM_ub=0.03-LRT_mf=0.011-LAM_mf=0.006-LRT_uf=0.006-LAM_uf0.08-LRT_mw=0.001-LAM_mw=0.03-NBINS=5", "r")
f_PP_100_8 = open("results/output9-F=100-LRT_mb0.003-LAM_mb=0-LRT_ub=0.012-LAM_ub=0.03-LRT_mf=0.011-LAM_mf=0.006-LRT_uf=0.006-LAM_uf0.08-LRT_mw=0.001-LAM_mw=0.03-NBINS=5", "r")
f_PP_200_8 = open("results/output7-F=200-LRT_mb0.003-LAM_mb=0-LRT_ub=0.012-LAM_ub=0.03-LRT_mf=0.011-LAM_mf=0.006-LRT_uf=0.006-LAM_uf0.08-LRT_mw=0.001-LAM_mw=0.03-NBINS=5", "r")
f_PP_300_8 = open("results/output8-F=300-LRT_mb0.003-LAM_mb=0-LRT_ub=0.012-LAM_ub=0.03-LRT_mf=0.011-LAM_mf=0.006-LRT_uf=0.006-LAM_uf0.08-LRT_mw=0.001-LAM_mw=0.03-NBINS=5", "r")

# Step decay

f_PPD_50_8 = open("results/output18-F=100-NR=99666408-NB=5-SD", "r")
f_PPD_100_8 = open("results/output17-F=100-NR=99666408-NB=5-SD", "r")
f_PPD_300_8 = open("results/output17-F=300-NR=99666408-NB=5-SD", "r")


#### RBM 
# -0.14 below water
f_RBM_200_181 = open("results/output-rbm-200-181", "r")
f_RBM_200_240 = open("results/output-rbm-200-240", "r")
f_RBM_200_349 = open("results/output-rbm-200-349", "r")
f_RBM_400_394 = open("results/output-rbm-400-394", "r")
f_RBM_200_422 = open("results/output-rbm-200-496-F", "r")
# f_RBM_400_389 = open("results/output-rbm-400-389", "r")



files = [f20_1, f20_2, f50_1, f100_1, f100_2, f_GC_07, f_GC_13, f_GC_29, f_PP_50_30_NA, f_PP_50_8, f_PP_100_8, f_PP_200_8, f_PP_300_8, f_PPD_50_8, f_PPD_100_8, f_PPD_300_8, f_RBM_200_240, f_RBM_200_349, f_RBM_400_394, f_RBM_200_422]

out = open("results/blended", "w")

#
# WEIGHTS
#

wf_20_1 = 0.145352861039
wf_20_2 = -0.201096680292
wf_50_1 = 0.0311585922382
wf_100_1 = 0.0427583098425
wf_100_2 = 0.0545166764465
wf_GC_07 = 0.0396868311269
wf_GC_13 = 0.0275531708823
wf_GC_29 = 0.0359214092646
wf_PP_50_30_NA = 0.127335052021
wf_PP_50_8 = -0.181986401224
wf_PP_100_8 = -0.352687807885
wf_PP_200_8 = 0.207198460815
wf_PP_300_8 = -0.0215820160259
wf_PPD_50_8 = 0.0314790432987
wf_PPD_100_8 = 0.229079501383
wf_PPD_300_8 = 0.423552171672
wf_RBM_200_240 = 0.0388671975371
wf_RBM_200_349 = 0.0880903507666
wf_RBM_400_394 = 0.0872880750619
wf_RBM_200_422 = 0.153178707569

weights = [wf_20_1, wf_20_2, wf_50_1, wf_100_1, wf_100_2, wf_GC_07, wf_GC_13, wf_GC_29, wf_PP_50_30_NA, wf_PP_50_8, wf_PP_100_8, wf_PP_200_8, wf_PP_300_8, wf_PPD_50_8, wf_PPD_100_8, wf_PPD_300_8, wf_RBM_200_240, wf_RBM_200_349, wf_RBM_400_394, wf_RBM_200_422]

assert(len(weights) == len(files))

for i in xrange(QUAL_SIZE):
    j = 0
    b = 0
    for f in files:
        val = f.readline().rstrip()
        b += float(val) * weights[j]
        j += 1
    b = round(b, 4)

    out.write(str(b) + "\n")

