PROBE_SIZE = 2749898

f5 =  open("results/output-OBO-F=60-E=130,160-k=0.02-l=0.001-SC-E=10-SCC=3")
f10 = open("results/output-OBO-F=50-E=130,160-k=0.02-l=0.001-SC-E=10-SCC=3")

out = open("results/blended", "w")

w5 = 12.9731248352
w10 = -12.1284005209

for i in xrange(PROBE_SIZE):
    r5 = float(f5.readline().rstrip())
    r10 = float(f10.readline().rstrip())
    b = r5 * w5 + r10 * w10
    out.write(str(b) + "\n")

