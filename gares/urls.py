from django.urls import path, re_path
from . import views


urlpatterns = [
	re_path(r'^gares', views.afficher_gares),
]
