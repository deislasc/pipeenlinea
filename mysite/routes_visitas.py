import json
import update
import collections
import datetime
import routes_users
import config


def getVisitas(formData):
	import esquemaReporteVisitas as esquema
	data = {}

	fechaInicio=""
	fechaFin=""

	if "fechaInicio" in formData:
		if formData["fechaInicio"]!="":
			fechaInicio=formData["fechaInicio"]+" 00:00:00"
			if(fechaInicio<"2019-01-02"):
				fechaInicio="2019-01-02 00:00:00"

	if "fechaFin" in formData:
		if formData["fechaFin"]!="":
			fechaFin=formData["fechaFin"]+" 23:59:59"
			if(fechaFin<"2019-01-02"):
				fechaFin="2019-01-02 23:59:59"
		else:
			fechaFin=str(datetime.date.today())+" 23:59:59"
	else:
		fechaFin=str(datetime.date.today())+" 23:59:59"

	if fechaInicio=="":
		fechaInicio=getFirstDayOfMonth(fechaFin)+" 00:00:00"


	nombresMeses=config.mesesNombres[0]
	renglon={}
	renglones=[]
	headers=[]

	esquemaReporte=esquema.esquemaReporteVisitas[0]

	for campo in esquemaReporte:
		headers.append(campo)


	listaVisitas=update.reloadJSONData("working/geolocations.json")
	listaVisitas.pop(0)
	listaVisitas = sorted(listaVisitas, key=lambda k: (k['fecha']))
	listaVisitas = convertirHoraCDMX(listaVisitas,'fecha')
	listaVisitas=list(filter(lambda d:
			( d["fecha"] >= fechaInicio  and d["fecha"] <= fechaFin),
		    listaVisitas))


	for visita in listaVisitas:
		for campo in esquemaReporte:
			renglon[campo]=visita[esquemaReporte[campo]]
		renglones.append(renglon.copy())

	data['listaVisitas']=renglones
	data['user']=routes_users.getUser(formData['ownerID'])
	data['headers']=headers


	return data


def getFirstDayOfMonth(fecha=None):
	fecha=datetime.datetime.strptime(fecha,  "%Y-%m-%d %H:%M:%S").replace(day=1)
	fecha=str(fecha)
	return fecha

def correctVisitasData():
	result={}
	result["message"]="Proceso Finalizado"
	return result

def convertirHoraCDMX(jsonData,field):
	from datetime import datetime, timedelta
	for registro in jsonData:
		dateData=datetime.strptime(registro[field],  "%Y-%m-%d %H:%M:%S")
		dateData = dateData - timedelta(hours=5, minutes=0)
		registro[field]=str(dateData)
	return jsonData



