import matplotlib.pyplot as plt

rmses = [float(v) for v in open('rmseOut.txt', 'r').readlines()]
features = range(50)

rmses_in = [float(v) for v in open('rmseIn.txt', 'r').readlines()]
delx = 49.0 / len(rmses_in) 
rmses_in_x = [delx * v for v in range(len(rmses_in))]

plt.plot(features, rmses)
plt.plot(rmses_in_x, rmses_in)
plt.xlabel('Number of Features')
plt.ylabel('RMSE')
plt.show()
