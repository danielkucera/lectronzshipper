#!/usr/bin/python3

import xmltodict
import sys
import json
import requests
import os

f = open(sys.argv[1], "r")

xml_data = f.read()

data = xmltodict.parse(xml_data)

headers = {
        "Authorization": "Bearer "+os.environ.get("LECTRONZ_TOKEN")
        }

zasielky = data["EPH"]["Zasielky"]["Zasielka"]

if not isinstance(zasielky, (list)):
    zasielky = [ zasielky ]

for e in zasielky:
    id = e["Info"]["Poznamka"]
    code = e["Info"].get("CiarovyKod")
    if not code:
        code = ""
    url = "https://tandt.posta.sk/en/items/"+code
    if not code.startswith("RF"):
        code = ""
        url = ""
    print(id, code)

    ship={"status":"fulfilled","tracking_code": code, "tracking_url":url }

    print(ship)

    res = requests.put("https://lectronz.com/api/v1/orders/"+str(id), headers=headers, data=ship)

    print(res.status_code)

