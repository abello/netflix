data = open("output-F=50-E=120,140-k=0.02-l=0.001-SC-E=0-SCC=0", "r")

out = open("output-F=50-E=120,140-k=0.02-l=0.001-SC-E=0-SCC=0 CLAMP", "w")

for line in data:
    dat = float(line[:-1])
    if dat < 1.0:
    	dat = 1.0;
    if dat > 5.0:
    	dat = 5.0
    out.write(str(dat) + '\n')


