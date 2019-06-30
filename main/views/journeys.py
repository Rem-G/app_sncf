from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from geojson_rewind import rewind
import requests
import json
import geojson
from datetime import datetime, timedelta
import os