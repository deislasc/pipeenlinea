import json
import update
import collections
import routes_users
import datetime
from routes_solicitudes import getIntervals as getIntervals


diasSemana=["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

def getAgendas(ownerID,formData):

	user=routes_users.getUser(ownerID)
	fechaInicio=""
	fechaFin=""
	fecha=""
	accion=""
	data = {}
	agendas=[]
	newData=[]


	if "accion" in formData:
		accion=formData["accion"]
		if accion=="Guardar":
			newData=limpiarDataConsulta(formData.copy())
			guardarCitas(newData)

	fecha=datetime.date.today()
	if "fechaInicio" in formData:
		fechaInicio=formData["fechaInicio"]
	else:
		fechaInicio = str(fecha) #- datetime.timedelta(days=fecha.weekday())

	if(fechaInicio<"2019-01-02"):
		fechaInicio="2019-01-02"

	if "fechaFin" in formData:
		fechaFin=formData["fechaFin"]
	else:
		fechaFin = str(fecha) #- datetime.timedelta(days=fecha.weekday())

	if(fechaFin<"2019-01-02"):
		fechaFin="2019-01-02"



	totalDias=days_between(fechaInicio,fechaFin)+1

	if "fecha" in formData:
		if formData["fecha"]!="":
			fecha=formData["fecha"]

	if "fechaInicio" in formData:
		if formData["fechaInicio"]!="":
			fechaInicio=formData["fechaInicio"]


	if "fechaFin" in formData:
		if formData["fechaFin"]!="":
			fechaFin=formData["fechaFin"]


	if "fechaInicio" not in formData:
		formData["fechaInicio"]=fechaInicio.split(" ")[0]
	if formData["fechaInicio"] =='':
		formData["fechaInicio"]=fechaInicio.split(" ")[0]


	if "fechaFin" not in formData:
		formData["fechaFin"]=fechaFin.split(" ")[0]
	if formData["fechaFin"] =='':
		formData["fechaFin"]=fechaFin.split(" ")[0]


	data["formData"]=formData



	asesores={}
	asesores=routes_users.getUsersList()
	asesores=list(filter(lambda d:  (d["acl"]=="asesor" or d["acl"]=="gestorCobranza") and d["userEstatus"]=="Activo", asesores))
	asesores= sorted(asesores, key=lambda k: (k['acl'],k['region']))
	if user["scope"]=="self":
		asesores=list(filter(lambda d:  d["ownerID"]==user["ownerID"], asesores))

	setHorarios=["5:00 a.m.","6:00 a.m.","7:00 a.m.","8:00 a.m.","9:00 a.m.","10:00 a.m.","11:00 a.m.","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00"]

	citas={}
	diasAgenda={}
	for asesor in asesores:
		citas[asesor["ownerID"]]={}
		for x in range(totalDias):
			fecha=datetime.datetime.strptime(fechaInicio, "%Y-%m-%d")
			fecha=fecha + datetime.timedelta(days=x)
			fechaStr=fecha.strftime("%d/%m/%Y")
			fecha=str(fecha).split(" ")[0]

			citas[asesor["ownerID"]][fecha]={}
			diasAgenda[fecha] = diasSemana[datetime.datetime.strptime(fecha, "%Y-%m-%d").weekday()] +" "+fechaStr
			for hora in setHorarios:
				citas[asesor["ownerID"]][fecha][hora]={}
				citas[asesor["ownerID"]][fecha][hora]["fecha"]=fecha
				citas[asesor["ownerID"]][fecha][hora]["hora"]=hora
				citas[asesor["ownerID"]][fecha][hora]["userName"]=asesor["userName"]
				citas[asesor["ownerID"]][fecha][hora]["ownerID"]=asesor["ownerID"]
				citas[asesor["ownerID"]][fecha][hora]["actividad"]=""
				citas[asesor["ownerID"]][fecha][hora]["empresa"]=""
				citas[asesor["ownerID"]][fecha][hora]["ubicacion"]=""
				citas[asesor["ownerID"]][fecha][hora]["clienteNombre"]=""
				citas[asesor["ownerID"]][fecha][hora]["clienteNuevoRenovacion"]=""
				citas[asesor["ownerID"]][fecha][hora]["comentarios"]=""

	user=routes_users.getUser(ownerID)

	listaAgendas=update.reloadJSONData("working/agendas.json")
	listaAgendas.pop(0)
	listaAgendas = list(filter(lambda d: d["fecha"] >= fechaInicio and d["fecha"] <= fechaFin , listaAgendas))
	# print(json.dumps(listaAgendas,indent=4))
	if user["scope"]=="self":
		listaAgendas = list(filter(lambda d: d["ownerID"] == user["ownerID"] , listaAgendas))


	# Aqui poner el codigo para acompletar las agendas
	for citaAgendada in listaAgendas:
		if citaAgendada["ownerID"] in citas:
			ownerIDAgenda=citaAgendada["ownerID"]
			if citaAgendada["fecha"] in citas[citaAgendada["ownerID"]]:
				fechaAgenda=citaAgendada["fecha"]
				if citaAgendada["hora"] in citas[citaAgendada["ownerID"]][citaAgendada["fecha"]]:
					horaAgenda=citaAgendada["hora"]
					citas[ownerIDAgenda][fechaAgenda][horaAgenda]["fecha"]=citaAgendada["fecha"]
					citas[ownerIDAgenda][fechaAgenda][horaAgenda]["hora"]=citaAgendada["hora"]
					citas[ownerIDAgenda][fechaAgenda][horaAgenda]["userName"]=citaAgendada["userName"]
					citas[ownerIDAgenda][fechaAgenda][horaAgenda]["ownerID"]=citaAgendada["ownerID"]
					citas[ownerIDAgenda][fechaAgenda][horaAgenda]["actividad"]=citaAgendada["actividad"]
					citas[ownerIDAgenda][fechaAgenda][horaAgenda]["empresa"]=citaAgendada["empresa"]
					citas[ownerIDAgenda][fechaAgenda][horaAgenda]["ubicacion"]=citaAgendada["ubicacion"]
					citas[ownerIDAgenda][fechaAgenda][horaAgenda]["clienteNombre"]=citaAgendada["clienteNombre"]
					citas[ownerIDAgenda][fechaAgenda][horaAgenda]["clienteNuevoRenovacion"]=citaAgendada["clienteNuevoRenovacion"]
					citas[ownerIDAgenda][fechaAgenda][horaAgenda]["comentarios"]=citaAgendada["comentarios"]
	# print(json.dumps(citas,indent=4))
	# print(json.dumps(diasAgenda,indent=4))
	data["user"]=user
	data["asesores"]=asesores
	data["citas"]=citas
	data["diasAgenda"]=diasAgenda
	return data

def limpiarDataConsulta(formData):
	if formData["accion"]=="Guardar":
		del formData["accion"]
		del formData["fechaInicio"]
		del formData["fechaFin"]
		formData["ownerID"]=formData["IdUsuarioAgenda"]
		del formData["IdUsuarioAgenda"]
		formData["comentarios"]=formData["comentarios"].replace('"',"")

	return formData


def guardarCitas(newData):
	listaAgendas=update.reloadJSONData("working/agendas.json")
	indices=[]
	for idx, cita in (enumerate(listaAgendas)):
		if (cita["ownerID"] == newData["ownerID"] and
			cita["fecha"] == newData["fecha"] and
			cita["hora"] == newData["hora"] ):
			indices.insert(0, idx)

	for indice in indices:
		del listaAgendas[indice]
	listaAgendas.append(newData)
	update.saveJsonData("working/agendas.json",listaAgendas)

	listaAgendas=update.reloadJSONData("working/agendas.json")
	return

def days_between(d1, d2):
    from datetime import datetime
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def reporteTexto(formData):
	data={}
	data["user"]=user=routes_users.getUser(formData["ownerID"])
	data["headers"]={}
	data["reporte"]=[]

	fechaInicio=""
	fechaFin=""
	fecha=""

	fecha=datetime.date.today()

	if "fechaInicio" in formData:
		fechaInicio=formData["fechaInicio"]
	else:
		fechaInicio = str(fecha) #- datetime.timedelta(days=fecha.weekday())

	if(fechaInicio<"2019-01-02" and fechaInicio!=""):
		fechaInicio="2019-01-02"

	if "fechaFin" in formData:
		fechaFin=formData["fechaFin"]
	else:
		fechaFin = str(fecha) #- datetime.timedelta(days=fecha.weekday())

	if(fechaFin<"2019-01-02" and fechaFin!=""):
		fechaFin="2019-01-02"

	if "fechaInicio" in formData:
		if formData["fechaInicio"]!="":
			fechaInicio=formData["fechaInicio"]


	if "fechaFin" in formData:
		if formData["fechaFin"]!="":
			fechaFin=formData["fechaFin"]

	if "fechaInicio" not in formData:
		formData["fechaInicio"]=fechaInicio.split(" ")[0]
	if formData["fechaInicio"] =='':
		formData["fechaInicio"]=fechaInicio.split(" ")[0]

	if "fechaFin" not in formData:
		formData["fechaFin"]=fechaFin.split(" ")[0]
	if formData["fechaFin"] =='':
		formData["fechaFin"]=fechaFin.split(" ")[0]


	agendas={}
	agendas=update.reloadJSONData("working/agendas.json")
	agendas.pop(0)

	if fechaInicio!="":
		agendas = list(filter(lambda d: d["fecha"] >= fechaInicio  , agendas))

	if fechaFin!="":
		agendas = list(filter(lambda d: d["fecha"] <= fechaFin , agendas))

	if "userName:NombreUsuario" not in formData["camposSolicitados"]:
		formData["camposSolicitados"]="userName:NombreUsuario|" + formData["camposSolicitados"]

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
	for cita in agendas:
		registro={}
		for idx, campo in enumerate(campos):
			if campo in cita:
				registro[encabezados[idx]]=cita[campo]
			if campo not in cita:
				registro[encabezados[idx]]=""
		data["reporte"].append(registro.copy())

	# AQUI ORDENAR POR NombreUsuario
	data["reporte"]=sorted( data["reporte"], key=lambda k: k["NombreUsuario"] )

	return data
