# RiverEye

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

## How to deploy it?

The easiest way to deploy and run the RiverEye platform is by running our docker image with the commands:
```
docker run -d -it --name rivereyecontainer -p 127.0.0.1:8010:8000/tcp -w /root/rivereye/code/mainsettings/ --entrypoint /bin/bash arturandre:rivereye
docker exec -w /root/rivereye/code/mainsettings/ rivereyecontainer bash ./start-server.sh
```

These commands will clone the RiverEye docker image to the local host and create a container out of it which will be listening to the port `8010` (which may be 
changed depending on the user prefereces). After executing these lines one may access locally the platform using any internet browser at the address:

`http://localhost:8010/home`

## The architecture of the project

## Acknowledgements

