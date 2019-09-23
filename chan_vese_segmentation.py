import os
import sys

import matplotlib

# matplotlib.use('TkAgg')
# matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
import numpy as np
import skimage
# from skimage import util
from matplotlib.widgets import Slider, Button
from skimage.color import rgb2gray
from skimage.segmentation import mark_boundaries, chan_vese
from skimage import io

np.set_printoptions(threshold=sys.maxsize)  # variable output

falseMatrixActivation = 0


def filename_plan_segmentation(imagestack, filename):
    imageStack = imagestack
    muDivision = np.linspace(0, 0.5, 15)
    lambda1Division = np.linspace(0, 4, 15)
    lambda2Division = np.linspace(0, 4, 15)

    zStack, width, length = np.shape(imageStack)
    maxImage = np.max(imageStack, axis=0)
    # maxImage = np.max(np.delete(imageStack, 0, 3), axis=0)

    # noColorPlan = rgb2gray(maxImage)

    mu_0 = 0.25
    delta_mu = 0.05
    lambda1_0 = 2
    lambda2_0 = 4
    tol = 1e-3
    max_iter = 1000
    dt = 0.5

    loopPosition = 0

    for plan in imageStack:
        global falseMatrixActivation
        falseMatrixActivation = 0
        fig, ax = plt.subplots()
        plt.subplots_adjust(left=0.1, bottom=0.3)
        graphTitle = 'Interactive segmentation  plan ' + str(loopPosition+1)
        plt.title(graphTitle)
        try:
            with open('cv_Parameter.txt', 'r') as cvParameter:

                print('cv_Parameter.txt found, loading previous parameters.')
                line = cvParameter.read().splitlines()
                mu_0 = float(line[0])
                lambda1_0 = float(line[1])
                lambda2_0 = float(line[2])
                delta_mu = 0.05
                tol = 1e-3
                max_iter = 1000
                dt = 0.5

        except FileNotFoundError:
            mu_0 = 0.25
            lambda1_0 = 2
            lambda2_0 = 4
            delta_mu = 0.05
            tol = 1e-3
            max_iter = 1000
            dt = 0.5

        noColorPlan = rgb2gray(plan)
        # print(plan, noColorPlan)
        cv = chan_vese(noColorPlan, mu=mu_0, lambda1=lambda1_0, lambda2=lambda2_0, tol=tol, max_iter=max_iter / 10, dt=dt,
                       init_level_set='checkerboard', extended_output=True)

        # if 16 bit image
        # maxImage2 = maxImage*16
        # maxImage3 = skimage.img_as_ubyte(maxImages2)
        # ax.imshow(mark_boundaries(maxImage, cv[0]), vmin=0, vmax=4096)
        ax.imshow(mark_boundaries(noColorPlan, cv[0]))

        # reinitialise value for slider

        # mu_0 = 0.25
        # lambda1_0 = 2
        # lambda2_0 = 4

        colorAxe = 'lightgray'
        muAxe = plt.axes([0.25, 0.2, 0.5, 0.03], facecolor='lightcoral')
        lambda1Axe = plt.axes([0.25, 0.15, 0.5, 0.03], facecolor='yellowgreen')
        lambda2Axe = plt.axes([0.25, 0.1, 0.5, 0.03], facecolor='mediumturquoise')
        muSlider = Slider(muAxe, '$\mu$', -0.05, 2., valinit=mu_0)
        lambda1Slider = Slider(lambda1Axe, '$\lambda_1$', 0., 10.0, valinit=lambda1_0)
        lambda2Slider = Slider(lambda2Axe, '$\lambda_2$', 0., 10.0, valinit=lambda2_0)

        def update(val):
            mu = muSlider.val
            lambda1 = lambda1Slider.val
            lambda2 = lambda2Slider.val
            cv = chan_vese(noColorPlan, mu=mu, lambda1=lambda1, lambda2=lambda2, tol=tol, max_iter=max_iter / 10, dt=dt,
                           init_level_set='checkerboard', extended_output=True)
            ax.imshow(mark_boundaries(noColorPlan, cv[0]), vmin=0, vmax=4096)
            #fig.canvas.draw_idle()

        muSlider.on_changed(update)
        lambda1Slider.on_changed(update)
        lambda2Slider.on_changed(update)

        resetAxe = plt.axes([0.65, 0.025, 0.1, 0.04])
        button = Button(resetAxe, 'Reset', color=colorAxe, hovercolor='0.6')

        def reset(event):
            muSlider.reset()
            lambda1Slider.reset()
            lambda2Slider.reset()

            try:
                with open('cv_Parameter.txt', 'r'):
                    pass
                os.remove('cv_Parameter.txt')

            except FileNotFoundError:
                pass

        button.on_clicked(reset)

        def keep_nothing(event):
            global falseMatrixActivation
            falseMatrixActivation = 1
            # print(f'falseMatrixActivation : {falseMatrixActivation}')
            plt.close()

        keepNothingAxe = plt.axes([0.25, 0.025, 0.2, 0.04])
        keepNothingButton = Button(keepNothingAxe, 'Keep Nothing', color=colorAxe, hovercolor='0.6')
        keepNothingButton.on_clicked(keep_nothing)

        saveAxe = plt.axes([0.5, 0.025, 0.1, 0.04])
        saveButton = Button(saveAxe, 'Save', color=colorAxe, hovercolor='0.6')

        def save(event):
            with open('cv_Parameter.txt', 'w') as cvParameter:
                cvParameter.write(str(muSlider.val) + '\n')
                cvParameter.write(str(lambda1Slider.val) + '\n')
                cvParameter.write(str(lambda2Slider.val) + '\n')
            print('Data saved in cv_Parameter.txt')
            plt.close()

        saveButton.on_clicked(save)

        plt.show()

        # Segmentation with best parameters or default
        if falseMatrixActivation == 1:
            imageStack[loopPosition] = np.zeros(np.shape(plan))
            print(f'no segmentation done')
        else:
            try:
                with open('cv_Parameter.txt', 'r') as cvParameter:

                    print('cv_Parameter.txt found, loading best parameters.')
                    line = cvParameter.read().splitlines()
                    mu = float(line[0])
                    lambda1 = float(line[1])
                    lambda2 = float(line[2])
            except FileNotFoundError:
                print('cv_Parameter.txt not found, loading default parameters.')
                mu = mu_0
                lambda1 = lambda1_0
                lambda2 = lambda2_0

            cv = chan_vese(noColorPlan, mu=mu, lambda1=lambda1, lambda2=lambda2, tol=tol, max_iter=max_iter, dt=dt,
                           init_level_set='checkerboard', extended_output=True)

            print('Segmentation done with parameter $\mu$ : {0}, $\lambda_1$ : {1}, $\lambda_2$ : {2}, '
                  'tolerance : {3:1.2e}, ''max iteration : {4:1.2e}, dt : {5}.'.format(mu, lambda1, lambda2, tol,
                                                                                       max_iter, dt))

            imageStack[loopPosition] = cv[0] * plan

        loopPosition += 1

    # Treatment and export

    segmentedImageName = 'segmented_Image/' + filename + '_segmentedImage.tif'
    # with skimage.external.tifffile.TiffWriter(segmentedImageName) as tif:
    #     for image in range(imageStack.shape[0]):
    #         tif.save(imageStack[image], compress=0)

    skimage.io.imsave(segmentedImageName, image)

    return imageStack


if __name__ == "__main__":
    filename = '/mnt/4EB2FF89256EC207/PycharmProjects/spineReconstruction/images/Deconvolved_3.tif'
    image = io.imread(filename)
    filename = 'deconvolved'
    filename_plan_segmentation(image, filename)
#
