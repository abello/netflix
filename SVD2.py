import numpy as np

if __name__ == '__main__':
    um_dta, mu_dta = None, None
    with open('data.npz', 'r') as um:
        um_dta = np.load(um)["arr_0"]
    with open('data-mu.npz', 'r') as mu:
        mu_dta = np.load(mu)["arr_0"]

