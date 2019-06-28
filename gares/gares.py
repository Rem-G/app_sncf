from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from geojson_rewind import rewind
import requests
import json
import geojson
from datetime import datetime, timedelta
import os


class ContexteGares():

	def __init__(self, request):
	    self.request = request
	    self.message_err = list()
	    self.token_auth = 'c644ccc4-01b2-4b7e-863d-4aa700dc7d73'
	    self.main()

	def main(self):
		pass

	def auth_api(self, url):
		#Se connecte à l'API SNCF à partir du token et de l'url passée en paramètre
		headers={'Authorization': self.token_auth}
		response = requests.get(url, headers=headers)
		return response

	def gares_page(self, numero_page):
		#Récupère les gares d'une page
		url = 'https://api.sncf.com/v1/coverage/sncf/stop_areas?start_page={}'.format(numero_page)
		return self.auth_api(url)

	def infos_gares_api(self):
		page_initiale = self.gares_page(0)
		items_per_page = page_initiale.json()['pagination']['items_per_page']
		total_items = page_initiale.json()['pagination']['total_result']

		infos_gares_api = dict()
		infos_gares_api['items_per_page'] = items_per_page
		infos_gares_api['total_items'] = total_items

		return infos_gares_api


	def fichier_gares(self, fichier):#lis le fichier contenant les gares
		items_per_page = self.infos_gares_api()['items_per_page']
		total_items = self.infos_gares_api()['total_items']

		infos_gares = list()

		try:
			with open(fichier, 'r', encoding='utf-8') as json_file:
				infos_gares = json.load(json_file)
				if sum(1 for line in infos_gares) > 0:
					file_is_empty = False
				else:
					file_is_empty = True
		except:
			file_is_empty = True #fichier inexistant

		if file_is_empty is True:
			for numero_page in range((int(total_items/items_per_page))+1):
				print(numero_page)
				page = self.gares_page(numero_page).json()
				for ligne in page:
					for element in page[ligne]:
						if 'name' in element:
							infos_gares.append(element)

			with open(fichier, 'w', encoding='utf-8') as file:
				json.dump(infos_gares, file, indent=3)

		return infos_gares

	def gares(self, fichier):#renvoie toutes les gares du fichier
		infos_gares = self.fichier_gares(fichier)

		dict_gares = dict()
		gare = dict()

		for keys in infos_gares:
			if 'id' in keys:
				gare['id'] = keys['id']
				if 'label' in keys:
					gare['label'] = keys['label']
				if 'insee' in keys:
					gare['insee'] = keys['insee']
				if 'coord' in keys:
					gare['coord'] = keys['coord']
				dict_gares[keys['id']] = gare
				gare = dict()

		return dict_gares
		#dict.values()

	def update_gares_json(self, fichier='gares.json'):
		dict_gares = self.gares(fichier)

		if len(dict_gares) != int(self.infos_gares_api()['total_items']): #fichier à mettre à jour
			self.fichier_gares(fichier.split(".")[0]+"_new.json")
			os.remove(fichier)
			os.rename(fichier.split(".")[0]+"_new.json", fichier)
		return None


	def afficher_gares_contexte(self, fichier='gares.json'):
		infos_gares = self.fichier_gares(fichier)
		return JsonResponse(self.gares(fichier), safe = False)
