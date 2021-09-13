# CarGen - A direct geometry processing cartilage generation method
![teaser](https://user-images.githubusercontent.com/45920627/132516658-57f5c910-2c20-474e-8c66-c60999289787.png)
## About
CarGen (short for Cartilage Generation) is a python code library to generate subject-specific cartilages. Given bone geometry, our approach is agnostic to image modality, creates conforming interfaces, and is well suited for finite element analysis.

## Installation
First, setup your conda environment for jupyter notebooks as below: 
```python
conda create -n cargen
conda activate cargen
conda config --add channels conda-forge
```
Next, install the following packages
```python
conda install igl
conda install meshplot 
conda install ipympl
conda install jupyter
```
Remember to activate your environment upon running the juyter notebook: 
```python
conda activate libisl
jupyter notebook
```
## Tutorials and examples
The pipeline has four main steps as below: 
* **Distance Filtering:** Select an initial subset of the primary bone as the bone-attached cartilage region based on the distance to the secondary bone

![screenshot-2021-09-08-at-16-25](https://user-images.githubusercontent.com/45920627/132528189-51d0c9b1-e168-45bc-8aab-efe00d45f7fc.png)

* **Curvature-Based Region Filling:** Apply our curvature-based region filling approach to ensure the bone-attached cartilage region extends to anatomical lines

![Webp net-resizeimage](https://user-images.githubusercontent.com/45920627/132529071-f1b3270f-b07a-4114-8a22-4bf428ff655d.png)

* **Extrusion:** Extrude a subset of the bone-attached region towards the secondary bone
* **Harmonic Boundary Blending:** Interpolate between the boundary of the extruded and bone-attached regions to create a soft blend

![Webp net-resizeimage-3](https://user-images.githubusercontent.com/45920627/132529700-37954ba0-8079-483b-9c07-dac0f112340f.png)


## Documentation 
Please refer to our published paper at [Computational Biomechanics for Medicine XVI](https://cbm.mech.uwa.edu.au/CBM2021/index.html)
## Citation
```python
soon to be added
```
## Acknowledgement 
This project has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie Sklodowska-Curie grant agreement No. 764644.
This repository only contains the [RAINBOW](https://rainbow.ku.dk) consortium’s views and the Research Executive Agency and the Commission are not responsible for any use that may be made of the information it contains.

![Webp net-resizeimage](https://user-images.githubusercontent.com/45920627/132510734-41c835fc-2502-4461-b3fd-770668d43c9d.jpg)


This project has also received funding from Independent Research Fund Denmark (DFF) under agreement No. 9131-00085B.

![dff_logo_uk_vertical_darkblue](https://user-images.githubusercontent.com/45920627/132513579-49a24905-bc53-43d5-a045-5370a7afc18a.png)
