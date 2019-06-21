import pymesh

from IO.draw import *


def center_mesh(mesh):
    centeredVertices = np.zeros(shape=(len(mesh.vertices), 3))

    centeredVertices[:, 0] = mesh.vertices[:, 0] - gravity_center(mesh)[0]
    centeredVertices[:, 1] = mesh.vertices[:, 1] - gravity_center(mesh)[1]
    centeredVertices[:, 2] = mesh.vertices[:, 2] - gravity_center(mesh)[2]
    centeredMesh = pymesh.meshio.form_mesh(centeredVertices, mesh.faces)

    return centeredMesh


def gravity_center(mesh):
    gravityCenter = np.array([np.mean(mesh.vertices[:, 0]), np.mean(mesh.vertices[:, 1]), np.mean(mesh.vertices[:, 2])])
    return gravityCenter


def gravity_median(mesh):
    gravityMean = [np.median(mesh.vertices[:, 0]), np.median(mesh.vertices[:, 1]), np.median(mesh.vertices[:, 2])]
    return gravityMean


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
    dist = np.sqrt(pow(vertex1[0]-vertex2[0], 2)+pow(vertex1[1]-vertex2[1], 2)+pow(vertex1[2]-vertex2[2], 2))
    return dist


def calculate_vector(vertex1, vertex2):
    vector = np.array([vertex1[0]-vertex2[0], vertex1[1]-vertex2[1], vertex1[2]-vertex2[2]])
    return vector


def spine_length(mesh):
    spineBaseCenter = find_spine_base_center2(mesh)
    length = []
    for vertice in mesh.vertices:
        length.append(calculate_distance(vertice, spineBaseCenter))

    length = np.array(length)
    length[::-1].sort()
    listOfLengths = range(0, int(0.05*np.size(length)))
    spineLength = np.mean(length[listOfLengths])

    return spineLength


def average_distance(mesh):
    spineBaseCenter = find_spine_base_center2(mesh)
    length = []
    for vertice in mesh.vertices:
        length.append(calculate_distance(vertice, spineBaseCenter))

    length = np.array(length)
    averageDistance = np.mean(length)

    return averageDistance


def coefficient_of_variation_in_distance(mesh):
    spineBaseCenter = find_spine_base_center2(mesh)
    length = []
    for vertice in mesh.vertices:
        length.append(calculate_distance(vertice, spineBaseCenter))

    length = np.array(length)
    averageDistance = np.mean(length)
    std = np.std(length)
    coefficientOfVariationInDistance = std/averageDistance

    return coefficientOfVariationInDistance


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
    angle = np.arccos(np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2)))

    return angle


def calculate_hull_volume(mesh):
    hullMesh = pymesh.convex_hull(mesh)
    hullVolume = mesh_volume(hullMesh)
    return hullVolume


def calculate_hull_ratio(mesh):
    hullVolume = calculate_hull_volume(mesh)
    meshVolume = mesh_volume(mesh)
    CHR = (hullVolume - meshVolume) / meshVolume
    return CHR


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
    lowerGaussianCurvature = np.mean(sortGaussianCurvature[0:round(0.2 * gaussianCurvature.size)])
    higherGaussianCurvature = np.mean(sortGaussianCurvature[round(0.8 * gaussianCurvature.size):gaussianCurvature.size])
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
    lowerMeanCurvature = np.mean(sortMeanCurvature[0:round(0.2 * meanCurvature.size)])
    higherMeanCurvature = np.mean(sortMeanCurvature[round(0.8 * meanCurvature.size):meanCurvature.size])
    return [meanMeanCurvature, varianceMeanCurvature, lowerMeanCurvature, higherMeanCurvature]


def mesh_treatment(mesh):
    # Calculation of node connectivity

    vertexConnectivity = calculate_vertex_connectivity(mesh)
    result = np.where(vertexConnectivity == 0)

    meshVertices = mesh.vertices
    for node in result:
        meshVertices = np.delete(meshVertices, node, 0)

    # firstTreatment = pymesh.meshio.form_mesh(meshVertices, mesh.faces)
    # vertexConnectivity = calculate_vertex_connectivity(firstTreatment)
    # result2 = np.where(vertexConnectivity == 1)

    # meshVertices2 = firstTreatment.vertices

    # for node2 in result2:
    #     meshVertices2 = np.delete(meshVertices2, node2, 0)
    #     #print('ok')

    newMesh = pymesh.meshio.form_mesh(meshVertices, mesh.faces)
    # if calculate_vertex_connectivity(newMesh).any() == 0 or calculate_vertex_connectivity(newMesh).any() == 1:
    #     mesh_treatment(newMesh)
    # else:
    return newMesh


