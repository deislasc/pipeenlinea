import update
from routes_solicitudes import correctSolicitudesData  as correctSolicitudesData
from routes_empresas import correctEmpresasData as correctEmpresasData
from routes_logs import correctLogsData as correctLogsData
import config
import sys
import json


'''
Este script se corre en la terminal
python3 qaTools nombreArchivo

Ejemplo:
	python3 qaTools.py select fileName.json where field value
	python3 qaTools.py select solicitudes.json where id 6252
	python3 qaTools.py select users.json

	python3 qaTools.py update fileName.json where indexID field newValue
	python3 qaTools.py update solicitudes.json where id 6252 fechaContratoImpreso "2022-01-31 13:08:09"

	python3 qaTools.py update solicitudes.json where id 6252 fechaEntregaContratoFirmado "2022-01-31 13:08:09"

	python3 qaTools.py update solicitudes.json where id 7105 solicitudSeguroFinanciado "407.01"

	python3 mySite/qaTools.py update solicitudes.json where id 6252 usuarioAutorizacionRiesgos "Alicia Beatriz Hampton Coleman Toledano"

	python3 qaTools.py deleteField solicitudes.json where id 7104 userName
	python3 qaTools.py deleteField solicitudes.json where id 7104 viewrName

	python3 qaTools.py delete solicitudes.json where id 6252

donde el archivo de fileName.json debe estar encriptado

En produccion se debe poner python3
	python3 mysite/qaTools.py .....
	python3 mySite/qaTools.py select users.json
	python3 mysite/qaTools.py update solicitudes.json where id 7105 solicitudSeguroFinanciado "407.01"
	python3 mysite/qaTools.py update solicitudes.json where id 7102 montoComision "330.00"




'''



arguments=sys.argv
verbo = arguments[1]
fileName = arguments[2]


if (fileName=="solicitudes.json" or
	fileName=="users.json" or
	fileName=="logs.json" or
	fileName=="empresas.json" or
	fileName=="geolocations.json" or
	fileName=="acl.json"):
	fileName="working/" + fileName


json_object=update.reloadJSONData(fileName)

if verbo=="select":
	if 'where' in arguments:
		field = arguments[4]
		value= arguments[5]
		json_object = list(filter(lambda d: d[field] == value, json_object))
	print(json.dumps(json_object, indent=4))

if verbo=="update":
	indexID = int(arguments[5])
	field = arguments[6]
	print("field= "+field)
	# print(json.dumps(json_object[indexID],indent=4))
	if field in json_object[indexID]:

		newValue= arguments[7]
		print("Original: "+json_object[indexID][field])
		json_object[indexID][field]=newValue
		print("Final:"+json_object[indexID][field])
		# print(json.dumps(json_object,indent=4))
		update.saveJsonData(fileName,json_object)





if verbo=="deleteField":
	indexID = int(arguments[5])
	field = arguments[6]
	print("field= "+field)
	# print(json.dumps(json_object[indexID],indent=4))
	if field in json_object[indexID]:
		print("Original: "+json_object[indexID][field])
		if field in json_object[indexID]:
			del json_object[indexID][field]
		if field not in json_object[indexID]:
			print("Se eliminó el campo:"+field)
		update.saveJsonData(fileName,json_object)


if verbo=="delete":
	if 'where' in arguments:
		field = arguments[4]
		value= arguments[5]
		idx=0
		for indx, row in enumerate (json_object):
			if row[field] == value:
				idx=indx
				break
		print(json.dumps(json_object[idx],indent=4))
		print(type(json_object))
		print(idx)
		del json_object[idx]
	update.saveJsonData(fileName,json_object)




print("Proceso Finalizado")


# **********************************************************
#            <-- SE ENCRYPTAN ARCHIVOS POR PRIMERA VEZ
# **********************************************************