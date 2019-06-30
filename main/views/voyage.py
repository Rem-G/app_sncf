from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from geojson_rewind import rewind
import requests
import json
import geojson
from datetime import datetime, timedelta
import os

from .gares import ContexteGares

class ContexteVoyage():
    

	def __init__(self, request):
		self.request = request
		self.message_err_voyage = list()
		self.token_auth = 'c644ccc4-01b2-4b7e-863d-4aa700dc7d73'
		self.main()
    
	def main(self):
		if 'recherche_voyage' in self.request.POST:
			return self.requete_api()

	def auth_api(self, url):
		#Se connecte à l'API SNCF à partir du token et de l'url passée en paramètre
		headers={'Authorization': self.token_auth}
		response = requests.get(url, headers=headers)
		return response

	def requete_voyage(self):
		voyage = dict()
		voyage['gare_depart'] = str()
		voyage['gare_arrivee'] = str()
		voyage['JMA_depart'] = str()
		voyage['heure_depart'] = str()
		voyage['minutes_depart'] = str()
		voyage['JMA_retour'] = str()
		voyage['heure_retour'] = str()
		voyage['minutes_retour'] = str()

		heure_retour=00
		minutes_retour=00
		JMA_retour = 00000000

		if 'gare_depart' in self.request.POST:
			voyage['gare_depart'] = self.request.POST['gare_depart']

		if 'gare_arrivee' in self.request.POST:
			voyage['gare_arrivee'] = self.request.POST['gare_arrivee']

		if 'date_depart' in self.request.POST:
			date_depart = self.request.POST['date_depart'].split(" ")
			JMA_depart = date_depart[0].replace("/", "")
			heure_depart = date_depart[1].split(":")[0]
			minutes_depart = date_depart[1].split(":")[1]

			voyage['JMA_depart'] = JMA_depart
			voyage['heure_depart'] = heure_depart
			voyage['minutes_depart'] = minutes_depart

		if 'date_retour' in self.request.POST:
			try:
				date_retour = self.request.POST['date_retour'].split(" ")
				JMA_retour = date_retour[0].replace("/", "")
				heure_retour = date_retour[1].split(":")[0]
				minutes_retour = date_retour[1].split(":")[1]
			except:
				self.message_err_voyage.append("Veuillez entrer une date de retour")

			voyage['JMA_retour'] = JMA_retour
			voyage['heure_retour'] = heure_retour
			voyage['minutes_retour'] = minutes_retour

		return voyage

	def requete_gare(self, valeur):
		voyage = self.requete_voyage()
		gares = ContexteGares(self.request).afficher_gares_contexte()

		return gares[voyage[valeur]]['id']

	def requete_api(self):
		#Format datetime YmdTHMS
		voyage = self.requete_voyage()
		gare_depart_id = self.requete_gare('gare_depart')
		gare_arrivee_id = self.requete_gare('gare_arrivee')

		print(self.request.POST)

		datetime = voyage['JMA_depart']+'T'+voyage['heure_depart']+voyage['minutes_depart']+'00'
		print(datetime)

		url = 'https://api.sncf.com/v1/coverage/sncf/journeys?from={}&to={}&datetime={}'.format(gare_depart_id, gare_arrivee_id, datetime)
		response = self.auth_api(url).json()

		for key in response['journeys']:
			print(key['departure_date_time'], key['arrival_date_time'], key['requested_date_time'])

#status fare from links tags nb_transfers arrival_date_time co2_emission to requested_date_time departure_date_time duration type

		return response




