import numpy as np
import networkx as nx
import pymesh
import IO.meshIO as meshIO
import trimesh

note = [0, 0, 0]


def pymesh_to_trimesh(mesh):
    """
        A function to convert pymesh object to trimesh.
        Trimesh has some built-in functions very useful to split mesh into submeshes

        :param mesh: Pymesh Mesh object
        :return: mesh : Trimesh Mesh object
    """
    return trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces)


def trimesh_to_pymesh(mesh):
    """
        A function to convert trimesh object to pymesh.
        Pymesh has some built-in functions very useful to count total number of vertices and to optimise mesh.

        :param mesh: Trimesh Mesh object
        :return: mesh : Pymesh Mesh object
        """
    return pymesh.form_mesh(vertices=mesh.vertices, faces=mesh.faces)


def remove_small_meshes(mesh):
    # todo : refactoring
    graph = create_graph(mesh)
    meshSizeList = get_size_of_meshes(graph)
    biggestMeshes = np.where(meshSizeList > 0.01*np.max(meshSizeList))[0]
    meshList = []
    for extractedMesh in biggestMeshes:
        meshList.append(get_list_of_nodes_in_each_meshes(graph)[extractedMesh])

    # convert list of set to np.array
    for meshNumber in range(len(meshList)):
        meshList[meshNumber] = list(meshList[meshNumber])

    isolatedMeshesList = recreate_meshes(meshList, mesh)
    return isolatedMeshesList


def new_remove_small_meshes(mesh, tolerance=5):
    meshT = pymesh_to_trimesh(mesh)
    meshList = meshT.split()
    biggestMeshesList = []
    for subMesh in meshList:
        if len(subMesh.vertices) > tolerance /100 * len(meshT.vertices):
            biggestMeshesList.append(subMesh)
    if biggestMeshesList is not None:
        if len(biggestMeshesList) > 1:
            finalMesh = trimesh.util.concatenate(biggestMeshesList)
        else:
            finalMesh = biggestMeshesList
        return trimesh_to_pymesh(finalMesh)

    else:
        print('Mesh seems broken')
        return mesh


def remove_noise(mesh, tolerance=5):
    meshT = pymesh_to_trimesh(mesh)
    meshList = meshT.split()
    biggestMeshesList = []
    for subMesh in meshList:
        if len(subMesh.vertices) > tolerance / 100 * len(meshT.vertices):
            biggestMeshesList.append(subMesh)
    if biggestMeshesList is not None:
        return biggestMeshesList
    else:
        print('Mesh seems broken')
        return [mesh]


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
    return isolatedMeshesList


def is_mesh_broken(mesh, meshCopy):
    """
        Easy way to see if the detail settings broke the mesh or not. It can happens with highly details settings.
        :param mesh: Pymesh Mesh object
        Mesh after optimisation
        :param meshCopy: Pymesh Mesh object
        Mesh before optimisation
        :return: boolean
        if True the mesh is broken, if False the mesh isn't broken
    """
    if mesh.vertices.size > 0:
        if np.max(get_size_of_meshes(create_graph(mesh))) < 0.1 * np.max(get_size_of_meshes(create_graph(meshCopy))):
            return True
        else:
            return False
    else:
        return True


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
    """
    A pipeline to optimise and fix mesh. # todo : More information about each steps
    :param mesh: Pymesh Mesh object to optimise
    :param detail: string 'high', 'normal' or 'low' ('normal' as default)
    Settings to choose the targeting minimum length of edges
    :return: Pymesh Mesh object
    An optimised mesh or not depending on detail settings and mesh quality
    """
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
    mesh, __ = pymesh.remove_degenerated_triangles(mesh, 5)
    mesh, __ = pymesh.split_long_edges(mesh, target_len)
    num_vertices = mesh.num_vertices
    while True:
        mesh, __ = pymesh.collapse_short_edges(mesh, target_len,
                                               preserve_feature=True)
        mesh, info = pymesh.remove_obtuse_triangles(mesh, 179.0, 5)
        if mesh.num_vertices == num_vertices:
            break

        num_vertices = mesh.num_vertices
        count += 1
        if count > 10:
            break

    mesh, __ = pymesh.remove_duplicated_vertices(mesh)
    mesh, __ = pymesh.remove_isolated_vertices(mesh)
    mesh = pymesh.resolve_self_intersection(mesh)
    mesh, __ = pymesh.remove_duplicated_faces(mesh)
    mesh, __ = pymesh.remove_duplicated_vertices(mesh)
    mesh = pymesh.compute_outer_hull(mesh)
    mesh, __ = pymesh.remove_duplicated_faces(mesh)
    mesh, __ = pymesh.remove_obtuse_triangles(mesh, 179.0, 5)
    mesh, __ = pymesh.remove_isolated_vertices(mesh)

    if is_mesh_broken(mesh, meshCopy) is True:
        if detail == "high":
            print(f'The function fix_meshes broke mesh, trying with lower details settings')
            fix_meshes(meshCopy, detail="normal")
            return mesh
        if detail == "normal":
            print(f'The function fix_meshes broke mesh, trying with lower details settings')
            mesh = fix_meshes(meshCopy, detail="low")
            return mesh
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
            optimisedMesh, _ = fix_meshes(isolatedMesh)
            meshIO.save_optimised_mesh(optimisedMesh, subMeshnumber, file.split('/')[-1])


if __name__ == "__main__":
    optimise()
