import numpy as np
import skimage.io


def remove_mean(img, factor=0.2, loop=10):
    for _ in range(loop):
        img = img - factor * np.mean(img)
        img[img < 0] = 0
    return img


def remove_mean_and_save(img, factor=0.2, loop=10, filename=''):
    if filename is None:
        filename = f'Deconvolved_{loop}_img'
    for _ in range(loop):
        img = img - factor * np.mean(img)
        img[img < 0] = 0
    skimage.io.imsave(filename, img.astype(np.uint16))

