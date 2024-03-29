import pymesh
import matplotlib
matplotlib.use("TkAgg")
# matplotlib.use('Qt5Agg')
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import plotly.graph_objects as go
import os
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from IO.draw import *


def center_mesh(mesh):
    centeredVertices = np.zeros(shape=(len(mesh.vertices), 3))

    centeredVertices[:, 0] = mesh.vertices[:, 0] - gravity_center(mesh)[0]
    centeredVertices[:, 1] = mesh.vertices[:, 1] - gravity_center(mesh)[1]
    centeredVertices[:, 2] = mesh.vertices[:, 2] - gravity_center(mesh)[2]
    return pymesh.meshio.form_mesh(centeredVertices, mesh.faces)


def gravity_center(mesh):
    return np.array(
        [
            np.mean(mesh.vertices[:, 0]),
            np.mean(mesh.vertices[:, 1]),
            np.mean(mesh.vertices[:, 2]),
        ]
    )


def gravity_median(mesh):
    return [
        np.median(mesh.vertices[:, 0]),
        np.median(mesh.vertices[:, 1]),
        np.median(mesh.vertices[:, 2]),
    ]


def mesh_surface(mesh):
    mesh.add_attribute("face_area")
    surface = sum(mesh.get_attribute("face_area"))  # type: float
    return surface


def mesh_volume2(mesh):
    volume = 0
    for faces in mesh.faces:
        a = mesh.vertices[faces[0]]
        b = mesh.vertices[faces[1]]
        c = mesh.vertices[faces[2]]
        d = gravity_center(mesh)


def mesh_volume(mesh):
    volume = 0
    for faces in mesh.faces:
        volume += tetrahedron_calc_volume(mesh.vertices[faces[0]], mesh.vertices[faces[1]], mesh.vertices[faces[2]],
                                          gravity_center(mesh))
    return volume


def mesh_volume3(mesh):
    volume = 0
    for faces in mesh.faces:
        volume += tetrahedron_calc_volume(mesh.vertices[faces[0]], mesh.vertices[faces[1]], mesh.vertices[faces[2]],
                                          find_spine_base_center(mesh))
    return volume


def determinant_3x3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
            m[1][0] * (m[0][1] * m[2][2] - m[0][2] * m[2][1]) +
            m[2][0] * (m[0][1] * m[1][2] - m[0][2] * m[1][1]))


def subtract(a, b):
    return (a[0] - b[0],
            a[1] - b[1],
            a[2] - b[2])


def tetrahedron_calc_volume(vertex1, vertex2, vertex3, vertex4):
    return (abs(determinant_3x3((subtract(vertex1, vertex2),
                                 subtract(vertex2, vertex3),
                                 subtract(vertex3, vertex4),
                                 ))) / 6.0)


def calculate_distance(vertex1, vertex2):
    return np.sqrt(
        pow(vertex1[0] - vertex2[0], 2)
        + pow(vertex1[1] - vertex2[1], 2)
        + pow(vertex1[2] - vertex2[2], 2)
    )


def calculate_vector(vertex1, vertex2):
    return np.array(
        [
            vertex1[0] - vertex2[0],
            vertex1[1] - vertex2[1],
            vertex1[2] - vertex2[2],
        ]
    )


def spine_length(mesh):
    spineBaseCenter = find_spine_base_center2(mesh)
    length = []
    for vertice in mesh.vertices:
        length.append(calculate_distance(vertice, spineBaseCenter))

    length = np.array(length)
    length[::-1].sort()
    listOfLengths = range(int(0.05 * np.size(length)))
    return np.mean(length[listOfLengths])


def average_distance(mesh):
    spineBaseCenter = find_spine_base_center2(mesh)
    length = []
    for vertice in mesh.vertices:
        length.append(calculate_distance(vertice, spineBaseCenter))

    length = np.array(length)
    return np.mean(length)


def coefficient_of_variation_in_distance(mesh):
    spineBaseCenter = find_spine_base_center2(mesh)
    length = []
    for vertice in mesh.vertices:
        length.append(calculate_distance(vertice, spineBaseCenter))

    length = np.array(length)
    averageDistance = np.mean(length)
    std = np.std(length)
    return std / averageDistance


