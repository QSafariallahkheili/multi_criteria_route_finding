from django.db import models
from django.contrib.gis.db import models
# Create your models here.

class Vertices(models.Model):
    id = models.FloatField(primary_key=True)
    val = models.IntegerField()
    geom = models.MultiPointField(srid=4326)
    def __unicode__(self):
        return self.val



class Routes(models.Model):
    id = models.FloatField(primary_key=True)
    old_id = models.BigIntegerField()
    sub_id = models.BigIntegerField()
    source = models.FloatField()
    target = models.FloatField()
    dist = models.FloatField()
    geom = models.MultiLineStringField(srid=4326)
    def __unicode__(self):
        return self.old_id

# Auto-generated `LayerMapping` dictionary for Vertices model
vertices_mapping = {
    "id": "id",
    "val": "val",
    "geom": "MULTIPOINT",
}


# Auto-generated `LayerMapping` dictionary for Routes model
routes_mapping = {
    "id": "id",
    "old_id": "old_id",
    "sub_id": "sub_id",
    "source": "source",
    "target": "target",
    "dist": "dist",
    "geom": "MULTILINESTRING",
}