def find_spine_base_center2(mesh):
    listOfNeighbors = np.bincount(mesh.faces.ravel())
    # neighborArray = np.zeros(int(mesh.vertices.size / 3))
    # for face in mesh.faces:
    #     neighborArray[face[0]] += 1
    #     neighborArray[face[1]] += 1
    #     neighborArray[face[2]] += 1

    verticesAndNeighbors = np.column_stack((mesh.vertices, np.transpose(listOfNeighbors)))
    lessConnectedVertices = np.where(verticesAndNeighbors[:, 3] <= 3)
    [X, Y, Z] = np.mean(mesh.vertices[lessConnectedVertices], axis=0)
    spine_base_center = [X, Y, Z]

    return spine_base_center


def find_spine_base_center(mesh):
    valence = get_mesh_valence(mesh)
    verticesAndNeighbors = np.column_stack((mesh.vertices, np.transpose(valence)))
    lessConnectedVertices = np.where(verticesAndNeighbors[:, 3] <= 3)
    [X, Y, Z] = np.mean(mesh.vertices[lessConnectedVertices], axis=0)
    spine_base_center = [X, Y, Z]

    return spine_base_center


def get_mesh_valence(mesh):
    mesh.add_attribute("vertex_valance")
    return mesh.get_attribute("vertex_valance")


def find_x_y_z_length(mesh):
    X = np.amax(mesh.vertices[0])-np.amin(mesh.vertices[0])
    Y = np.amax(mesh.vertices[1])-np.amin(mesh.vertices[1])
    Z = np.amax(mesh.vertices[2])-np.amin(mesh.vertices[2])
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


def neighbor_calc(mesh):
    neighborArray = np.zeros(int(mesh.vertices.size/3))
    for face in mesh.faces:
        neighborArray[face[0]] = neighborArray[face[0]]+1
        neighborArray[face[1]] = neighborArray[face[1]]+1
        neighborArray[face[2]] = neighborArray[face[2]]+1

    result = np.column_stack((mesh.vertices, np.transpose(neighborArray)))

    # plot_3d_scatter_with_color(result, 'X', 'Y', "Z", 'title')
    plot_3d_scatter_with_color_and_gravity_center_and_gravity_median(result, 'X', 'Y', "Z", 'Spine in pixel',
                                                                     gravity_center(mesh), find_spine_base_center(mesh))
    plot_frequency(np.transpose(neighborArray), 'frequency', 'neighbor', "node")
    print(find_spine_base_center(mesh))


def neighbor_calc2(mesh):
    neighborArray = get_mesh_valence(mesh)

    result = np.column_stack((mesh.vertices, np.transpose(neighborArray)))

    # plot_3d_scatter_with_color(result, 'X', 'Y', "Z", 'title')
    plot_3d_scatter_with_color_and_gravity_center_and_gravity_median(result, 'X', 'Y', "Z", 'Spine in pixel',
                                                                     gravity_center(mesh), find_spine_base_center2(mesh))
    plot_frequency(np.transpose(neighborArray), 'frequency', 'neighbor', "node")
    print(find_spine_base_center2(mesh))


def get_frequency2(mesh):
    array = np.zeros(int(mesh.vertices.size/3))
    for face in mesh.faces:
        array[face[0]] = array[face[0]] + 1
        array[face[1]] = array[face[1]] + 1
        array[face[2]] = array[face[2]] + 1
    unique, counts = np.unique(array, return_counts=True)
    frequencyArray = np.column_stack((unique, counts))
    print(frequencyArray)
    print('\n')


if __name__ == "__main__":
    # Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    # filename = askopenfilename()
    filename = '/mnt/4EB2FF89256EC207/PycharmProjects/Segmentation/Reconstruction/spine255.ply'
    # filename = '/mnt/4EB2FF89256EC207/PycharmProjects/3D_projection/cube_simple.ply'
    meshSpine = pymesh.load_mesh(filename)
    # neighbor_calc(meshSpine)
    # find_spine_base_center(meshSpine)
    # find_spine_base_center(meshSpine)
    # neighbor_calc(meshSpine)
    # neighbor_calc2(meshSpine)
    calculate_metrics(meshSpine)
    # print(mesh_volume(meshSpine))
    # print(mesh_volume3(meshSpine))
