from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction

from .gares import ContexteGares
from .voyage import ContexteVoyage


@login_required
def update_gares(request):
	contexte_gares = ContexteGares(request)
	if contexte_gares.update_gares_json() is None:
		return HttpResponse("Fichier à jour")
	else:
		return HttpResponse("Fichier ms à jour")

def voyage(request):
	contexte_gares = ContexteGares(request).afficher_gares_contexte()#Obsolète ?
	contexte_voyage = ContexteVoyage(request)
	return render(request, 'main.html', locals())

