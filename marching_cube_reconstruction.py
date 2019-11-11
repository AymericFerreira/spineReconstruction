import sys
import os
import numpy as np
from pymesh import form_mesh, save_mesh
from skimage import measure, io
import optimise

np.set_printoptions(threshold=sys.maxsize)  # variable output

# matplotlib.use('TkAgg')
# matplotlib.use('Qt5Agg')


def construct_mesh_from_lewiner(imageStack, spacingData, levelThreshold):
    """
        Lewiner marching cubes algorithm using skimage.measure.marching_cubes_lewiner to find surfaces in 3d volumetric data.

        Convert an imagestack to a pymesh Mesh object

        :param imageStack: (M, N, P) array
        Volume data aka each stack of an  image to find isosurfaces
        :param spacingData: (3) list
        Information about the image properties, size of voxel z, x, y
        Note that you should correct Z-axis depending of medium refraction index
        :param levelThreshold: float
        Contour value to search for isosurfaces

        :return:
        A pymesh Mesh object
    """
    vertices, faces, normals, values = measure.marching_cubes_lewiner(imageStack,
                                                                      level=float(levelThreshold),
                                                                      spacing=spacingData,
                                                                      allow_degenerate=False)
    mesh = form_mesh(vertices, faces)
    return mesh


def construct_and_optimise_from_lewiner(imageStack, spacingData, levelThreshold, tol=5):
    """
        Lewiner marching cubes algorithm using skimage.measure.marching_cubes_lewiner
        to find surfaces in 3d volumetric data.

        Convert an imagestack to a pymesh Mesh object, improve it via an optimisation pipeline and delete 'noise' aka
        small meshes

        :param imageStack: (M, N, P) array
        Volume data aka each stack of an  image to find isosurfaces
        :param spacingData: (3) list
        Information about the image properties, size of voxel z, x, y
        Note that you should correct Z-axis depending of medium refraction index
        :param levelThreshold: float
        Contour value to search for isosurfaces
        :param tol: float
        Percentage of tolerance when looking for small meshes. If the submesh contains less than tol% (5% by default)
        vertices, delete this mesh from output object

        :return:
        An optimised pymesh Mesh object
        """
    mesh = optimise.fix_meshes(construct_mesh_from_lewiner(imageStack, spacingData, levelThreshold))
    mesh = optimise.new_remove_small_meshes(mesh, tolerance=tol)
    return mesh


def verify_mesh_stability(mesh):
    meshList = optimise.get_size_of_meshes(optimise.create_graph(mesh))
    meshList.sort(reverse=True)
    if len(meshList) > 1:
        if (meshList[0] + meshList[1]) / np.sum(meshList) > 0.9 and meshList[0] / np.sum(meshList) < 0.8:
            stability = False
            print(f'Can"t recontruct this spine {filename}')
    pass


def automatic_marching_cube_reconstruction(dirpath, filename):
    """

    :param dirpath:
    :param filename:
    :return:
    """
    print(f'Computing : {filename.strip(".tif").split("/")[-1]}_mesh')
    imageStack = io.imread(f'{dirpath}/{filename}')
    zSpacing = 0.35 / 1.518

    levelThreshold = 0
    stability = True

    mesh = construct_mesh_from_lewiner(imageStack, (zSpacing, 0.05, 0.05), levelThreshold)

    # Todo : refactoring and cut into more functions
    while stability is True:
        if levelThreshold > 200:
            print('Image seems to be mostly noise, or resolution is super good. Stopping at levelTreshold 200')
            stability = False
            levelThreshold = 200

        mesh2 = construct_mesh_from_lewiner(imageStack, (zSpacing, 0.05, 0.05), levelThreshold)
        meshList = optimise.get_size_of_meshes(optimise.create_graph(mesh2))
        meshList.sort(reverse=True)
        meshList = [x if x > 0.01 * np.sum(meshList) else 0 for x in meshList]
        if len(meshList) > 1:
            if (meshList[0]+meshList[1])/np.sum(meshList) > 0.9 and meshList[0]/np.sum(meshList) < 0.8:
                stability = False
                stability2 = False
                # neck and head are dissociated
                while stability2 is False:
                    # levelThreshold -= levelThreshold/10
                    levelThreshold -= 1
                    mesh2 = construct_mesh_from_lewiner(imageStack, (zSpacing, 0.05, 0.05), levelThreshold)
                    # meshL = optimise.remove_noise(mesh2)
                    meshL = optimise.remove_noise(mesh2)
                    if len(meshL) > 1:
                        if (len(meshL[0].vertices) + len(meshL[1].vertices)) / len(mesh2.vertices) > 0.9 \
                                and len(meshL[0].vertices) / len(mesh2.vertices) < 0.8:
                            pass
                        else:
                            levelThreshold -= levelThreshold/10
                            break
                            # mesh2 = construct_mesh_from_lewiner(imageStack, (zSpacing, 0.05, 0.05), levelThreshold)
                            # mesh2 = optimise.remove_noise(mesh2)
                    else:
                        levelThreshold -= levelThreshold / 10
                        break
                        # mesh2 = construct_mesh_from_lewiner(imageStack, (zSpacing, 0.05, 0.05), levelThreshold)
                        # mesh2 = optimise.remove_noise(mesh2)
            else:
                levelThreshold += 5
        else:
            levelThreshold += 5
            # Look for narrow reconstruction
    mesh3 = construct_and_optimise_from_lewiner(imageStack, (zSpacing, 0.05, 0.05), levelThreshold)
    # meshList = meshList[meshList > 0.01 * np.sum(meshList)] # this line remove 'noise'

    # mesh3 = optimise.fix_meshes(mesh2)
    print(f'Saving mesh with level threshold : {levelThreshold} in optimisedMeshes')
    save_mesh(f'optimisedMeshes/{filename.split(".")[0]}_{levelThreshold}_optimised.stl', mesh3)


if __name__ == "__main__":
    for (dirpath, _, filenames) in os.walk("segmentedImages/"):
        for filename in filenames:
            automatic_marching_cube_reconstruction(dirpath, filename)