def open_angle(mesh):
    spineCenter = gravity_center(mesh)
    spineBaseCenter = find_spine_base_center(mesh)

    openAngle = []

    for vertice in mesh.vertices:
        openAngle.append(calculate_angle(spineCenter, spineBaseCenter, vertice))

    return np.mean(openAngle)


def calculate_angle(point1, point2, point3):
    point1 = np.array(point1)
    point2 = np.array(point2)
    point3 = np.array(point3)

    vector1 = calculate_vector(point1, point2)
    vector2 = calculate_vector(point3, point2)
    return np.arccos(
        np.dot(vector1, vector2)
        / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
    )


def calculate_edges(mesh):
    edgeList = []
    for face in mesh.faces:
        edgeList.append([face[0], face[1]])
        edgeList.append([face[0], face[2]])
        edgeList.append([face[1], face[2]])

    return edgeList


def calculate_hull_volume(mesh):
    hullMesh = pymesh.convex_hull(mesh)
    return mesh_volume(hullMesh)


def calculate_hull_ratio(mesh):
    hullVolume = calculate_hull_volume(mesh)
    meshVolume = mesh_volume(mesh)
    return (hullVolume - meshVolume) / meshVolume


def calculate_gaussian_curvature(mesh):
    mesh.add_attribute('vertex_gaussian_curvature')
    gaussianCurvature = mesh.get_attribute('vertex_gaussian_curvature')
    # remove infinite value
    # gaussianCurvature = gaussianCurvature[gaussianCurvature < 1E308]

    if np.amax(gaussianCurvature) > 1E308:
        print('mesh is not clean')

    meanGaussianCurvature = np.mean(gaussianCurvature)
    varianceGaussianCurvature = np.var(gaussianCurvature)
    sortGaussianCurvature = np.sort(gaussianCurvature)
    lowerGaussianCurvature = np.mean(sortGaussianCurvature[0:round(0.05 * gaussianCurvature.size)])
    higherGaussianCurvature = np.mean(sortGaussianCurvature[round(0.95 * gaussianCurvature.size):gaussianCurvature.size])
    return [meanGaussianCurvature, varianceGaussianCurvature, lowerGaussianCurvature, higherGaussianCurvature]


def calculate_mean_curvature(mesh):
    mesh.add_attribute('vertex_mean_curvature')
    meanCurvatureDivideBySurface = mesh.get_attribute('vertex_mean_curvature')
    # mean curvature in pymesh is divide by vertex voronoi area so we will revert it
    mesh.add_attribute('vertex_voronoi_area')
    # vertexVoronoiArea = mesh.get_attribute('vertex_voronoi_area')

    # meanCurvature = meanCurvatureDivideBySurface/vertexVoronoiArea
    meanCurvature = meanCurvatureDivideBySurface

    # remove nan value
    meanCurvature = meanCurvature[~np.isnan(meanCurvature)]

    meanMeanCurvature = np.mean(meanCurvature)
    varianceMeanCurvature = np.var(meanCurvature)
    sortMeanCurvature = np.sort(meanCurvature)
    lowerMeanCurvature = np.mean(sortMeanCurvature[0:round(0.05 * meanCurvature.size)])
    higherMeanCurvature = np.mean(sortMeanCurvature[round(0.95 * meanCurvature.size):meanCurvature.size])
    return [meanMeanCurvature, varianceMeanCurvature, lowerMeanCurvature, higherMeanCurvature]


def mesh_treatment(mesh):
    vertexConnectivity = calculate_vertex_connectivity(mesh)
    result = np.where(vertexConnectivity == 0)

    meshVertices = mesh.vertices
    for node in result:
        meshVertices = np.delete(meshVertices, node, 0)

    return pymesh.meshio.form_mesh(meshVertices, mesh.faces)


def find_spine_base_center2(mesh):
    listOfNeighbors = np.bincount(mesh.faces.ravel())

    verticesAndNeighbors = np.column_stack((mesh.vertices, np.transpose(listOfNeighbors)))
    lessConnectedVertices = np.where(verticesAndNeighbors[:, 3] <= 3)
    [X, Y, Z] = np.mean(mesh.vertices[lessConnectedVertices], axis=0)
    return [X, Y, Z]


def find_spine_base_center(mesh):
    valence = get_mesh_valence(mesh)
    verticesAndNeighbors = np.column_stack((mesh.vertices, np.transpose(valence)))
    lessConnectedVertices = np.where(verticesAndNeighbors[:, 3] <= 3)
    [X, Y, Z] = np.mean(mesh.vertices[lessConnectedVertices], axis=0)
    return [X, Y, Z]


