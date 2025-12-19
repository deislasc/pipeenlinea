import json
import update
import collections
import routes_users

def getAsignacionEmpresas():

	empresas=update.reloadJSONData("working/empresas.json")
	asesores={}
	asesores=routes_users.getUsersList()
	asesores=list(filter(lambda d:  d["acl"]=="asesor" and d["userEstatus"]=="Activo", asesores))

	grouped={}

	for asesor in asesores:
		userField="userID_"+asesor['ownerID']
		if asesor['name'] not in grouped:
			grouped[asesor['name']]=[]
		for empresa in empresas:
			if empresa['ownerID']==asesor['ownerID']:
				grouped[asesor['name']].append(empresa)
			if (userField in empresa and empresa[userField]=="true"):
				grouped[asesor['name']].append(empresa)

	data = []
	asignacionPorAsesor={}

	for asesor, group in grouped.items():
		empresasAsignadas=[]
		if group:
			for item in group:
				empresasAsignadas.append(item["nombre"])

			asignacionPorAsesor["asesor"]=asesor
			asignacionPorAsesor["ownerID"]=group[0]["ownerID"]
			asignacionPorAsesor["empresas"]=empresasAsignadas
			data.append(asignacionPorAsesor.copy())

	return data

def getEmpresas(ownerID):
	data = {}
	exceptionArray=['ownerID','name','userEstatus','region']
	listaEmpresas=update.reloadJSONData("working/empresas.json")
	data['listaEmpresas']=listaEmpresas
	data['listaAsesores']=routes_users.getUsersByAcl("asesor",exceptionArray)
	data['user']=routes_users.getUser(ownerID)
	return data

def getEmpresasRestringidas():
	data = []
	exceptionArray=['ownerID','name']
	listaEmpresas=update.reloadJSONData("working/empresas.json")
	listaEmpresas=list(filter(lambda d: d["autorizacionDG"] == "Estricta", listaEmpresas))

	for i, item in enumerate(listaEmpresas):
		data.append(item["nombre"])

	return data


def correctEmpresasData():
	# Forma de ejecutar en consola
	# python3 -c "import routes_empresas; print (routes_empresas.correctEmpresasData())"

	fileName="working/empresas.json"

	json_object=update.reloadJSONData(fileName)

	json_object = sorted(json_object, key=lambda k: (k['nombre']))

	for i, item in enumerate(json_object):
		item["id"]=str(i)
		if item["region"]=="México":
			item["region"]="CDMX"


	update.saveJsonData(fileName,json_object)

	result={}
	result["message"]="Proceso Finalizado"
	return result

def getlistEmpresasTipo():
	data={}
	fileName="working/empresas.json"

	json_object=update.reloadJSONData(fileName)

	json_object = sorted(json_object, key=lambda k: (k['nombre']))
	for item in json_object:
		data[item["nombre"]]=item["tipo"]

	return data

def getEmpresaByName(nombre):
	data={}
	fileName="working/empresas.json"
	json_object=update.reloadJSONData(fileName)
	json_object = sorted(json_object, key=lambda k: (k['nombre']))
	data=list(filter(lambda d: d["nombre"] == nombre , json_object))
	if data:
		return data[0]
	else:
		return

def reporteTexto(formData):
	data={}
	empresas=getEmpresas(formData["ownerID"])
	data["user"]=empresas["user"]
	data["headers"]={}
	data["reporte"]=[]

	if "nombre:Nombre" not in formData["camposSolicitados"]:
		formData["camposSolicitados"]="nombre:Nombre|" + formData["camposSolicitados"]

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

	listaEmpresas=empresas['listaEmpresas']

	for empresa in listaEmpresas:
		registro={}
		for idx, campo in enumerate(campos):
			if campo in empresa:
				registro[encabezados[idx]]=empresa[campo]
			if campo not in empresa:
				registro[encabezados[idx]]=""
		data["reporte"].append(registro.copy())

	# AQUI ORDENAR POR ID
	data["reporte"]=sorted( data["reporte"], key=lambda k: int(k["Id"]) )

	return data



