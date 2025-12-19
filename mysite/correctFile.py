import update
from routes_solicitudes import correctSolicitudesData  as correctSolicitudesData
from routes_empresas import correctEmpresasData as correctEmpresasData
from routes_logs import correctLogsData as correctLogsData
import config
import sys


'''
Este script se corre en la terminal
python3 correctFile nombreArchivo

Ejemplo:  
	python3 correctFile.py solicitudes.json
	python3 correctFile.py empresas.json
	python3 correctFile.py logs.json

donde nombre Archivo es un arhivo que está en el directorio "working" y sin "encriptar"

'''
# **********************************************************
#             SE ENCRYPTAN ARCHIVOS POR PRIMERA VEZ-->
# **********************************************************



arguments=sys.argv


fileName="working/"+arguments[1]
update.encrypt_file(fileName)
print("Se encriptó el archivo...")
if arguments[1]=="solicitudes.json":
	correctSolicitudesData();
if arguments[1]=="empresas.json":
	correctEmpresasData();
if arguments[1]=="logs.json":
	correctLogsData();

print("Se corrigió el archivo...")
print("Proceso finalizado.")
exit()


''' IMPORTANTE:  PRIMERO SE DEBE CORRER EL PROCESO DE ENCRIPTACION Y DESPUES EL DE CORRECCIÒN DE ARCHIVOS
'''


# **********************************************************
#            <-- SE ENCRYPTAN ARCHIVOS POR PRIMERA VEZ
# **********************************************************