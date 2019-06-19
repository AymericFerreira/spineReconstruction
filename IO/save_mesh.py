import pymesh


def save_mesh(mesh, filename):
    pymesh.save_mesh(f"/meshes/{filename}{isolatedMeshes + 1}.ply", out_mesh, ascii=True)
    pass


def save_optimised_mesh(mesh, filename):
    pass


def ask_save_mesh(mesh):
    pass