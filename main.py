from optimise import *
from chan_vese_segmentation import *
from marching_cube_reconstruction import *


if __name__ == "__main__":
    for (dirpath, _, filenames) in os.walk("images/"):
        for filename in filenames:
            # filename_plan_segmentation(dirpath, filename)
            automatic_marching_cube_reconstruction(dirpath, filename)
