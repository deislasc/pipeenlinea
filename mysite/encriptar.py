import update
import config
import sys


'''
Este script se corre en la terminal
python3 enriptar nombreArchivo

donde nombre Archivo es un arhivo que está en el directorio "working"

si se pasa como nombre de archivo "all" significa que se encriptaran todos los archivos del directorio working

si se pasa como argumento "genNewKey"  se genera una nueva llave de encriptacion, perdiendose acceso a la informacion ya encriptada
'''
# **********************************************************
#             SE ENCRYPTAN ARCHIVOS POR PRIMERA VEZ-->
# **********************************************************



arguments=sys.argv

if arguments[1]=="genNewKey":
	# update.generate_key() ''' Sólo se corre una vez para crear la llave'''
	#print("Se genero una nueva llave de encriptado.")
	print("Active el código dentro del script")
	exit()

if arguments[1]=="all":
	db=config.DB
	for table in db:
		fileName=db[table]
		update.encrypt_file(fileName)
	print("Se encriptaron todos los archivos. Proceso finalizado.")
	exit()
else:
	fileName="working/"+arguments[1]
	update.encrypt_file(fileName)
	print("Se encriptó el archivo. Proceso finalizado.")
	exit()


''' IMPORTANTE:  PRIMERO SE DEBE CORRER EL PROCESO DE ENCRIPTACION Y DESPUES EL DE CORRECCIÒN DE ARCHIVOS
'''


# **********************************************************
#            <-- SE ENCRYPTAN ARCHIVOS POR PRIMERA VEZ
# **********************************************************