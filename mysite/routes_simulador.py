import config
import json
import collections
import datetime
from re import sub
from decimal import Decimal
from itertools import groupby
from operator import itemgetter


import numpy



diasFestivos=config.diasFestivos



def getSimulacion(data):
	if "buroCredito" not in data:
		data["buroCredito"]="bueno"

	tipo=data["tipoConvenio"]
	parametros=[]

	costoSeguros=config.costoSeguros
	costoSeguro=costoSeguros[data["seguro"]]

	if("groupFrecuencia" in data):
		if(data["groupFrecuencia"]=="semanal"):
			costoSeguro=costoSeguro/2.0
		if(data["groupFrecuencia"]=="mensual"):
			costoSeguro=costoSeguro*2.0

	if ("montoIngresos" in data):
	    if data["montoIngresos"]=="":
	        data["montoIngresos"]="0"


	if data["buroCredito"]=="bueno":
		parametros=config.parametricosSimuladorBuroBueno[tipo]

	if data["buroCredito"]=="regular":
		parametros=config.parametricosSimuladorBuroRegular[tipo]

	if ("montoIngresos" in data):
		if (int(data["montoIngresos"])>=40000 and
			data["buroCredito"]=="bueno" and
			data["tipoConvenio"]=="internos" and
			int(data["antiguedad"])>=12):
			parametros=config.parametricosSimuladorBuroBueno["directivoInterno"]

	if ("montoIngresos" in data):
		if (int(data["montoIngresos"])>=40000 and
			data["buroCredito"]=="bueno" and
			data["tipoConvenio"]=="externos" and
			int(data["antiguedad"])>=24):
			parametros=config.parametricosSimuladorBuroBueno["directivoExterno"]

	if("montoIngresos" not in data):
		if("tipoConenio" in data and
			data["tipoConvenio"]!="auxiliaresCaabsaEagle" and
			data["tipoConvenio"]!="choferesCaabsaEagle"):
			costoSeguro=0.00


	if("montoIngresos" in data and data["montoIngresos"]=="0"):
		if("tipoConenio" in data and
			data["tipoConvenio"]!="auxiliaresCaabsaEagle" and
			data["tipoConvenio"]!="choferesCaabsaEagle"):
			costoSeguro=0.00

	if ("antiguedad" in data):
		antiguedad=data["antiguedad"]
		rango=0
		parametricos=[]
		for item in parametros:
			if(int(item)<=int(antiguedad)):
				parametricos=parametros[item]

	data.update(parametricos)
	data["costoSeguro"]=costoSeguro
	return data

