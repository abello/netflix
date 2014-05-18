QUAL_SIZE = 2749898

f5 =  open("results/output-F=5-E=20,20-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f10 = open("results/output-F=10-E=15,15-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")

out = open("results/blended", "w")

w5 = 1.4085301516
w10 = -0.4181661914

for i in xrange(QUAL_SIZE):
    l5 = f5.readline().rstrip()
    l10 = f10.readline().rstrip()
    r5 = float(l5)
    r10 = float(l10)
    b = round(r5 * w5 + r10 * w10, 4)
    out.write(str(b) + "\n")

