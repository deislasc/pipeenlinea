import routes_users
import routes_empresas
import metas
import config
import json
import update
import collections
import datetime
from re import sub
from decimal import Decimal
from itertools import groupby
from operator import itemgetter
import numpy



diasFestivos=config.diasFestivos
camposNumericos=config.camposNumericos



def getSolicitudById(indice):
	solicitudes = update.reloadJSONData("working/solicitudes.json")
	solicitud=solicitudes[indice]
	return solicitud

def getSolicitudes(ownerID):
	data={}
	user=routes_users.getUser(ownerID)
	listaSolicitudes = update.reloadJSONData("working/solicitudes.json")
	listaSolicitudes.pop(0)
	if user["scope"]=="self":
		listaSolicitudes = list(filter(lambda d: d["inheritedID"] == user["ownerID"] or d["ownerID"] == user["ownerID"] , listaSolicitudes))
		listaSolicitudes = correctSolicitudesForRunTime(listaSolicitudes)
	listaSolicitudes = sorted(listaSolicitudes, key=lambda k: (k['asesorNombre'].lower(),k['fechaContacto']))
	data["user"]=user
	data["listaSolicitudes"]=listaSolicitudes

	return data

def getsolicitudesByFilter(ownerID,field,value):
	data={}
	user=routes_users.getUser(ownerID)
	data["user"]=user

	if field=="":
		return data


	data=getSolicitudes(ownerID)
	listaSolicitudes = data["listaSolicitudes"]
	listaFiltro=[]

	for solicitud in listaSolicitudes:
		if field in solicitud:

			if value!="*" and value!="":
				if field!="clienteNombre":
					if value.lower() in solicitud[field].lower():
						listaFiltro.append(solicitud.copy())

				if field=="clienteNombre":
					nombreCompleto=solicitud["clienteNombre"].strip().lower() + " " + solicitud["clienteApellidoPaterno"].strip().lower() + " " + solicitud["clienteApellidoMaterno"].strip().lower()
					nombreCompleto=nombreCompleto.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ü","u")
					if (value.strip().lower() in solicitud["clienteNombre"].strip().lower() or
						value.strip().lower() in solicitud["clienteApellidoPaterno"].strip().lower() or
						value.strip().lower() in solicitud["clienteApellidoMaterno"].strip().lower() or
						value.strip().lower() in nombreCompleto):
							listaFiltro.append(solicitud.copy())

			if value=="*":
				if solicitud[field]!="":
					listaFiltro.append(solicitud.copy())

			if value=="":
				if solicitud[field]=="":
					listaFiltro.append(solicitud.copy())

	listaFiltro = sorted(listaFiltro, key=lambda k: (k['fechaContacto']))
	listaFiltro=correctSolicitudesForRunTime(listaFiltro)
	data["listaSolicitudes"]=listaFiltro
	return data

def getSolicitudesInProcess(ownerID):
	data={}
	user=routes_users.getUser(ownerID)
	listaSolicitudes = update.reloadJSONData("working/solicitudes.json")
	listaSolicitudes.pop(0)
	if user["scope"]=="self":
		listaSolicitudes = list(filter(lambda d: d["inheritedID"] == user["ownerID"] or d["ownerID"] == user["ownerID"] , listaSolicitudes))

	listaSolicitudes = list(filter(lambda d: d["solicitudEstatus"] != "FONDEADO", listaSolicitudes))
	listaSolicitudes = list(filter(lambda d: d["solicitudEstatus"] != "RECHAZADO", listaSolicitudes))
	#Se ordena por asesorNombre y fecha Contacto
	# listaSolicitudes = sorted(listaSolicitudes, key=lambda k: (k['asesorNombre'].lower(),k['fechaContacto']))
	listaSolicitudes = correctSolicitudesForRunTime(listaSolicitudes)
	listaSolicitudes = sorted(listaSolicitudes, key=lambda k: (k['fechaContacto']))

	listaSolicitudes=formatSolicitudesData(listaSolicitudes)

	data["user"]=user
	data["listaSolicitudes"]=listaSolicitudes
	return data

def getSolicitudesInProcessReport(ownerID):
	data={}
	user=routes_users.getUser(ownerID)
	listaSolicitudes = update.reloadJSONData("working/solicitudes.json")
	listaSolicitudes.pop(0)
	correctSolicitudesForRunTime(listaSolicitudes)
	if user["scope"]=="self":
		listaSolicitudes = list(filter(lambda d: d["inheritedID"] == user["ownerID"] or d["ownerID"] == user["ownerID"] , listaSolicitudes))

	listaSolicitudes = list(filter(lambda d: d["solicitudEstatus"] != "FONDEADO", listaSolicitudes))
	listaSolicitudes = list(filter(lambda d: d["solicitudEstatus"] != "RECHAZADO", listaSolicitudes))
	listaSolicitudes = list(filter(lambda d: d["solicitudEstatus"] != "EN AUTORIZACION DG", listaSolicitudes))
	#Se ordena por estatus,asesorNombre, Empresa, fecha Contacto
	reporte=[]
	import esquemaReporteSolicitudesEnProceso as esquemaReporte
	esquema = esquemaReporte.esquemaSolicitudesEnProceso[0]

	for solicitud in listaSolicitudes:
		registro={}
		fechaReferencia=""
		diasLaboralesTranscurridos=0

		for campo in esquema:
			registro["id"]=solicitud["id"]
			if esquema[campo] in solicitud:
				registro[campo]=solicitud[esquema[campo]]
			if campo=="CLIENTE":
				registro[campo]=solicitud["clienteNombre"]+" "+solicitud["clienteApellidoPaterno"]+" "+solicitud["clienteApellidoMaterno"]
			if campo=="AREA RESPONSABLE":
				registro[campo]=config.estatusOrden[2][solicitud["solicitudEstatus"]]["areaResponsable"]
			if campo=="FECHA REFERENCIA":
				fechaReferencia=config.estatusOrden[2][solicitud["solicitudEstatus"]]["fechaReferencia"]
				registro[campo]=fechaReferencia
			if campo=="FECHA":
				registro[campo]=solicitud[fechaReferencia].split(" ")[0]
			if campo=="DIAS TRANSCURRIDOS":
				fechaActual = str(datetime.date.today())
				fechaInicio=solicitud[fechaReferencia].split(" ")[0]
				# diasLaboralesTranscurridos=numpy.busday_count(fechaInicio,fechaActual,weekmask=[1,1,1,1,1,0,0],holidays=diasFestivos)-1
				diasLaboralesTranscurridos=numpy.busday_count(fechaInicio,fechaActual,weekmask=[1,1,1,1,1,1,1])-1
				if diasLaboralesTranscurridos<0:
					diasLaboralesTranscurridos=0
				registro[campo]=str(diasLaboralesTranscurridos)
				if diasLaboralesTranscurridos>=config.estatusOrden[2][solicitud["solicitudEstatus"]]["diasMax"]:
					registro["bgcolor"]="#FF0000"
					registro["color"]="#FFFF00"
				else:
					registro["bgcolor"]="#FFFFFF"
					registro["color"]="#000000"

			if (solicitud["fechaPropuesta"]=="" and solicitud["fechaVoBo"]=="" and solicitud["fechaPrimerSolicitudVoBo"]!="" and solicitud["solicitudEstatus"]=="ENTREGA A RIESGOS"):
				registro["ESTATUS"] = solicitud["solicitudEstatus"] + " // ESPERA VoBo"
				registro["bgcolor"]="#FFFF00"
				registro["color"]="#000000"


		registro["MONTO SOLICITADO"]='${:0,.2f}'.format(Decimal(sub(r'[^\d.]', '',registro["MONTO SOLICITADO"])))
		registro["#"]=""
		reporte.append(registro.copy())


	reporte = sorted(reporte, key=lambda k: (k['AREA RESPONSABLE'],k['ESTATUS'],k['PRODUCTO'],k['PROMOTOR'],k['EMPRESA'], k['CLIENTE'], k['DIAS TRANSCURRIDOS']))

	# reporte = sorted(reporte, key=lambda k: (k['AREA RESPONSABLE'],k['ESTATUS'],k['PRODUCTO'],k['PROMOTOR'],k['EMPRESA'], k['CLIENTE'],k['DIAS TRANSCURRIDOS'].lower))
	# for registro in reporte:
	# 	print(('\033[32m {:10s} {:18s} {:33s} {:23s} {:35s} {:11s} {:3s} \033[0m').format(
	# 			registro["AREA RESPONSABLE"],
	# 			registro["ESTATUS"],
	# 			registro["PROMOTOR"],
	# 			registro["EMPRESA"],
	# 			registro["CLIENTE"],
	# 			registro["FECHA"],
	# 			registro["DIAS TRANSCURRIDOS"]
	# 		))


	headers=[]
	headers.append("#")
	for campo in esquema:
		if campo!="FECHA REFERENCIA":
			headers.append(campo)


	#Elimino Campos Sensibles
	listaSolicitudes=limpiarDatosSensible(listaSolicitudes)


	data["headers"]=headers
	data["user"]=user
	data["reporte"]=reporte
	data["listaSolicitudes"]=listaSolicitudes
	return data

def getSolicitudesFilteredByEstatus(ownerID,estatus):
	data={}
	user=routes_users.getUser(ownerID)
	listaSolicitudes = update.reloadJSONData("working/solicitudes.json")
	listaSolicitudes.pop(0)
	# Se filtra por scope
	if user["scope"]=="self":
		listaSolicitudes = list(filter(lambda d: d["ownerID"] == user["ownerID"], listaSolicitudes))
	# Se filtra por status
	listaSolicitudes=list(filter(lambda d: d["solicitudEstatus"] == estatus,listaSolicitudes))

	# En el caso de Fondeados y Rechazados se consideran aquellos que su fecha del estatus sea del mes
	fecha=datetime.datetime.now()
	fecha=fecha.strftime("%Y-%m-%d %H:%M:%S")
	inicio=getFirstDayOfMonth(fecha).split(" ")[0]+" 00:00:00"
	if (estatus=="FONDEADO"):
		listaSolicitudes=list(filter(lambda d: d["fechaFondeado"] >= inicio,listaSolicitudes))

	if (estatus=="RECHAZADO"):
		listaSolicitudes=list(filter(lambda d: d["fechaRechazo"] >= inicio,listaSolicitudes))


	#Se ordena por asesorNombre y fecha Contacto
	if config.estatusOrden[0][estatus]==0:
		listaSolicitudes = sorted(listaSolicitudes, key=lambda k: (k['fechaRechazo']))
	if config.estatusOrden[0][estatus]==1:
		listaSolicitudes = sorted(listaSolicitudes, key=lambda k: (k['fechaContacto']))
	if config.estatusOrden[0][estatus]>1:
		listaSolicitudes = sorted(listaSolicitudes, key=lambda k: (k['fechaEntregaARiesgos']))

	listaSolicitudes=correctSolicitudesForRunTime(listaSolicitudes)
	listaSolicitudes=formatSolicitudesData(listaSolicitudes)

	data["user"]=user
	data["listaSolicitudes"]=listaSolicitudes
	return data

def getSolicitudesFilteredByAutorizacionDG(ownerID,estatus):
    data={}
    user=routes_users.getUser(ownerID)
    listaSolicitudes = update.reloadJSONData("working/solicitudes.json")
    listaSolicitudes.pop(0)
    # Se filtra por scope
    if user["scope"]=="self":
    	listaSolicitudes = list(filter(lambda d: d["ownerID"] == user["ownerID"], listaSolicitudes))
    # Se filtra por status
    listaSolicitudes=list(filter(lambda d: d["solicitudEstatus"] == estatus,listaSolicitudes))
    listaSolicitudes=list(filter(lambda d: d["autorizacionDG"] == "Requerida",listaSolicitudes))
    #Se ordena por asesorNombre y fecha Contacto
    listaSolicitudes = sorted(listaSolicitudes, key=lambda k: (k['fechaEntregaARiesgos']))

    listaSolicitudes=correctSolicitudesForRunTime(listaSolicitudes)
    listaSolicitudes=formatSolicitudesData(listaSolicitudes)

    data["user"]=user
    data["listaSolicitudes"]=listaSolicitudes
    return data


def formatSolicitudesData(listaSolicitudes):
	for item in listaSolicitudes:
		for campo in camposNumericos:
			if campo in item and item[campo]!="":
				item[campo]='{:0,.2f}'.format(float(item[campo]))

	return listaSolicitudes

def getPipeLine(formData):

	fechaInicio=""
	fechaFin=""
	fecha=""
	producto=""
	frecuencia="1"

	if "fecha" in formData:
		if formData["fecha"]!="":
			fecha=formData["fecha"]

	if "fechaInicio" in formData:
		if formData["fechaInicio"]!="":
			fechaInicio=formData["fechaInicio"]
			if(fechaInicio<"2019-01-02"):
				fechaInicio="2019-01-02"

	if "fechaFin" in formData:
		if formData["fechaFin"]!="":
			fechaFin=formData["fechaFin"]
			if(fechaFin<"2019-01-02"):
				fechaFin="2019-01-02"

	if "producto" in formData:
		if formData["producto"]!="":
			producto=formData["producto"]

	if "frecuencia" in formData:
		if formData["frecuencia"]!="":
			frecuencia=formData["frecuencia"]

	data={}
	columnas={"PRODUCTO":"PRODUCTO",
	"FECHA":"FECHA",
	"ASESOR":"ASESOR",
	"UNIDAD":"UNIDAD",
	"CONTACTO":"CONTACTADOS",
	"ENTREGA A RIESGOS":"ENTREGADOS A RIESGOS",
	"AUTORIZADO":"AUTORIZADOS",
	"CONTRATO IMPRESO":"CONTRATOS IMPRESOS",
	"FIRMAR CONTRATO":"CONTRATOS FIRMADOS",
	"ENPROCESO":"EN PROCESO",
	"FONDEADO":"FONDEADOS",
	"RECHAZADO":"RECHAZADOS",
	"TOTAL":"TOTAL"
	}
	data["columnas"]=columnas
	user=routes_users.getUser(formData["ownerID"])
	data["user"]=user


	data["pipelines"]=[]

	intervalos={}
	intervalos=getIntervals(fecha,fechaInicio,fechaFin,frecuencia)

	if frecuencia=="3":
		intervalos=getIntervals(fecha,fechaInicio,fechaFin,"1")
		if fechaFin=="":
			fechaFin = str(datetime.date.today())

		fechaActual = fechaFin+" 23:59:59"
		inicioMes=getFirstDayOfMonth(fechaActual).split(" ")[0]
		fechaActual = fechaFin
		diasLaboralesTranscurridos=numpy.busday_count(inicioMes,fechaActual,weekmask=[1,1,1,1,1,0,0],holidays=diasFestivos)
		# Calculo el intervalo para el mes inmediato anterior
		for intervalo in intervalos:
			inicioMesAnterior=intervalo["inicio"].split(" ")[0]
			finMesAnterior=intervalo["fin"].split(" ")[0]
			nthdiaLaboralMesAnterior=numpy.busday_offset(inicioMesAnterior, diasLaboralesTranscurridos, roll='forward')
			if(str(nthdiaLaboralMesAnterior)<finMesAnterior):
				intervalo["fin"]=str(nthdiaLaboralMesAnterior)+" 23:59:59"

	for intervalo in intervalos:
		if frecuencia=="1":
			data["pipelines"].append(getPipeLineOfDate(fecha,intervalo["inicio"],intervalo["fin"],producto).copy())
		else:
			fin=intervalo["fin"].split(" ")[0]
			if numpy.is_busday(fin,weekmask=[1,1,1,1,1,0,0],holidays=diasFestivos):
				data["pipelines"].append(getStoryOfDate(fecha,intervalo["inicio"],intervalo["fin"],producto).copy())



	return data


