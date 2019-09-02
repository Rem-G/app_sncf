from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction

from .gares import ContexteGares
from .voyage import ContexteVoyage
from .comparateur import ContexteComparateur

import json

@login_required
def update_gares(request):
	contexte_gares = ContexteGares(request)
	if contexte_gares.update_gares_json() is None:
		return HttpResponse("Fichier à jour")
	else:
		return HttpResponse("Fichier ms à jour")

def voyage(request):
	#contexte_gares = ContexteGares(request).afficher_gares_contexte()#Obsolète ?
	if "comparer_prix_voyage" in request.POST:
		contexte_comparateur = ContexteComparateur(request)
		return render(request, 'comparateur.html', locals())
	else:
		contexte_voyage = ContexteVoyage(request)
		request.session = contexte_voyage.request.session

		if contexte_voyage.message_err_voyage is not []:
			for message_erreur in contexte_voyage.message_err_voyage:
				messages.add_message(request, messages.ERROR, message_erreur)
		#print(dir(contexte_voyage))
		return render(request, 'main.html', locals())