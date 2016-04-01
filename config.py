import json,os, http.client, urllib.request, urllib.parse, urllib.error, numpy as np, facebook, datetime
from operator import itemgetter
connection = http.client.HTTPSConnection('api.parse.com', 443, timeout = 5)
connection.connect()

# def restartConnection() :
#     connection.close()
#     connection.connect()