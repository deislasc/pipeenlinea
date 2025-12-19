import update
import routes_users,routes_OAuth2Generator,routes_BearerGenerator
import hashlib
from flask import session, current_app, Flask, request


def loginCheckByApiKey(data):
	listaUsuarios=update.reloadJSONData("working/users.json")
	listaUsuarios.pop(0)

	listaUsuariosToken=[]

	for usuario in listaUsuarios:
		if 'hash' in usuario:
			listaUsuariosToken.append(usuario.copy())

	if data['autorizationType']!='apiKey':
		result={}
		result["feedback"]="Token no Autorizado"
		result["code"]=404
		logData["resultado"]=result
		update.addLog(logData,accion="Ingreso fallido")
		return result

	loginHash=data['hash']
	usuario = []
	usuario = list(filter(lambda d: d["apiKey"] == loginHash, listaUsuariosToken))

	logData={}
	logData=routes_users.cleanUser(data)
	logData["viewName"]="Log In"

	if len(usuario)>0:
		usuario=usuario[0]
	else:
		result={}
		result["feedback"]="Token no Autorizado"
		result["code"]=404
		logData["resultado"]=result
		update.addLog(logData,accion="Ingreso fallido")
		return result

	if(usuario["userEstatus"]=="Baja"):
		result={}
		result["feedback"]="Usuario dado de baja"
		result["code"]=403
		logData["resultado"]=result
		update.addLog(logData,accion="Ingreso fallido")
		return result

	result={}
	result["feedback"]=""
	result["ownerID"]=usuario["ownerID"]
	result["code"]=200

	logData["resultado"]=result
	update.addLog(logData,accion="Ingreso exitoso")

	session['username'] = usuario['userName']
	auth_token=getUserBearer(usuario)
	result["auth_token"]=auth_token
	session['auth_token']=auth_token

	return result

def loginCheckByToken(data):
	listaUsuarios=update.reloadJSONData("working/users.json")
	listaUsuarios.pop(0)

	listaUsuariosToken=[]

	for usuario in listaUsuarios:
		if 'hash' in usuario:
			listaUsuariosToken.append(usuario.copy())

	if data['autorizationType']!='Bearer':
		result={}
		result["feedback"]="Token no Autorizado"
		result["code"]=404
		logData["resultado"]=result
		update.addLog(logData,accion="Ingreso fallido")
		return result

	loginHash=data['hash']
	usuario = []
	usuario = list(filter(lambda d: d["hash"] == loginHash, listaUsuariosToken))

	logData={}
	logData=routes_users.cleanUser(data)
	logData["viewName"]="Log In"


	if len(usuario)>0:
		usuario=usuario[0]
	else:
		result={}
		result["feedback"]="Token no Autorizado"
		result["code"]=404
		logData["resultado"]=result
		update.addLog(logData,accion="Ingreso fallido")
		return result

	if(usuario["userEstatus"]=="Baja"):
		result={}
		result["feedback"]="Usuario dado de baja"
		result["code"]=403
		logData["resultado"]=result
		update.addLog(logData,accion="Ingreso fallido")
		return result

	result={}
	result["feedback"]=""
	result["ownerID"]=usuario["ownerID"]
	result["code"]=200
	logData["resultado"]=result
	update.addLog(logData,accion="Ingreso exitoso")

	session['username'] = usuario['userName']
	auth_token=getUserBearer(usuario)
	result["auth_token"]=auth_token
	session['auth_token']=auth_token



	return result



def loginCheck(data):
	listaUsuarios=update.reloadJSONData("working/users.json")
	listaUsuarios.pop(0)

	data=hashLoggingUser(data)

	loginUser=data['username']
	loginPassword=data['password']
	loginHash=data['hash']
	usuario = []
	usuario = list(filter(lambda d: d["correo"] == loginUser, listaUsuarios))

	logData={}
	logData=routes_users.cleanUser(data)
	logData["viewName"]="Log In"


	if len(usuario)>0:
		usuario=usuario[0]
	else:
		result={}
		result["feedback"]="La combinación usuario y contraseña es incorrecta. Vuelva a intentar"
		result["code"]=404
		logData["resultado"]=result
		update.addLog(logData,accion="Ingreso fallido")
		return result

	if(usuario["userEstatus"]=="Baja"):
		result={}
		result["feedback"]="Usuario dado de baja"
		result["code"]=403
		logData["resultado"]=result
		update.addLog(logData,accion="Ingreso fallido")
		return result


	# print(">>>>>>>>>>>>>> EN CHECK IN RESULTADO  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
	if "hash" in usuario:
		currentHash=usuario["hash"]
		if currentHash!=loginHash:
			result={}
			result["feedback"]="La combinación usuario y contraseña es incorrecta. Vuelva a intentar"
			result["code"]=404
			logData["resultado"]=result
			update.addLog(logData,accion="Ingreso fallido")
			return result
		else:
			result={}
			result["feedback"]=""
			result["ownerID"]=usuario["ownerID"]
			result["code"]=200
			logData["resultado"]=result
			update.addLog(logData,accion="Ingreso exitoso")
			session['username'] = usuario['userName']
			auth_token=getUserBearer(usuario)
			result["auth_token"]=auth_token
			session['auth_token']=auth_token
			return result

	if "hash" not in usuario:
		currentPassword=usuario["password"]
		if currentPassword!=loginPassword:
			result={}
			result["feedback"]="La combinación usuario y contraseña es incorrecta. Vuelva a intentar"
			result["code"]=404
			logData["resultado"]=result
			update.addLog(logData,accion="Ingreso fallido")
			return result
		else:
			result={}
			result["feedback"]="Actualice su Password."
			result["ownerID"]=usuario["ownerID"]
			result["code"]=200
			logData["resultado"]=result
			update.addLog(logData,accion="Ingreso exitoso")
			session['username'] = usuario['userName']
			auth_token=getUserBearer(usuario)
			result["auth_token"]=auth_token
			session['auth_token']=auth_token
			return result




def hashLoggingUser(data):
	loginUser=data['username']
	loginPassword=data['password']
	hashed=loginPassword+loginUser
	hash_object = hashlib.sha512(hashed.encode())
	data["hash"]= hash_object.hexdigest()
	return data

def getUserOAuth(user):
	app = current_app
	hashed=''
	oauth_consumer_key=''
	access_key_secret=''
	url=str(request.url)

	if 'hash' not in user:
		hashed=user['password']+user['correo']
		hashed=hashlib.sha512(hashed.encode())
	else:
		hashed=user['hash']

	if user['tipoUsuario']=='Interno':
		oauth_consumer_key=app.config['SECRET_KEY']
	else:
		oauth_consumer_key=user['ApiKey']

	access_key_secret=hashed

	response=routes_OAuth2Generator.get_OAuth_Signature(oauth_consumer_key,access_key_secret,url)
	return response

def getUserBearer(user):
	auth_token=routes_BearerGenerator.encode_auth_token(user)
	return auth_token
	#return auth_token.decode()

def isLogInBearer(auth_token):
	response=routes_BearerGenerator.decode_auth_token(auth_token)
	return response





