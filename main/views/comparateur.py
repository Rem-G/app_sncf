import trainline
import csv
import os

class ContexteComparateur():


	def __init__(self, request):
		self.request = request
		self.gare_depart = str()
		self.gare_arrivee  = str()
		self.message_err_voyage = list()

	def main(self):
		if 'comparer_prix_voyage' in self.request.POST:
			self.gare_conversion_SNCF_trainline()
			return self.prix_voyage()

	def analyse_gare(self, gare, station):
		#Fait le lien entre syntaxe SNCF et syntaxe Trainline
		len_response = 0
		for element in gare:
			if element in station:
				station_analyse = station.split(";")[1:]
				' '.join(station_analyse)
				station_analyse = station_analyse[0]

				if ('-') in station_analyse:
					station_analyse = station_analyse.replace("-", " ").split(" ")
				else:
					station_analyse = station_analyse.split(" ")

				try:
					if element in station_analyse:
						len_response += 1
				except:
					pass

				if len_response == len(gare)-1:
					return station

		return None


	def recherche_gare(self, gare_depart, gare_arrivee):
		try:
			os.chdir("./static/csv/")
		except:
			pass

		if '-' in gare_depart:
			gare_depart = gare_depart.lower().replace("-", " ").split(" ")
		else:
			gare_depart = gare_depart.lower().split(" ")
		if '-' in gare_arrivee:
			gare_arrivee = gare_arrivee.lower().replace('-', ' ').split(" ")
		else:
			gare_arrivee = gare_arrivee.lower().split(" ")

		with open('stations_mini.csv', mode='r') as file:
			file = file.read().split("\n")
			for station in file:
				if self.analyse_gare(gare_depart, station):
					self.gare_depart = self.analyse_gare(gare_depart, station).split(";")[1]

				if self.analyse_gare(gare_arrivee, station):
					self.gare_arrivee = self.analyse_gare(gare_arrivee, station).split(";")[1]


	def gare_conversion_SNCF_trainline(self):
		if 'gare_depart' in self.request.POST and 'gare_arrivee' in self.request.POST:
			self.recherche_gare(self.request.POST['gare_depart'], self.request.POST['gare_arrivee'])


	def prix_voyage(self):
		print(self.request.POST)
		resultats = trainline.search(
			departure_station = self.gare_depart,
			arrival_station = self.gare_arrivee,
			from_date="15/09/2019 08:00",
			to_date="15/09/2019 10:00")


		trajet = dict()
		liste_trajet_prix = list()

		resultats = resultats.csv().split("\n")
		for resultat in resultats:
			resultat = resultat.split(";")
			if resultat != ['']:
				horaire_depart = resultat[0]
				horaire_arrivee = resultat[1]
				temps_trajet = resultat[2]
				prix = resultat[4]
				mode = resultat[6]

				if horaire_depart != 'departure_date' and mode == 'train':
					trajet['horaire'] = horaire_depart
					trajet['prix'] = prix.replace(',', '.')
					liste_trajet_prix.append(trajet)
					trajet = dict()
		return liste_trajet_prix

