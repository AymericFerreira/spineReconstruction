A collection of python scripts to extract objects from microscopic images and reconstruct the object in 
3 dimensions. It's also possible to calculate some metrics on the reconstructed objects. 

This project is based mainly on [Pymesh](https://github.com/PyMesh/PyMesh) and 
[Scikit-Image](https://scikit-image.org/).

The project is **still in development** if you need to use a part or all the project and you need help, do not hesitate to contact me ! 


## Installation

PyMesh is the only one who can't be installed through pip. See [Pymesh official install documentation](https://pymesh.readthedocs.io/en/latest/installation.html)
 and [Non-official installation doc (working better)](https://github.com/PyMesh/PyMesh/files/2999684/PyMesh.Installation.on.Ubuntu.18.10.docx).
Others can be installed via pip with the command : *pip install -r requirements.txt*


### Utilisation

You can use it simply with the command *python scriptname.py* if you match with the image files names.
Also, if you are more familiar with python you can import the functions directly in your python project.


## Purpose

The code is divided in 5 steps, from the image obtained after acquisition to the calculation of metrics, and
divided in 5 explicitly named python files.

### Image enhancement
I received microscopic images of a dendrite shaft with some spines. 
First of all the signal is very low, so I enhanced the signal from the neck by using two images, one focused
on the neck and another one focused on the spine head. This method is automatic.

### Segmentation
For the segmentation I used a semi-automatic method based on **Chan-Vese algorithm**. 

`An Active Contour Model without Edges, Tony Chan and Luminita Vese, Scale-Space Theories in Computer Vision, 1999, DOI:10.1007/3-540-48236-9_13)`

Each plans are segmented according to the z-stack.
z-Projection of maximum intensity of the image before segmentation (left) and 
z-Projection of maximum intensity of the image after segmentation (right) : 

![Spine before Segmentation](https://github.com/AymericFerreira/spineReconstruction/blob/master/resultExamples/MAX_spine_9.png)
![Spine after Segmentation](https://github.com/AymericFerreira/spineReconstruction/blob/master/resultExamples/MAX_spine_9_segmentedImage.png)




### Reconstruction
For the reconstruction I used a fully-automatic method based on **Marching-Cubes algorithm**

`
Thomas Lewiner, Helio Lopes, Antonio Wilson Vieira and Geovan Tavares. Efficient implementation of Marching Cubes’
 cases with topological guarantees. Journal of Graphics Tools 8(2) pp. 1-15 (december 2003). DOI:10.1080/10867651.2003.10487582`
![Spine after reconstruction](https://github.com/AymericFerreira/spineReconstruction/blob/master/resultExamples/reconstruction.png)


### Optimisation
After reconstruction the mesh can be noisy and not optimised (isolated vertices, duplicated faces, too long or
too short segments). This script consist of some methods to get the best mesh. I am not aiming at giving a 
good looking mesh (aka smoothing), only to fit well from segmented images.

### Metrics
Some metrics to analyse meshes :

    - Center of the base of the mesh    
    - Gravity center
    - Surface
    - Volume
    - Open angle between the vertices and the normal of length
    - Average distance between the base of the mesh and all vertices
    - Mesh length
    - Gaussian and mean curvature
    - And more ...

![Spine length](https://github.com/AymericFerreira/spineReconstruction/blob/master/resultExamples/spine_length.png)
![Surface](https://github.com/AymericFerreira/spineReconstruction/blob/master/resultExamples/surface.png)
![Volume](https://github.com/AymericFerreira/spineReconstruction/blob/master/resultExamples/volume.png)
![Connectivity](https://github.com/AymericFerreira/spineReconstruction/blob/master/resultExamples/connectivity.png)
![Open angle](https://github.com/AymericFerreira/spineReconstruction/blob/master/resultExamples/open_angle.png)
![Average distance](https://github.com/AymericFerreira/spineReconstruction/blob/master/resultExamples/average_distance.png)
![Gaussian curvature](https://github.com/AymericFerreira/spineReconstruction/blob/master/resultExamples/gauss_curv.png)
![Mean curvature](https://github.com/AymericFerreira/spineReconstruction/blob/master/resultExamples/mean_curv.png)

