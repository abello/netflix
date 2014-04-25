with open('../um/all.dta', 'r') as dta:
    with open('../um/all.idx', 'r') as idx:
        with open('../processed_data/train.dta', 'w+') as train:
            for line in dta:
                line_idx = int(idx.readline())
                if line_idx <= 3:
                    train.write(line)
