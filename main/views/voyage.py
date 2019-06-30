from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from geojson_rewind import rewind
import requests
import json
import geojson
from datetime import datetime, timedelta
import os

class ContexteVoyage():
    
    def __init__(self, request):
        self.request = request
        self.message_err_voyage = list()
        self.main()
    
    def main(self):
        if "recherche_voyage" in self.request.POST:
            print(self.request.POST)
