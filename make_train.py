with open('all.dta', 'r') as dta:
    with open('all.idx', 'r') as idx:
        with open('train.dta', 'w+') as train:
            for line in dta:
                line_idx = int(idx.readline())
                if line_idx <= 3:
                    train.write(line)
