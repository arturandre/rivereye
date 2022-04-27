# RiverEye

(Oliveira, Artur Andre & Casagrande, Luan C. & Soler, Diego Pavan)

Welcome! The RiverEye platform collects and displays riparian forests and vegetation alongside riverbanks, or the lack of them.

Riparian forests are essential for the life and maintanance of rivers. Natural causes and human interference can lead to
deforestation of the riparian zones which in turn affects fish and other organisms living in rivers which eventually can make the river
steril.

Due to the long extents of rivers and water bodies it is unfeasible to manually keep monitoring the riverbanks and properly protect those areas.
Moreover, landowners are required by governments to properly document such Permanent Preservation Areas (PPA) inside their properties, but still,
manually mapping all the PPA area may be cumbersome and prone to errors.

In order to solve the aforementioned shortcomings of the manual mapping process we developed the RiverEye platform. Our solution automatically
collects satellite imagery, analyses those images using State-Of-The-Art Deep Learning networks and provide rapidly the results of the analyses
for users. Furthermore our platform is easy to deploy, maintain and extend, by using Docker images one just need to clone our image from Docker hub and
run it. Using a modular approach the Geographic data, satellite imagery providers and Deep Learning networks can be easily replaced and adapted for
case-specific scenarios.

## Quick demo

[Here](http://rivereye.inacity.org/home) you can access our self-hosted online platform directly!

[![image](https://github.com/arturandre/rivereye/blob/d83f9ec74a0acba7ef4835c7dce4ba66c8b75a6d/documentation/coverpicture.png)](http://rivereye.inacity.org/home)

## How to deploy it?

The easiest way to deploy and run the RiverEye platform is by running our docker image with the commands:
```
docker run -d -it --name rivereye -p 127.0.0.1:8010:8000/tcp -w /root/rivereye/code/mainsettings/ --entrypoint /bin/bash arturandre/rivereye:1.0
docker exec -w /root/rivereye/code/mainsettings/ rivereyecontainer bash ./start-server.sh
```

These commands will clone the RiverEye docker image to the local host and create a container out of it which will be listening to the port `8010` (which may be 
changed depending on the user prefereces). After executing these lines one may access locally the platform using any internet browser at the address:

`http://localhost:8010/home`

Alternatively it is possible to deploy it manually without the use of docker. This requires:

  - downloading this repository via `https://github.com/arturandre/rivereye.git` 
  - Installing the following python packages (we recommend the usage of a conda environment with python 3.8)
    - the installation of [GeoDjango](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/install/geolibs/)
    - the installation of `rasterio` and `osgeo` (preferably using a conda environment)
    - the installation of python packages (via `python -m pip install -r requirements`) at the `code/` directory
  - [Postgres](https://www.postgresql.org/download/) database with the [PostGIS](https://postgis.net/install/) extension.

After installing the required packages and softwares go to the directory `code/mainsetings` (not to be confused with `code/mainsetings/mainsetings` which correspond to the app not the project folder!), and initialize the database with the commands:

```
python manage.py makemigrations
python manage.py migrate
```

After initializing the database the last step is to run the server with the command:

`python manage.py runserver 0:8000`

Notice that the command-line parameter `0:8000` means that (`0`) the server will respond to requests originated by any IP address at the port `8000`. In the local computer where the server is deployed one may access it using any internet browser and going for the address `http://localhost:8000/home` .


## The architecture of the project

We employ the use of a server-client architecture. At the server side a Django based platform take user requests, manages the databases and provides responses for the users' requests. Besides that, scheduled services keep collecting asyncronously, satellite imagery and also keep processing those imagery in order to automatically detect rivers, water bodies, riparian and Permanent Preservation Areas. PPA areas that are violated (e.g. roads, buildings or bare soil near a river) are also detected and highlighted as irregular areas. The detection is performed by Deep Learning Networks fine-tuned with sattelite images annotatted at the pixel level.

![Use case diagram with flow diagram](documentation/Use-cases.drawio.png)

In the following sections we briefly describe the dataset and the deep learning method employed, the full description can be read [here](https://github.com/arturandre/rivereye/blob/66942455d3b3db753d8c9ac24938bedac739207e/documentation/rivereye_dataset_deeplearning.pdf).

### Dataset

The dataset is composed of 96 multispectral sentinel 2 rasters. We have used only Level-2A products since it provides bottom of atmosphere reflectance. Even though 13 spectral bands are available, only bands 2, 3, 4, and 8 (blue, green, red, and NIR) were used. We have selected these bands by their resolution since it might impact the potential of our solution.

Two methodologies were used to compose our dataset: based on Copernicus Priority Area Monitoring product Riparian Zones (RZ Land Cover) [1] and based on our semi-supervised solution for regions covered by the previous product.

RZ Land Cover product provides a consistent and very-high resolution delineation and characterization of the Riparian Zones of major and medium-sized rivers for most of Europe and Turkey (i.e. the 38 EEA member and cooperating countries + UK), based on optical 2.5m spatial resolution satellite imagery from the ESA Data Warehouse [1]. However, the dataset was not externally validated and its reference is 2018. Consequently, a team of specialists visually inspected the polygons aiming to guarantee their accuracy.

The same approach was used for results achieved using the semi-supervised approach. Aiming to guarantee that the dataset was composed properly, each result was visually inspected by a team of specialists before its inclusion in the dataset.

### Deep Learning Network training and deployment pipeline

Our solution can be divided into two parts: The fully automatic and semi-automatic approaches. Even though mapping forest vegetation in riparian zones seems to be a trivial problem, it is important to note that we are proposing a solution that should be capable of mapping forests in any place and under any conditions. That is, the generalization needed is high and, consequently, the process to compose a model/solution capable of achieving good results for it is complex.

The automatic solution was trained using data from multiple biomass and under different conditions. However, it is important to highlight that this solution is prone to errors. That is, free accounts will be able to use such models and achieve results, but our company doesn’t guarantee the output quality. That is an opportunity for users to get used to our platform and better understand its potential.

This fully automatic solution will be used as a basis for our paying users as well, however, a quality assurance team will be part of the process (human in the loop) aiming to guarantee that the result is inside the minimum requirements. In addition, this team has access to a semi-automatic solution that recognizes specific patterns and can help to achieve better results for situations that are not being covered by our fully automatic models.

In addition to being an option to overcome cases where the model is not being able to generalize correctly, such a semi-automatic solution can be used to continuously improve our automatic solution, since it can be used to compose additional data for our datasets.