def get_mesh_valence(mesh):
    mesh.add_attribute("vertex_valance")
    return mesh.get_attribute("vertex_valance")


def find_x_y_z_length(mesh):
    X = np.amax(mesh.vertices[0]) - np.amin(mesh.vertices[0])
    Y = np.amax(mesh.vertices[1]) - np.amin(mesh.vertices[1])
    Z = np.amax(mesh.vertices[2]) - np.amin(mesh.vertices[2])
    return [X, Y, Z]


def calculate_vertex_connectivity(mesh):
    vertexConnectivity = np.array([])

    wire_network = pymesh.wires.WireNetwork.create_from_data(mesh.vertices, mesh.faces)
    for vertex in range(mesh.num_vertices):
        vertexConnectivity = np.append(vertexConnectivity, wire_network.get_vertex_neighbors(vertex).size)
    return vertexConnectivity


def calculate_metrics(mesh):
    spineLength = spine_length(mesh)
    meshSurface = mesh_surface(mesh)
    meshVolume = mesh_volume(mesh)
    hullVolume = calculate_hull_volume(mesh)
    hullRatio = calculate_hull_ratio(mesh)
    meshLength = find_x_y_z_length(mesh)
    averageDistance = average_distance(mesh)
    CVD = coefficient_of_variation_in_distance(mesh)
    OA = open_angle(mesh)
    gaussianCurvature = calculate_gaussian_curvature(mesh)
    meanCurvature = calculate_mean_curvature(mesh)

    metricsFile = open('3DImages/newSpines/spineProperties.txt', 'w')
    metricsFile.write('')

    metricsFile.write(f'Spine Length : {spineLength}\n'
                      f'Mesh surface : {meshSurface}\n'
                      f'Mesh volume : {meshVolume}\n'
                      f'Hull Volume : {hullVolume}\n'
                      f'Hull Ratio : {hullRatio}\n'
                      f'Average distance : {averageDistance}\n'
                      f'Coefficient of variation in distance : {CVD}\n'
                      f'Open angle : {OA}\n'
                      f'Average of mean curvature : {meanCurvature[0]}\n'
                      f'Variance of mean curvature : {meanCurvature[1]}\n'
                      f'Average of gaussian curvature : {gaussianCurvature[0]}\n'
                      f'Variance of gaussian curvature : {gaussianCurvature[1]}\n'
                      f'Average of lower 20 percent mean curvature : {meanCurvature[2]}\n'
                      f'Average of higher 20 percent mean curvature : {meanCurvature[3]}\n'
                      f'Average of lower 20 percent gauss curvature : {gaussianCurvature[2]}\n'
                      f'Average of higher 20 percent gauss curvature : {gaussianCurvature[3]}\n'
                      f'Length X Y Z : {meshLength}\n'
                      f'Gravity center computed with median : {gravity_median(mesh)}\n'
                      f'Gravity center computed with mean : {gravity_center(mesh)}\n')

    metricsFile.close()

    metricsFile2 = open('3DImages/newSpines/spinePropertiesExport.txt', 'w')
    metricsFile2.write('')

    metricsFile2.write(f'{spineLength}\n'
                       f'{meshSurface}\n'
                       f'{meshVolume}\n'
                       f'{hullVolume}\n'
                       f'{hullRatio}\n'
                       f'{averageDistance}\n'
                       f'{CVD}\n'
                       f'{OA}\n'
                       f'{meanCurvature[0]}\n'
                       f'{meanCurvature[1]}\n'
                       f'{gaussianCurvature[0]}\n'
                       f'{gaussianCurvature[1]}\n'
                       f'{meanCurvature[2]}\n'
                       f'{meanCurvature[3]}\n'
                       f'{gaussianCurvature[2]}\n'
                       f'{gaussianCurvature[3]}\n')

    metricsFile2.close()


