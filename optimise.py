import sys
import glob
import os

import numpy as np

import networkx as nx
import pymesh
import IO.meshIO as meshIO


def remove_small_meshes(mesh):
    #todo : refactoring
    graph = create_graph(mesh)
    meshSizeList = get_size_of_meshes(graph)
    print(meshSizeList)
    biggestMeshes = np.where(meshSizeList > 0.01*np.max(meshSizeList))[0]
    meshList = []
    for extractedMesh in biggestMeshes:
        meshList.append(get_list_of_nodes_in_each_meshes(graph)[extractedMesh])

    # convert list of set to np.array
    for meshNumber in range(len(meshList)):
        meshList[meshNumber] = list(meshList[meshNumber])

    isolatedMeshesList = recreate_meshes(meshList, mesh)
    return isolatedMeshesList


def recreate_meshes(nodeList, mesh):
    # todo : refactoring

    isolatedMeshesList = []

    for isolatedMeshes in range(len(nodeList)):
        to_keep = np.ones(mesh.num_vertices, dtype=bool)
        to_keep[nodeList[0]] = False  # all matching value become false
        to_keep = ~np.array(to_keep)  # True become False and vice-versa

        faces_to_keep = mesh.faces[np.all(to_keep[mesh.faces], axis=1)]
        out_mesh = pymesh.form_mesh(mesh.vertices, faces_to_keep)
        isolatedMeshesList.append(out_mesh)
        # pymesh.save_mesh(f"/isolatedMeshes/a{isolatedMeshes+1}.ply", out_mesh, ascii=True)
        # meshIO.save_optimised_mesh(isolatedMeshes, )


    return isolatedMeshesList


def is_mesh_broken(mesh, meshCopy):
    # print(np.max((get_size_of_meshes(create_graph(mesh)))))
    # print(0.1*np.max(get_size_of_meshes(create_graph(mesh))))
    if np.max((get_size_of_meshes(create_graph(mesh))) < 0.1*np.max(get_size_of_meshes(create_graph(mesh)))):
        return True
    else:
        return False


def create_graph(mesh):
    meshGraph = nx.Graph()
    for faces in mesh.faces:
        meshGraph.add_edge(faces[0], faces[1])
        meshGraph.add_edge(faces[1], faces[2])
        meshGraph.add_edge(faces[0], faces[2])
    return meshGraph


def get_size_of_meshes(graph):
    meshSize = [len(c) for c in nx.connected_components(graph)]
    return meshSize


def get_list_of_nodes_in_each_meshes(graph):
    list_of_set = []
    for subG in nx.connected_components(graph):
        list_of_set.append(subG)
    return list_of_set


def count_number_of_meshes(mesh):
    get_size_of_meshes(create_graph(mesh))


def fix_meshes(mesh, detail="normal"):
    meshCopy = mesh

    # copy/pasta of pymesh script fix_mesh from qnzhou, see pymesh on GitHub
    bbox_min, bbox_max = mesh.bbox
    diag_len = np.linalg.norm(bbox_max - bbox_min)
    if detail == "normal":
        target_len = diag_len * 5e-3
    elif detail == "high":
        target_len = diag_len * 2.5e-3
    elif detail == "low":
        target_len = diag_len * 1e-2

    count = 0
    mesh, __ = pymesh.remove_degenerated_triangles(mesh, 100)
    mesh, __ = pymesh.split_long_edges(mesh, target_len)
    num_vertices = mesh.num_vertices
    while True:
        mesh, __ = pymesh.collapse_short_edges(mesh, 1e-4)
        mesh, __ = pymesh.collapse_short_edges(mesh, target_len,
                                               preserve_feature=True)
        mesh, __ = pymesh.remove_obtuse_triangles(mesh, 150.0, 100)
        if mesh.num_vertices == num_vertices:
            break

        num_vertices = mesh.num_vertices
        count += 1
        if count > 10:
            break

    mesh = pymesh.resolve_self_intersection(mesh)
    mesh, __ = pymesh.remove_duplicated_faces(mesh)
    mesh = pymesh.compute_outer_hull(mesh)
    mesh, __ = pymesh.remove_duplicated_faces(mesh)
    mesh, __ = pymesh.remove_obtuse_triangles(mesh, 179.0, 5)
    mesh, __ = pymesh.remove_isolated_vertices(mesh)

    if is_mesh_broken(mesh, meshCopy) is True:
        if detail == "high":
            print(f'The function fix_meshes broke mesh, trying with lower details settings')
            fix_meshes(mesh, detail="normal")
        if detail == "normal":
            print(f'The function fix_meshes broke mesh, trying with lower details settings')
            fix_meshes(mesh, detail="low")
        if detail == "low":
            print(f'The function fix_meshes broke mesh, no lower settings can be applied, no fix was done')
            return meshCopy
    else:
        return mesh


def optimise():
    filenameList = meshIO.load_folder()

    for file in filenameList:
        mesh = pymesh.load_mesh(file)
        isolatedMeshesList = remove_small_meshes(mesh)
        for subMeshnumber, isolatedMesh in enumerate(isolatedMeshesList):
            optimisedMesh = fix_meshes(isolatedMesh)
            meshIO.save_optimised_mesh(optimisedMesh, subMeshnumber, file.split('/')[-1])


if __name__ == "__main__":
    # mesh = pymesh.load_mesh('/mnt/4EB2FF89256EC207/PycharmProjects/Reconstruction/mesh/'
                            # 'spine_11_18_0.230566534914361.ply')
    # remove_small_meshes(mesh)
    optimise()
