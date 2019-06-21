import skimage
from skimage import io
from skimage import external

# todo : It's possible to store data in non fixe dimensional variable
# todo : example head, *body, tail = range(5)
# print(head, body, tail)
# 0 [1, 2, 3] 4
# todo : It should be useful to use it here
# todo : Remove all comments
# todo : Make it works for 16bit images
# todo : deconvolution


def enhance_image_head_neck():
    headImage = io.imread('images/head.tif')
    neckImage = io.imread('images/neck.tif')

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
    # improvedImage.astype(int)
    # skimage.img_as_ubyte(improvedImage)

    # io.imsave('images/image.tif', improvedImage.astype(int))
    # skimage.external.tifffile.TiffWriter('images/image.tif', improvedImage)
    with skimage.external.tifffile.TiffWriter('images/image.tif') as tif:
        for i in range(improvedImage.shape[0]):
            tif.save(improvedImage[i], compress=0)


def deconvolution():
    pass


if __name__ == '__main__':
    enhance_image_head_neck()