def compute_metrics():
    """
        Calculate all metrics of all meshes in folder toAnalyse/, put them into a dataframes object
         and save it as metrics.csv in toAnalyse folder
        :return:
    """
    colList = ['Name', 'Length', 'Surface', 'Volume', 'Hull Volume', 'Hull Ratio',
               'Average Distance', 'CVD', 'Open Angle', 'Mean Curvature', 'Variance Curvature',
               'Mean Gaussian', 'Variance Gaussian', 'Highest Curvature', 'Lowest Curvature',
               'Lowest Gaussian', 'Highest Gaussian']
    df = pd.DataFrame(columns=colList)
    for (dirpath, _, filenames) in os.walk("toAnalyse/"):
        for filename in filenames:
            if filename != 'metrics.csv':
                mesh = pymesh.load_mesh(os.path.join(dirpath, filename))
                meanCurvature = calculate_mean_curvature(mesh)
                gaussianCurvature = calculate_gaussian_curvature(mesh)
                df2 = pd.DataFrame([{'Name': str(filename),
                                     'Length': spine_length(mesh),
                                     'Surface': mesh_surface(mesh),
                                     'Volume': mesh_volume(mesh),
                                     'Hull Volume': calculate_hull_volume(mesh),
                                     'Hull Ratio': calculate_hull_ratio(mesh),
                                     'Average Distance': average_distance(mesh),
                                     'CVD': coefficient_of_variation_in_distance(mesh),
                                     'Open Angle': open_angle(mesh),
                                     'Mean Curvature': meanCurvature[0],
                                     'Variance Curvature': meanCurvature[1],
                                     'Mean Gaussian': gaussianCurvature[0],
                                     'Variance Gaussian': gaussianCurvature[1],
                                     'Highest Curvature': meanCurvature[2],
                                     'Lowest Curvature': meanCurvature[3],
                                     'Lowest Gaussian': gaussianCurvature[2],
                                     'Highest Gaussian': gaussianCurvature[3]}])
                df = df.append(df2, ignore_index=True)
    df.to_csv('toAnalyse/metrics.csv')


def neighbor_calc(mesh):
    neighborArray = np.zeros(int(mesh.vertices.size / 3))
    for face in mesh.faces:
        neighborArray[face[0]] = neighborArray[face[0]] + 1
        neighborArray[face[1]] = neighborArray[face[1]] + 1
        neighborArray[face[2]] = neighborArray[face[2]] + 1

    result = np.column_stack((mesh.vertices, np.transpose(neighborArray)))

    plot_3d_scatter_with_color_and_gravity_center_and_gravity_median(result, 'X', 'Y', "Z", 'Spine in pixel',
                                                                     gravity_center(mesh), find_spine_base_center(mesh))
    print(find_spine_base_center(mesh))


def neighbor_calc2(mesh):
    neighborArray = get_mesh_valence(mesh)

    result = np.column_stack((mesh.vertices, np.transpose(neighborArray)))

    plot_3d_scatter_with_color_and_gravity_center_and_gravity_median(result, 'X', 'Y', "Z", 'Spine in pixel',
                                                                     gravity_center(mesh),
                                                                     find_spine_base_center2(mesh))
    plot_frequency(np.transpose(neighborArray), 'frequency', 'neighbor', "node")
    print(find_spine_base_center2(mesh))


def get_frequency2(mesh):
    array = np.zeros(int(mesh.vertices.size / 3))
    for face in mesh.faces:
        array[face[0]] = array[face[0]] + 1
        array[face[1]] = array[face[1]] + 1
        array[face[2]] = array[face[2]] + 1
    unique, counts = np.unique(array, return_counts=True)
    frequencyArray = np.column_stack((unique, counts))
    print(frequencyArray)
    print('\n')


def find_fixed(mesh):
    """
        Find the fixed points of a mesh by finding the less connected vertices
        :param mesh:
        :return:
    """
    edges = calculate_edges(mesh)
    fixed = []
    for edge in edges:
        if np.sum(np.multiply(np.sum(mesh.faces == edge[0], axis=1), np.sum(mesh.faces == edge[1], axis=1))) < 2:
            fixed.append(edge[0])
            fixed.append(edge[1])

    plot_3d_scatter_fixed(mesh.vertices, fixed, 'X', 'Y', "Z", 'Spine in pixel')


def calculate_fixed(mesh):
    """
        Find the fixed points of a mesh by finding the less connected edges
        :param mesh:
        :return:
    """
    edges = calculate_edges(mesh)
    fixed = []
    for edge in edges:
        if np.sum(np.multiply(np.sum(mesh.faces == edge[0], axis=1), np.sum(mesh.faces == edge[1], axis=1))) < 2:
            fixed.append(edge[0])
            fixed.append(edge[1])
    return fixed


