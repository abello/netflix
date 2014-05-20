QUAL_SIZE = 2749898

f20_1 =  open("results/output-F=20-E=80,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f20_2 = open("results/output-F=20-E=80,180-k=0.02-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f50_1 =  open("results/output-F=50-E=120,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f100_1 = open("results/output-F=100-E=120,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f100_2 = open("results/output-F=100-E=120,180-k=0.02-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f_GC_07 = open("results/output-GC-0.07", "r")
f_GC_13 = open("results/output-GC-0.13", "r")
f_GC_29 = open("results/output-GC-0.29", "r")
f_PP_50_30_NA = open("results/output-F=50-LRT_mb0.003-LAM_mb=0-LRT_ub=0.012-LAM_ub=0.03-LRT_mf=0.011-LAM_mf=0.006-LRT_uf=0.006-LAM_uf0.08-LRT_mw=0.001-LAM_mw=0.03-NBINS=5", "r")



files = [f20_1, f20_2, f50_1, f100_1, f100_2, f_GC_07, f_GC_13, f_GC_29, f_PP_50_30_NA]

out = open("results/blended", "w")


wf_20_1 = -0.374593836973
wf_20_2 = 0.527927470019
wf_50_1 = 0.0365392710056
wf_100_1 = 0.113381423947
wf_100_2 = 0.107134928888
wf_GC_07 = 0.088384089707
wf_GC_13 = 0.0714154029464
wf_GC_29 = 0.0765151460297
wf_PP_50_30_NA = 0.351212798433

weights = [wf_20_1, wf_20_2, wf_50_1, wf_100_1, wf_100_2, wf_GC_07, wf_GC_13, wf_GC_29, wf_PP_50_30_NA]

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

