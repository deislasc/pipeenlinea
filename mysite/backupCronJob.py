import config
import sys
import datetime
import json
import os
import zipfile
import shutil


'''
Este script se corre en la terminal
python3 respaldar

Se genera un archivo año_mes_dia_backup
'''
# **********************************************************
#             SE GENERAN ARCHIVOS DE BACK UP-->
# **********************************************************



def copiarBD():
	workingDir="/home/pipeenlinea/"
	datetimeObj=datetime.datetime.now()
	fechaRespaldo=datetimeObj.strftime("%Y-%m-%d %H_%M_%S")
	dirPath=workingDir+"working/backup/"+fechaRespaldo;
	os.makedirs(dirPath)
	db=config.DB
	for table in db:
		fileName=workingDir+db[table]
		backupFile=workingDir+"working/backup/"+fechaRespaldo+"/"+table+".json"
		shutil.copyfile(fileName, backupFile)
	print("Se copiaron todos los archivos. Proceso finalizado.")
	comprimir(dirPath)
	print("Se comprimieron todos los archivos. Proceso finalizado.")
	removedir(dirPath)
	print("Se removió el directorio. Proceso finalizado.")

	myFile = open(workingDir+"mysite/appendBackUps.txt", "a")
	myFile.write('\nBackUp: ' + fechaRespaldo)
	myFile.close()

	return


def comprimir(dirPath):
	zipFileName=dirPath+".bku"
	zipf = zipfile.ZipFile(zipFileName, 'w', zipfile.ZIP_DEFLATED)
	zipdir(dirPath, zipf)
	zipf.close()
	return

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))
    return

def removedir(dirPath):
	if os.path.exists(dirPath):
		shutil.rmtree(dirPath)
	return


copiarBD()
exit()



# **********************************************************
#            <-- SE GENERAN ARCHIVOS DE BACK UP
# **********************************************************