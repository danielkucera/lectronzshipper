#!/usr/bin/python3

import requests
import json
import os
import sys

url = "https://lectronz.com/api/v1"

headers = {
        "Authorization": "Bearer "+os.environ.get("LECTRONZ_TOKEN")
        }


#https://mojezasielky.posta.sk/public/manuals/technicke-parametre-epodaci-harok-platne-od-042013.pdf

REGISTERED_LETTER=1
INSURED_LETTER=2
LETTER=30

xml_head = """<EPH verzia="3.0" xmlns="http://ekp.posta.sk/LOGIS/Formulare/Podaj_v03">
	<InfoEPH>
		<Mena>EUR</Mena>
		<TypEPH>2</TypEPH>
		<EPHID>EPH300851978</EPHID>
		<Datum>20221105</Datum>
		<PocetZasielok>2</PocetZasielok>
		<Uhrada>
			<SposobUhrady>6</SposobUhrady>
			<SumaUhrady>9.80</SumaUhrady>
		</Uhrada>
		<DruhZasielky>{{package_type}}</DruhZasielky>
		<SposobSpracovania>3</SposobSpracovania>
		<Odosielatel>
			<OdosielatelID>WEB_EPH</OdosielatelID>
			<Meno>{SENDER_NAME}</Meno>
			<Organizacia>{SENDER_ORG}</Organizacia>
			<Ulica>{SENDER_STREET}</Ulica>
			<Mesto>{SENDER_CITY}</Mesto>
			<PSC>{SENDER_ZIP}</PSC>
			<Krajina>{SENDER_COUNTRY_CODE}</Krajina>
			<Telefon>{SENDER_PHONE}</Telefon>
			<Email>{SENDER_EMAIL}</Email>
		</Odosielatel>
	</InfoEPH>
	<Zasielky>
""".format(**os.environ)

packet_tpl ="""		<Zasielka>
			<Adresat>
				<Meno>{first_name} {last_name}</Meno>
				<Organizacia>{organization}</Organizacia>
				<Ulica>{street}, {street_extension}</Ulica>
				<Mesto>{city}</Mesto>
				<PSC>{postal_code}</PSC>
				<Krajina>{country_code}</Krajina>
				<Telefon>{customer_phone}</Telefon>
				<Email>{customer_email}</Email>
			</Adresat>
			<Info>
				<CiarovyKod></CiarovyKod>
				<Hmotnost>{weight}</Hmotnost>
				<PocetKusov>1</PocetKusov>
				<Poznamka>{order_id}</Poznamka>
				<ObsahZasielky>0</ObsahZasielky>
			</Info>
			<DalsieUdaje>
				<Udaj>
					<Nazov>UloznaLehota</Nazov>
					<Hodnota>7</Hodnota>
				</Udaj>
				<Udaj>
					<Nazov>Obal</Nazov>
					<Hodnota>0</Hodnota>
				</Udaj>
			</DalsieUdaje>
		</Zasielka>
"""

xml_foot = """	</Zasielky>
</EPH>
"""

argt = sys.argv[1]

xml = open("export-"+argt+".xml", "w")

if argt == "1":
    ptype=REGISTERED_LETTER
elif argt == "2":
    ptype=LETTER
else:
    raise Exception("not specified")

if ptype == REGISTERED_LETTER:
    shipping = "Registered"
if ptype == LETTER:
    shipping = "Untracked"

xml.write(xml_head.format(package_type=ptype))

r = requests.get(url+"/orders?limit=1000", headers=headers)

if r.status_code != 200:
    print(r)

for e in r.json()["orders"]:
    if e["status"] in ["payment_success"] and shipping in e["shipping_method"]:
        print(e)
        addr = e["shipping_address"]
        addr["customer_email"] = e["customer_email"]
        addr["customer_phone"] = ""
        addr["order_id"] = e["id"]
        if e["customer_phone"]:
            addr["customer_phone"] = e["customer_phone"]
        addr["weight"] = e["shipping_weight"]["total"]
        xml.write(packet_tpl.format(**addr))

xml.write(xml_foot)

print(xml)


