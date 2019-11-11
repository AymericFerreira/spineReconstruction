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
    vertices, faces, normals, values = measure.marching_cubes_lewiner(imageStack,
                                                                      level=float(levelThreshold),
                                                                      spacing=spacingData,
                                                                      allow_degenerate=False)
    mesh = form_mesh(vertices, faces)
    return mesh


def construct_and_optimise_from_lewiner(imageStack, spacingData, levelThreshold):
    mesh = optimise.fix_meshes(construct_mesh_from_lewiner(imageStack, spacingData, levelThreshold))
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
    print(f'optimisedMeshes/{filename.strip(".tif").split("/")[-1]}_mesh_.stl')
    imageStack = io.imread(f'{dirpath}/{filename}')
    zSpacing = 0.35 / 1.518

    levelThreshold = 0
    stability = True

    mesh = construct_mesh_from_lewiner(imageStack, (zSpacing, 0.05, 0.05), levelThreshold)


    while stability is True:
        if levelThreshold > 200:
            print('Image seems to be mostly noise, or resolution is super good. Stopping at levelTreshold 200')
            stability = False
            levelThreshold = 200

        vertices, faces, normals, values = measure.marching_cubes_lewiner(imageStack,
                                                                          level=float(levelThreshold),
                                                                          spacing=(zSpacing, 0.05, 0.05),
                                                                          allow_degenerate=False)
        mesh2 = form_mesh(vertices, faces)
        meshList = optimise.get_size_of_meshes(optimise.create_graph(mesh2))
        meshList.sort(reverse=True)
        # meshList = meshList[meshList > 0.01 * np.sum(meshList)] # this line remove 'noise'
        meshList = [x if x > 0.01 * np.sum(meshList) else 0 for x in meshList]
        if len(meshList) > 1:
            if (meshList[0]+meshList[1])/np.sum(meshList) > 0.9 and meshList[0]/np.sum(meshList) < 0.8:
                stability = False
                stability2 = False
                # neck and head are dissociated
                while stability2 is False:
                    levelThreshold -= levelThreshold/10
                    vertices, faces, normals, values = measure.marching_cubes_lewiner(imageStack,
                                                                                  level=float(levelThreshold),
                                                                                  spacing=(zSpacing, 0.05, 0.05),
                                                                                  allow_degenerate=False)
                    mesh2 = form_mesh(vertices, faces)
                    meshList = optimise.get_size_of_meshes(optimise.create_graph(mesh2))
                    if len(meshList) > 1:
                        if (meshList[0] + meshList[1]) / np.sum(meshList) > 0.9 and meshList[0]/np.sum(meshList) < 0.8:
                            pass
                        else:
                            break
                    else:
                        break
            else:
                levelThreshold += 5
        else:
            levelThreshold += 5
            # Look for narrow reconstruction

    mesh3 = optimise.fix_meshes(mesh2)
    print(f'Saving mesh with level threshold : {levelThreshold}')
    save_mesh(f'optimisedMeshes/{filename.split(".")[0]}_{levelThreshold}_optimised.stl', mesh3)


if __name__ == "__main__":
    for (dirpath, _, filenames) in os.walk("segmentedImages/"):
        for filename in filenames:
            automatic_marching_cube_reconstruction(dirpath, filename)
