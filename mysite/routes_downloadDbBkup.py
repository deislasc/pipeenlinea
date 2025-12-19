import glob

def getBackUpFiles():
	baseDir='/home/pipeenlinea/'
	baseDir=''  # Probar si funciona en produccion
	data={}
	listaarchivos=[]
	archivos=(glob.glob(baseDir+"working/backup/*.bku"))
	for archivo in archivos:
		archivo_nombre=archivo.split("/").pop()
		listaarchivos.append(archivo_nombre)
	listaarchivos.sort(reverse=True)
	data['archivos']=listaarchivos
	return data
