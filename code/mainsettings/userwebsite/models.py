#from django.db import models
from email.policy import strict
from tabnanny import verbose
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Centroid

def load_database():
    import os
    from django.contrib.gis.gdal import DataSource
    from django.contrib.gis.utils import LayerMapping

    map0_path = os.path.join(settings.STATIC_ROOT, 'mapretriever', 'demo', 'map0', '0_out.shp')
    if not os.path.exists(map0_path):
        raise Exception("map0 shapefile couldn't be found! collectstatic has been executed?")

    mappings = {
        'MYFLD' : 'MYFLD', # model_field : shapefile_field
        'poly' : 'MULTIPOLYGON'
    }

    #ds = DataSource(map0_path)
    lm = LayerMapping(Riversides, map0_path, mappings, transform=True)
    lm.save(strict=True, verbose=True)
    


class Riversides(models.Model):
    """
    Represent all the geometries related to rivers and
    the forestation/bare soil at its sides
    """

    MYFLD = models.IntegerField()

    poly = models.MultiPolygonField(geography=False)
    #poly = models.PolygonField(geography=False)

    def __str__(self) -> str:
        return f"centroid: {self.poly.centroid.coords} - {self.MYFLD}" 



class testtable(models.Model):
    title = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=50, unique=True)
    location = models.PointField()

    def __str__(self):
        return self.title