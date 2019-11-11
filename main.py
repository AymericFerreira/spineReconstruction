from chan_vese_segmentation import *
from marching_cube_reconstruction import *


if __name__ == "__main__":
    for (dirpath, _, filenames) in os.walk("Images/"):
        for filename in filenames:
            filename_plan_segmentation(dirpath, filename)
    for (dirpath, _, filenames) in os.walk("segmentedImages/"):
        for filename in filenames:
            automatic_marching_cube_reconstruction(dirpath, filename)
