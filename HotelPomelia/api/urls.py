from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import EnergyViewSet
# set the web page where we will receive external information in Json format
router = DefaultRouter()
router.register('energy', EnergyViewSet)
# url pages
urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.home, name="home"),
    path('signup/', views.signup, name="signup"),
    path('signin/', views.signin, name="signin"),
    path('signout/', views.signout, name="signout"),
    path('Report-Chart/', views.ReportChart, name="Report-Chart"),
]