def compare_gravity_and_edges(mesh):
    """
        Compare the results of gravity center computed via mass center (mean of all vertices) and mean
        :param mesh: a pymesh mesh object
        :return:
    """
    edges = calculate_edges(mesh)
    fig = plt.figure()
    scatterPlot = fig.add_subplot(111, projection='3d')

    scatterPlot.scatter(mesh.vertices[:, 0], mesh.vertices[:, 1], mesh.vertices[:, 2], alpha=0.75)
    fixed = []
    for edge in edges:
        if np.sum(np.multiply(np.sum(mesh.faces == edge[0], axis=1), np.sum(mesh.faces == edge[1], axis=1))) < 2:
            fixed.append(edge[0])
            fixed.append(edge[1])
            xs = [mesh.vertices[edge[0], 0], mesh.vertices[edge[1], 0]]
            ys = [mesh.vertices[edge[0], 1], mesh.vertices[edge[1], 1]]
            zs = [mesh.vertices[edge[0], 2], mesh.vertices[edge[1], 2]]
            plt.plot(xs, ys, zs, color='red')

    plt.show()


def plot_number_of_nodes(mesh):
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    i = np.linspace(0, mesh.num_vertices, mesh.num_vertices, endpoint=False)
    x = mesh.vertices[:, 0]
    y = mesh.vertices[:, 1]
    z = mesh.vertices[:, 2]
    for w in range(np.shape(x)[0]):
        ax.text(x[w], y[w], z[w], int(i[w]), None)

    ax.set_xlim(np.min(mesh.vertices[:, 0]), np.max(mesh.vertices[:, 0]))
    ax.set_ylim(np.min(mesh.vertices[:, 1]), np.max(mesh.vertices[:, 1]))
    ax.set_zlim(np.min(mesh.vertices[:, 2]), np.max(mesh.vertices[:, 2]))
    plt.show()


def plotly_number_of_nodes(mesh):
    """
        Plot all vertices of a mesh and show them via plotly with blue dots. Plotly is far better than matplotlib
        when you have a lot of points to deal with.
        :param mesh: a pymesh Mesh object
        :return:
    """
    fig = go.Figure()
    i = np.linspace(0, mesh.num_vertices, mesh.num_vertices, endpoint=False)
    fig.add_trace(go.Scatter3d(
        x=mesh.vertices[:, 0],
        y=mesh.vertices[:, 1],
        z=mesh.vertices[:, 2],
        hovertext=i,
        mode='markers',
        # text=i
    ))
    fig.show()


def plotly_number_of_nodes_and_fixed(mesh):
    """
        Plot all vertices of a mesh and show them via plotly with blue dots. Plotly is far better than matplotlib
        when you have a lot of points to deal with. Also calculate "fixed" points by finding less connected vertices
        and show them in red.
        :param mesh: a pymesh Mesh object
        :return:
    """
    fig = go.Figure()
    fixed = np.unique(calculate_fixed(mesh))
    fixedVertices = mesh.vertices[fixed]
    i = np.linspace(0, mesh.num_vertices, mesh.num_vertices, endpoint=False)
    # print(i)
    # w = []
    # for j in i:
    #     print(j)
    #     w.append(int(i[int(j)]))
    fig.add_trace(go.Scatter3d(
        x=mesh.vertices[:, 0],
        y=mesh.vertices[:, 1],
        z=mesh.vertices[:, 2],
        hovertext=i,
        mode='markers',
        # text=i
    ))
    fig.add_trace(go.Scatter3d(
        x=fixedVertices[:, 0],
        y=fixedVertices[:, 1],
        z=fixedVertices[:, 2],
        # hovertext=i,
        mode='markers',
        marker=dict(color='red'),
    ))
    fig.show()


