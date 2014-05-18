QUAL_SIZE = 2749898

f5 =  open("results/output-F=10-E=30,30-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f10 = open("results/output-F=5-E=40,40-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")

out = open("results/blended", "w")

w5 = 0.730466
w10 = 0.28808

for i in xrange(QUAL_SIZE):
    r5 = float(f5.readline().rstrip())
    r10 = float(f10.readline().rstrip())
    b = round(r5 * w5 + r10 * w10, 4)
    out.write(str(b) + "\n")

