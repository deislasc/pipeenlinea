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


def getExpedientes(formData,listaSolicitudes):
	if ( "numeroControl" not in formData or formData['numeroControl']=="" ):
		if ('fechaInicio' in formData and
			formData['fechaInicio'] != ""):
			listaSolicitudes=list(filter(lambda d:  (d["fechaEntregaARiesgos"]>=formData['fechaInicio'] or (d["fechaContacto"]>=formData['fechaInicio'] and "tipoBuroCredito" in d)) , listaSolicitudes))
		else:
			if ( "numeroControl" not in formData or formData['numeroControl']=="" ):
				currentYear = datetime.date.today().year
				fechaInicio=str(currentYear)+"-01-01"
				formData['fechaInicio']=fechaInicio
				listaSolicitudes=list(filter(lambda d:  d["fechaEntregaARiesgos"]>=fechaInicio, listaSolicitudes))

		if ('fechaFin' in formData and
			formData['fechaFin'] != ""):
			listaSolicitudes=list(filter(lambda d: (d["fechaEntregaARiesgos"]<=formData['fechaFin'] or (d["fechaContacto"]<=formData['fechaFin'] and "tipoBuroCredito" in d)), listaSolicitudes))

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

	if ('numeroControl' in formData and
		formData['numeroControl'] != ""):
		listaSolicitudes=list(filter(lambda d:  formData['numeroControl'].lower() in d["solicitudNumeroControl"].lower(), listaSolicitudes))

	if ('estatusResguardo' in formData and
			formData['estatusResguardo'] != ""):
			listaSolicitudes=list(filter(lambda d:  formData['estatusResguardo'].lower() == d['expedienteResguardoStatus'].lower(), listaSolicitudes))

	listaSolicitudes=sorted(listaSolicitudes, key=lambda k: (k['fechaContacto'].upper()))

	return listaSolicitudes


def completaDatosResguardo(listaSolicitudes):
	for idx, solicitud in enumerate(listaSolicitudes):
		if "expedienteResguardoStatus" not in listaSolicitudes[idx]:
			listaSolicitudes[idx]["expedienteResguardoStatus"]="Comercial"

	return listaSolicitudes

def actualizaCampos(formData):
	usuario=routes_users.getUser(formData["ownerID"])['userName']
	solicitudes={}
	for data in formData:
		if 'check' not in data:
			if ('ExpedienteRecibidoRiesgos' in data or
			   'ExpedienteRevisadoRiesgos' in data or
			   'ExpedienteDevueltoAComercial' in data or
			   'ExpedienteResguardadoEnBoveda' in data or
			   'comentariosResguardoExpedientes' in data):
				idx=data.split("_").pop()
				if(idx not in solicitudes):
					solicitudes[idx]={}
				solicitudes[idx][data.split("_")[0]]=formData[data]

	# Actualizo el estatus
	for idx in solicitudes:
		solicitudes[idx]['expedienteResguardoStatus']="Comercial"

		if  solicitudes[idx]['fechaExpedienteRecibidoRiesgos']!="":
			if solicitudes[idx]['fechaExpedienteRecibidoRiesgos'] > solicitudes[idx]['fechaExpedienteDevueltoAComercial']:
				solicitudes[idx]['fechaExpedienteDevueltoAComercial']=""
			solicitudes[idx]['expedienteResguardoStatus']="Riesgos"

		if  solicitudes[idx]['fechaExpedienteRevisadoRiesgos']!="":
			solicitudes[idx]['expedienteResguardoStatus']="Riesgos"

		if  solicitudes[idx]['fechaExpedienteDevueltoAComercial']!="":
			solicitudes[idx]['expedienteResguardoStatus']="Comercial"
			if solicitudes[idx]['fechaExpedienteDevueltoAComercial'] > solicitudes[idx]['fechaExpedienteResguardadoEnBoveda']:
				solicitudes[idx]['fechaExpedienteResguardadoEnBoveda']=""
			if solicitudes[idx]['fechaExpedienteDevueltoAComercial'] > solicitudes[idx]['fechaExpedienteRecibidoRiesgos']:
				solicitudes[idx]['fechaExpedienteRecibidoRiesgos']=""
			if solicitudes[idx]['fechaExpedienteDevueltoAComercial'] > solicitudes[idx]['fechaExpedienteRevisadoRiesgos']:
				solicitudes[idx]['fechaExpedienteRevisadoRiesgos']=""

		if  solicitudes[idx]['fechaExpedienteResguardadoEnBoveda']!="":
			solicitudes[idx]['expedienteResguardoStatus']="Boveda"
			if solicitudes[idx]['fechaExpedienteResguardadoEnBoveda'] > solicitudes[idx]['fechaExpedienteDevueltoAComercial']:
				solicitudes[idx]['fechaExpedienteDevueltoAComercial']=""

	result=update.actualizarDataControlExpedientes(solicitudes,formData)

	return result


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



