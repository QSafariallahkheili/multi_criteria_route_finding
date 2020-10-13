from pathlib import Path
from django.contrib.gis.utils import LayerMapping
from .models import Vertices, Routes

BASE_DIR = Path(__file__).resolve().parent.parent

vertices_mapping = {
    "id": "id",
    "val": "val",
    "geom": "MULTIPOINT",
}

def run(verbose=True):
    lm = LayerMapping(Vertices, "paris/data/paris_routes_noded_vertices_pgr.shp", vertices_mapping, transform=False, encoding="iso-8859-1")
    lm.save(strict=True, verbose=verbose)


routes_mapping = {
    "id": "id",
    "old_id": "old_id",
    "sub_id": "sub_id",
    "source": "source",
    "target": "target",
    "dist": "dist",
    "geom": "MULTILINESTRING",
}

def run(verbose=True):
    lm = LayerMapping(Routes, "paris/data/paris_routes_noded.shp", routes_mapping, transform=False, encoding="iso-8859-1")
    lm.save(strict=True, verbose=verbose)
