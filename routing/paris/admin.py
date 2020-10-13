from django.contrib import admin
from .models import Vertices, Routes
from leaflet.admin import LeafletGeoAdmin

# Register your models here.
class VerticesAdmin(LeafletGeoAdmin):
    list_display = ("id", "val")

class RoutesAdmin(LeafletGeoAdmin):
    list_display = ("id", "old_id")


admin.site.register(Vertices, VerticesAdmin)
admin.site.register(Routes, RoutesAdmin)