import trainline
import csv
import os

class ContexteComparateur():


	def __init__(self, request):
		self.request = request
		self.message_err_voyage = list()

	def main(self):
		if 'comparer_prix_voyage' in self.request.POST:
			return self.prix_voyage()

	def recherche_gare(self, gare):
		try:
			os.chdir("./static/csv/")
		except:
			pass
		gare = gare.lower()

		with open('stations_mini.csv', mode='r') as file:
			print(file.readline())

	def prix_voyage(self):
		resultats = trainline.search(
			departure_station="Lille-europe",
			arrival_station="Paris",
			from_date="15/07/2019 08:00",
			to_date="15/07/2019 17:00")

		#self.recherche_gare("test")

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

