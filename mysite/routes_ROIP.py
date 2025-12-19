import routes_users
import routes_empresas
import json
import update
import collections
import datetime
from re import sub
from decimal import Decimal



def getReportesOperacionesInternasPreocupantes(ownerID):
	data={}
	user=routes_users.getUser(ownerID)
	

	listaSolicitudes = update.reloadJSONData("working/roips.json")
	listaSolicitudes.pop(0)
	if user["acl"]!="oficialDeCumplimiento":
		listaSolicitudes = list(filter(lambda d: d["inheritedID"] == user["ownerID"] or d["ownerID"] == user["ownerID"] , listaSolicitudes))
	data["user"]=user
	data["listaSolicitudes"]=listaSolicitudes
	return data	

