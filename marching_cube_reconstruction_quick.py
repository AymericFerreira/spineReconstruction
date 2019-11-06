import sys

import matplotlib

import numpy as np
from pymesh import form_mesh, remove_isolated_vertices, save_mesh
from skimage import measure, io
import optimise_quick

np.set_printoptions(threshold=sys.maxsize)  # variable output

# matplotlib.use('TkAgg')
matplotlib.use('Qt5Agg')


def range_slider_reconstruction(imagestack):
    imageStack = imagestack
    zSpacing = 0.35/1.518

    for levelThreshold in range(0, 20, 2):

        vertices, faces, normals, values = measure.marching_cubes_lewiner(imageStack,
                                                                          level=float(levelThreshold),
                                                                          spacing=(zSpacing, 0.05, 0.05),
                                                                          allow_degenerate=False)
        mesh2 = form_mesh(vertices, faces)
        optimise_quick.optimise(mesh2)
        # clean mesh
        # mesh3, dictMesh = remove_isolated_vertices(mesh2)
        # print('Vertices removed : {0}'.format(dictMesh[0]))
        # meshName = '{0}_{1}_{2}.ply'.format(filename, str(levelThreshold), zSpacing)
        # save_mesh(meshName, mesh3)
        return mesh2


def automatic_reconstruction(imagestack):
    imageStack = imagestack
    zSpacing = 0.35 / 1.518

    reconstructionList = []
    noteList = []
    parameterList = []

    for levelThreshold in range(0, 20, 2):
        vertices, faces, normals, values = measure.marching_cubes_lewiner(imageStack,
                                                                          level=float(levelThreshold),
                                                                          spacing=(zSpacing, 0.05, 0.05),
                                                                          allow_degenerate=False)
        mesh2 = form_mesh(vertices, faces)
        mesh3, note = optimise_quick.find_best_mesh(mesh2)

        print(f'Note : {note}')
        
        reconstructionList.append(mesh3)
        noteList.append(note)
        parameterList.append(levelThreshold)

    meanList = []
    for note_ in noteList:
        meanList.append(np.mean(note_))

    meanList = np.asarray(meanList)
    print(type(meanList))
    # print(noteList)

    result = np.where(meanList == np.amax(meanList))
    print(type(result))
    print(f'result : {type(result[0][0])}')
    print(reconstructionList)

    meshList = reconstructionList[result[0][0]]
    print(f'Best parameters seem to be : {parameterList[result[0][0]]}')
    for idx, subMesh in enumerate(meshList):
        meshName = f'/mnt/4EB2FF89256EC207/PycharmProjects/spineReconstruction/optimisedMeshes/deconvolved_mesh_{idx}_{parameterList[result[0][0]]}.stl'
        save_mesh(meshName, subMesh)
        # clean mesh
        # mesh3, dictMesh = remove_isolated_vertices(mesh2)
        # print('Vertices removed : {0}'.format(dictMesh[0]))
        # meshName = '{0}_{1}_{2}.ply'.format(filename, str(levelThreshold), zSpacing)
        # save_mesh(meshName, mesh3)


def calculate_mesh_note():
    pass


if __name__ == "__main__":
    filename = '/mnt/4EB2FF89256EC207/PycharmProjects/spineReconstruction/segmentedImages/deconvolved_segmentedImage.tif'
    image = io.imread(filename)
    automatic_reconstruction(image)