def calculate_PCA():
    """
        Compute PCA analysis with the best 2 dimensions and show the results in 2D with the percentage of information
        in the best two dimensions based on file toAnalyse/metrics.csv
        :return:
    """
    df = pd.read_csv('toAnalyse/metrics.csv')
    features = list(df.columns)[2:]
    x = df.loc[:, features].values
    x = StandardScaler().fit_transform(x)

    pca = PCA(n_components=2)
    principalComponents = pca.fit_transform(x)
    principalDf = pd.DataFrame(data=principalComponents
                               , columns=['principal component 1', 'principal component 2'])
    finalDf = pd.concat([principalDf, df[['Name']]], axis=1)

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel('Principal Component 1', fontsize=15)
    ax.set_ylabel('Principal Component 2', fontsize=15)
    ax.set_title('2 component PCA', fontsize=20)
    targets = df['Name'].values
    viridis = cm.get_cmap('viridis', 12)
    colors = viridis(np.linspace(0, 1, len(targets)))
    for target, color in zip(targets, colors):
        # print(tuple(color))
        indicesToKeep = finalDf['Name'] == target
        ax.scatter(finalDf.loc[indicesToKeep, 'principal component 1'],
                   finalDf.loc[indicesToKeep, 'principal component 2'],
                   c=tuple(color),
                   s=50)
    ax.legend(targets)
    ax.grid()

    plt.title(pca.explained_variance_ratio_)

    plt.show()


def calculate_PCA3D():
    """
        Compute PCA analysis with the best 3 dimensions and show the results in 3D with the percentage of information
        in the best three dimensions based on file toAnalyse/metrics.csv
        :return:
        """
    df = pd.read_csv('toAnalyse/metrics.csv')
    features = list(df.columns)[2:]
    x = df.loc[:, features].values
    x = StandardScaler().fit_transform(x)

    pca = PCA(n_components=3)
    principalComponents = pca.fit_transform(x)
    principalDf = pd.DataFrame(data=principalComponents
                               , columns=['principal component 1', 'principal component 2', 'principal component 3'])
    finalDf = pd.concat([principalDf, df[['Name']]], axis=1)

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('Principal Component 1', fontsize=15)
    ax.set_ylabel('Principal Component 2', fontsize=15)
    ax.set_zlabel('Principal Component 3', fontsize=15)
    ax.set_title('3 component PCA', fontsize=20)
    targets = df['Name'].values
    viridis = cm.get_cmap('viridis', 12)
    colors = viridis(np.linspace(0, 1, len(targets)))
    for target, color in zip(targets, colors):
        indicesToKeep = finalDf['Name'] == target
        ax.scatter(finalDf.loc[indicesToKeep, 'principal component 1'],
                   finalDf.loc[indicesToKeep, 'principal component 2'],
                   finalDf.loc[indicesToKeep, 'principal component 3'],
                   c=tuple(color),
                   s=50)
    ax.legend(targets)
    ax.grid()

    plt.title(f'PCA1 : {round(pca.explained_variance_ratio_[0] * 100, 1)}%, '
              f'PCA2 : {round(pca.explained_variance_ratio_[1] * 100, 1)}%, '
              f'PCA3 : {round(pca.explained_variance_ratio_[2] * 100, 1)}%')

    plt.show()


if __name__ == "__main__":
    # messy exemples of commands
    # filename = askopenfilename()
    # filename = '/mnt/4EB2FF89256EC207/PycharmProjects/Segmentation/Reconstruction/spine255.ply'

    # filename = '/mnt/4EB2FF89256EC207/PycharmProjects/spineReconstruction/optimisedMeshes/' \
    #            'deconvolved_spine_mesh_0_0.stl'

    filename = '/mnt/4EB2FF89256EC207/PycharmProjects/spineReconstruction/optimisedMeshes/' \
               'Slice2_spine6_new_9.0_optimised.stl'

    mesh = pymesh.load_mesh(filename)
    # plotly_number_of_nodes_and_fixed(mesh)
    # compute_metrics()
    # calculate_PCA3D()
    # meshSpine = pymesh.load_mesh(filename)
    # plotly_number_of_nodes_and_fixed(meshSpine)

    # plot_3d_scatter_with_color_and_gravity_center_and_gravity_median(m)
    # neighbor_calc(meshSpine)
    # compare_gravity_and_edges(mesh)
    find_fixed(mesh)
    calculate_fixed(mesh)
    # print(calculate_edges(meshSpine))
    # neighbor_calc(meshSpine)
    # find_spine_base_center(meshSpine)
    # find_spine_base_center(meshSpine)
    # neighbor_calc(meshSpine)
    # neighbor_calc2(meshSpine)
    # calculate_metrics(meshSpine)
    # print(mesh_volume(meshSpine))
    # print(mesh_volume3(meshSpine))
