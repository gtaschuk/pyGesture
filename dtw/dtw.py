import mlpy
import matplotlib.pyplot as pyplot
import matplotlib.cm as cm


x = [0,0,0,0,1,1,2,2,3,2,1,1,0,0,0,0]
y = [0,0,1,1,2,2,3,3,3,3,2,2,1,1,0,0]



dist, cost, path = mlpy.dtw_std(x, y, dist_only=False)
print dist
fig = pyplot.figure(1)

ax = fig.add_subplot(111)

plot1 = pyplot.imshow(cost.T, origin='lower', cmap=cm.gray, interpolation='nearest')
plot2 = pyplot.plot(path[0], path[1], 'w')
xlim = ax.set_xlim((-0.5, cost.shape[0]-0.5))
ylim = ax.set_ylim((-0.5, cost.shape[1]-0.5))
pyplot.show()
