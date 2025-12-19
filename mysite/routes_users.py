import json
import update

# Activar para subir a GCloud
from importlib import reload

def cleanUser(user):
	if "password" in user:
		del user["password"]
	if "hash" in user:
		del user["hash"]
	if "randomKey" in user:
		del user["randomKey"]
	if "apiKey" in user:
		del user["apiKey"]
	return user	

def cleanExcept(user,exceptionArray):
	newUser={}
	for item in user:
		if item in exceptionArray:
			newUser[item]=user[item]
	return newUser

def getUser(ownerID):
	noNumerico=False
	if ownerID.isnumeric()==False:
		noNumerico=True
	usuarios=update.reloadJSONData("working/users.json")
	usuarios.pop(0)
	listaAcl=update.reloadJSONData("working/acl.json")
	user=[]
	if noNumerico==False:
		user = list(filter(lambda d: d["ownerID"] == ownerID, usuarios))[0]
	else:
		user = list(filter(lambda d: d["name"] == ownerID, usuarios))[0]

	acl=list(filter(lambda d: d["acl"] == user["acl"], listaAcl))[0]
	user["scope"]=acl["scope"]
	user["forbidden"]=acl["forbidden"]
	user["feedback"]=""
	if "hash" not in user:
	    user["feedback"]="Actualice su Password."
	else:
		user["feedback"]=""
	cleanedUser=cleanUser(user)
	return cleanedUser

def getUsers(ownerID):
	user=getUser(ownerID)
	if "acl" in user["forbidden"]:
		response={}	
		response['data']=[]
		response['message']="Operación no permitida."	
		response['messageCode']="403"
		return(response)

	listaUsuarios=update.reloadJSONData("working/users.json")
	listaUsuarios.pop(0)


	usuarios = []
	for user in listaUsuarios:
	    usuarios.append(cleanUser(user).copy())

	usuarios=sorted(usuarios, key=lambda k: (k['userEstatus'],k['userName']))

	data={};
	data['listaUsuarios']=usuarios
	data['user']=getUser(ownerID)

	return data

def getUserProfile(ownerID):
	listaUsuarios=update.reloadJSONData("working/users.json")
	listaUsuarios.pop(0)
	listaUsuarios = list(filter(lambda d: d["ownerID"] == ownerID, listaUsuarios))
	usuarios = []
	for user in listaUsuarios:
	    usuarios.append(cleanUser(user).copy())

	data={};
	data['listaUsuarios']=usuarios
	data['user']=getUser(ownerID)
	return data

def getUsersList():
	listaUsuarios=update.reloadJSONData("working/users.json")
	listaUsuarios.pop(0)
	usuarios = []
	for user in listaUsuarios:
	    usuarios.append(cleanUser(user).copy())
	return usuarios

def getUsersByAcl(acl,exceptionArray):
	listaUsuarios=update.reloadJSONData("working/users.json")
	listaUsuarios.pop(0)
	listaUsuarios = list(filter(lambda d: d["acl"] == acl, listaUsuarios))
	usuarios = []
	for user in listaUsuarios:
	    usuarios.append(cleanExcept(user,exceptionArray).copy())

	data=[];
	data=usuarios
	return data

def getUsersByPuesto(puesto,exceptionArray):
	listaUsuarios=update.reloadJSONData("working/users.json")
	listaUsuarios.pop(0)
	listaUsuarios = list(filter(lambda d: d["puesto"] == puesto, listaUsuarios))
	usuarios = []
	for user in listaUsuarios:
	    usuarios.append(cleanExcept(user,exceptionArray).copy())

	data=[];
	data=usuarios
	return data

def getUserByName(name):
	usuarios=update.reloadJSONData("working/users.json")
	usuarios.pop(0)
	listaAcl=update.reloadJSONData("working/acl.json")
	user=[]
	user = list(filter(lambda d: d["name"] == name, usuarios))[0]
	acl=list(filter(lambda d: d["acl"] == user["acl"], listaAcl))[0]
	user["scope"]=acl["scope"]
	user["forbidden"]=acl["forbidden"]
	user["feedback"]=""
	if "password" in user:
	    user["feedback"]="Actualice su Password"
	cleanedUser=cleanUser(user)
	return cleanedUser


def addUser(data):
	
	return getUsersList();

