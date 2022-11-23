#importing xmltodict module
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

for e in data["EPH"]["Zasielky"]["Zasielka"]:
    id = e["Info"]["Poznamka"]
    code = e["Info"]["CiarovyKod"]
    url = "https://tandt.posta.sk/en/items/"+code
    if not code.startswith("RE"):
        code = ""
        url = ""
    print(id, code)

    ship={"status":"fulfilled","tracking_code": code, "tracking_url":url }

    print(ship)

    res = requests.put("https://lectronz.com/api/v1/orders/"+str(id), headers=headers, data=ship)

    print(res.status_code)

