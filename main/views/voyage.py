from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from geojson_rewind import rewind
import requests
import json
import geojson
from datetime import datetime, timedelta
import time
import os

from .gares import ContexteGares

class ContexteVoyage():
    

	def __init__(self, request):
		self.request = request
		self.message_err_voyage = list()
		self.token_auth = 'c644ccc4-01b2-4b7e-863d-4aa700dc7d73'
		self.run = False
		self.main()
    
	def main(self):
		if 'recherche_voyage' in self.request.POST:
			return self.requete_api()

	def auth_api(self, url):
		"""
			Se connecte à l'API SNCF à partir du token et de l'url passée en paramètre
		"""
		headers={'Authorization': self.token_auth}
		response = requests.get(url, headers=headers)
		return response

	def requete_voyage(self):
		"""
			Récupère les variables à partir du POST
		"""
		voyage = dict()
		voyage['gare_depart'] = str()
		voyage['gare_arrivee'] = str()
		voyage['JMA_depart'] = str()
		voyage['heure_depart'] = str()
		voyage['minutes_depart'] = str()
		voyage['JMA_retour'] = str()
		voyage['heure_retour'] = str()
		voyage['minutes_retour'] = str()
		voyage['date_depart'] = str()
		voyage['date_retour'] = str()

		heure_retour=00
		minutes_retour=00
		JMA_retour = 00000000

		if 'gare_depart' in self.request.POST:
			voyage['gare_depart'] = self.request.POST['gare_depart']
			self.request.session['gare_depart'] = self.request.POST['gare_depart']

		if 'gare_arrivee' in self.request.POST:
			voyage['gare_arrivee'] = self.request.POST['gare_arrivee']
			self.request.session['gare_arrivee'] = self.request.POST['gare_arrivee']

		if 'date_depart' in self.request.POST:
			if self.request.POST['date_depart'] is not '':
				date_depart = self.request.POST['date_depart'].split(" ")
				JMA_depart = date_depart[0].replace("/", "")
				heure_depart = date_depart[1].split(":")[0]
				minutes_depart = date_depart[1].split(":")[1]

				voyage['JMA_depart'] = JMA_depart
				voyage['heure_depart'] = heure_depart
				voyage['minutes_depart'] = minutes_depart

				voyage['date_depart'] = self.request.POST['date_depart']
				self.request.session['date_depart'] = self.request.POST['date_depart']
			else:
				if "Veuillez entrer une date de départ" not in self.message_err_voyage:
					self.message_err_voyage.append("Veuillez entrer une date de départ")

		if 'date_retour' in self.request.POST:
			try:#A supprimer à la mise en place du trajet retour
				date_retour = self.request.POST['date_retour'].split(" ")
				JMA_retour = date_retour[0].replace("/", "")
				heure_retour = date_retour[1].split(":")[0]
				minutes_retour = date_retour[1].split(":")[1]
			except:
				pass

			voyage['JMA_retour'] = JMA_retour
			voyage['heure_retour'] = heure_retour
			voyage['minutes_retour'] = minutes_retour

			voyage['date_retour'] = self.request.POST['date_retour']
			self.request.session['date_retour'] = self.request.POST['date_retour']

		return voyage

	def requete_gare(self, label_gare, AR):
		"""
			Renvoie l'id de la gare passée en paramètre
		"""
		voyage = self.requete_voyage()
		gares = ContexteGares(self.request).infos_gares(fichier='gares.json')

		try:
			return gares[voyage[label_gare]]['id']
		except:
			if AR == 'depart':
				self.message_err_voyage.append("Le nom de gare de départ entré est incorrect")
			elif AR == 'arrivee':
				self.message_err_voyage.append("Le nom de gare d'arrivée entré est incorrect")

	def verif_date(self, datetime_voyage_verif):
		"""
			Vérifie si la date de départ ou de retour n'est pas passée
		"""
		now_JMA = str(datetime.now()).replace("-", "/").split(".")[0]#remplace - par /, supprime les millisecondes -> split(".")

		datetime_voyage_verif = datetime_voyage_verif+":00"#Ajoute les secondes à 0 à l'heure de voyage
		now_JMA = datetime.strptime(now_JMA, "%Y/%m/%d %H:%M:%S")

		date_depart_JMA = datetime.strptime(datetime_voyage_verif, "%Y/%m/%d %H:%M:%S")

		if now_JMA < date_depart_JMA:
			return True
		return False

	def correspondances_journey(self, response_links):
		correspondances = dict()
		liste_correspondances = list()
		limite_nbre_correspondances = 0

		if 'journeys' in response_links:#A remplacer par if 'journeys' in reponse_links	
			for journey in response_links['journeys']:
				if journey['type'] == 'best' or journey['type'] == 'rapid' and limite_nbre_correspondances < 2:
					limite_nbre_correspondances += 1
					sections = journey['sections']

					for section in sections:
						if 'from' in section and 'to' in section:
							section_depart = section['from']
							section_arrivee = section['to']

							if 'stop_point' in section_depart and 'stop_point' in section_arrivee:
								if section_depart['stop_point']['label'] != section_arrivee['stop_point']['label']:
									correspondances['gare_depart_section'] = section_depart['stop_point']['label']
									correspondances['gare_arrivee_section'] = section_arrivee['stop_point']['label']
									correspondances['train'] = section_depart['id'], "train"
									correspondances['depart_section'] = self.conversion_sncf_to_datetime(section['departure_date_time'])
									correspondances['arrivee_section'] = self.conversion_sncf_to_datetime(section['arrival_date_time'])
									correspondances['type'] = journey['type']

									liste_correspondances.append(correspondances)

									correspondances = dict()
		return liste_correspondances

	def links_journey(self, journey):
		url = journey[0]['href']
		response_links = self.auth_api(url).json()

		#print(response_links['links'])

		response_links = self.correspondances_journey(response_links)

		return response_links

	def conversion_sncf_to_datetime(self, horaire):
		horaire = horaire.split("T")
		annee = horaire[0][0:4]
		mois = horaire[0][4:6]
		jour = horaire[0][6:8]

		heure = horaire[1][0:2]
		minutes = horaire[1][2:4]

		return str(annee+"/"+mois+"/"+jour+" "+heure+":"+minutes)

	def convertSeconds(self, seconds):
	    h = seconds//(60*60)
	    m = (seconds-h*60*60)//60
	    s = seconds-(h*60*60)-(m*60)

	    if len(str(h)) <= 1:
	    	h = '0'+str(h)
	    if len(str(m)) <= 1:
	    	m = '0'+str(m)

	    return str(h)+":"+str(m)

	def requete_api(self):
		#Format datetime YmdTHMS
		voyage = self.requete_voyage()
		gare_depart_id = self.requete_gare('gare_depart', 'depart')
		gare_arrivee_id = self.requete_gare('gare_arrivee', 'arrivee')

		#print(self.request.POST)

		datetime_voyage = voyage['JMA_depart']+'T'+voyage['heure_depart']+voyage['minutes_depart']+'00'

		if voyage['date_depart'] is not '':
			if self.verif_date(voyage['date_depart']):
				url = 'https://api.sncf.com/v1/coverage/sncf/journeys?from={}&to={}&datetime={}&datetime_represents=departure&count=7'.format(gare_depart_id, gare_arrivee_id, datetime_voyage)
				response = self.auth_api(url).json()

				if 'journeys' in response:
					for journey in response['journeys']:
						journey['horaire_depart'] = self.conversion_sncf_to_datetime(journey['departure_date_time'])
						journey['horaire_arrivee'] = self.conversion_sncf_to_datetime(journey['arrival_date_time'])
						journey['horaire_param'] = self.conversion_sncf_to_datetime(journey['requested_date_time'])
						journey['temps_trajet'] = self.convertSeconds(journey['durations']['total'])
						if journey['links'] is not [] and journey['nb_transfers'] > 0:
							journey['links'] = self.links_journey(journey['links'])
					return response
			else:
				self.message_err_voyage.append("Date de départ passée")


#status fare from links tags nb_transfers arrival_date_time co2_emission to requested_date_time departure_date_time duration type




