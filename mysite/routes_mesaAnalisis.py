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
camposControlExpedientes=config.camposControlExpedientes


def getSolicitudesEnMesa(ownerID):
	import routes_solicitudes
	listaSolicitudes=routes_solicitudes.getSolicitudes(ownerID)["listaSolicitudes"]
	for solicitud in listaSolicitudes:
		if "analistaNombre" not in solicitud:
			solicitud['analistaNombre']=""
		if "estatusAnalisis" not in solicitud:
			solicitud["estatusAnalisis"]=""
	listaSolicitudes=list(filter(lambda d: ((d["solicitudEstatus"] == "CONTACTO" and d['analistaNombre']!="" ) or 
		                                     d["solicitudEstatus"] == "ENTREGA A RIESGOS"),listaSolicitudes))
 
	return listaSolicitudes



def actualizaCampos(formData):
	usuario=routes_users.getUser(formData["ownerID"])['userName']
	solicitudes={}
	for data in formData:
		if 'check' not in data:
			idx=data.split("_").pop()
			if(idx not in solicitudes):
				solicitudes[idx]={}
			solicitudes[idx][data.split("_")[0]]=formData[data]
	result=update.actualizarDataSolicitudes(solicitudes,formData)

	return result

def getMesaControl(formData,listaSolicitudes):
	
	if ('fechaInicio' in formData and 
		formData['fechaInicio'] != ""):
		fechaInicio=formData['fechaInicio']+" 00:00:00"
		listaSolicitudes=list(filter(lambda d:  d["fechaEntregaARiesgos"]>=fechaInicio, listaSolicitudes)) 
	
	if ('fechaFin' in formData and 
		formData['fechaFin'] != ""):
		fechaFin=formData['fechaFin']+" 23:59:59"
		listaSolicitudes=list(filter(lambda d:  d["fechaEntregaARiesgos"]<=fechaFin, listaSolicitudes))
	
	if ('producto' in formData and 
		formData['producto'] != "" and
		formData['producto'] != "General"):
		if formData['producto']=="Adelanto":
			listaSolicitudes=list(filter(lambda d: d["producto"]=="Adelanto de Nómina", listaSolicitudes))
		if formData['producto']=="Nómina":
			listaSolicitudes=list(filter(lambda d: d["producto"]=="Nómina", listaSolicitudes))
	
	if ('region' in formData and 
		formData['region'] != "" and 
		formData['region'] !="General"):
		listaSolicitudes=list(filter(lambda d:  d["regionNombre"]==formData['region'], listaSolicitudes))
	
	if ('asesor' in formData and 
		formData['asesor'] != ""):
		listaSolicitudes=list(filter(lambda d:  formData['asesor'].lower() in d["asesorNombre"].lower(), listaSolicitudes))
	
	if ('empresa' in formData and 
		formData['empresa'] != ""):
		listaSolicitudes=list(filter(lambda d:  formData['empresa'].lower() in d["clienteEmpresa"].lower(), listaSolicitudes))

	if ('cliente' in formData and 
		formData['cliente'] != ""):
		listaSolicitudes=getsolicitudesByFilter(listaSolicitudes,'clienteNombre',formData['cliente'])

	if ('analistaNombre' in formData and 
		formData['analistaNombre'] != "General"):
		listaSolicitudes=list(filter(lambda d:  formData['analistaNombre'] == d["analistaNombre"], listaSolicitudes))

	if ('estatusAnalisis' in formData and 
		formData['estatusAnalisis'] != "General"):
		listaSolicitudes=list(filter(lambda d:  formData['estatusAnalisis'] == d["estatusAnalisis"], listaSolicitudes))
	
	listaSolicitudes=sorted(listaSolicitudes, key=lambda k: (k["fechaEntregaARiesgos"]))

	return listaSolicitudes

def getsolicitudesByFilter(listaSolicitudes,field,value):
	data={}
	
	if field=="":
		return data

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

	return listaFiltro



