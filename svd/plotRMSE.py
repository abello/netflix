import matplotlib.pyplot as plt

rmses = [float(v) for v in open('rmseOut.txt', 'r').readlines()]
features = range(50)

plt.plot(features, rmses)
plt.show()
