import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from IO.extractData import *


def plot_numpy_bar(array, xLabel, yLabel, title):
    print(array.size)
    plt.bar(array[:,0], array[:,1])  # arguments are passed to np.histogram
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.show()


def plot_frequency(array, xLabel, yLabel, title):
    npFrequency = get_frequency(array)
    print(npFrequency)
    plot_numpy_bar(npFrequency, xLabel, yLabel, title)


def plot_3d_scatter_with_color(array, xLabel, yLabel, zLabel, title):
    fig = plt.figure()
    scatterPlot = fig.add_subplot(111, projection='3d')

    p = scatterPlot.scatter(array[:, 0], array[:, 1], array[:, 2], c=array[:, 3], cmap='Set1', alpha=0.75, vmin=2, vmax=15)
    scatterPlot.set_xlabel(xLabel)
    scatterPlot.set_ylabel(yLabel)
    scatterPlot.set_zlabel(zLabel)
    scatterPlot.set_title(title)

    fig.colorbar(p, label='number of neighbors')
    plt.show()


def plot_3d_scatter_with_color_and_gravity_center(array, xLabel, yLabel, zLabel, title, gravity_center):
    fig = plt.figure()
    scatterPlot = fig.add_subplot(111, projection='3d')

    p = scatterPlot.scatter(array[:, 0], array[:, 1], array[:, 2], c=array[:, 3], cmap='Set1', alpha=0.75)
    scatterPlot.set_xlabel(xLabel)
    scatterPlot.set_ylabel(yLabel)
    scatterPlot.set_zlabel(zLabel)
    scatterPlot.set_title(title)
    scatterPlot.scatter(gravity_center[0], gravity_center[1], gravity_center[2], c='black')

    fig.colorbar(p, label='number of neighbors')
    plt.show()


def plot_3d_scatter_fixed(array, fixedList, xLabel, yLabel, zLabel, title):
    fig = plt.figure()
    scatterPlot = fig.add_subplot(111, projection='3d')

    scatterPlot.scatter(array[:, 0], array[:, 1], array[:, 2], c='grey', cmap='Set1', alpha=0.5)
    scatterPlot.scatter(array[fixedList, 0], array[fixedList, 1], array[fixedList, 2], color='red')
    scatterPlot.set_xlabel(xLabel)
    scatterPlot.set_ylabel(yLabel)
    scatterPlot.set_zlabel(zLabel)
    scatterPlot.set_title(title)
    # scatterPlot.scatter(gravity_center[0], gravity_center[1], gravity_center[2], c='black')

    # fig.colorbar(p, label='number of neighbors')
    plt.show()


def plot_3d_scatter_with_color_and_gravity_center_and_gravity_median(array, xLabel, yLabel, zLabel, title, gravityCenter, gravityMedian):
    fig = plt.figure()
    scatterPlot = fig.add_subplot(111, projection='3d')

    # p = scatterPlot.scatter(array[:, 0], array[:, 1], array[:, 2], c=array[:, 3], cmap='Set1', alpha=0.75)
    scatterPlot.scatter(array[:, 0], array[:, 1], array[:, 2], alpha=0.75)
    scatterPlot.set_xlabel(xLabel)
    scatterPlot.set_ylabel(yLabel)
    scatterPlot.set_zlabel(zLabel)
    scatterPlot.set_title(title)
    scatterPlot.scatter(gravityCenter[0], gravityCenter[1], gravityCenter[2], c='black')
    scatterPlot.scatter(gravityMedian[0], gravityMedian[1], gravityMedian[2], c='blue')

    # fig.colorbar(p, label='number of neighbors')
    plt.show()


def plot_metrics_and_variance():
    data=[24,8,8,0,-11.63,0.72]
    data2=[24,8,8,0,0.71,0.7]
    data3=[24,8,8,0,1.87,0.73]
    x = ['Surface','Volume','hullVolume','hullRatio','meanCurv','gaussCurv']
    var=[99.54,32.71,74.24,0.01,0.16,0.46,0.14,4.77,13.23,8.51]
    plt.plot(x, data, linestyle='-', marker='x',color='red')
    plt.plot(x, data2, linestyle='-', marker='x', color='blue')
    plt.plot(x, data3, linestyle='-', marker='x', color='green')
    plt.xticks(rotation=90)
    plt.legend(('Nature', 'Perso', 'Meshlab'))
    plt.title('cube * 16')

    plt.show()
