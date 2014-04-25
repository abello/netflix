with open('../mu/all.dta', 'r') as dta:
    with open('../mu/all.idx', 'r') as idx:
        with open('mu/train-mu.dta', 'w+') as train:
            for line in dta:
                line_idx = int(idx.readline())
                if line_idx <= 3:
                    train.write(line)
