from django.http import HttpResponse, JsonResponse

from django.shortcuts import render
from geojson_rewind import rewind
import requests
import json
import geojson
from datetime import datetime, timedelta

token_auth = 'c644ccc4-01b2-4b7e-863d-4aa700dc7d73'

def auth_api(url):
	#Se connecte à l'API SNCF à partir du token et de l'url passée en paramètre
	headers={'Authorization': token_auth}
	response = requests.get(url, headers=headers)
	return response

def gares_page(numero_page):
	#Récupère les gares d'une page
	url = 'https://api.sncf.com/v1/coverage/sncf/stop_areas?start_page={}'.format(numero_page)
	return auth_api(url)

def infos_gares_api():
	page_initiale = gares_page(0)
	items_per_page = page_initiale.json()['pagination']['items_per_page']
	total_items = page_initiale.json()['pagination']['total_result']

	infos_gares_api = dict()
	infos_gares_api['items_per_page'] = items_per_page
	infos_gares_api['total_items'] = total_items

	return infos_gares_api


def fichier_gares(fichier):
	items_per_page = infos_gares_api()['items_per_page']
	total_items = infos_gares_api()['total_items']

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
			page = gares_page(numero_page).json()
			for ligne in page:
				for element in page[ligne]:
					if 'name' in element:
						infos_gares.append(element)

		with open(fichier, 'w', encoding='utf-8') as file:
			json.dump(infos_gares, file, indent=3)

	return infos_gares

def maj_json(fichier):
	dict_gares = gares(fichier)
	print(len(dict_gares), int(infos_gares_api()['total_items']))
	print(type(len(dict_gares)), type(int(infos_gares_api()['total_items'])))


	if len(dict_gares) is not int(infos_gares_api()['total_items']): #fichier à mettre à jour
		fichier_gares(fichier.split(".")[0]+"_new.json")
	else:
		print("fichier à jour")


def gares(fichier):
	infos_gares = fichier_gares(fichier)

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

def afficher_gares(request):
	fichier = 'gares.json'
	maj_json(fichier)

	infos_gares = fichier_gares(fichier)
	return JsonResponse(gares(fichier), safe = False)
