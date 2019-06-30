from django.urls import path, re_path
from django.conf.urls import url
from .views import views


urlpatterns = [
	url(r'^voyage$', views.voyage, name='voyage'),
	re_path(r'^voyage/gares/update$', views.update_gares)

]
