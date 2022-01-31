#from django.db import models
from django.contrib.gis.db import models

class testtable(models.Model):
    title = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=50, unique=True)
    location = models.PointField()

    def __str__(self):
        return self.title