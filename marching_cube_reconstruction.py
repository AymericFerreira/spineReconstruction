import sys

import matplotlib

# matplotlib.use('TkAgg')
matplotlib.use('Qt5Agg')

import numpy as np
# from skimage import util
from pymesh import form_mesh, remove_isolated_vertices, save_mesh
from skimage import measure

np.set_printoptions(threshold=sys.maxsize)  # variable output


def filename_range_slider_reconstruction(imagestack, filename):
    imageStack = imagestack
    zSpacing = 0.35/1.518

    for levelThreshold in range(0, 20, 2):

        vertices, faces, normals, values = measure.marching_cubes_lewiner(imageStack,
                                                                          level=float(levelThreshold),
                                                                          spacing=(zSpacing, 0.05, 0.05),
                                                                          allow_degenerate=False)
        mesh2 = form_mesh(vertices, faces)

        # clean mesh
        mesh3, dictMesh = remove_isolated_vertices(mesh2)
        # print('Vertices removed : {0}'.format(dictMesh[0]))
        meshName = '{0}_{1}_{2}.ply'.format(filename, str(levelThreshold), zSpacing)
        save_mesh(meshName, mesh3)