import numpy as np


def get_frequency(array):
    unique, counts = np.unique(array, return_counts=True)
    return np.column_stack((unique, counts))
