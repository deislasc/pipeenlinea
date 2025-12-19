import update
import config
import sys
import routes_users
import json


def getACLList(ownerID):
	data={}
	user=routes_users.getUser(ownerID)
	
	if "acl" in user:
		if user["acl"]!="sysAdmin":
			user["feedback"]="Usuario no Autorizado"
			data["list"]="Usuario no Autorizado"
			data["user"]=user
			return data


	
	aclList = update.reloadJSONData("working/acl.json")
	data["list"]=aclList
	data["user"]=user
	
	return data

def saveACLList(ownerID,acl):



	requiredACLS={
				  	"sysAdmin":{},
				  	"all":{},
				  	"all_limited":{},
				  	"oficialDeCumplimiento":{},
				  	"asesor":{},
				  	"gerenteComercial":{},
				  	"gerenteCartera":{},
				  	"gerenteRiesgos":{},
				  	"analistaRiesgos":{},
				  	"gestorCobranza":{},
				  	"supervisorContable":{},
				  	"analistaCumplimiento":{}
				}

	user=routes_users.getUser(ownerID)

	if "menuACL" in user["forbidden"]:
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

	newAcl=json.loads("[]")
	try:			
		newAcl=json.loads(acl)
	except:
		data={}
		user["feedback"]="Estructura Invalida."
		data["list"]="Estructura invalida. Vuelva a seleccionar ACL del menu principal."
		data["user"]=user
		return data

	for acl in newAcl:
		if "acl" not in acl:
			data={}
			user["feedback"]="Estructura Incompleta."
			data["list"]="Estructura Incompleta, verifique que todos los elementos cuenten con --> acl <--. Vuelva a seleccionar ACL del menu principal."
			data["user"]=user
			return data

		if "forbidden" not in acl:
			data={}
			user["feedback"]="Estructura Incompleta."
			data["list"]="Estructura Incompleta, verifique que todos los elementos cuenten con --> forbidden<--. Vuelva a seleccionar ACL del menu principal. <--"
			data["user"]=user
			return data

		if "scope" not in acl:
			data={}
			user["feedback"]="Estructura Incompleta."
			data["list"]="Estructura Incompleta, verifique que todos los elementos cuenten con --> scope <--. Vuelva a seleccionar ACL del menu principal."
			data["user"]=user
			return data

		if acl["acl"]=="":
			data={}
			user["feedback"]="Valor Inválido."
			data["list"]="Valor Inválido. El valor de --> acl <-- no puede estar vacio. Vuelva a seleccionar ACL del menu principal."
			data["user"]=user
			return data

		if acl["forbidden"]=="":
			data={}
			user["feedback"]="Valor Inválido."
			data["list"]="Valor Inválido. El valor de --> forbidden <-- no puede estar vacio. Vuelva a seleccionar ACL del menu principal."
			data["user"]=user
			return data

		if acl["scope"]=="":
			data={}
			user["feedback"]="Valor Inválido."
			data["list"]="Valor Inválido. El valor de --> scope <-- no puede estar vacio. Vuelva a seleccionar ACL del menu principal."
			data["user"]=user
			return data

		requiredACLS[acl["acl"]]["valid"]="true"

	

	string=""
	for acl in requiredACLS:
		if "valid" not in requiredACLS[acl]:
			string +="---> "+ acl + " <---"

	if string != "":
		data={}
		user["feedback"]="Esquema Incompleto"
		string  ="Esquema Incompleto. Falta Definir:"+string
		string +="Vuelva a seleccionar ACL del menu principal."

		data["list"]= string
		data["user"]=user
		return data

	fileName="working/acl.json"
	update.saveJsonData(fileName,newAcl)
	

	return getACLList(ownerID)



