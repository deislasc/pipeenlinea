import update
import config
import sys
import routes_users
import json




def getPagadorasList(ownerID):
	data={}
	user=routes_users.getUser(ownerID)

	# if "acl" in user:
	# 	if user["acl"]!="sysAdmin":
	# 		user["feedback"]="Usuario no Autorizado"
	# 		data["list"]="Usuario no Autorizado"
	# 		data["user"]=user
	# 		return data

	data["user"]=user
	fileName="working/pagadoras.json"
	with open(fileName,'r') as f:
		contenido = f.read()
	pagadoras=json.loads(contenido)
	data["list"]=pagadoras
	return data

def savePagadorasList(ownerID,formData):

	user=routes_users.getUser(ownerID)

	if "menuPagadoras" in user["forbidden"]:
		data={}
		user["feedback"]="Usuario no Autorizado"
		data["list"]="Usuario no Autorizado"
		data["user"]=user
		return data

	if "acl" in user:
		if user["acl"]!="sysAdmin":
			data={}
			user["feedback"]="Usuario no Autorizado"
			data["list"]="Usuario no Autorizado"
			data["user"]=user
			return data

	contenidoStr=formData["contenido"].replace("\r\n","")

	contenido=json.loads("[]")

	try:
		contenido=json.loads(contenidoStr)
	except:
		data={}
		user["feedback"]="Estructura Invalida."
		data["list"]="Estructura invalida. Vuelva a seleccionar Pagadoras del menu principal."
		data["user"]=user
		return data

	# contenido=sorted(contenido)
	contenidoStr=(json.dumps(contenido,indent=4))
	fileName="working/pagadoras.json"
	with open(fileName,'w') as f:
		f.write(contenidoStr)
		f.close()
	return getPagadorasList(ownerID)



