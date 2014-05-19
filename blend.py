QUAL_SIZE = 2749898

# TODO: Fix mismatch in f100_1!!!!

f20_1 =  open("results/output-F=20-E=80,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f20_2 = open("results/output-F=20-E=80,180-k=0.02-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f50_1 =  open("results/output-F=50-E=120,180-k=0.015-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")
f100_1 = open("results/output-F=100-E=120,180-k=0.02-l=0.001-SC-E=0-SCC=0-NBINS=5", "r")

files = [f20_1, f20_2, f50_1, f100_1]

out = open("results/blended", "w")


w20_1 = -0.235276048724
w20_2 = 0.473523895167
w50_1 = 0.277299341734
w100_1 = 0.480955148007

weights = [w20_1, w20_2, w50_1, w100_1]

for i in xrange(QUAL_SIZE):
    j = 0
    b = 0
    for f in files:
        val = f.readline().rstrip()
        b += float(val) * weights[j]
        j += 1
    b = round(b, 4)

    out.write(str(b) + "\n")

