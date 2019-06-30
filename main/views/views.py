from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction

from .gares import ContexteGares


@login_required
def update_gares(request):
	contexte_gares = ContexteGares(request)
	if contexte_gares.update_gares_json() is None:
		return HttpResponse("Fichier à jour")
	else:
		return HttpResponse("Fichier ms à jour")


def afficher_gares(request):
	contexte_gares = ContexteGares(request).afficher_gares_contexte()
	return render(request, 'main.html', locals())
