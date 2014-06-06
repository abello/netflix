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

f_PPD_50_8 = open("results/output18-F=50-NR=99666408-NBINS=5-SD", "r")
f_PPD_100_8 = open("results/output17-F=100-NR=99666408-NB=5-SD", "r")
f_PPD_300_8 = open("results/output17-F=300-NR=99666408-NB=5-SD", "r")
f_PPD_300_2 = open("results/output22-F=300-NR=99666408-NB=5-SD-TBS", "r")

# f_PPD_100_t = open("results/output17-F=100-NR=99666408-NB=5-SD-TBS-AU", "r")
f_PPD_100_t = open("results/output18-F=100-NR=99666408-NB=5-SD-TBS-Time", "r")


#### RBM 
# -0.14 below water
f_RBM_200_181 = open("results/output-rbm-200-181", "r")
f_RBM_200_240 = open("results/output-rbm-200-240", "r")
f_RBM_200_349 = open("results/output-rbm-200-349", "r")
f_RBM_400_394 = open("results/output-rbm-400-394", "r")
f_RBM_200_422 = open("results/output-rbm-200-496-F", "r")
# f_RBM_400_389 = open("results/output-rbm-400-389", "r")

f_last = open("results/outlast-ronnel", "r")

f_KNN = open("results/output-KNN-", "r")



files = [f20_1, f20_2, f50_1, f100_1, f100_2, f_GC_07, f_GC_13, f_GC_29, f_PP_50_8, f_PP_100_8, f_PP_200_8, f_PP_300_8, f_PPD_50_8, f_PPD_100_8, f_PPD_300_8, f_PPD_300_2, f_RBM_200_240, f_RBM_200_349, f_RBM_400_394, f_RBM_200_422, f_KNN]

out = open("results/blended", "w")

#
# WEIGHTS
#

wf_20_1 = 0.156783858303
wf_20_2 = -0.219996811196
wf_50_1 = 0.0322490798408
wf_100_1 = 0.0557374680864
wf_100_2 = 0.0440871966253
wf_GC_07 = 0.0294266618189
wf_GC_13 = 0.020331852616
wf_GC_29 = 0.0298937679577
wf_PP_50_8 = -0.188645611633
wf_PP_100_8 = -0.374253103589
wf_PP_200_8 = 0.225597506233
wf_PP_300_8 = 0.16230794715
wf_PPD_50_8 = 0.18456256565
wf_PPD_100_8 = 0.288589148608
wf_PPD_300_8 = -0.222940719709
wf_PPD_300_2 = 0.434571870907
wf_RBM_200_240 = 0.0390400604803
wf_RBM_200_349 = 0.0823263793292
wf_RBM_400_394 = 0.072376347641
wf_RBM_200_422 = 0.143640011709
wf_KNN = 0.0128919636531


weights = [wf_20_1, wf_20_2, wf_50_1, wf_100_1, wf_100_2, wf_GC_07, wf_GC_13, wf_GC_29, wf_PP_50_8, wf_PP_100_8, wf_PP_200_8, wf_PP_300_8, wf_PPD_50_8, wf_PPD_100_8, wf_PPD_300_8, wf_PPD_300_2, wf_RBM_200_240, wf_RBM_200_349, wf_RBM_400_394, wf_RBM_200_422, wf_KNN]

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

