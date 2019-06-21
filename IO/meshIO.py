import pymesh
import tkinter


def save_mesh(mesh, filename, extension='stl'):
    pymesh.save_mesh(f"/meshes/{filename}.{extension}", mesh)


def save_optimised_mesh(mesh, subMeshNumber, filename, extension='stl'):
    pymesh.save_mesh(f"/optimisedMeshes/{filename}_optimisedMesh_{subMeshNumber}.{extension}", mesh)


def ask_save_mesh(mesh):
    tkinter.Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = tkinter.Tk.asksaveasfile(mode='w', defaultextension=".stl")
    pymesh.save_mesh(filename, mesh)

if __name__ == '__main__':
    pass