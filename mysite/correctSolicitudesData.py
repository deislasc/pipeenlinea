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
	python3 correctSolicitudesData
	

donde el archivo de solicitudes.json debe estar encriptado

'''
# **********************************************************
#             SE ENCRYPTAN ARCHIVOS POR PRIMERA VEZ-->
# **********************************************************


print(correctSolicitudesData());


# **********************************************************
#            <-- SE ENCRYPTAN ARCHIVOS POR PRIMERA VEZ
# **********************************************************