# metro_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'stations', views.StationViewSet)
router.register(r'lines', views.MetroLineViewSet)
router.register(r'routes', views.RouteViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]