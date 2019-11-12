import chan_vese_segmentation
import marching_cube_reconstruction
import os


if __name__ == "__main__":
    # Segmentation of all images in Images/ folder.
    for (dirpath, _, filenames) in os.walk("Images/"):
        for filename in filenames:
            chan_vese_segmentation.filename_plan_segmentation(dirpath, filename)
    # Reconstruction  via marching cubes algorithm of all segmented images in segmentedImages/ folder.
    for (dirpath, _, filenames) in os.walk("segmentedImages/"):
        for filename in filenames:
            marching_cube_reconstruction.automatic_marching_cube_reconstruction(dirpath, filename)
