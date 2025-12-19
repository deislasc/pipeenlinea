import json
import datetime
import update
import routes_users
import update


def getLogs(ownerID,formData):
	data={}
	user=routes_users.getUser(ownerID)

	listaLogs = update.reloadJSONData("working/logs.json")
	listaLogs.pop(0)
	listaLogs = list(filter(lambda d: d["Objeto"] == "Solicitudes", listaLogs))

	if "fechaInicio" in formData:
		fechaInicio=formData["fechaInicio"]+" 00:00:00.00000"
		listaLogs = list(filter(lambda d: d["timeStamp"] >= fechaInicio, listaLogs))

	if "fechaFin" in formData:
		fechaFin=formData["fechaFin"]+" 23:59:59.99999"
		listaLogs = list(filter(lambda d: d["timeStamp"] <= fechaFin, listaLogs))
 	


	listaLogs=sorted(listaLogs, key=lambda k: k["timeStamp"], reverse=True)



	logs=[]

	fileName="working/solicitudes.json"
	solicitudes=update.reloadJSONData(fileName)

	for i, log in enumerate(listaLogs):
		if "Objeto" in log:
			if log["Objeto"]=="Solicitudes":
				# print(log["logData"]["id"])
				idx=int(log["logData"]["id"])
				log["solicitudNumeroControl"]=solicitudes[idx]["solicitudNumeroControl"]
				log["clienteNombre"]=solicitudes[idx]["clienteNombre"]

				if "clienteApellidoPaterno" in solicitudes[idx]:
					log["clienteNombre"] += " "+solicitudes[idx]["clienteApellidoPaterno"]
				if "clienteApellidoMaterno" in solicitudes[idx]:
					log["clienteNombre"] += " "+solicitudes[idx]["clienteApellidoMaterno"]
				if log["accion"]!="agregar":
					log["userName"] = log["logData"]["userName"]
				log["id"]=i+1

				if (solicitudes[idx]["solicitudEstatus"]!="FONDEADO"):
					logs.append(log)



	# if user["scope"]=="self":
	# 	listaLogs = list(filter(lambda d: d["inheritedID"] == user["ownerID"] or d["ownerID"] == user["ownerID"] , listaLogs))
	data["user"]=user
	data["listaLogs"]=logs
	return data

def correctLogsData():
	# Forma de ejecutar en consola
	# python3 -c "import routes_logs; print (routes_empresas.correctLogsData())"
	fileName="working/logs.json"

	json_object=update.reloadJSONData(fileName)


	for i, item in enumerate(json_object):
		if ("Objeto" not in item):

			viewName=item["logData"]["viewName"]
			if (viewName=="Solicitudes"  or
				viewName=="Contactados"   or
				viewName=="Entregados a Riesgos" or
				viewName=="Solicitar VoBo" or
				viewName=="Autorizacion Riesgos" or
				viewName=="Autorizacion DG" or
				viewName=="Imprimir Contrato" or
				viewName=="Firmar Contrato" or
				viewName=="Por Fondear" or
				viewName=="Transferencias" or
				viewName=="Fondeados" or
				viewName=="Rechazados" or
				viewName=="CLABES" or
				viewName=="Cobranza" or 
				viewName=="PreAnalisis" or
				viewName=="Analisis de Creditos" or
				viewName=="Revision Documental" or
				viewName=="Control de Expedientes"
				):
				item["Objeto"]="Solicitudes"
			elif viewName=="Usuarios":
				item["Objeto"]="Usuarios"
			elif viewName=="Perfil de Usuario":
				item["Objeto"]="Usuarios"
			elif viewName=="Log In":
				item["Objeto"]="Ingreso"
			elif viewName=="Empresas":
				item["Objeto"]="Empresas"
			elif viewName=="Asignaciones":
				item["Objeto"]="Empresas"
			elif viewName=="Operacion Interna Preocupante":
				item["Objeto"]="Operacion Interna Preocupante"
			elif viewName=="Operaciones Internas Preocupantes":
				item["Objeto"]="Operacion Interna Preocupante"

	update.saveJsonData(fileName,json_object)

	result={}
	result["message"]="Proceso Finalizado"
	return result

def getLogins(ownerID):
	data={}
	user=routes_users.getUser(ownerID)

	listaUsuarios=routes_users.getUsersList()
	listaUsuarios=list(filter(lambda d:d["userEstatus"]!="Baja",listaUsuarios))

	listaLogs = update.reloadJSONData("working/logs.json")
	listaLogs.pop(0)
	listaLogs = list(filter(lambda d: d["Objeto"] == "Ingreso" and d["accion"] == "Ingreso exitoso", listaLogs))


	data=[]

	for i, log in enumerate(listaLogs):
		row={}
		if "username" in log["logData"]:
			for userRow in  listaUsuarios:
				if log["logData"]["username"] == userRow["correo"]:
					row['usuario']=userRow["userName"]
			inicio=log["timeStamp"]
			hora_inicio=datetime.datetime.strptime(inicio,  "%Y-%m-%d %H:%M:%S.%f")
			hora_actual=datetime.datetime.now()
			diferencia= hora_actual - hora_inicio

			ajusteHorario=datetime.timedelta(minutes=360)
			inicio=hora_inicio - ajusteHorario
			row['Ingreso']=str(inicio)
			row['diferencia']=diferencia
			if(diferencia.total_seconds() / 60)>60:
				row['estatus']="expirada"
			else:
				row['estatus']="activa"

			if "usuario" in row:
				data.append(row)


	data = sorted(data, key=lambda k: (k['usuario'],k['Ingreso'].lower()),reverse=True)



	sesiones=[]
	usuario_actual=""

	for i, row in enumerate(data):
		usuario=row["usuario"]
		if usuario != usuario_actual:
			usuario_actual=usuario
			sesion={}
			sesion["usuario"]=row["usuario"]
			sesion["ingreso"]=row["Ingreso"]
			sesion["estatus"]=row["estatus"]
			sesiones.append(sesion)
	sesiones= sorted(sesiones, key= lambda k:k['ingreso'],reverse=True)

	data={}
	data["user"]=user
	data["sesiones"]=sesiones

	return data
