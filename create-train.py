data = open("um/all.dta", "r")
idx = open("um/all.idx", "r")

out = open("processed_data/train+probe.dta", "w")

for line in data:
    index = int(idx.readline())
    if index in [1, 2, 3, 4]:
        out.write(line)