def getScoreCard(formData):

	fechaInicio=""
	fechaFin=""
	fecha=""
	producto=""
	frecuencia="3"


	if "fecha" in formData:
		if formData["fecha"]!="":
			fecha=formData["fecha"]

	if "fechaInicio" in formData:
		if formData["fechaInicio"]!="":
			fechaInicio=formData["fechaInicio"]
			if(fechaInicio<"2019-01-02"):
				fechaInicio="2019-01-02"

	if "fechaFin" in formData:
		if formData["fechaFin"]!="":
			fechaFin=formData["fechaFin"]
			if(fechaFin<"2019-01-02"):
				fechaFin="2019-01-02"

	if "producto" in formData:
		if formData["producto"]!="":
			producto=formData["producto"]

	if "frecuencia" in formData:
		if formData["frecuencia"]!="":
			frecuencia=formData["frecuencia"]

	data={}
	user=routes_users.getUser(formData["ownerID"])
	data["user"]=user


	data["scorecards"]=[]
	intervalos={}
	intervalos=getIntervals(fecha,fechaInicio,fechaFin,frecuencia)

	if frecuencia=="3":
		intervalos=getIntervals(fecha,fechaInicio,fechaFin,"1")
		if fechaFin=="":
			fechaFin = str(datetime.date.today())

		fechaActual = fechaFin+" 23:59:59"
		inicioMes=getFirstDayOfMonth(fechaActual).split(" ")[0]
		fechaActual = fechaFin
		diasLaboralesTranscurridos=numpy.busday_count(inicioMes,fechaActual,weekmask=[1,1,1,1,1,0,0],holidays=diasFestivos)
		# Calculo el intervalo para el mes inmediato anterior
		for intervalo in intervalos:
			inicioMesAnterior=intervalo["inicio"].split(" ")[0]
			finMesAnterior=intervalo["fin"].split(" ")[0]
			nthdiaLaboralMesAnterior=numpy.busday_offset(inicioMesAnterior, diasLaboralesTranscurridos, roll='forward')
			if(str(nthdiaLaboralMesAnterior)<finMesAnterior):
				intervalo["fin"]=str(nthdiaLaboralMesAnterior)+" 23:59:59"


	for intervalo in intervalos:
			fin=intervalo["fin"].split(" ")[0]
			if frecuencia=="2":
				if numpy.is_busday(fin,weekmask=[1,1,1,1,1,0,0],holidays=diasFestivos):
					diaLaboralAnterior=getBeforeWorkDate(intervalo["fin"])
					if numpy.is_busday(diaLaboralAnterior.split(" ")[0],weekmask=[1,1,1,1,1,0,0],holidays=diasFestivos):
						data["scorecards"].append(getScoreCardOfDate(fecha,intervalo["inicio"],intervalo["fin"],producto,diaLaboralAnterior).copy())
			else:
				diaLaboralAnterior=getBeforeWorkDate(intervalo["fin"])
				data["scorecards"].append(getScoreCardOfDate(fecha,intervalo["inicio"],intervalo["fin"],producto,diaLaboralAnterior).copy())

	return data

