from django.contrib import admin
from .models import MetroLine,Station,Connection,Route,RouteStep
# Register your models here.
admin.site.register(MetroLine)
admin.site.register(Station)
admin.site.register(Connection)
admin.site.register(Route)
admin.site.register(RouteStep)