import skimage.external.tifffile


def save_segmented_images(image, filename):
    with skimage.external.tifffile.TiffWriter(filename) as tif:
        for stack in range(image.shape[0]):
            tif.save(image[stack], compress=0)


def ask_save_image(image):
    pass


def ask_save_object(image):
    pass
