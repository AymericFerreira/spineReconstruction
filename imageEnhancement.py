import skimage
import numpy as np

# todo : It's possible to store data in non fixe dimensional variable
# todo : example head, *body, tail = range(5)
# print(head, body, tail)
# 0 [1, 2, 3] 4
# todo : It should be useful to use it here
# todo : Remove all comments
# todo : Make it works for 16bit images
# todo : deconvolution


def enhance_image_head_neck():
    headImage = skimage.io.imread('images/Deconvolved_head.tif')
    neckImage = skimage.io.imread('images/Deconvolved_neck.tif')

    # if the image is superior to 3D, transform to 3D :
    try:
        headImage.shape[3]
    except IndexError:
        pass
    else:
        headImage = headImage[:, :, :, 1]

    try:
        neckImage.shape[3]
    except IndexError:
        pass
    else:
        neckImage = neckImage[:, :, :, 1]

    # Improve Images

    # improvedImage = headImage
    # skimage.img_as_ubyte(improvedImage)

    # Convert to 8 bytes
    ubyteHeadImage = skimage.img_as_ubyte(headImage)
    ubyteNeckImage = skimage.img_as_ubyte(neckImage)

    # remove 200+ pixel from neck Image and also saturation

    ubyteNeckImage[ubyteNeckImage >= 255] = 0

    # Sum Images

    improvedImage = (ubyteHeadImage + ubyteNeckImage)

    improvedImage[improvedImage > 255] = 255

    with skimage.external.tifffile.TiffWriter('images/Deconvolved_image.tif') as tif:
        for i in range(improvedImage.shape[0]):
            tif.save(improvedImage[i], compress=0)


def remove_mean(img, factor=0.2, loop=10):
    for loopCounter in range(loop):
        img = img - factor * np.mean(img)
        img[img < 0] = 0
    return img


def remove_mean_and_save(img, factor=0.2, loop=10, filename=''):
    if filename is None:
        filename = f'Deconvolved_{loop}_img'
    for loopCounter in range(loop):
        img = img - factor * np.mean(img)
        img[img < 0] = 0
    skimage.io.imsave(filename, img.astype(np.uint16))


if __name__ == '__main__':
    enhance_image_head_neck()
