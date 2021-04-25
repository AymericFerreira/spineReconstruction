import pymesh
import tkinter
import glob


def save_mesh(mesh, filename, extension='stl'):
    pymesh.save_mesh(f"/meshes/{filename}.{extension}", mesh)


def save_optimised_mesh(mesh, subMeshNumber, filename, extension='stl'):
    print(f"optimisedMeshes/{filename.split()[0]}_optimisedMesh_{subMeshNumber}.{extension}")
    pymesh.save_mesh(f"optimisedMeshes/{filename.split()[0]}_optimisedMesh_{subMeshNumber}.{extension}", mesh)


def ask_save_mesh(mesh):
    tkinter.Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = tkinter.Tk.asksaveasfile(mode='w', defaultextension=".stl")
    pymesh.save_mesh(filename, mesh)


def load_folder(folder_path='meshes/'):
    # filenameList = glob.glob1(f'{folder_path}/', "*.off") + glob.glob1(f'{folder_path}/', "*.mesh") + \
    #                glob.glob1(f'{folder_path}/', "*.msh") + glob.glob1(f'{folder_path}/', "*.node") + \
    #                glob.glob1(f'{folder_path}/', "*.ply") + glob.glob1(f'{folder_path}/', "*.poly") + \
    #                glob.glob1(f'{folder_path}/', "*.stl")
    filenameList = glob.glob(f'{folder_path}*')

    return filenameList


pass