def getPipeLineOfDate(fecha=None,inicio=None,fin=None,productoFiltro=None):
	data={}

	if fecha < inicio:
		data["feedback"]="La fecha de referencia no puede ser menor al inicio del intervalo."
		data["code"]="400"

	if fecha==None or fecha=="":
		dFecha=datetime.datetime.now()
		fecha=dFecha.strftime("%Y-%m-%d %H:%M:%S")
	else:
		fecha=fecha+" 00:00:00"

	listaSolicitudesOriginal = update.reloadJSONData("working/solicitudes.json")
	listaSolicitudesOriginal.pop(0)

	# OBTENGO SEGUROS ASOCIADOS
	seguros={}
	seguros=obtenerSegurosdeSolicitudes()
	for seguro in seguros:
		listaSolicitudesOriginal.append(seguro.copy())

	correctSolicitudesForRunTime(listaSolicitudesOriginal)

	# OBTENGO CONTACTADOS
	listaTemp={}
	if (fecha>=inicio  and fecha<= fin):
		listaTemp=list(filter(lambda d:
			(d["solicitudEstatus"] == "CONTACTO"  and d["fechaContacto"] >= inicio  and d["fechaContacto"] <= fin) or
		    (d["solicitudEstatus"] == "CONTACTO"  and d["fechaContacto"] < inicio),
		    listaSolicitudesOriginal))

	else:
			listaTemp=list(filter(lambda d: d["solicitudEstatus"]!="" and(
				(d["solicitudEstatus"] != "RECHAZADO" and d["fechaContacto"] <= fin and d["fechaEntregaARiesgos"] == "") or
		    	(d["solicitudEstatus"] != "RECHAZADO" and d["fechaContacto"] <= fin and d["fechaEntregaARiesgos"] > fin)
		    	), listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="CONTACTO"
		item["montoSolicitado"]=item["montoSolicitado"]
	listaSolicitudes=listaTemp

	# OBTENGO ENTREGADOS A RIESGOS
	listaTemp={}
	if (fecha>=inicio  and fecha<= fin):
		listaTemp=list(filter(lambda d:
			(d["solicitudEstatus"] == "ENTREGA A RIESGOS"  and d["fechaEntregaARiesgos"] >= inicio  and d["fechaEntregaARiesgos"] <= fin) or
		    (d["solicitudEstatus"] == "ENTREGA A RIESGOS"  and d["fechaEntregaARiesgos"] < inicio),
		    listaSolicitudesOriginal))
	else:
		listaTemp=list(filter(lambda d: d["fechaEntregaARiesgos"] != "" and (
		    (d["solicitudEstatus"] != "RECHAZADO" and d["fechaEntregaARiesgos"] <= fin and d["fechaPropuesta"] == "") or
		    (d["solicitudEstatus"] != "RECHAZADO" and d["fechaEntregaARiesgos"] <= fin and d["fechaPropuesta"] > fin)
		    ),listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="ENTREGA A RIESGOS"
		item["montoSolicitado"]=item["montoSolicitado"]
	listaSolicitudes=listaSolicitudes+listaTemp

	# OBTENGO AUTORIZADOS
	listaTemp={}
	listaTemp=list(filter(lambda d:
		d["solicitudEstatus"] == "AUTORIZADO" and
		d["fechaPropuesta"] >= inicio and
		d["fechaPropuesta"] <= fin,
		listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="AUTORIZADO"
		if(item["producto"]!="Seguro"):
			item["montoSolicitado"]=item["montoAutorizado"]
	listaSolicitudes=listaSolicitudes+listaTemp

	# CONTRATOS IMPRESOS
	listaTemp={}
	listaTemp=list(filter(lambda d:
		d["solicitudEstatus"] == "CONTRATO IMPRESO" and
		d["fechaContratoImpreso"] >= inicio and
		d["fechaContratoImpreso"] <= fin,
		listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="CONTRATO IMPRESO"
		if(item["producto"]!="Seguro"):
			item["montoSolicitado"]=item["montoAutorizado"]
	listaSolicitudes=listaSolicitudes+listaTemp

	# CONTRATOS FIRMADOS
	listaTemp={}
	listaTemp=list(filter(lambda d:
		d["solicitudEstatus"] == "FIRMAR CONTRATO" and
		d["fechaContratoImpreso"] >= inicio and
		d["fechaContratoImpreso"] <= fin,
		listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="FIRMAR CONTRATO"
		if(item["producto"]!="Seguro"):
			item["montoSolicitado"]=item["montoAutorizado"]
	listaSolicitudes=listaSolicitudes+listaTemp

	# FONDEADOS
	listaTemp={}
	listaTemp=list(filter(lambda d:
		d["solicitudEstatus"] == "FONDEADO" and
		d["fechaContratoImpreso"] >= inicio and
		d["fechaContratoImpreso"] <= fin,
		listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="FONDEADO"
		if(item["producto"]!="Seguro"):
			item["montoSolicitado"]=item["montoAutorizado"]
	listaSolicitudes=listaSolicitudes+listaTemp

	# RECHAZADOS
	listaTemp={}
	listaTemp=list(filter(lambda d:
		d["solicitudEstatus"] == "RECHAZADO" and
		d["fechaRechazo"] >= inicio and
		d["fechaRechazo"] <= fin,
		listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="RECHAZADO"
		if(item["montoAutorizado"]==""):
			item["montoSolicitado"]=item["montoSolicitado"]
		else:
			if(item["producto"]!="Seguro"):
				item["montoSolicitado"]=item["montoAutorizado"]
	listaSolicitudes=listaSolicitudes+listaTemp

	#Elimino Campos Sensibles
	listaSolicitudes=limpiarDatosSensible(listaSolicitudes)

	#Obtengo listado de Productos
	productos = collections.defaultdict(list)
	for item in listaSolicitudesOriginal:
		if(productoFiltro!=""):
			if(item['producto']==productoFiltro):
				productos[item['producto']].append(item)
		else:
			productos[item['producto']].append(item)


    #Obtengo listado de Asesores
	asesores = collections.defaultdict(list)
	for item in listaSolicitudes:
		if item['inheritedID']=="" or item['inheritedID']==item['ownerID']:
			nombreAsesorOrigen=routes_users.getUser(item['ownerID'])['name']
			item['ownerID']=nombreAsesorOrigen
			item['inheritedID']=nombreAsesorOrigen
			asesores[item['asesorNombre']].append(item)
		if (item['inheritedID']!=item['ownerID'] and item['inheritedID']!=""):
			item['asesorNombre']="Otros"
			item['ownerID']=routes_users.getUser(item['ownerID'])['name']
			item['inheritedID']=routes_users.getUser(item['inheritedID'])['name']
			asesores["Otros"].append(item)

	asesores=sorted(asesores)


	#Obtengo listado de estados
	estados = collections.defaultdict(list)
	for item in listaSolicitudesOriginal:
		estados[item['solicitudEstatus']].append(item)

	if productoFiltro!="":
		listaSolicitudes=list(filter(lambda d: d["producto"] == productoFiltro,listaSolicitudes))

	pipeline={}
	solicitudesData=[]
	groupedByStatus = collections.defaultdict(list)
	for producto in productos:
		pipeline[producto]={}
		for asesor in asesores:
			pipeline[producto][asesor]={}
			for estado in estados:
				pipeline[producto][asesor][estado]={}
				pipeline[producto][asesor][estado]["numero"]=0
				pipeline[producto][asesor][estado]["montoSolicitado"]='${:0,.2f}'.format(0)

				pipeline[producto][asesor]["ENPROCESO"]={}
				pipeline[producto][asesor]["ENPROCESO"]["numero"]=0
				pipeline[producto][asesor]["ENPROCESO"]["montoSolicitado"]='${:0,.2f}'.format(0)

				pipeline[producto][asesor]["TOTAL"]={}
				pipeline[producto][asesor]["TOTAL"]["numero"]=0
				pipeline[producto][asesor]["TOTAL"]["montoSolicitado"]='${:0,.2f}'.format(0)

				solicitudes = []
				for item in listaSolicitudes:
					if(item["producto"]==producto):
						if(item["asesorNombre"]==asesor):
							if(item["estatusPipeLine"]==estado):
								solicitudes.append(item)
								pipeline[producto][asesor][estado]["numero"]=0
								pipeline[producto][asesor][estado]["montoSolicitado"]='{:0,.2f}'.format(0)
								pipeline[producto][asesor][estado]["numero"]=len(solicitudes)
								monto=sum(Decimal(sub(r'[^\d.]', '',item['montoSolicitado'])) for item in solicitudes)
								# monto=sum(float(item['montoSolicitado']) for item in solicitudes)
								pipeline[producto][asesor][estado]["montoSolicitado"]='${:0,.2f}'.format(monto)
								pipeline[producto][asesor][estado]["solicitudes"]=solicitudes

			#Selecciono las solicitudes en Proceso por Asesor
			enProceso = list(filter(lambda d: d["estatusPipeLine"] != "FONDEADO"  and
				d["asesorNombre"] == asesor and
				d["producto"] == producto, listaSolicitudes))
			enProceso = list(filter(lambda d: d["estatusPipeLine"] != "RECHAZADO" and
				d["asesorNombre"] == asesor and
				d["producto"] == producto, enProceso))
			pipeline[producto][asesor]["ENPROCESO"]["numero"]=len(enProceso)
			monto=sum(Decimal(sub(r'[^\d.]', '',item['montoSolicitado'])) for item in enProceso)
			# monto=sum(float(item['montoSolicitado']) for item in enProceso)
			pipeline[producto][asesor]["ENPROCESO"]["montoSolicitado"]='${:0,.2f}'.format(monto)
			pipeline[producto][asesor]["ENPROCESO"]["solicitudes"]=enProceso


            #Selecciona las solicitudes para Calcular el Total por Asesor
			enTotal = list(filter(lambda d: d["estatusPipeLine"] != "RECHAZADO"  and
				d["asesorNombre"] == asesor and
				d["producto"] == producto, listaSolicitudes))
			pipeline[producto][asesor]["TOTAL"]["numero"]=len(enTotal)
			monto=sum(Decimal(sub(r'[^\d.]', '',item['montoSolicitado'])) for item in enTotal)
			# monto=sum(float(item['montoSolicitado']) for item in enTotal)
			pipeline[producto][asesor]["TOTAL"]["montoSolicitado"]='${:0,.2f}'.format(monto)

		#SELECCIONA LAS SOLICITUDES PARA CALCULAR LOS TOTALES POR PRODUCTO
		pipeline[producto]["TOTAL"]={}
		for estado in estados:
			pipeline[producto]["TOTAL"][estado]={}
			pipeline[producto]["TOTAL"][estado]["numero"]=0
			pipeline[producto]["TOTAL"][estado]["montoSolicitado"]='${:0,.2f}'.format(0)
			solicitudes = []
			for item in listaSolicitudes:
				if(item["producto"]==producto):
					if(item["estatusPipeLine"]==estado):
						solicitudes.append(item)
						pipeline[producto]["TOTAL"][estado]["numero"]=len(solicitudes)
						monto=sum(Decimal(sub(r'[^\d.]', '',item['montoSolicitado'])) for item in solicitudes)
						# monto=sum(float(item['montoSolicitado']) for item in solicitudes)
						pipeline[producto]["TOTAL"][estado]["montoSolicitado"]='${:0,.2f}'.format(monto)

					pipeline[producto]["TOTAL"]["TOTAL"]={}
					pipeline[producto]["TOTAL"]["TOTAL"]["numero"]=0
					pipeline[producto]["TOTAL"]["TOTAL"]["montoSolicitado"]='${:0,.2f}'.format(0)
					totalSolicitudes = list(filter(lambda d: d["producto"] == producto,listaSolicitudes))
					totalSolicitudes = list(filter(lambda d: d["estatusPipeLine"] != "RECHAZADO",totalSolicitudes))
					monto=sum(Decimal(sub(r'[^\d.]', '',item['montoSolicitado'])) for item in totalSolicitudes)
					# monto=sum(float(item['montoSolicitado']) for item in totalSolicitudes)
					pipeline[producto]["TOTAL"]["TOTAL"]["montoSolicitado"]='${:0,.2f}'.format(monto)
					pipeline[producto]["TOTAL"]["TOTAL"]["numero"]=len(totalSolicitudes)

					pipeline[producto]["TOTAL"]["ENPROCESO"]={}
					pipeline[producto]["TOTAL"]["ENPROCESO"]["numero"]=0
					pipeline[producto]["TOTAL"]["ENPROCESO"]["montoSolicitado"]='${:0,.2f}'.format(0)
					totalSolicitudes = list(filter(lambda d: d["estatusPipeLine"] != "FONDEADO",totalSolicitudes))
					monto=sum(Decimal(sub(r'[^\d.]', '',item['montoSolicitado'])) for item in totalSolicitudes)
					# monto=sum(float(item['montoSolicitado']) for item in totalSolicitudes)
					pipeline[producto]["TOTAL"]["ENPROCESO"]["montoSolicitado"]='${:0,.2f}'.format(monto)
					pipeline[producto]["TOTAL"]["ENPROCESO"]["numero"]=len(totalSolicitudes)



	if productoFiltro=="":
		data["productos"]={}
		if "Nómina" in pipeline:
			data["productos"]["Nómina"]=pipeline["Nómina"]
		if "Adelanto de Nómina" in pipeline:
			data["productos"]["Adelanto de Nómina"]=pipeline["Adelanto de Nómina"]
		if "Vehículo" in pipeline:
			data["productos"]["Vehículos"]=pipeline["Vehículos"]
		if "Seguro" in pipeline and fin>'2020-09-01 00:00:00':
			data["productos"]["Seguro"]=pipeline["Seguro"]
		if "Seguro Independiente" in pipeline and fin>'2020-09-01 00:00:00':
			data["productos"]["Seguro Independiente"]=pipeline["Seguro Independiente"]

	else:
		data["productos"]=pipeline #Envia los resultados sin ordenar


	data["fecha"]=fin.split(" ")[0]
	anioMes=data["fecha"].split("-")
	data["fecha"]=anioMes[0]+"-"+anioMes[1]
	data["code"]="200"



	return data

def getStoryOfDate(fecha=None,inicio=None,fin=None,productoFiltro=None):
	data={}


	if fecha < inicio:
		data["feedback"]="La fecha de referencia no puede ser menor al inicio del intervalo."
		data["code"]="400"

	if fecha==None or fecha=="":
		dFecha=datetime.datetime.now()
		fecha=dFecha.strftime("%Y-%m-%d %H:%M:%S")

	listaSolicitudesOriginal = update.reloadJSONData("working/solicitudes.json")
	listaSolicitudesOriginal.pop(0)

	# OBTENGO SEGUROS ASOCIADOS
	seguros={}
	seguros=obtenerSegurosdeSolicitudes()
	for seguro in seguros:
		listaSolicitudesOriginal.append(seguro.copy())

	# ELIMINO FECHAS POSTERIORES Y RECALCULO EL ESTATUS DE CADA SOLICITUD
	for idx, item in enumerate(listaSolicitudesOriginal):
		listaSolicitudesOriginal[idx]=aplicarRegresion(item,fin)

	# OBTENGO CONTACTADOS
	listaTemp={}
	listaSolicitudes={}
	if (fecha>=inicio  and fecha<= fin):
		listaTemp=list(filter(lambda d:
			(d["solicitudEstatus"] == "CONTACTO"  and d["fechaContacto"] >= inicio  and d["fechaContacto"] <= fin) or
		    (d["solicitudEstatus"] == "CONTACTO"  and d["fechaContacto"] < inicio),
		    listaSolicitudesOriginal))

	else:
			listaTemp=list(filter(lambda d: d["solicitudEstatus"]!="" and(
				(d["solicitudEstatus"] != "RECHAZADO" and d["fechaContacto"] <= fin and d["fechaEntregaARiesgos"] == "") or
		    	(d["solicitudEstatus"] != "RECHAZADO" and d["fechaContacto"] <= fin and d["fechaEntregaARiesgos"] > fin)
		    	),listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="CONTACTO"
	listaSolicitudes=listaTemp


	# OBTENGO ENTREGADOS A RIESGOS
	listaTemp={}
	if (fecha>=inicio  and fecha<= fin):
		listaTemp=list(filter(lambda d:
			(d["solicitudEstatus"] == "ENTREGA A RIESGOS"  and d["fechaEntregaARiesgos"] >= inicio  and d["fechaEntregaARiesgos"] <= fin) or
		    (d["solicitudEstatus"] == "ENTREGA A RIESGOS"  and d["fechaEntregaARiesgos"] < inicio),
		    listaSolicitudesOriginal))
	else:
		listaTemp=list(filter(lambda d: d["fechaEntregaARiesgos"] != "" and(
		    (d["solicitudEstatus"] != "RECHAZADO" and d["fechaEntregaARiesgos"] <= fin and d["fechaPropuesta"] == "") or
		    (d["solicitudEstatus"] != "RECHAZADO" and d["fechaEntregaARiesgos"] <= fin and d["fechaPropuesta"] > fin)
		    ),listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="ENTREGA A RIESGOS"
	listaSolicitudes=listaSolicitudes+listaTemp




	# OBTENGO AUTORIZADOS
	listaTemp={}
	listaTemp=list(filter(lambda d:
		d["solicitudEstatus"] == "AUTORIZADO" and
		d["fechaPropuesta"] >= inicio and
		d["fechaPropuesta"] <= fin,
		listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="AUTORIZADO"
	listaSolicitudes=listaSolicitudes+listaTemp

	# CONTRATOS IMPRESOS
	listaTemp={}
	listaTemp=list(filter(lambda d:
		d["solicitudEstatus"] == "CONTRATO IMPRESO" and
		d["fechaContratoImpreso"] >= inicio and
		d["fechaContratoImpreso"] <= fin,
		listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="CONTRATO IMPRESO"
	listaSolicitudes=listaSolicitudes+listaTemp

	# CONTRATOS FIRMADOS
	listaTemp={}
	listaTemp=list(filter(lambda d:
		d["solicitudEstatus"] == "FIRMAR CONTRATO" and
		d["fechaContratoImpreso"] >= inicio and
		d["fechaContratoImpreso"] <= fin,
		listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="FIRMAR CONTRATO"
	listaSolicitudes=listaSolicitudes+listaTemp

	# FONDEADOS
	listaTemp={}
	listaTemp=list(filter(lambda d:
		d["solicitudEstatus"] == "FONDEADO" and
		d["fechaContratoImpreso"] >= inicio and
		d["fechaContratoImpreso"] <= fin,
		listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="FONDEADO"
	listaSolicitudes=listaSolicitudes+listaTemp

	# RECHAZADOS
	listaTemp={}
	listaTemp=list(filter(lambda d:
		d["solicitudEstatus"] == "RECHAZADO" and
		d["fechaRechazo"] >= inicio and
		d["fechaRechazo"] <= fin,
		listaSolicitudesOriginal))

	for item in listaTemp:
		item["estatusPipeLine"]="RECHAZADO"
	listaSolicitudes=listaSolicitudes+listaTemp

	#Elimino Campos Sensibles
	listaSolicitudes=limpiarDatosSensible(listaSolicitudes)


	#Obtengo listado de Productos
	productos = collections.defaultdict(list)
	for item in listaSolicitudesOriginal:
		if(productoFiltro!=""):
			if(item['producto']==productoFiltro):
				productos[item['producto']].append(item)
		else:
			productos[item['producto']].append(item)


    #Obtengo listado de Asesores
	asesores = collections.defaultdict(list)
	for item in listaSolicitudes:
		if item['inheritedID']=="" or item['inheritedID']==item['ownerID']:
			nombreAsesorOrigen=routes_users.getUser(item['ownerID'])['name']
			item['ownerID']=nombreAsesorOrigen
			item['inheritedID']=nombreAsesorOrigen
			asesores[item['asesorNombre']].append(item)
		if (item['inheritedID']!=item['ownerID'] and item['inheritedID']!=""):
			item['asesorNombre']="Otros"
			item['ownerID']=routes_users.getUser(item['ownerID'])['name']
			item['inheritedID']=routes_users.getUser(item['inheritedID'])['name']
			asesores["Otros"].append(item)

	asesores=sorted(asesores)


	#Obtengo listado de estados
	estados = collections.defaultdict(list)
	for item in listaSolicitudesOriginal:
		estados[item['solicitudEstatus']].append(item)

	if productoFiltro!="":
		listaSolicitudes=list(filter(lambda d: d["producto"] == productoFiltro,listaSolicitudes))

	pipeline={}
	solicitudesData=[]
	groupedByStatus = collections.defaultdict(list)
	for producto in productos:
		pipeline[producto]={}
		for asesor in asesores:
			pipeline[producto][asesor]={}
			for estado in estados:
				pipeline[producto][asesor][estado]={}
				pipeline[producto][asesor][estado]["numero"]=0
				pipeline[producto][asesor][estado]["montoSolicitado"]='${:0,.2f}'.format(0)

				pipeline[producto][asesor]["ENPROCESO"]={}
				pipeline[producto][asesor]["ENPROCESO"]["numero"]=0
				pipeline[producto][asesor]["ENPROCESO"]["montoSolicitado"]='${:0,.2f}'.format(0)

				pipeline[producto][asesor]["TOTAL"]={}
				pipeline[producto][asesor]["TOTAL"]["numero"]=0
				pipeline[producto][asesor]["TOTAL"]["montoSolicitado"]='${:0,.2f}'.format(0)

				solicitudes = []
				for item in listaSolicitudes:
					if(item["producto"]==producto):
						if(item["asesorNombre"]==asesor):
							if(item["estatusPipeLine"]==estado):
								solicitudes.append(item)
								pipeline[producto][asesor][estado]["numero"]=0
								pipeline[producto][asesor][estado]["montoSolicitado"]='{:0,.2f}'.format(0)
								pipeline[producto][asesor][estado]["numero"]=len(solicitudes)
								monto=sum(Decimal(sub(r'[^\d.]', '',item['montoSolicitado'])) for item in solicitudes)
								# monto=sum(float(item['montoSolicitado']) for item in solicitudes)
								pipeline[producto][asesor][estado]["montoSolicitado"]='${:0,.2f}'.format(monto)
								pipeline[producto][asesor][estado]["solicitudes"]=solicitudes

			#Selecciono las solicitudes en Proceso por Asesor
			enProceso = list(filter(lambda d: d["estatusPipeLine"] != "FONDEADO"  and
				d["asesorNombre"] == asesor and
				d["producto"] == producto, listaSolicitudes))
			enProceso = list(filter(lambda d: d["estatusPipeLine"] != "RECHAZADO" and
				d["asesorNombre"] == asesor and
				d["producto"] == producto, enProceso))
			pipeline[producto][asesor]["ENPROCESO"]["numero"]=len(enProceso)
			monto=sum(Decimal(sub(r'[^\d.]', '',item['montoSolicitado'])) for item in enProceso)
			# monto=sum(float(item['montoSolicitado']) for item in enProceso)
			pipeline[producto][asesor]["ENPROCESO"]["montoSolicitado"]='${:0,.2f}'.format(monto)
			pipeline[producto][asesor]["ENPROCESO"]["solicitudes"]=enProceso

            #Selecciona las solicitudes para Calcular el Total por Asesor
			enTotal = list(filter(lambda d: d["estatusPipeLine"] != "RECHAZADO"  and
				d["asesorNombre"] == asesor and
				d["producto"] == producto, listaSolicitudes))
			pipeline[producto][asesor]["TOTAL"]["numero"]=len(enTotal)
			monto=sum(Decimal(sub(r'[^\d.]', '',item['montoSolicitado'])) for item in enTotal)
			# monto=sum(float(item['montoSolicitado']) for item in enTotal)
			pipeline[producto][asesor]["TOTAL"]["montoSolicitado"]='${:0,.2f}'.format(monto)

		#SELECCIONA LAS SOLICITUDES PARA CALCULAR LOS TOTALES POR PRODUCTO
		pipeline[producto]["TOTAL"]={}
		for estado in estados:
			pipeline[producto]["TOTAL"][estado]={}
			pipeline[producto]["TOTAL"][estado]["numero"]=0
			pipeline[producto]["TOTAL"][estado]["montoSolicitado"]='${:0,.2f}'.format(0)
			solicitudes = []
			for item in listaSolicitudes:
				if(item["producto"]==producto):
					if(item["solicitudEstatus"]==estado):
						solicitudes.append(item)
						pipeline[producto]["TOTAL"][estado]["numero"]=len(solicitudes)
						monto=sum(Decimal(sub(r'[^\d.]', '',item['montoSolicitado'])) for item in solicitudes)
						# monto=sum(float(item['montoSolicitado']) for item in solicitudes)
						pipeline[producto]["TOTAL"][estado]["montoSolicitado"]='${:0,.2f}'.format(monto)

					pipeline[producto]["TOTAL"]["TOTAL"]={}
					pipeline[producto]["TOTAL"]["TOTAL"]["numero"]=0
					pipeline[producto]["TOTAL"]["TOTAL"]["montoSolicitado"]='${:0,.2f}'.format(0)
					totalSolicitudes = list(filter(lambda d: d["producto"] == producto,listaSolicitudes))
					totalSolicitudes = list(filter(lambda d: d["estatusPipeLine"] != "RECHAZADO",totalSolicitudes))
					monto=sum(Decimal(sub(r'[^\d.]', '',item['montoSolicitado'])) for item in totalSolicitudes)
					# monto=sum(float(item['montoSolicitado']) for item in totalSolicitudes)
					pipeline[producto]["TOTAL"]["TOTAL"]["montoSolicitado"]='${:0,.2f}'.format(monto)
					pipeline[producto]["TOTAL"]["TOTAL"]["numero"]=len(totalSolicitudes)

					pipeline[producto]["TOTAL"]["ENPROCESO"]={}
					pipeline[producto]["TOTAL"]["ENPROCESO"]["numero"]=0
					pipeline[producto]["TOTAL"]["ENPROCESO"]["montoSolicitado"]='${:0,.2f}'.format(0)
					totalSolicitudes = list(filter(lambda d: d["estatusPipeLine"] != "FONDEADO",totalSolicitudes))
					monto=sum(Decimal(sub(r'[^\d.]', '',item['montoSolicitado'])) for item in totalSolicitudes)
					# monto=sum(float(item['montoSolicitado']) for item in totalSolicitudes)
					pipeline[producto]["TOTAL"]["ENPROCESO"]["montoSolicitado"]='${:0,.2f}'.format(monto)
					pipeline[producto]["TOTAL"]["ENPROCESO"]["numero"]=len(totalSolicitudes)

	# data["solicitudes"]=listaSolicitudes
	if productoFiltro=="":
		data["productos"]={}
		if "Nómina" in pipeline:
			data["productos"]["Nómina"]=pipeline["Nómina"]
		if "Adelanto de Nómina" in pipeline:
			data["productos"]["Adelanto de Nómina"]=pipeline["Adelanto de Nómina"]
		if "Vehículo" in pipeline:
			data["productos"]["Vehículo"]=pipeline["Vehículo"]
		if "Seguro" in pipeline and fin>'2020-09-01 00:00:00':
			data["productos"]["Seguro"]=pipeline["Seguro"]
		if "Seguro Independiente" in pipeline and fin>'2020-09-01 00:00:00':
			data["productos"]["Seguro Independiente"]=pipeline["Seguro"]
	else:
		data["productos"]=pipeline #Envia los resultados sin ordenar

	# data["fecha"]=str(datetime.date.today())
	data["fecha"]=fin.split(" ")[0]
	data["code"]="200"



	return data

def correctSolicitudesData():
	hoy=datetime.datetime.now()
	shoy=hoy.strftime("%Y-%m-%d %H:%M:%S")
	mes=hoy.month-1
	anio=hoy.year

	empresasRestringidas=routes_empresas.getEmpresasRestringidas()

	if mes<=0:
		anio=anio-1
		mes=12+mes

	fechalimRechazo=str(anio)+"-"+'{:02d}'.format(mes)+"-01 00:00:00"

	data={}
	data["fechaContacto"]=""
	data["fechaEntregaARiesgos"]=""
	data["fechaPropuesta"]=""
	data["fechaPrimerSolicitudVoBo"]=""
	data["fechaSegundaSolicitudVoBo"]=""
	data["fechaTercerSolicitudVoBo"]=""
	data["fechaVoBo"]=""
	data["fechaRechazoRiesgos"]=""
	data["fechaContratoImpreso"]=""
	data["fechaAutorizacionDG"]=""
	data["fechaRechazoDG"]=""
	data["fechaCancelacionCartera"]=""
	data["fechaEntregaContratoFirmado"]=""
	data["fechaFondeado"]=""
	data["fechaCancelacionCliente"]=""
	data["fechaRechazo"]=""
	data["inheritedID"]=""
	data["usuarioAutorizacionRiesgos"]=""
	data["autorizacionDG"]=""
	data["montoAutorizado"]=""
	data["plazoAutorizado"]=""
	data["clienteNombre"]=""
	data["clienteApellidoPaterno"]=""
	data["clienteApellidoMaterno"]=""
	data["clienteCorreoJefe"]=""
	data["clienteNombreJefe"]=""
	data["polizaSeguro"]=""
	data["clienteSeEnteroPor"]=""
	data["montoAutorizado"]="0"
	data["montoSolicitado"]="0"
	data["montoTransferencia"]="0"
	data["etapaEmbudo"]=""
	data["estatusEmbudo"]=""
	data["tipoDeNegocio"]=""
	data["motivoNoCierre"]=""
	data["solicitudNumeroControl"]=""
	data["oldID"]=""
	data["regionNombre"]=""
	data["clienteNuevoRenovacion"]=""
	data["clienteClabe"]=""
	data["fechaValidacionClabe"]="",
	data["clienteReferenciaCobranza"]=""
	data["fechaReferenciaCobranza"]=""
	data["documentos"]=""



	fileName="working/solicitudes.json"

	json_object=update.reloadJSONData(fileName)

	json_object = sorted(json_object, key=lambda k: (k['fechaContacto']))

	for i, item in enumerate(json_object):



		for field in data:
			#Completa los campos para la nueva version
			if not field in item:
				item[field]=data[field]

			if item[field]==" ":
				item[field]=""

		# Corrige el id
		if item["oldID"]=="":
			item["oldID"]=item["id"]
		item["id"]=str(i)

		#Corrige los montos
		if item["montoSolicitado"]=="":
			item["montoSolicitado"]="0"
		if item["montoAutorizado"]=="":
			item["montoAutorizado"]="0"

		#Corrige Nombre de Producto Nómina
		if item["producto"].strip()=="Nomina" or item["producto"].strip()=="Nòmina":
			item["producto"]="Nómina"

		if item["producto"].strip()=="Adelanto de Nomina" or item["producto"].strip()=="Adelanto de Nòmina":
			item["producto"]="Adelanto de Nómina"

		if item["producto"].strip()=="Vehiculo" or item["producto"].strip()=="Vehìculo":
			item["producto"]="Vehículos"

		if item["producto"].strip()=="Vehiculos" or item["producto"].strip()=="Vehìculos":
			item["producto"]="Vehículos"

		#Rellena Campos de Fecha en Solicitudes
		if item["fechaFondeado"]!="" and item["fechaRechazoRiesgos"]=="":
			if item["fechaEntregaARiesgos"]=="":
				item["fechaEntregaARiesgos"]=item["fechaFondeado"]

			if item["fechaPropuesta"]=="":
				item["fechaPropuesta"]=item["fechaFondeado"]

			if item["fechaContratoImpreso"]=="":
				item["fechaContratoImpreso"]=item["fechaFondeado"]

			if item["fechaEntregaContratoFirmado"]=="":
				item["fechaEntregaContratoFirmado"]=item["fechaFondeado"]

		#Rellena Campos de Fecha en Solicitudes
		if item["fechaEntregaContratoFirmado"]!="" and item["fechaRechazoRiesgos"]=="":
			if item["fechaEntregaARiesgos"]=="":
				item["fechaEntregaARiesgos"]=item["fechaEntregaContratoFirmado"]

			if item["fechaPropuesta"]=="":
				item["fechaPropuesta"]=item["fechaEntregaContratoFirmado"]

			if item["fechaContratoImpreso"]=="":
				item["fechaContratoImpreso"]=item["fechaEntregaContratoFirmado"]

		#Rellena Campos de Fecha en Solicitudes
		if item["fechaContratoImpreso"]!="" and item["fechaRechazoRiesgos"]=="":
			if item["fechaEntregaARiesgos"]=="":
				item["fechaEntregaARiesgos"]=item["fechaContratoImpreso"]

			if item["fechaPropuesta"]=="":
				item["fechaPropuesta"]=item["fechaContratoImpreso"]

		#Rellena Campos de Fecha en Solicitudes
		if item["fechaPropuesta"]!="" and item["fechaRechazoRiesgos"]=="":
			if item["fechaEntregaARiesgos"]=="":
				item["fechaEntregaARiesgos"]=item["fechaPropuesta"]

		#Revisa el orden cronologico de las fechas, sino lo corrige
		if  item["fechaFondeado"]!="" and item["fechaFondeado"]< item["fechaEntregaContratoFirmado"]:
			item["fechaEntregaContratoFirmado"]=item["fechaFondeado"]

		if  item["fechaEntregaContratoFirmado"]!="" and item["fechaEntregaContratoFirmado"]<item["fechaContratoImpreso"]:
			item["fechaContratoImpreso"]=item["fechaEntregaContratoFirmado"]

		if  item["fechaContratoImpreso"]!="" and item["fechaContratoImpreso"]<item["fechaPropuesta"]:
			item["fechaPropuesta"]=item["fechaContratoImpreso"]

		if  item["fechaPropuesta"]!="" and item["fechaPropuesta"]<item["fechaEntregaARiesgos"]:
			item["fechaEntregaARiesgos"]=item["fechaPropuesta"]

		if  item["fechaEntregaARiesgos"]!="" and item["fechaEntregaARiesgos"]<item["fechaContacto"]:
			item["fechaContacto"]=item["fechaEntregaARiesgos"]



		item["autorizacionDG"]="Normal"
		if  item["montoSolicitado"]!="":
			if  float(item["montoSolicitado"])>=100000:
				if (item["producto"]=="Nómina" or item["producto"]=="Adelanto de Nómina" or item["producto"]=="Vehículos") :
					item["autorizacionDG"]="Requerida"

		if  item["clienteEmpresa"] in empresasRestringidas:
			if (item["producto"]=="Nómina" or item["producto"]=="Adelanto de Nómina" or item["producto"]=="Vehículos"):
					item["autorizacionDG"]="Requerida"


		if  item["polizaSeguro"]=="":
			item["polizaSeguro"]="Ninguna"



		#Cancelo los creditos en Estado de Contactado cuya fecha de contacto sea menor al inicio del mes inmediato anterior

		if item["solicitudEstatus"]=="CONTACTO" and item["fechaContacto"]<fechalimRechazo:
			item["fechaRechazoRiesgos"]=shoy
			item["fechaCancelacionCliente"]=shoy

		#Corrige Estatus
		item=update.setEstatusSolicitud(item)

		#Corrige Nombres
		if item["asesorNombre"]=="Guadalupe Godina":
			item["asesorNombre"]="Maria Guadalupe Godina Loza"

		# Corrige Region
		if item["regionNombre"]=="":
			if item["asesorNombre"]!="":
				item["regionNombre"]=routes_users.getUserByName(item["asesorNombre"])["region"]

		# Corrige Antigüedad
		if item["clienteAntiguedad"]=="1 año  - 2 años":
			item["clienteAntiguedad"]="1 año - 2 años"


	update.saveJsonData(fileName,json_object)

	result={}
	result["message"]="Proceso Finalizado"
	return result

def getFirstDayOfMonth(fecha=None):
	fecha=datetime.datetime.strptime(fecha,  "%Y-%m-%d %H:%M:%S").replace(day=1)
	fecha=str(fecha)
	return fecha

def getLastDayOfMonth(fecha=None):
	fecha=datetime.datetime.strptime(fecha,  "%Y-%m-%d %H:%M:%S")
	if fecha.month == 12:
		return str(fecha.replace(day=31))
	return str(fecha.replace(month=fecha.month+1, day=1) - datetime.timedelta(days=1))

def getBeforeWorkDate(fecha=None):
	fecha = fecha.split(" ")[0]
	delta = 1
	diaLaboralPrevio = numpy.datetime64(fecha) - numpy.timedelta64(delta,'D')

	if numpy.is_busday(diaLaboralPrevio,weekmask=[1,1,1,1,1,0,0],holidays=diasFestivos):
		diaLaboralPrevio=str(diaLaboralPrevio)+" 23:59:59"
		return diaLaboralPrevio
	else:
		diaPrevio=str(diaLaboralPrevio)+" 23:59:59"
		return getBeforeWorkDate(diaPrevio)


def getIntervals(fecha="",inicio="",fin="",frecuencia="1"):
	#frecuencia==1==Mensual
	#frecuencia==2==Diaria
	hoy=datetime.date.today()

	if inicio=="" and fin!="":
		temp=fin+" 00:00:00"
		inicio=getFirstDayOfMonth(temp)
		inicio=inicio.split(" ").pop(0)

	if fecha=="":
		fecha=str(datetime.date.today())

	if fin=="":
		fin=str(hoy)

	if inicio=="":
		dInicio='{:02d}'.format(1)
		mInicio=hoy.month-2
		yInicio=hoy.year
		if mInicio <=0:
		   yInicio=hoy.year-1
		   mInicio =12+mInicio
		mInicio='{:02d}'.format(mInicio)
		inicio=str(yInicio)+"-"+str(mInicio)+"-"+str(dInicio)

	inicio=inicio+" 00:00:00"
	fin=fin+" 23:59:59"

	intervalos=[]
	if frecuencia=="1":
		inicio=getFirstDayOfMonth(inicio)
		dateInicio=datetime.datetime.strptime(inicio,  "%Y-%m-%d %H:%M:%S")
		dateFin=datetime.datetime.strptime(fin,  "%Y-%m-%d %H:%M:%S")
		mInicio=dateInicio.month
		yInicio=dateInicio.year
		mFin=dateFin.month
		yFin=dateFin.year
		anio=yInicio
		mes=mInicio

		# print(anio)
		# print(yFin)

		while (anio<yFin) or (mes<=mFin):
			intervalo={}
			intervalo["inicio"]=str(anio)+"-"+'{:02d}'.format(mes)+"-01 00:00:00"
			dFin=getLastDayOfMonth(intervalo["inicio"])
			dFin=dFin.split(" ")[0]
			intervalo["fin"]=dFin+" 23:59:59"
			# print(intervalo)
			intervalos.append(intervalo.copy())
			mes=mes+1
			if mes==13:
				anio=anio+1
				mes=1
			if(anio>yFin):
				return intervalos

	if frecuencia=="2":


		diaInicio=inicio.split(" ")[0].split("-")[2]
		dActual=int(diaInicio)
		inicio=getFirstDayOfMonth(inicio)
		dateInicio=datetime.datetime.strptime(inicio,  "%Y-%m-%d %H:%M:%S")
		dateFin=datetime.datetime.strptime(fin,  "%Y-%m-%d %H:%M:%S")
		mInicio=dateInicio.month
		yInicio=dateInicio.year
		mFin=dateFin.month
		yFin=dateFin.year
		anio=yInicio
		mes=mInicio

		# print(anio)
		# print(yFin)
		vuelta=1
		while (anio<yFin) or (mes<=mFin):
			intervalo={}
			intervalo["inicio"]=str(anio)+"-"+'{:02d}'.format(mes)+"-01 00:00:00"
			dFin=getLastDayOfMonth(intervalo["inicio"])
			dFin=dFin.split(" ")[0]+" 23:59:59"


			if dFin>hoy.strftime("%Y-%m-%d %H:%M:%S"):
				dFin=hoy.strftime("%Y-%m-%d %H:%M:%S")

			if fin<dFin:
				dFin=fin

			vuelta += 1
			fechaFin=dFin.split(" ")[0]
			dFinalMes=fechaFin.split("-")[2]
			mFinalMes=fechaFin.split("-")[1]
			aFinalMes=fechaFin.split("-")[0]

			while dActual <= int(dFinalMes):
				intervalo["fin"]=aFinalMes+"-"+mFinalMes+"-"+'{:02d}'.format(dActual)+" 23:59:59"
				intervalos.append(intervalo.copy())
				dActual=dActual+1
			if(dActual>int(dFinalMes)):
				mes += 1
				dActual = 1
			if mes==13:
				anio=anio+1
				mes=1
			if(anio>yFin):
				return intervalos



	return intervalos


def aplicarRegresion(item,fin):

	dates=[]
	dates=["fechaContacto",
	"fechaEntregaARiesgos",
	"fechaPropuesta",
	"fechaRechazoRiesgos",
	"fechaContratoImpreso",
	"fechaAutorizacionDG",
	"fechaRechazoDG",
	"fechaCancelacionCartera",
	"fechaEntregaContratoFirmado",
	"fechaFondeado",
	"fechaCancelacionCliente"]


	for field in item:
		if field in dates:
			if item[field]>fin:
				item[field]=""
				item["solicitudEstatus"]=""


	item=update.setEstatusSolicitud(item)

	return item

def clear_duplicates(data):
  return list(dict.fromkeys(data))


def limpiarDatosSensible(lista):
	for item in lista:
		if "clienteSalario" in item:
			del item["clienteSalario"]

		if  "listaArchivos" in item:
			del item["clienteSalario"]

		if item["montoSolicitado"]=="":
			item["montoSolicitado"]='${:0,.2f}'.format(0)
		else:
			item["montoSolicitado"]=item["montoSolicitado"].replace("$","").replace(",","")
			item["montoSolicitado"]='${:0,.2f}'.format(float(item["montoSolicitado"]))

		if item["montoAutorizado"]=="":
			item["montoAutorizado"]='${:0,.2f}'.format(0)
		else:
			item["montoAutorizado"]=item["montoAutorizado"].replace("$","").replace(",","")
			item["montoAutorizado"]='${:0,.2f}'.format(float(item["montoAutorizado"]))


	return lista


def getScoreCardOfDate(fecha=None,inicio=None,fin=None,producto=None,diaPrevio=None):
	data={}
	if fecha < inicio:
		data["feedback"]="La fecha de referencia no puede ser menor al inicio del intervalo."
		data["code"]="400"

	if fecha==None or fecha=="":
		dFecha=datetime.datetime.now()
		fecha=dFecha.strftime("%Y-%m-%d %H:%M:%S")
	else:
		fecha=fecha+" 00:00:00"



	listaSolicitudesOriginal = update.reloadJSONData("working/solicitudes.json")
	listaSolicitudesOriginal.pop(0)

	correctSolicitudesForRunTime(listaSolicitudesOriginal)

	# INICIALIZO ESTATUS EN CADA ITEM
	for item in listaSolicitudesOriginal:
		item["contactado"]=False
		item["entregadoARiesgos"]=False
		item["autorizado"]=False
		if (item["fechaContacto"]>=inicio and item["fechaContacto"] <= fin):
			item["contactado"]=True
		if (item["fechaEntregaARiesgos"]>=inicio and item["fechaEntregaARiesgos"] <= fin):
			item["entregadoARiesgos"]=True
		if (item["solicitudEstatus"] != "RECHAZADO"  and
			item["fechaContratoImpreso"] >= inicio and
			item["fechaContratoImpreso"] <= fin):
			item["autorizado"]=True
		item["agrupador"]=metas.agrupadores[item["producto"]]

	listaSolicitudes={}
	listaSolicitudes=list(filter(lambda d:
		(d["contactado"]==True or d["entregadoARiesgos"]==True or d["autorizado"]==True),
		listaSolicitudesOriginal))

	#Elimino Campos Sensibles
	listaSolicitudes=limpiarDatosSensible(listaSolicitudes)

	#Ordeno las Solicitudes por Producto y Asesor
	listaSolicitudes= sorted(listaSolicitudes, key=lambda k: (k['producto'], k['asesorNombre']))


	#Obtengo listado de Asesores
	asesores = collections.defaultdict(list)
	for item in listaSolicitudes:
		if item['inheritedID']=="" or item['inheritedID']==item['ownerID']:
			nombreAsesorOrigen=routes_users.getUser(item['ownerID'])['name']
			item['ownerID']=nombreAsesorOrigen
			item['inheritedID']=nombreAsesorOrigen
			asesores[item['asesorNombre']].append(item)
		if (item['inheritedID']!=item['ownerID'] and item['inheritedID']!=""):
			item['asesorNombre']="Otros"
			item['ownerID']=routes_users.getUser(item['ownerID'])['name']
			item['inheritedID']=routes_users.getUser(item['inheritedID'])['name']
			asesores["Otros"].append(item)

	asesores=sorted(asesores)

	scoreCard={}
	# preparo el Mix
	# Agrego Niveles de Cumplimiento
	agrupadores=metas.agrupadoresScoreCards
	estatus=['contactados','entregadosARiesgos','autorizados']
	for agrupador in agrupadores:
		scoreCard[agrupador]={}
		scoreCard[agrupador]['asesores']={}
		scoreCard[agrupador]['Total']={}


		scoreCard[agrupador]['Total']['monto']='${:0,.2f}'.format(0)
		scoreCard[agrupador]['Total']['montoComision']='${:0,.2f}'.format(0)

		for e in estatus:
			scoreCard[agrupador]['Total'][e]={}
			scoreCard[agrupador]['Total'][e]['total']=0
			scoreCard[agrupador]['Total'][e]['set']=[]

		for asesor in asesores:
			scoreCard[agrupador]['asesores'][asesor]={}
			scoreCard[agrupador]['asesores'][asesor]['anPonderados']=0
			scoreCard[agrupador]['asesores'][asesor]['total']=0
			scoreCard[agrupador]['asesores'][asesor]['nivel']=0
			scoreCard[agrupador]['asesores'][asesor]['factorComision']=0
			scoreCard[agrupador]['asesores'][asesor]['montoTotal']=0
			scoreCard[agrupador]['asesores'][asesor]['montoComision']=0
			scoreCard[agrupador]['asesores'][asesor]['porcientoCumplimiento']=0
			for e in estatus:
				scoreCard[agrupador]['asesores'][asesor][e]={}
				scoreCard[agrupador]['asesores'][asesor][e]['set']=[]
				scoreCard[agrupador]['asesores'][asesor][e]['monto']='${:0,.2f}'.format(0)
				scoreCard[agrupador]['asesores'][asesor][e]['total']=0
				scoreCard[agrupador]['asesores'][asesor][e]['anPonderados']=0
				scoreCard[agrupador]['asesores'][asesor][e]['total']=0
				scoreCard[agrupador]['asesores'][asesor][e]['nivel']=0
				scoreCard[agrupador]['asesores'][asesor][e]['factorComision']=0
				scoreCard[agrupador]['asesores'][asesor][e]['montoComision']='${:0,.2f}'.format(0)
				scoreCard[agrupador]['asesores'][asesor][e]['porcientoCumplimiento']=0

				scoreCard[agrupador]['Total'][e]={}
				scoreCard[agrupador]['Total'][e]['total']=0
				scoreCard[agrupador]['Total'][e]['set']=[]

	for idx, item in enumerate(listaSolicitudes):

	    if(item["contactado"]==True):
	    	scoreCard[item['agrupador']]['asesores'][item['asesorNombre']]['contactados']['total']  +=1
	    	scoreCard[item['agrupador']]['asesores'][item['asesorNombre']]['contactados']['set'].append([item['id']])

	    	scoreCard[item['agrupador']]['Total']['contactados']['total'] +=1
	    	scoreCard[item['agrupador']]['Total']['contactados']['set'].append([item['id']])


	    if(item["entregadoARiesgos"]==True):
	    	scoreCard[item['agrupador']]['asesores'][item['asesorNombre']]['entregadosARiesgos']['total']  +=1
	    	scoreCard[item['agrupador']]['asesores'][item['asesorNombre']]['entregadosARiesgos']['set'].append([item['id']])

	    	scoreCard[item['agrupador']]['Total']['entregadosARiesgos']['total'] +=1
	    	scoreCard[item['agrupador']]['Total']['entregadosARiesgos']['set'].append([item['id']])


	    if(item["autorizado"]==True):
	    	scoreCard[item['agrupador']]['asesores'][item['asesorNombre']]['autorizados']['total']  +=1
	    	scoreCard[item['agrupador']]['asesores'][item['asesorNombre']]['autorizados']['set'].append([item['id']])

	    	scoreCard[item['agrupador']]['Total']['autorizados']['total'] +=1
	    	scoreCard[item['agrupador']]['Total']['autorizados']['set'].append([item['id']])

	    	# Obtengo el monto Autorizado por cada Asessor
	    	monto=Decimal(sub(r'[^\d.]', '',item['montoAutorizado']))
	    	montoprev=Decimal(sub(r'[^\d.]', '',scoreCard[item['agrupador']]['asesores'][item['asesorNombre']]['autorizados']['monto']))
	    	montonuevo=monto+montoprev
	    	scoreCard[item['agrupador']]['asesores'][item['asesorNombre']]['autorizados']['monto']='${:0,.2f}'.format(montonuevo)
	    	# print('{:5s}  {:35s}  ${:10,.2f}   ${:10,.2f}   ${:10,.2f}  {:10s}   {:15s}   {:1d}'.format(
	    	# 	item['agrupador'],
	    	# 	item["asesorNombre"],
	    	# 	monto,
	    	# 	montoprev,
	    	# 	montonuevo,
	    	# 	item["solicitudNumeroControl"],
	    	# 	item["solicitudEstatus"],
	    	# 	item["autorizado"]))

	    	# Obtengo el monto Autorizado Total por Producto
	    	monto=Decimal(sub(r'[^\d.]', '',item['montoAutorizado']))
	    	montoprev=Decimal(sub(r'[^\d.]', '',scoreCard[item['agrupador']]['Total']['monto']))
	    	montonuevo=monto+montoprev
	    	scoreCard[item['agrupador']]['Total']['monto']='${:0,.2f}'.format(montonuevo)

	# CALCULO LAS METAS DEL DIA
	# Obtengo los dias laborales en el mes
	inicioMes=getFirstDayOfMonth(fin)
	finMes=getLastDayOfMonth(fin)
	inicioMesLaboral=inicioMes.split(" ")[0]
	finMesLaboral=finMes.split(" ")[0]
	diasLaboralesMes=numpy.busday_count(inicioMesLaboral,finMesLaboral,weekmask=[1,1,1,1,1,0,0],holidays=diasFestivos)

	inicio=inicio.split(" ")[0]
	if(fecha < fin):
		fin=fecha.split(" ")[0]
	else:
		fin=fin.split(" ")[0]
	diasLaborales=numpy.busday_count(inicio,fin,weekmask=[1,1,1,1,1,0,0],holidays=diasFestivos)
	if numpy.is_busday(fin,weekmask=[1,1,1,1,1,0,0],holidays=diasFestivos):
		diasLaborales +=1

	porcientoTranscurrido=(diasLaborales-1)/diasLaboralesMes
	metaContactados=metas.metasCN["contactados"]
	metaEntregadosARiesgos=metas.metasCN["entregadosARiesgos"]
	metaAutorizados=metas.metasCN["autorizados"]

	metaContactadosDiasTranscurridos=int(metaContactados*porcientoTranscurrido)
	if metaContactadosDiasTranscurridos==0:
		metaContactadosDiasTranscurridos =1

	metaEntregadosARiesgosDiasTranscurridos=int(metaEntregadosARiesgos*porcientoTranscurrido)
	if metaEntregadosARiesgosDiasTranscurridos==0:
		metaEntregadosARiesgosDiasTranscurridos=1

	metaAutorizadosDiasTranscurridos=int(metaAutorizados*porcientoTranscurrido)
	if metaAutorizadosDiasTranscurridos==0:
		metaAutorizadosDiasTranscurridos=1

	# print(inicio + " --- "+
	# 	fin+ " --- dias laborales: " +
	# 	str(diasLaborales) + " de: "+ str(diasLaboralesMes) +
	# 	" : "+'{:0,.2f}'.format(porcientoTranscurrido) +
	# 	" metas: " +
	# 	'{:2,.0f}'.format(metaContactadosDiasTranscurridos)+" "
	# 	'{:2,.0f}'.format(metaEntregadosARiesgosDiasTranscurridos)+" "
	# 	'{:2,.0f}'.format(metaAutorizadosDiasTranscurridos))

	scoreCard['CN']['metasMes']=metas.metasCN
	scoreCard['CN']['metasDia']={"contactados":metaContactadosDiasTranscurridos,
								 "entregadosARiesgos":metaEntregadosARiesgosDiasTranscurridos,
								 "autorizados":metaAutorizadosDiasTranscurridos
								 }


	# Calculos para CN
	for asesor in scoreCard['CN']['asesores']:
		for e in estatus:
			porcientoCumplimiento=scoreCard['CN']['asesores'][asesor][e]['total']/scoreCard['CN']['metasDia'][e]
			for comision in metas.comisionesCN:
				if (porcientoCumplimiento>=comision['min'] and
					porcientoCumplimiento<comision['max']):
					# print('{:35s}  {:20s}  {:2d} de {:2d} = {:2,.2f}  {:10s}'.format(asesor,e,scoreCard['CN']['asesores'][asesor][e]['total'],scoreCard['CN']['metasDia'][e],porcientoCumplimiento,comision['nivel']))
					scoreCard['CN']['asesores'][asesor][e]['nivel']=comision['nivel']
					scoreCard['CN']['asesores'][asesor][e]['color']=comision['color']
					scoreCard['CN']['asesores'][asesor][e]['bgcolor']=comision['bgcolor']

					if(e=="autorizados"):
						scoreCard['CN']['asesores'][asesor][e]['nivel'] = comision['nivel']
						scoreCard['CN']['asesores'][asesor][e]['color']=comision['color']
						scoreCard['CN']['asesores'][asesor][e]['bgcolor']=comision['bgcolor']
						autorizados=scoreCard['CN']['asesores'][asesor][e]['total']
						monto = Decimal(sub(r'[^\d.]', '',scoreCard['CN']['asesores'][asesor][e]['monto']))
						factor = comision['comision']
						factor = Decimal(factor)
						montoComision = monto * factor
						scoreCard['CN']['asesores'][asesor][e]['factorComision']='{:0,.3f}'.format(factor)
						scoreCard['CN']['asesores'][asesor][e]['montoComision']='${:0,.2f}'.format(montoComision)
						scoreCard['CN']['asesores'][asesor][e]['porcientoCumplimiento']='{:0,.2f}%'.format(porcientoCumplimiento*100)
						montoTotalComisionPrevio=Decimal(sub(r'[^\d.]', '',scoreCard['CN']['Total']['montoComision']))
						montoTotalComision=montoComision+montoTotalComisionPrevio
						scoreCard['CN']['Total']['montoComision']='${:0,.2f}'.format(montoTotalComision)
						# scoreCard['MIX']['Total']['montoComision']='${:0,.2f}'.format(montoTotalComision)







	# Calculos para AN
	for asesor in scoreCard['AN']['asesores']:
		monto = Decimal(sub(r'[^\d.]', '',scoreCard['AN']['asesores'][asesor]['autorizados']['monto']))
		factor = metas.comisionesAN[0]
		factor = Decimal(factor)
		montoComision = monto * factor
		scoreCard['AN']['asesores'][asesor]['autorizados']['factorComision']='{:0,.3f}'.format(factor)
		scoreCard['AN']['asesores'][asesor]['autorizados']['montoComision']='${:0,.2f}'.format(montoComision)
		montoTotalComisionPrevio=Decimal(sub(r'[^\d.]', '',scoreCard['AN']['Total']['montoComision']))
		montoTotalComision=montoComision+montoTotalComisionPrevio
		scoreCard['AN']['Total']['montoComision']='${:0,.2f}'.format(montoTotalComision)


	# Calculos para MIX
	acumulador=0
	totalAutorizados=0
	acumuladorComision=0
	for asesor in scoreCard['MIX']['asesores']:
		montoCN=Decimal(sub(r'[^\d.]', '',scoreCard['CN']['asesores'][asesor]['autorizados']['monto']))
		montoAN=Decimal(sub(r'[^\d.]', '',scoreCard['AN']['asesores'][asesor]['autorizados']['monto']))
		montoTotal=montoCN+montoAN
		acumulador+=montoTotal

		scoreCard['MIX']['Total']['monto']='${:0,.2f}'.format(acumulador)
		scoreCard['MIX']['asesores'][asesor]['montoTotal']='${:0,.2f}'.format(montoTotal)

		totalAN=scoreCard['AN']['asesores'][asesor]['autorizados']['total']
		totalCN=scoreCard['CN']['asesores'][asesor]['autorizados']['total']

		scoreCard['MIX']['asesores'][asesor]['total']=totalCN

		# print('{:10s}  {:35s}  \033[32m {:2d} \033[0m  {:2d}'.format(fin,asesor,totalCN,totalAN))
		totalAutorizados=totalCN
		if totalCN >= metas.ponderacion['min']:
			scoreCard['MIX']['asesores'][asesor]['total']=totalCN + totalAN/metas.ponderacion['divisor']
			totalAutorizados=totalCN + totalAN/metas.ponderacion['divisor']

		porcientoCumplimiento=totalAutorizados/metaAutorizadosDiasTranscurridos
		# print(porcientoCumplimiento)
		for comision in metas.comisionesCN:
			if (porcientoCumplimiento>=comision['min'] and
				porcientoCumplimiento<comision['max']):
				factor = comision['comision']
				factor = Decimal(factor)
				montoComision = montoTotal * factor
				scoreCard['MIX']['asesores'][asesor]['factorComision']='{:0,.3f}'.format(factor)
				scoreCard['MIX']['asesores'][asesor]['montoComision']='${:0,.2f}'.format(montoComision)
				scoreCard['MIX']['asesores'][asesor]['nivel']=comision['nivel']
				scoreCard['MIX']['asesores'][asesor]['color']=comision['color']
				scoreCard['MIX']['asesores'][asesor]['bgcolor']=comision['bgcolor']
				acumuladorComision += montoComision


				# print(('\033[32m {:10s}  {:5s}  {:35s}  {:10s}   {:2f} de {:2d} = {:2,.2f}  {:10s} --> {:10s} * {:6s} =  {:10s} \033[0m').format(
				#    fin,
				#    'MIX',
				#    asesor,
				#    e,
				#    scoreCard['MIX']['asesores'][asesor]['total'],
				#    scoreCard['CN']['metasDia'][e],
				#    porcientoCumplimiento,
				#    comision['nivel'],
				#    scoreCard['MIX']['asesores'][asesor]['montoTotal'],
				#    scoreCard['MIX']['asesores'][asesor]['factorComision'],
				#    scoreCard['MIX']['asesores'][asesor]['montoComision']
				#  ))

		totalAutorizados+=scoreCard['MIX']['asesores'][asesor]['total']
		scoreCard['MIX']['Total']['total']=totalAutorizados
		scoreCard['MIX']['Total']['montoComision']='${:0,.2f}'.format(acumuladorComision)


	# Calculo el día previo
	if diaPrevio!=None:
		aPrevio=diaPrevio.split(" ")[0].split("-")[0]
		mPrevio=diaPrevio.split(" ")[0].split("-")[1]
		inicioPrevio=aPrevio+"-"+mPrevio+'-01 00:00:00'
		scoreCard['diaPrevio']={}
		scoreCard['diaPrevio']=getScoreCardOfDate(fecha,inicioPrevio,diaPrevio,producto,None)

	# Armo el arreglo Final
	data["solicitudes"]=listaSolicitudes
	data["scoreCard"]=scoreCard
	data["fecha"]=fin.split(" ")[0]
	anioMes=data["fecha"].split("-")
	# data["fecha"]=anioMes[0]+"-"+anioMes[1]
	data["code"]="200"


	return data




def reporteVentas(formData):
	import esquemaReporteVentas as esquema
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
	empresasExternas=config.empresasExternas
	renglon={}
	renglones=[]
	headers=[]

	empresasTipo=routes_empresas.getlistEmpresasTipo()
	esquemaReporte=esquema.esquemaReporteVentas[0]

	for campo in esquemaReporte:
		headers.append(campo)

	listaSolicitudes = update.reloadJSONData("working/solicitudes.json")
	listaSolicitudes.pop(0)
	listaSolicitudes = sorted(listaSolicitudes, key=lambda k: (k['fechaContacto']))


	listaSolicitudes=list(filter(lambda d:
			( d["fechaContacto"] >= fechaInicio  and d["fechaContacto"] <= fechaFin),
		    listaSolicitudes))

	for solicitud in listaSolicitudes:
		for campo in esquemaReporte:
			if esquemaReporte[campo] not in renglon:
				renglon[campo]="Falta Calcular"
			if esquemaReporte[campo]!="calculado":
				renglon[campo]=solicitud[esquemaReporte[campo]]

		#Campos Calculados

		if solicitud["clienteEmpresa"] in empresasTipo:
				renglon["TIPO DE VENTA EXTERNA O INTERNA"]=empresasTipo[solicitud["clienteEmpresa"]]
		else:
			if solicitud["clienteEmpresa"] in empresasExternas:
				renglon["TIPO DE VENTA EXTERNA O INTERNA"]="Externa"
			else:
				renglon["TIPO DE VENTA EXTERNA O INTERNA"]="Interna"


		renglon["FECHA COTIZACIÓN"]=renglon["FECHA COTIZACIÓN"].split(" ")[0]
		renglon["FECHA PROSPECTO"]=renglon["FECHA PROSPECTO"].split(" ")[0]
		renglon["AÑO CREDITO"]=renglon["FECHA COTIZACIÓN"].split("-")[0]
		renglon["FECHA PROBABLE DE CIERRE"]=getFechaProbableCierre(renglon["FECHA COTIZACIÓN"], 7)
		renglon["MES PROBABLE DE CIERRE"]=nombresMeses[renglon["FECHA PROBABLE DE CIERRE"].split("-")[1]]
		if(renglon["FECHA CIERRE"]!="" and renglon["FECHA CIERRE"]!="Falta Calcular"):
			renglon["FECHA CIERRE"]=renglon["FECHA CIERRE"].split(" ")[0]
			renglon["MES DE CIERRE"]=nombresMeses[renglon["FECHA CIERRE"].split("-")[1]]

		if(renglon["FECHA CIERRE"]==""):
			renglon["MES DE CIERRE"]=""

		if(solicitud["solicitudEstatus"]!="RECHAZADO"):
			renglon["FECHA PERDIDO"]=""
		else:
			renglon["FECHA PERDIDO"]=solicitud["fechaRechazoRiesgos"]
			renglon["FECHA CIERRE"]=""
			renglon["MES DE CIERRE"]=""

		renglon["TAMAÑO CUENTA"]=getSolicitudTamanodeCuenta(solicitud)


		renglones.append(renglon.copy())
	data={}
	data["headers"]=headers
	data["reporte"]=renglones

	return data


def reporteCobranza(ownerID):
	import esquemaReporteCobranzaReferenciada as esquema

	renglon={}
	renglones=[]
	headers=[]

	esquemaReporte=esquema.esquemaReporteCobranza[0]

	for campo in esquemaReporte:
		headers.append(campo)

	listaSolicitudes=getSolicitudes(ownerID)["listaSolicitudes"]
	listaSolicitudes = list(filter(lambda d: d["clienteReferenciaCobranza"] != "", listaSolicitudes))

	for solicitud in listaSolicitudes:
		for campo in esquemaReporte:

			if campo=="CLIENTE":
				renglon[campo]=solicitud[esquemaReporte[campo]]
				if solicitud["clienteApellidoPaterno"]!="":
					renglon[campo] += " "+ solicitud["clienteApellidoPaterno"]
				if solicitud["clienteApellidoMaterno"]!="":
					renglon[campo] += " "+ solicitud["clienteApellidoMaterno"]
				renglon[campo]=renglon[campo].upper()
				renglon[campo]=sub(' +', ' ', renglon[campo])

			else:
				if campo=="ID_SOLICITUD":
					renglon[campo]=int(solicitud[esquemaReporte[campo]])
				else:
					renglon[campo]=solicitud[esquemaReporte[campo]]
		renglones.append(renglon.copy())

	renglones=sorted(renglones, key=lambda k: (k["ID_SOLICITUD"]))

	for renglon in renglones:
		renglon["ID_SOLICITUD"]=str(renglon["ID_SOLICITUD"])

	data={}
	data["headers"]=headers
	data["reporte"]=renglones

	return data

def getFechaProbableCierre(fecha,delta):
	fecha=fecha + " 23:59:59"
	fecha=datetime.datetime.strptime(fecha,  "%Y-%m-%d %H:%M:%S")

	return str(fecha + datetime.timedelta(days=7)).split(" ")[0]

def getSolicitudTamanodeCuenta(solicitud):
	nivelCuentas=config.niveldeCuenta
	data=""
	for nivel in nivelCuentas:
		monto=Decimal(sub(r'[^\d.]', '',solicitud['montoSolicitado']))
		if (monto>=nivel["min"] and monto<nivel["max"]):
			data=nivel["nivel"]

	return data

def obtenerSegurosdeSolicitudes():
	solicitudes = update.reloadJSONData("working/solicitudes.json")
	solicitudes.pop(0)
	seguros={}
	seguros=list(filter(lambda d:
		(d["polizaSeguro"]!="Ninguna" and d["polizaSeguro"]!=""),
		solicitudes))
	for item in seguros:
		item["id"]="1000000"+item["id"]
		item["producto"]="Seguro"
		item["montoSolicitado"]=item["polizaSeguro"]
	return seguros

def getColocacion(formData):

	fechaInicio=""
	fechaFin=""
	fecha=""
	producto=""
	frecuencia="1"

	if "fecha" in formData:
		if formData["fecha"]!="":
			fecha=formData["fecha"]

	if "fechaInicio" in formData:
		if formData["fechaInicio"]!="":
			fechaInicio=formData["fechaInicio"]
			if(fechaInicio<"2019-01-02"):
				fechaInicio="2019-01-02"
		if formData["fechaInicio"]=="":
			if formData["frecuencia"]=="2":
				fechaInicio="2019-01-02"

	if "fechaFin" in formData:
		if formData["fechaFin"]!="":
			fechaFin=formData["fechaFin"]
			if(fechaFin<"2019-01-02"):
				fechaFin="2019-01-02"

	if "producto" in formData:
		if formData["producto"]!="":
			producto=formData["producto"]

	if "frecuencia" in formData:
		if formData["frecuencia"]!="":
			frecuencia=formData["frecuencia"]

	data={}
	user=routes_users.getUser(formData["ownerID"])
	data["user"]=user


	data["series"]=[]
	data["etiquetas"]=[]
	data["productos"]=["Nómina","Adelanto de Nómina"]


	intervalos={}
	intervalos=getIntervals(fecha,fechaInicio,fechaFin,"1") #Obtengo intevalos diarios


	if frecuencia=="3":
		intervalos=getIntervals(fecha,fechaInicio,fechaFin,"1")
		if fechaFin=="":
			fechaFin = str(datetime.date.today())

		fechaActual = fechaFin+" 23:59:59"
		inicioMes=getFirstDayOfMonth(fechaActual).split(" ")[0]
		fechaActual = fechaFin
		diasLaboralesTranscurridos=numpy.busday_count(inicioMes,fechaActual,weekmask=[1,1,1,1,1,0,0],holidays=diasFestivos)
		# Calculo el intervalo para el mes inmediato anterior
		for intervalo in intervalos:
			inicioMesAnterior=intervalo["inicio"].split(" ")[0]
			finMesAnterior=intervalo["fin"].split(" ")[0]
			nthdiaLaboralMesAnterior=numpy.busday_offset(inicioMesAnterior, diasLaboralesTranscurridos, roll='forward')
			if(str(nthdiaLaboralMesAnterior)<finMesAnterior):
				intervalo["fin"]=str(nthdiaLaboralMesAnterior)+" 23:59:59"

	for intervalo in intervalos:
		if frecuencia=="1":
			data["series"].append(getSerieColocacionDiaria(fecha,intervalo["inicio"],intervalo["fin"],producto).copy())
		if frecuencia=="2":
			data["series"].append(getSerieColocacionDiaria(fecha,intervalo["inicio"],intervalo["fin"],producto).copy())


	if frecuencia=="1":
		for i in range(1,24):
			data["etiquetas"].append(str(i));




	seriesAnual={}
	if frecuencia=="2":
		# for i in range(1,13):
		# 	data["etiquetas"].append(str(i));
		data["etiquetas"]=[ "ene","feb","mar",
							"abr","may","jun",
							"jul","ago","sep",
							"oct","nov","dic"]

		for serie in data["series"]:
			for mes in serie:
				nombre=serie[mes]["nombre"]
				anio=nombre.split("-")[0]
				# nmes=str(int(nombre.split("-")[1]))
				nmes=data["etiquetas"][int(nombre.split("-")[1])-1]

				if (anio not in seriesAnual):
					seriesAnual[anio]={}
					seriesAnual[anio]["nombre"]=str(anio)

				for producto in data['productos']:
					if producto not in seriesAnual[anio]:
						seriesAnual[anio][producto]={}
					if (mes not in seriesAnual[anio][producto]):
						seriesAnual[anio][producto][nmes]={}
						for dia in range(23,1,-1):
							if producto in serie[mes]:
								if str(dia) in serie[mes][producto]:
									seriesAnual[anio][producto][nmes]=serie[mes][producto][str(dia)]
									seriesAnual[anio][producto][nmes]['bgcolor']="#FFFFFF"
									break

		seriesFinal={}
		for serie in seriesAnual:
			if serie not in seriesFinal:
				seriesFinal[serie]=seriesAnual[serie]

		data["series"]=[]
		data["series"].append(seriesFinal.copy())


	#se agreaga un arreglo vacio para tener una respuesta estandarizada
	data['headers']=[]
	data['asesores']=[]
	data['seguros']=[]

	# print(json.dumps(seriesAnual,indent=4))
	# print(json.dumps(data,indent=4))

	return data




def getSerieColocacionDiaria(fecha=None,inicio=None,fin=None,producto=None,diaPrevio=None):

	productos=["Nómina","Adelanto de Nómina"]
	data={}

	if fecha < inicio:
		data["feedback"]="La fecha de referencia no puede ser menor al inicio del intervalo."
		data["code"]="400"

	if fecha==None or fecha=="":
		dFecha=datetime.datetime.now()
		fecha=dFecha.strftime("%Y-%m-%d %H:%M:%S")
	else:
		fecha=fecha+" 00:00:00"


	serie={}

	listaSolicitudes = update.reloadJSONData("working/solicitudes.json")
	listaSolicitudes.pop(0)
	listaSolicitudes = sorted(listaSolicitudes, key=lambda k: (k['producto'],k['fechaContratoImpreso']))


	listaSolicitudes=list(filter(lambda d:
			(   d["fechaContratoImpreso"] >= inicio and
				d["fechaContratoImpreso"] <= fin and
				d["solicitudEstatus"]!="RECHAZADO"),
			listaSolicitudes))


	mesSerie=inicio.split(" ")[0]
	mesSerie=mesSerie.split("-")[0]+"-"+mesSerie.split("-")[1]

	serie[mesSerie]={}
	serie[mesSerie]["nombre"]=mesSerie
	maxDiaLaboral=0
	for producto in productos:
		for solicitud in listaSolicitudes:

			fechaContratoImpreso=solicitud['fechaContratoImpreso'].split(" ")[0]
			diaLaboral=str(numpy.busday_count(inicio.split(" ")[0],fechaContratoImpreso,weekmask=[1,1,1,1,1,0,0],holidays=diasFestivos)+1)

			if int(diaLaboral)>maxDiaLaboral:
				maxDiaLaboral=int(diaLaboral)

			if(producto not in serie[mesSerie]):
				serie[mesSerie][producto]={}

			if(diaLaboral not in serie[mesSerie][producto]):
				serie[mesSerie][producto][diaLaboral]={}
				serie[mesSerie][producto][diaLaboral]['fechaContratoImpreso']=fechaContratoImpreso
				serie[mesSerie][producto][diaLaboral]['cuenta']=0
				serie[mesSerie][producto][diaLaboral]['montoSolicitado']=0
				serie[mesSerie][producto][diaLaboral]['montoAutorizado']=0
				serie[mesSerie][producto][diaLaboral]['montoTransferencia']=0
				serie[mesSerie][producto][diaLaboral]['montoSolicitadoAcumulado']=0
				serie[mesSerie][producto][diaLaboral]['montoAutorizadoAcumulado']=0
				serie[mesSerie][producto][diaLaboral]['montoTransferenciaAcumulado']=0
				serie[mesSerie][producto][diaLaboral]['cuentaAcumulado']=0


		if(producto not in serie[mesSerie]):
			serie[mesSerie][producto]={}
			diaLaboral=0
			if(diaLaboral not in serie[mesSerie][producto]):
				serie[mesSerie][producto][diaLaboral]={}
				serie[mesSerie][producto][diaLaboral]['fechaContratoImpreso']=""
				serie[mesSerie][producto][diaLaboral]['cuenta']=0
				serie[mesSerie][producto][diaLaboral]['montoSolicitado']=""
				serie[mesSerie][producto][diaLaboral]['montoAutorizado']=""
				serie[mesSerie][producto][diaLaboral]['montoTransferencia']=""
				serie[mesSerie][producto][diaLaboral]['montoSolicitadoAcumulado']=""
				serie[mesSerie][producto][diaLaboral]['montoAutorizadoAcumulado']=""
				serie[mesSerie][producto][diaLaboral]['montoTransferenciaAcumulado']=""
				serie[mesSerie][producto][diaLaboral]['cuentaAcumulado']=0



	for producto in productos:
		for intDiaLaboral in range(1,maxDiaLaboral):
			diaLaboral=str(intDiaLaboral)
			if(diaLaboral not in serie[mesSerie][producto]):
				serie[mesSerie][producto][diaLaboral]={}
				serie[mesSerie][producto][diaLaboral]['fechaContratoImpreso']=""
				serie[mesSerie][producto][diaLaboral]['cuenta']=0
				serie[mesSerie][producto][diaLaboral]['montoSolicitado']=0
				serie[mesSerie][producto][diaLaboral]['montoAutorizado']=0
				serie[mesSerie][producto][diaLaboral]['montoTransferencia']=0
				serie[mesSerie][producto][diaLaboral]['montoSolicitadoAcumulado']=0
				serie[mesSerie][producto][diaLaboral]['montoAutorizadoAcumulado']=0
				serie[mesSerie][producto][diaLaboral]['montoTransferenciaAcumulado']=0
				serie[mesSerie][producto][diaLaboral]['cuentaAcumulado']=0



	for producto in productos:
		for solicitud in listaSolicitudes:
			fechaContratoImpreso=solicitud['fechaContratoImpreso'].split(" ")[0]
			diaLaboral=str(numpy.busday_count(inicio.split(" ")[0],fechaContratoImpreso,weekmask=[1,1,1,1,1,0,0],holidays=diasFestivos)+1)
			if solicitud["producto"]==producto:
				serie[mesSerie][producto][diaLaboral]['cuenta']            += 1
				serie[mesSerie][producto][diaLaboral]['montoSolicitado']   += float(solicitud['montoSolicitado'])
				serie[mesSerie][producto][diaLaboral]['montoAutorizado']   += float(solicitud['montoAutorizado'])
				serie[mesSerie][producto][diaLaboral]['montoTransferencia']+= float(solicitud['montoTransferencia'])

	# Obtengo acumulados por dia
	for producto in productos:
		montoSolicitadoAcumulado=0
		montoAutorizadoAcumulado=0
		montoTransferenciaAcumulado=0
		cuentaAcumulado=0
		for intDiaLaboral in range(1,maxDiaLaboral+1):
			diaLaboral=str(intDiaLaboral)
			cuentaAcumulado             += serie[mesSerie][producto][diaLaboral]['cuenta']
			montoSolicitadoAcumulado    += serie[mesSerie][producto][diaLaboral]['montoSolicitado']
			montoAutorizadoAcumulado    += serie[mesSerie][producto][diaLaboral]['montoAutorizado']
			montoTransferenciaAcumulado += serie[mesSerie][producto][diaLaboral]['montoTransferencia']
			serie[mesSerie][producto][diaLaboral]['cuentaAcumulado']             = cuentaAcumulado
			serie[mesSerie][producto][diaLaboral]['montoSolicitadoAcumulado']    = montoSolicitadoAcumulado
			serie[mesSerie][producto][diaLaboral]['montoAutorizadoAcumulado']    = montoAutorizadoAcumulado
			serie[mesSerie][producto][diaLaboral]['montoTransferenciaAcumulado'] = montoTransferenciaAcumulado

	# Doy formato de moneda a los campos de montos
	for producto in productos:
		for intDiaLaboral in range(1,maxDiaLaboral+1):
			diaLaboral=str(intDiaLaboral)
			serie[mesSerie][producto][diaLaboral]['montoSolicitado']    = '${:0,.2f}'.format(serie[mesSerie][producto][diaLaboral]['montoSolicitado'] )
			serie[mesSerie][producto][diaLaboral]['montoAutorizado']    = '${:0,.2f}'.format(serie[mesSerie][producto][diaLaboral]['montoAutorizado'] )
			serie[mesSerie][producto][diaLaboral]['montoTransferencia'] = '${:0,.2f}'.format(serie[mesSerie][producto][diaLaboral]['montoTransferencia'] )
			serie[mesSerie][producto][diaLaboral]['montoSolicitadoAcumulado']    = '${:0,.2f}'.format(serie[mesSerie][producto][diaLaboral]['montoSolicitadoAcumulado'] )
			serie[mesSerie][producto][diaLaboral]['montoAutorizadoAcumulado']    = '${:0,.2f}'.format(serie[mesSerie][producto][diaLaboral]['montoAutorizadoAcumulado'] )
			serie[mesSerie][producto][diaLaboral]['montoTransferenciaAcumulado'] = '${:0,.2f}'.format(serie[mesSerie][producto][diaLaboral]['montoTransferenciaAcumulado'] )
			if(serie[mesSerie][producto][diaLaboral]['cuenta'] == 0):
				serie[mesSerie][producto][diaLaboral]['bgcolor']='#FFFF00'
				serie[mesSerie][producto][diaLaboral]['color']="#FF0000"
			else:
				serie[mesSerie][producto][diaLaboral]['color']="#000000"
				serie[mesSerie][producto][diaLaboral]['bgcolor']='#FFFFFF'




	# print(json.dumps(serie,indent=4))
	return serie


def getTabularColocacion(formData):
	import esquemaReporteTabularColocacion as esquema
	esquemaReporte=esquema.esquemaReporteTabularColocacion[0]

	renglon={}
	renglones=[]
	headers=[]

	data={}
	user=routes_users.getUser(formData["ownerID"])
	data["user"]=user

	data["series"]=[]
	data["etiquetas"]=[]
	data["productos"]=["Nómina","Adelanto de Nómina","Seguro"]
	data["seguros"]=["25000","50000","75000","100000"]
	data["años"]=[]
	data["resumenProducto"]=[]
	data["resumenAsesor"]=[]
	data["resumenEntregados"]=[]

	fechaInicio=""
	fechaFin=""
	fecha=""
	producto=""
	frecuencia="1"

	if "fecha" in formData:
		if formData["fecha"]!="":
			fecha=formData["fecha"]

	if "fechaInicio" in formData:
		if formData["fechaInicio"]!="":
			fechaInicio=formData["fechaInicio"]
			if(fechaInicio<"2019-01-02"):
				fechaInicio="2019-01-02"

	if "fechaFin" in formData:
		if formData["fechaFin"]!="":
			fechaFin=formData["fechaFin"]
			if(fechaFin<"2019-01-02"):
				fechaFin="2019-01-02"

	if "producto" in formData:
		if formData["producto"]!="":
			producto=formData["producto"]

	# Se forza para que no busque datos mensuales
	# if "frecuencia" in formData:
	# 	if formData["frecuencia"]!="":
	# 		frecuencia=formData["frecuencia"]


	intervalos={}
	intervalos=getIntervals(fecha,fechaInicio,fechaFin,"1") #Obtengo intevalos diarios
	# print(json.dumps(intervalos,indent=4))

	if fechaInicio=="":
		inicio=intervalos[len(intervalos)-1]["inicio"]
	else:
		inicio=fechaInicio + " 00:00:00"
	if fechaFin=="":
		fin=intervalos[len(intervalos)-1]["fin"]
	else:
		fin=fechaFin + " 23:59:59"

	if "fechaFin" not in formData:
		formData["fechaFin"]=fin.split(" ")[0]
	if formData["fechaFin"] =='':
		formData["fechaFin"]=fin.split(" ")[0]

	if "fechaInicio" not in formData:
		formData["fechaInicio"]=inicio.split(" ")[0]
	if formData["fechaInicio"] =='':
		formData["fechaInicio"]=inicio.split(" ")[0]

	formData["fechaReporte"]=datetime.date.today()

	anioInicio=int(inicio.split("-")[0])
	anioFin=int(fin.split("-")[0])
	anio=anioInicio

	data["años"].append(anioInicio)
	while anio < anioFin:
		anio=anio + 1
		data["años"].append(anio)




	listaSolicitudes = update.reloadJSONData("working/solicitudes.json")
	listaSolicitudes.pop(0)

	seguros=obtenerSegurosdeSolicitudes()
	for seguro in seguros:
		if seguro["polizaSeguro"]=="Ninguna":
			seguro["montoAutorizado"]="0"
		listaSolicitudes.append(seguro.copy())

	listaSolicitudes = sorted(listaSolicitudes, key=lambda k: (k['producto'],k['fechaFondeado']))

	for solicitud in listaSolicitudes:
		if not 'expedienteResguardoStatus' in solicitud:
			solicitud['expedienteResguardoStatus']=''

		if solicitud['expedienteResguardoStatus']=='':
			solicitud['expedienteResguardoStatus']="Comercial"



	if formData['accion']=="Expedientes Faltantes":
		now = datetime.date.today()
		fechaExigibilidad=now - datetime.timedelta(days=15)
		listaSolicitudes=list(filter(lambda d:
			(   (d["fechaEntregaARiesgos"]   >= inicio and
				d["fechaEntregaARiesgos"]   <= fin) and
			    d["expedienteResguardoStatus"]=="Comercial" and
			    ( d["solicitudEstatus"] == "FONDEADO" or d["solicitudEstatus"] == "RECHAZADO" )
			),listaSolicitudes))
		for solicitud in listaSolicitudes:
			solicitud["expedienteExigible"]="No"
			if solicitud['solicitudEstatus']=="FONDEADO":
				if solicitud['fechaEntregaContratoFirmado']<=str(fechaExigibilidad)+"23:59:59":
					solicitud["expedienteExigible"]="Sí"
			if solicitud['solicitudEstatus']=="RECHAZADO":
				if solicitud['fechaEntregaARiesgos']<=str(fechaExigibilidad)+"23:59:59":
					solicitud["expedienteExigible"]="Sí"
			if (solicitud['producto']=="Adelanto de Nómina" and
				solicitud['solicitudEstatus']=="RECHAZADO" and
				solicitud['fechaEntregaARiesgos']<"2023-01-01"
				):
				solicitud["expedienteExigible"]="No"

		listaSolicitudes=list(filter(lambda d:
			(d["expedienteExigible"]=="Sí"),listaSolicitudes))
		data["resumenProducto"]=obtenerResumenProductoExpedientesFaltantes(listaSolicitudes)
		data["resumenAsesor"]=obtenerResumenAsesorExpedientesFaltantes(listaSolicitudes)
		data["resumenEntregados"]=obtenerResumenEntregadosExpedientesFaltantes(inicio,fin)


	if formData['accion']!="Expedientes Faltantes":
		listaSolicitudes=list(filter(lambda d:
				(   d["fechaContratoImpreso"]   >= inicio and
					d["fechaContratoImpreso"]   <= fin and
					d["solicitudEstatus"] != "RECHAZADO"),
				listaSolicitudes))


	for solicitud in listaSolicitudes:
		#Obtengo listado de Asesores
		asesores = collections.defaultdict(list)

		if (solicitud['inheritedID']!=solicitud['ownerID'] and solicitud['inheritedID']!=""):
			solicitud['asesorNombre']="Otros"

		if 'montoComision' not in solicitud:
			solicitud['montoComision']=0

		if solicitud['montoComision']=="":
			solicitud['montoComision']=0


		for campo in esquemaReporte:

			if campo=="CLIENTE":
				renglon[campo]=solicitud[esquemaReporte[campo]]
				if solicitud["clienteApellidoPaterno"]!="":
					renglon[campo] += " "+ solicitud["clienteApellidoPaterno"]
				if solicitud["clienteApellidoMaterno"]!="":
					renglon[campo] += " "+ solicitud["clienteApellidoMaterno"]
				renglon[campo]=renglon[campo].upper()
				renglon[campo]=sub(' +', ' ', renglon[campo])

			else:
				if campo=="ID_SOLICITUD":
					renglon[campo]=int(solicitud[esquemaReporte[campo]])
				else:
					if esquemaReporte[campo] not in solicitud:
						solicitud[esquemaReporte[campo]]=""
					renglon[campo]=solicitud[esquemaReporte[campo]]

			if campo=="MONTO AUTORIZADO":
				if solicitud["producto"]=="Seguro":
					renglon["MONTO AUTORIZADO"]=solicitud["polizaSeguro"]

			if campo == "FECHA CONTRATO IMPRESO":
				renglon["FECHA CONTRATO IMPRESO"]=solicitud["fechaContratoImpreso"].split(" ")[0]

			if campo == "SEGURO FINANCIADO":
				if ("solicitudSeguroFinanciado" not in solicitud or
					solicitud["solicitudSeguroFinanciado"]==""):
					renglon["SEGURO FINANCIADO"]="0"


		renglones.append(renglon.copy())


	if formData['accion']=="Expedientes Faltantes":
		renglones=sorted(renglones, key=lambda k: (k["ESTATUS"],k["PRODUCTO"],k["PROMOTOR"],k["FECHA CONTRATO IMPRESO"],k["CLIENTE"]))
	else:
		renglones=sorted(renglones, key=lambda k: (k["PRODUCTO"],k["PROMOTOR"],k["FECHA CONTRATO IMPRESO"],k["CLIENTE"]))

	totales={}
	asesores=[]

	for renglon in renglones:
		if renglon["PROMOTOR"] not in asesores:
			asesores.append(renglon["PROMOTOR"])
	asesores=sorted(asesores)
	data['asesores']=asesores

	for producto in data['productos']:
		totales[producto]={}
		for asesor in asesores:
			totales[producto][asesor]={}
			totales[producto][asesor]["nombre"]=asesor
			totales[producto][asesor]["totalCreditos"]=0
			totales[producto][asesor]["totalCreditosNuevos"]=0
			totales[producto][asesor]["totalCreditosCleanUps"]=0
			totales[producto][asesor]["totalSegurosFinanciados"]=0
			totales[producto][asesor]["montoTotal"]=0
			totales[producto][asesor]["montoTotalTransferencia"]=0
			totales[producto][asesor]["montoTotalTransferenciaNuevos"]=0
			totales[producto][asesor]["montoTotalTransferenciaCleanUps"]=0
			totales[producto][asesor]["montoTotalComisiones"]=0
			totales[producto][asesor]["montoTotalSegurosFinanciados"]=0
			totales[producto][asesor]["0"]=0
			totales[producto][asesor]["25000"]=0
			totales[producto][asesor]["50000"]=0
			totales[producto][asesor]["75000"]=0
			totales[producto][asesor]["100000"]=0
			totales[producto][asesor]["totalSeguros"]=0
			totales[producto][asesor]["solicitudes"]=[]
			totales[producto][asesor]["eRatificacionDomiciliaria"]=0
			totales[producto][asesor]["eAvanceCleanUp"]=0
			totales[producto][asesor]["e1_7CleanUp"]=0
			totales[producto][asesor]["eBuro"]=0
			totales[producto][asesor]["totalExcepciones"]=0
			totales[producto][asesor]["totalExpedientesConExcepcion"]=0
			totales[producto][asesor]["expedientesComercial"]=0
			totales[producto][asesor]["expedientesRiesgos"]=0
			totales[producto][asesor]["expedientesBoveda"]=0


		totales[producto]['Total']={}
		totales[producto]['Total']["nombre"]="total"
		totales[producto]['Total']["totalCreditos"]=0
		totales[producto]['Total']["totalCreditosNuevos"]=0
		totales[producto]['Total']["totalCreditosCleanUps"]=0
		totales[producto]['Total']["totalSegurosFinanciados"]=0
		totales[producto]['Total']["montoTotal"]=0
		totales[producto]['Total']["montoTotalTransferencia"]=0
		totales[producto]['Total']["montoTotalTransferenciaNuevos"]=0
		totales[producto]['Total']["montoTotalTransferenciaCleanUps"]=0
		totales[producto]['Total']["montoTotalComisiones"]=0
		totales[producto]['Total']["montoTotalSegurosFinanciados"]=0
		totales[producto]['Total']["eRatificacionDomiciliaria"]=0
		totales[producto]['Total']["eAvanceCleanUp"]=0
		totales[producto]['Total']["e1_7CleanUp"]=0
		totales[producto]['Total']["eBuro"]=0
		totales[producto]['Total']["totalExcepciones"]=0
		totales[producto]['Total']["totalExpedientesConExcepcion"]=0
		totales[producto]['Total']["expedientesComercial"]=0
		totales[producto]['Total']["expedientesRiesgos"]=0
		totales[producto]['Total']["expedientesBoveda"]=0


	totales['Total']={}
	totales['Total']['Total']={}
	totales['Total']['Total']["nombre"]="Gran Total"
	totales['Total']['Total']["totalCreditos"]=0
	totales['Total']['Total']["totalCreditosNuevos"]=0
	totales['Total']['Total']["totalCreditosCleanUps"]=0
	totales['Total']['Total']["totalSegurosFinanciados"]=0
	totales['Total']['Total']["montoTotalSegurosFinanciados"]=0
	totales['Total']['Total']["montoTotal"]=0
	totales['Total']['Total']["montoTotalTransferencia"]=0
	totales['Total']['Total']["montoTotalTransferenciaNuevos"]=0
	totales['Total']['Total']["montoTotalTransferenciaCleanUps"]=0
	totales['Total']['Total']["montoTotalComisiones"]=0
	totales['Total']['Total']["montoTotalSegurosFinanciados"]=0
	totales['Total']['Total']["0"]=0
	totales['Total']['Total']["25000"]=0
	totales['Total']['Total']["50000"]=0
	totales['Total']['Total']["75000"]=0
	totales['Total']['Total']["100000"]=0
	totales['Total']['Total']["totalSeguros"]=0
	totales['Total']['Total']["eRatificacionDomiciliaria"]=0
	totales['Total']['Total']["eAvanceCleanUp"]=0
	totales['Total']['Total']["e1_7CleanUp"]=0
	totales['Total']['Total']["eBuro"]=0
	totales['Total']['Total']["totalExcepciones"]=0
	totales['Total']['Total']["totalExpedientesConExcepcion"]=0
	totales['Total']['Total']["expedientesComercial"]=0
	totales['Total']['Total']["expedientesRiesgos"]=0
	totales['Total']['Total']["expedientesBoveda"]=0



	for renglon in renglones:
		producto=renglon["PRODUCTO"]
		asesor=renglon["PROMOTOR"]
		if producto!="Seguro":
			totales['Total']['Total']["totalCreditos"]+=1
			totales['Total']['Total']["montoTotal"]+=float(renglon["MONTO AUTORIZADO"])
			totales['Total']['Total']["montoTotalTransferencia"]+=float(renglon["MONTO TRANSFERENCIA"])
			totales['Total']['Total']["montoTotalComisiones"]+=float(renglon["COMISION"])
			totales['Total']['Total']["montoTotalSegurosFinanciados"]+=float(renglon["SEGURO FINANCIADO"])
			if float(renglon["MONTO AUTORIZADO"]) == float(renglon["MONTO TRANSFERENCIA"]) :
				totales['Total']['Total']["totalCreditosNuevos"]+=1
				totales['Total']['Total']["montoTotalTransferenciaNuevos"]+=float(renglon["MONTO TRANSFERENCIA"])
			else:
				totales['Total']['Total']["totalCreditosCleanUps"]+=1
				totales['Total']['Total']["montoTotalTransferenciaCleanUps"]+=float(renglon["MONTO TRANSFERENCIA"])

			if renglon["expedienteResguardoStatus"]=="Comercial":
				totales['Total']['Total']["expedientesComercial"]+=1
			if renglon["expedienteResguardoStatus"]=="Riesgos":
				totales['Total']['Total']["expedientesRiesgos"]+=1
			if renglon["expedienteResguardoStatus"]=="Boveda":
				totales['Total']['Total']["expedientesBoveda"]+=1
			if renglon["excepcionDocumentada1"]!="":
				totales['Total']['Total']["totalExcepciones"] +=1
			if renglon["excepcionDocumentada2"]!="":
				totales['Total']['Total']["totalExcepciones"] +=1
			if renglon["excepcionDocumentada3"]!="":
				totales['Total']['Total']["totalExcepciones"] +=1

			if (renglon["excepcionDocumentada1"]!="" or
				renglon["excepcionDocumentada2"]!="" or
				renglon["excepcionDocumentada3"]!=""):
				totales['Total']['Total']["totalExpedientesConExcepcion"] +=1


		if producto=="Seguro":
			totales['Total']['Total'][renglon["MONTO AUTORIZADO"]]+=1
			totales['Total']['Total']["totalSeguros"]+=1
			totales[producto][asesor][renglon["MONTO AUTORIZADO"]]+=1
			totales[producto][asesor]["totalSeguros"]+=1


		totales[producto]['Total']["totalCreditos"]+=1
		totales[producto]['Total']["montoTotal"]+=float(renglon["MONTO AUTORIZADO"])
		totales[producto]['Total']["montoTotalTransferencia"]+=float(renglon["MONTO TRANSFERENCIA"])
		totales[producto]['Total']["montoTotalComisiones"]+=float(renglon["COMISION"])
		totales[producto]['Total']["montoTotalSegurosFinanciados"]+=float(renglon["SEGURO FINANCIADO"])
		if float(renglon["MONTO AUTORIZADO"]) == float(renglon["MONTO TRANSFERENCIA"]) :
			totales[producto]['Total']["totalCreditosNuevos"]+=1
			totales[producto]['Total']["montoTotalTransferenciaNuevos"]+=float(renglon["MONTO TRANSFERENCIA"])
		else:
			totales[producto]['Total']["totalCreditosCleanUps"]+=1
			totales[producto]['Total']["montoTotalTransferenciaCleanUps"]+=float(renglon["MONTO TRANSFERENCIA"])

		if renglon["expedienteResguardoStatus"]=="Comercial":
			totales[producto]['Total']["expedientesComercial"]+=1
		if renglon["expedienteResguardoStatus"]=="Riesgos":
			totales[producto]['Total']["expedientesRiesgos"]+=1
		if renglon["expedienteResguardoStatus"]=="Boveda":
			totales[producto]['Total']["expedientesBoveda"]+=1

		if renglon["excepcionDocumentada1"]!="":
			totales[producto]['Total']["totalExcepciones"] +=1
		if renglon["excepcionDocumentada2"]!="":
			totales[producto]['Total']["totalExcepciones"] +=1
		if renglon["excepcionDocumentada3"]!="":
			totales[producto]['Total']["totalExcepciones"] +=1
		if (renglon["excepcionDocumentada1"]!="" or
			renglon["excepcionDocumentada2"]!="" or
			renglon["excepcionDocumentada3"]!=""):
			totales[producto]['Total']["totalExpedientesConExcepcion"] +=1


		totales[producto][asesor]["totalCreditos"]+=1
		totales[producto][asesor]["montoTotal"]+=float(renglon["MONTO AUTORIZADO"])
		totales[producto][asesor]["montoTotalTransferencia"]+=float(renglon["MONTO TRANSFERENCIA"])
		totales[producto][asesor]["montoTotalComisiones"]+=float(renglon["COMISION"])
		totales[producto][asesor]["montoTotalSegurosFinanciados"]+=float(renglon["SEGURO FINANCIADO"])
		if float(renglon["MONTO AUTORIZADO"]) == float(renglon["MONTO TRANSFERENCIA"]) :
			totales[producto][asesor]["totalCreditosNuevos"]+=1
			totales[producto][asesor]["montoTotalTransferenciaNuevos"]+=float(renglon["MONTO TRANSFERENCIA"])
		else:
			totales[producto][asesor]["totalCreditosCleanUps"]+=1
			totales[producto][asesor]["montoTotalTransferenciaCleanUps"]+=float(renglon["MONTO TRANSFERENCIA"])

		if renglon["expedienteResguardoStatus"]=="Comercial":
			totales[producto][asesor]["expedientesComercial"]+=1
		if renglon["expedienteResguardoStatus"]=="Riesgos":
			totales[producto][asesor]["expedientesRiesgos"]+=1
		if renglon["expedienteResguardoStatus"]=="Boveda":
			totales[producto][asesor]["expedientesBoveda"]+=1

		if renglon["excepcionDocumentada1"]!="":
			totales[producto][asesor]["totalExcepciones"] +=1
		if renglon["excepcionDocumentada2"]!="":
			totales[producto][asesor]["totalExcepciones"] +=1
		if renglon["excepcionDocumentada3"]!="":
			totales[producto][asesor]["totalExcepciones"] +=1
		if (renglon["excepcionDocumentada1"]!="" or
			renglon["excepcionDocumentada2"]!="" or
			renglon["excepcionDocumentada3"]!=""):
			totales[producto][asesor]["totalExpedientesConExcepcion"] +=1

		totales[producto][asesor]["solicitudes"].append(renglon.copy())


	# print(json.dumps(totales,indent=4))

	data["series"]=totales

	for campo in esquemaReporte:
		headers.append(campo)

	data["headers"]=headers
	data["asesores"]=asesores
	data["formData"]=formData


	return data

def obtenerResumenProductoExpedientesFaltantes(listaSolicitudes):
	data={}
	for solicitud in listaSolicitudes:
		anioBase=solicitud["fechaEntregaARiesgos"].split("-")[0]
		if anioBase not in data:
			data[anioBase]={}
		if solicitud["producto"] not in data[anioBase]:
			data[anioBase][solicitud["producto"]]={}
		if 'fondeados' not in data[anioBase][solicitud["producto"]]:
			data[anioBase][solicitud["producto"]]["fondeados"]=0
		if 'rechazados' not in data[anioBase][solicitud["producto"]]:
			data[anioBase][solicitud["producto"]]["rechazados"]=0
		if 'total' not in data[anioBase][solicitud["producto"]]:
			data[anioBase][solicitud["producto"]]["total"]=0

		if 'total' not in data:
			data['total']={}
		if solicitud["producto"] not in data['total']:
			data['total'][solicitud['producto']]={}
		if 'fondeados' not in data['total'][solicitud["producto"]]:
			data['total'][solicitud["producto"]]["fondeados"]=0
		if 'rechazados' not in data['total'][solicitud["producto"]]:
			data['total'][solicitud["producto"]]["rechazados"]=0
		if 'total' not in data['total'][solicitud["producto"]]:
			data['total'][solicitud["producto"]]["total"]=0


		if solicitud["solicitudEstatus"]=="FONDEADO":
			data[anioBase][solicitud["producto"]]["fondeados"] +=1
			data['total'][solicitud["producto"]]["fondeados"] +=1

		if solicitud["solicitudEstatus"]=="RECHAZADO":
			data[anioBase][solicitud["producto"]]["rechazados"] +=1
			data['total'][solicitud["producto"]]["rechazados"] +=1

		data[anioBase][solicitud["producto"]]["total"] +=1
		data['total'][solicitud["producto"]]["total"] +=1

	return data

def obtenerResumenAsesorExpedientesFaltantes(listaSolicitudes):
	data={}
	for solicitud in listaSolicitudes:
		if (solicitud['inheritedID']!=solicitud['ownerID'] and solicitud['inheritedID']!=""):
			solicitud['asesorNombre']="Otros"

		anioBase=solicitud["fechaEntregaARiesgos"].split("-")[0]

		if solicitud["asesorNombre"] not in data:
			data[solicitud["asesorNombre"]]={}
		if solicitud["producto"] not in data[solicitud["asesorNombre"]]:
			data[solicitud["asesorNombre"]][solicitud['producto']]={}
		if anioBase not in data[solicitud["asesorNombre"]][solicitud['producto']]:
			data[solicitud["asesorNombre"]][solicitud['producto']][anioBase]={}
		if "fondeados" not in data[solicitud["asesorNombre"]][solicitud['producto']][anioBase]:
			data[solicitud["asesorNombre"]][solicitud['producto']][anioBase]["fondeados"]=0
		if "rechazados" not in data[solicitud["asesorNombre"]][solicitud['producto']][anioBase]:
			data[solicitud["asesorNombre"]][solicitud['producto']][anioBase]["rechazados"]=0
		if "total" not in data[solicitud["asesorNombre"]][solicitud['producto']][anioBase]:
			data[solicitud["asesorNombre"]][solicitud['producto']][anioBase]["total"]=0

		if 'total' not in data:
			data['total']={}
		if solicitud["producto"] not in data['total']:
			data['total'][solicitud['producto']]={}
		if anioBase not in data['total'][solicitud["producto"]]:
			data['total'][solicitud['producto']][anioBase]={}
		if 'fondeados' not in data['total'][solicitud["producto"]][anioBase]:
			data['total'][solicitud["producto"]][anioBase]["fondeados"]=0
		if 'rechazados' not in data['total'][solicitud["producto"]][anioBase]:
			data['total'][solicitud["producto"]][anioBase]["rechazados"]=0
		if 'total' not in data['total'][solicitud["producto"]][anioBase]:
			data['total'][solicitud["producto"]][anioBase]["total"]=0

		if solicitud["solicitudEstatus"]=="FONDEADO":
			data[solicitud["asesorNombre"]][solicitud["producto"]][anioBase]["fondeados"] +=1
			data['total'][solicitud["producto"]][anioBase]["fondeados"] +=1

		if solicitud["solicitudEstatus"]=="RECHAZADO":
			data[solicitud["asesorNombre"]][solicitud["producto"]][anioBase]["rechazados"] +=1
			data['total'][solicitud["producto"]][anioBase]["rechazados"] +=1

		data[solicitud["asesorNombre"]][solicitud["producto"]][anioBase]["total"] +=1
		data["total"][solicitud["producto"]][anioBase]["total"] +=1

	return data

def obtenerResumenEntregadosExpedientesFaltantes(inicio, fin):

	listaSolicitudes = update.reloadJSONData("working/solicitudes.json")
	listaSolicitudes.pop(0)

	seguros=obtenerSegurosdeSolicitudes()
	for seguro in seguros:
		if seguro["polizaSeguro"]=="Ninguna":
			seguro["montoAutorizado"]="0"
		listaSolicitudes.append(seguro.copy())

	listaSolicitudes = sorted(listaSolicitudes, key=lambda k: (k['producto'],k['fechaFondeado']))

	for solicitud in listaSolicitudes:
		if not 'expedienteResguardoStatus' in solicitud:
			solicitud['expedienteResguardoStatus']=''

		if solicitud['expedienteResguardoStatus']=='':
			solicitud['expedienteResguardoStatus']="Comercial"

	listaSolicitudes=listaSolicitudes=list(filter(lambda d:
	(   (d["fechaEntregaARiesgos"]   >= inicio and
		d["fechaEntregaARiesgos"]   <= fin) and
	    (d["expedienteResguardoStatus"]=="Boveda" or d["expedienteResguardoStatus"]=="Riesgos") and
	    ( d["solicitudEstatus"] == "FONDEADO" or d["solicitudEstatus"] == "RECHAZADO" )
	),listaSolicitudes))


	dt = datetime.datetime.now()
	inicioSemanaActual = dt - datetime.timedelta(days=dt.weekday())
	finSemanaActual = inicioSemanaActual + datetime.timedelta(days=6)

	inicioSemanaAnterior=dt - datetime.timedelta(days=dt.weekday()+7)
	finSemanaAnterior=inicioSemanaAnterior + datetime.timedelta(days=6)

	data={}
	data["semanaAnterior"]={}
	data["semanaActual"]={}


	for solicitud in listaSolicitudes:
		anioBase=solicitud["fechaEntregaARiesgos"].split("-")[0]
		if anioBase not in data["semanaAnterior"]:
			data["semanaAnterior"][anioBase]={}
		if anioBase not in data["semanaActual"]:
			data["semanaActual"][anioBase]={}
		if solicitud["producto"] not in data["semanaAnterior"][anioBase]:
			data["semanaAnterior"][anioBase][solicitud["producto"]]=0
		if solicitud["producto"] not in data["semanaActual"][anioBase]:
			data["semanaActual"][anioBase][solicitud["producto"]]=0

		if "fechaExpedienteRecibidoRiesgos" in solicitud:
			if solicitud["fechaExpedienteRecibidoRiesgos"]!="":
				if (solicitud["fechaExpedienteRecibidoRiesgos"].split(" ")[0] >= str(inicioSemanaAnterior).split(" ")[0] and
					solicitud["fechaExpedienteRecibidoRiesgos"].split(" ")[0] <= str(finSemanaAnterior).split(" ")[0]):
					data["semanaAnterior"][anioBase][solicitud["producto"]] +=1

				if (solicitud["fechaExpedienteRecibidoRiesgos"].split(" ")[0] >= str(inicioSemanaActual).split(" ")[0] and
					solicitud["fechaExpedienteRecibidoRiesgos"].split(" ")[0] <= str(finSemanaActual).split(" ")[0]):
					data["semanaActual"][anioBase][solicitud["producto"]] +=1


	return data


def correctSolicitudesForRunTime(listaSolicitudes):
	for solicitud in listaSolicitudes:
		if (solicitud["inheritedID"]=="" and solicitud["ownerID"]!=""):
			solicitud["inheritedID"]=solicitud["ownerID"]
		solicitud["clienteNombre"]=solicitud["clienteNombre"].upper()
		solicitud["clienteApellidoPaterno"]=solicitud["clienteApellidoPaterno"].upper()
		solicitud["clienteApellidoMaterno"]=solicitud["clienteApellidoMaterno"].upper()
		solicitud["clientePagadora"]=""
		solicitud["voboRequerido"]="Sí"

		empresa=routes_empresas.getEmpresaByName(solicitud["clienteEmpresa"])
		if empresa:
			if "empresaPagadora" in empresa:
			    solicitud["clientePagadora"]=empresa["empresaPagadora"]
			if "voboRequerido" in empresa:
				solicitud["voboRequerido"]=empresa["voboRequerido"]
			if "empresaSegmentacionCobranza" in empresa:
				solicitud["empresaSegmentacionCobranza"]=empresa["empresaSegmentacionCobranza"]

		if solicitud["producto"]=="Adelanto de Nómina":
			solicitud["voboRequerido"]="No"



		solicitud["clienteEmpresa"]=solicitud["clienteEmpresa"].upper()
		# solicitud["asesorNombre"]=solicitud["asesorNombre"].upper()

	return listaSolicitudes


def reporteTexto(formData):
	data={}
	solicitudes=getSolicitudes(formData["ownerID"])
	data["user"]=solicitudes["user"]
	data["headers"]={}
	data["reporte"]=[]

	if "solicitudNumeroControl:Solicitud Numero De Control" not in formData["camposSolicitados"]:
		formData["camposSolicitados"]="solicitudNumeroControl:Solicitud Numero De Control|" + formData["camposSolicitados"]

	if "id:Id" not in formData["camposSolicitados"]:
		formData["camposSolicitados"]="id:Id|" + formData["camposSolicitados"]

	camposSolicitados=formData["camposSolicitados"].split("|")
	campos=[]
	encabezados=[]
	for campo in camposSolicitados:
		if campo!="":
			campos.append(campo.split(":")[0])
			encabezados.append(campo.split(":")[1])
	data["headers"]=encabezados
	data["campos"]=campos

	# Aqui aplicar filtros sobre  solicitudes['listaSolicitudes']
	fechaInicio=""
	fechaFin=""
	fechaCriterio=formData["fechaCriterio"]
	filtroCriterio1=formData["filtroCriterio1"]
	filtroValor1=formData["filtroValor1"].upper()
	filtroCriterio2=formData["filtroCriterio2"]
	filtroValor2=formData["filtroValor2"].upper()
	filtroCriterio3=formData["filtroCriterio3"]
	filtroValor3=formData["filtroValor3"].upper()

	if "fechaInicio" in formData:
		fechaInicio= formData["fechaInicio"]
	if "fechaFin" in formData:
		fechaFin=formData["fechaFin"]

	if(fechaCriterio==""):
			fechaCriterio="fechaContacto"

	if (fechaInicio != "" and fechaFin!=""):
		if(fechaFin < fechaInicio):
			fechaInicio=fechaFin
			fechaFin=formData["fechaInicio"]

	if filtroCriterio1 in camposNumericos:
		try:
			filtroValor1=float(filtroValor1)
		except ValueError:
			filtroValor1=0.00
		filtroValor1=str(filtroValor1)

	if filtroCriterio2 in camposNumericos:
		try:
			filtroValor2=float(filtroValor2)
		except ValueError:
			filtroValor2=0.00
		filtroValor2=str(filtroValor2)

	if filtroCriterio3 in camposNumericos:
		try:
			filtroValor3=float(filtroValor3)
		except ValueError:
			filtroValor3=0.00
		filtroValor3=str(filtroValor3)


	listaSolicitudes=solicitudes['listaSolicitudes']

	for solicitud in listaSolicitudes:
		if fechaCriterio not in solicitud:
			solicitud[fechaCriterio]=""

		if filtroCriterio1 not in solicitud:
			solicitud[filtroCriterio1]=""
		if filtroCriterio1 in camposNumericos:
			if type(solicitud[filtroCriterio1]=="str"):
				if solicitud[filtroCriterio1].strip() == "" :
					solicitud[filtroCriterio1]="0.00"
			solicitud[filtroCriterio1]=str(float(solicitud[filtroCriterio1]))

		if filtroCriterio2 not in solicitud:
			solicitud[filtroCriterio2]=""
		if filtroCriterio2 in camposNumericos:
			if type(solicitud[filtroCriterio2]=="str"):
				if solicitud[filtroCriterio2].strip() == "" :
					solicitud[filtroCriterio2]="0.00"
			solicitud[filtroCriterio2]=str(float(solicitud[filtroCriterio2]))

		if filtroCriterio3 not in solicitud:
			solicitud[filtroCriterio3]=""
		if filtroCriterio3 in camposNumericos:
			if type(solicitud[filtroCriterio3]=="str"):
				if solicitud[filtroCriterio3].strip() == "" :
					solicitud[filtroCriterio3]="0.00"
			solicitud[filtroCriterio3]=str(float(solicitud[filtroCriterio3]))



	if fechaInicio !="":
		fechaInicio=fechaInicio+" 00:00:00"
		listaSolicitudes=list(filter(lambda d:
			(d[fechaCriterio]   >= fechaInicio),
			listaSolicitudes))


	if fechaFin !="":
		fechaFin=fechaFin+" 23:59:59"
		listaSolicitudes=list(filter(lambda d:
			(d[fechaCriterio]  <= fechaFin),
			listaSolicitudes))



	# FILTRO 1
	if filtroCriterio1 != "" and filtroCriterio1!="clienteNombre":
		listaSolicitudes=list(filter(lambda d:
			( filtroValor1.upper() in d[filtroCriterio1].upper() ),
			listaSolicitudes))

	if filtroCriterio1 in camposNumericos:
		listaSolicitudes=list(filter(lambda d:
			( filtroValor1.upper() == d[filtroCriterio1].upper() ),
			listaSolicitudes))

	if ( (filtroCriterio1=="producto") and
		 ("ADELANTO" not in filtroValor1)):
		listaSolicitudes=list(filter(lambda d:
			( "ADELANTO" not in d[filtroCriterio1].upper() ),
			listaSolicitudes))

	if filtroCriterio1 =="clienteNombre":
		listaSolicitudes=list(filter(lambda d:
			( filtroValor1.upper() in d["clienteNombre"].upper() or
			  filtroValor1.upper() in d["clienteApellidoPaterno"].upper() or
			  filtroValor1.upper() in d["clienteApellidoMaterno"].upper()
			),
			listaSolicitudes))

	# FILTRO 2
	if filtroCriterio2 != "" and filtroCriterio2!="clienteNombre":
		listaSolicitudes=list(filter(lambda d:
			( filtroValor2.upper() in d[filtroCriterio2].upper() ),
			listaSolicitudes))

	if filtroCriterio2 in camposNumericos:
		listaSolicitudes=list(filter(lambda d:
			( filtroValor2.upper() == d[filtroCriterio2].upper() ),
			listaSolicitudes))

	if ( (filtroCriterio2=="producto") and
		 ("ADELANTO" not in filtroValor2)):
		listaSolicitudes=list(filter(lambda d:
			( "ADELANTO" not in d[filtroCriterio2].upper() ),
			listaSolicitudes))

	if filtroCriterio2 =="clienteNombre":
		listaSolicitudes=list(filter(lambda d:
			( filtroValor2.upper() in d["clienteNombre"].upper() or
			  filtroValor2.upper() in d["clienteApellidoPaterno"].upper() or
			  filtroValor2.upper() in d["clienteApellidoMaterno"].upper()
			),
			listaSolicitudes))

	# FILTRO 3
	if filtroCriterio3 != "" and filtroCriterio3!="clienteNombre":
		listaSolicitudes=list(filter(lambda d:
			( filtroValor2.upper() in d[filtroCriterio2].upper() ),
			listaSolicitudes))

	if filtroCriterio2 in camposNumericos:
		listaSolicitudes=list(filter(lambda d:
			( filtroValor3.upper() == d[filtroCriterio3].upper() ),
			listaSolicitudes))

	if filtroCriterio3=="producto" and "ADELANTO" not in filtroValor3.upper:
		listaSolicitudes=list(filter(lambda d:
			( "ADELANTO" not in d[filtroCriterio2].upper() ),
			listaSolicitudes))

	if filtroCriterio3 =="clienteNombre":
		listaSolicitudes=list(filter(lambda d:
			( filtroValor3.upper() in d["clienteNombre"].upper() or
			  filtroValor3.upper() in d["clienteApellidoPaterno"].upper() or
			  filtroValor3.upper() in d["clienteApellidoMaterno"].upper()
			),
			listaSolicitudes))


	for solicitud in listaSolicitudes:
		registro={}
		for idx, campo in enumerate(campos):
			if campo in solicitud:
				registro[encabezados[idx]]=solicitud[campo]
			if campo not in solicitud:
				registro[encabezados[idx]]=""
		data["reporte"].append(registro.copy())

	# AQUI ORDENAR POR ID
	data["reporte"]=sorted( data["reporte"], key=lambda k: int(k["Id"]) )

	return data


def getMontosTransferenciasSinFondear():
    data={}
    registro={}
    data["productos"]=["Nómina","Adelanto de Nómina"]
    listaSolicitudes = update.reloadJSONData("working/solicitudes.json")
    listaSolicitudes.pop(0)
    listaSolicitudes = sorted(listaSolicitudes, key=lambda k: (k['producto'],k['fechaFondeado']))
    listaSolicitudes=list(filter(lambda d:
    	(   d["montoTransferencia"]   != "" and
    		d["solicitudEstatus"] != "RECHAZADO" and
    		d["solicitudEstatus"] != "FONDEADO"
    	),listaSolicitudes))
    totalMontoTransferenciaAutorizado=0

    for producto in data["productos"]:
    	data[producto]["Total"]=0.00

    for solicitud in listaSolicitudes:
    	print("Por Transferir:"+solicitud["montoTransferencia"])
    	totalMontoTransferenciaAutorizado += float(solicitud["montoTransferencia"])
    	nombre=solicitud["clienteNombre"]+" "+ solicitud["clienteApellidoPaterno"]+  solicitud["clienteApellidoMaterno"]
    	montoTransferencia=solicitud["montoTransferencia"]

    if montoTransferencia.replace(".","").isnumeric():
    	if float(montoTransferencia)>0:
    		data[producto][nombre]=montoTransferencia
    		data[producto][nombre]["solicitudEstatus"]=solicitud["solicitudEstatus"]
    		data[producto]["Total"] += float(montoTransferencia)

    data["granTotal"]=0.00
    for producto in data["productos"]:
    	data["granTotal"] += data[producto]["Total"]

    return data