import json
import routes_empresas as empresas
import datetime
import config
import os

def actualizarCosechas(newData):
	result=True
	data={}
	fileName="working/cosechas.json"
	# 1.  Leer la data existente del archivo de cosechas
	data=leer_cosechas()
	# 2. Agregar nuevos registros a "cosechas.json"
	for row in newData:
		if "PERIODO" in row:
			key=row["PERIODO"]+"_"+row["NO. CONTROL"]
			if key not in data:
				data[key]={}
				data[key]["Capital Vencido"]={}
				data[key]["Interes Vencido"]={}
			for field in row:
				if "CV " in field:
					bucket=field.split(" ")[1]
					data[key]["Capital Vencido"][bucket]=row[field] 
				else:
					if "IV " in field:
						bucket=field.split(" ")[1]
						data[key]["Interes Vencido"][bucket]=row[field]
					else:
						data[key][field.strip()]=row[field]
		if "FECHA OTORGAMIENTO" in data[key]:
			if "-" in data[key]["FECHA OTORGAMIENTO"]:
				data[key]["MES OTORGAMIENTO"]=data[key]["FECHA OTORGAMIENTO"].split("-")[0] +"-" + data[key]["FECHA OTORGAMIENTO"].split("-")[1]
		if "NO. CONTROL" in data[key]:
			data[key]["PRODUCTO"]=getProductFrom(data[key]["NO. CONTROL"])
	# 3. Guardar el archivo cosechas.json
	salvar_cosechas(data)
	
    

	return result

def leer_cosechas():
	fileName="working/cosechas.json"
	data={}
	if os.path.exists(fileName):
		with open(fileName,'r') as json_file:
			data = json.load(json_file)
			json_file.close()
	return data

def salvar_cosechas(data):
	result=True
	fileName="working/cosechas.json"
	with open(fileName,'w') as f:
		json.dump(data, f,indent=4)
		f.close()
	return result

def getPeriodos_y_FechasDeOtorgamiento(formData):
	data={}
	periodos=[]
	mesesOtorgamiento=[]
	buckets=[]
	cosechas=leer_cosechas()

	inicio=""
	if ("fechaInicio" in formData and
		formData["fechaInicio"]!=""):
		inicio=formData["fechaInicio"].split("-")[0]+"-"+formData["fechaInicio"].split("-")[1]

	fin=""
	if ("fechaFin" in formData and
		formData["fechaFin"]!=""):
		fin=formData["fechaFin"].split("-")[0]+"-"+formData["fechaFin"].split("-")[1]	

	for cosecha in cosechas:
		if("PERIODO" in cosechas[cosecha] and
			cosechas[cosecha]["PERIODO"]!="" and 
			cosechas[cosecha]["PERIODO"] not in periodos):
				periodos.append(cosechas[cosecha]["PERIODO"])


		if("MES OTORGAMIENTO" in cosechas[cosecha] and
			cosechas[cosecha]["MES OTORGAMIENTO"]!="" and 
			cosechas[cosecha]["MES OTORGAMIENTO"] not in mesesOtorgamiento):
				mesesOtorgamiento.append(cosechas[cosecha]["MES OTORGAMIENTO"])

		if("Capital Vencido" in cosechas[cosecha]):
			for bucket in cosechas[cosecha]["Capital Vencido"]:
				if bucket not in buckets:
					buckets.append(bucket)
		
	periodos.sort(reverse=True)
	mesesOtorgamiento.sort(reverse=True)
	data["periodos"]=periodos
	data["mesesOtorgamiento"]=mesesOtorgamiento
	data["buckets"]=buckets
	data["productos"]=["Adelanto","ARF","ARR","CNP","CSP","Factoraje","Nómina","Seguro"]

	return data

def getProductFrom(valor=""):
	producto=""
	if valor=="":
		return producto

	if "SG" in valor:
		producto="Seguro"
		return producto 

	if "CNP" in valor:
		producto="CNP"
		return producto 

	if "CN" in valor:
		producto="Nómina"
		return producto 

	if "AN" in valor:
		producto="Adelanto"
		return producto 

	if "CSP" in valor:
		producto="CSP"
		return producto 

	if "ARF" in valor:
		producto="ARF"
		return producto 

	if "ARR" in valor:
		producto="ARR"
		return producto 

	if "FACT" in valor:
		producto="Factoraje"
		return producto 

	return producto

def getGraficaCosechas(formData):
	data={}
	# print("graficar")
	return data


def getTabularCosechas(formData):
	# print(formData)
	data={}
	cosechas=leer_cosechas()
	cosechas=filtraPorProducto(formData,cosechas)
	cosechas=filtraPorDesde(formData,cosechas)
	cosechas=filtraPorHasta(formData,cosechas)
	data=getPeriodos_y_FechasDeOtorgamiento(formData)
	data=getCosechas(data,cosechas,formData["contenidoTipo"],formData["accion"])
	return data

def filtraPorProducto(formData,cosechas):
	filtroCosechas={}
	for cosecha in cosechas:
		if cosechas[cosecha]['PRODUCTO']==formData['producto']:
			filtroCosechas[cosecha]=cosechas[cosecha]
		if formData['producto']=="General" and cosechas[cosecha]['PRODUCTO']!="":
			filtroCosechas[cosecha]=cosechas[cosecha]
	
	return filtroCosechas

def filtraPorDesde(formData,cosechas):
	filtroCosechas={}
	if ("fechaInicio" not in formData or
		formData["fechaInicio"]==""):
		return cosechas
	inicio=formData["fechaInicio"].split("-")[0]+"-"+formData["fechaInicio"].split("-")[1]
	for cosecha in cosechas:
		if("MES OTORGAMIENTO" in cosechas[cosecha] and 
			"PERIODO" in cosechas[cosecha]):
			if (cosechas[cosecha]['PERIODO']>=inicio and
				cosechas[cosecha]["MES OTORGAMIENTO"]>=inicio):
				filtroCosechas[cosecha]=cosechas[cosecha]
	return filtroCosechas

def filtraPorHasta(formData,cosechas):
	filtroCosechas={}
	if ("fechaFin" not in formData or
		formData["fechaFin"]==""):
		return cosechas
	fin=formData["fechaFin"].split("-")[0]+"-"+formData["fechaFin"].split("-")[1]
	for cosecha in cosechas:
		if("MES OTORGAMIENTO" in cosechas[cosecha] and 
			"PERIODO" in cosechas[cosecha]):
			if (cosechas[cosecha]['PERIODO']<=fin and
				cosechas[cosecha]["MES OTORGAMIENTO"]<=fin):
				filtroCosechas[cosecha]=cosechas[cosecha]
	return filtroCosechas

def getCosechas(data,cosechas,contenidoTipo,tabularTipo):
	if "Periodo/Otorgamiento" in tabularTipo:
		data=getReportePeriodoOtorgamiento(data,cosechas,contenidoTipo)

	if "Otorgamiento/Periodo" in tabularTipo:
		data=getReporteOtorgamientoPeriodo(data,cosechas,contenidoTipo)

	return data

def getReportePeriodoOtorgamiento(data,cosechas,contenidoTipo):
	reporte={}
	for periodo in data["periodos"]:
		reporte[periodo]={}
		for mesOtorgamiento in data["mesesOtorgamiento"]:
			reporte[periodo][mesOtorgamiento]={}
			reporte[periodo][mesOtorgamiento]["Capital Vencido"]={}
			reporte[periodo][mesOtorgamiento]["Interes Vencido"]={}
			reporte[periodo][mesOtorgamiento]["Total Vencido"]={}
	


	for cosecha in cosechas:
		if "Capital Vencido" in cosechas[cosecha]:
			if "MES OTORGAMIENTO" in cosechas[cosecha]:			
				periodo=cosechas[cosecha]["PERIODO"]
				mesOtorgamiento=cosechas[cosecha]["MES OTORGAMIENTO"]
				if "Monto Colocacion" not in reporte[periodo][mesOtorgamiento]:
					reporte[periodo][mesOtorgamiento]["Monto Colocacion"]=0.00
				valorMonto=float(cosechas[cosecha]["MONTO"])
				reporte[periodo][mesOtorgamiento]["Monto Colocacion"]+=valorMonto

				for bucket in cosechas[cosecha]["Capital Vencido"]:
					if bucket not in reporte[periodo][mesOtorgamiento]["Capital Vencido"]:
						reporte[periodo][mesOtorgamiento]["Capital Vencido"][bucket]=0.00
						reporte[periodo][mesOtorgamiento]["Interes Vencido"][bucket]=0.00
						reporte[periodo][mesOtorgamiento]["Total Vencido"][bucket]=0.00					
					
					if cosechas[cosecha]["Capital Vencido"][bucket]=="":
						valorCapital=0.00
					else:
						valorCapital=float(cosechas[cosecha]["Capital Vencido"][bucket])
					
					if cosechas[cosecha]["Interes Vencido"][bucket]=="":
						valorInteres=0.00
					else:
						valorInteres=float(cosechas[cosecha]["Interes Vencido"][bucket])						

					
					reporte[periodo][mesOtorgamiento]["Capital Vencido"][bucket]+=valorCapital
					reporte[periodo][mesOtorgamiento]["Interes Vencido"][bucket]+=valorInteres
					reporte[periodo][mesOtorgamiento]["Total Vencido"][bucket]+=valorCapital+valorInteres

	reporteFinal={}
	for periodo in reporte:
		for renglon in reporte[periodo]:
			if "Monto Colocacion" in reporte[periodo][renglon]:
				if periodo not in reporteFinal:
					reporteFinal[periodo]={}
				reporteFinal[periodo][renglon]=reporte[periodo][renglon]

	data["renglones"]=reporteFinal
	return data


def getReporteOtorgamientoPeriodo(data,cosechas,contenidoTipo):
	reporte={}
	for mesOtorgamiento in data["mesesOtorgamiento"]:
		reporte[mesOtorgamiento]={}
		for periodo in data["periodos"]:
		
			reporte[mesOtorgamiento][periodo]={}
			reporte[mesOtorgamiento][periodo]["Capital Vencido"]={}
			reporte[mesOtorgamiento][periodo]["Interes Vencido"]={}
			reporte[mesOtorgamiento][periodo]["Total Vencido"]={}
	


	for cosecha in cosechas:
		if "Capital Vencido" in cosechas[cosecha]:
			if "MES OTORGAMIENTO" in cosechas[cosecha]:			
				periodo=cosechas[cosecha]["PERIODO"]
				mesOtorgamiento=cosechas[cosecha]["MES OTORGAMIENTO"]
				if "Monto Colocacion" not in reporte[mesOtorgamiento][periodo]:
					reporte[mesOtorgamiento][periodo]["Monto Colocacion"]=0.00
				valorMonto=float(cosechas[cosecha]["MONTO"])
				reporte[mesOtorgamiento][periodo]["Monto Colocacion"]+=valorMonto

				for bucket in cosechas[cosecha]["Capital Vencido"]:
					if bucket not in reporte[mesOtorgamiento][periodo]["Capital Vencido"]:
						reporte[mesOtorgamiento][periodo]["Capital Vencido"][bucket]=0.00
						reporte[mesOtorgamiento][periodo]["Interes Vencido"][bucket]=0.00
						reporte[mesOtorgamiento][periodo]["Total Vencido"][bucket]=0.00					
					
					if cosechas[cosecha]["Capital Vencido"][bucket]=="":
						valorCapital=0.00
					else:
						valorCapital=float(cosechas[cosecha]["Capital Vencido"][bucket])
					
					if cosechas[cosecha]["Interes Vencido"][bucket]=="":
						valorInteres=0.00
					else:
						valorInteres=float(cosechas[cosecha]["Interes Vencido"][bucket])						

					
					reporte[mesOtorgamiento][periodo]["Capital Vencido"][bucket]+=valorCapital
					reporte[mesOtorgamiento][periodo]["Interes Vencido"][bucket]+=valorInteres
					reporte[mesOtorgamiento][periodo]["Total Vencido"][bucket]+=valorCapital+valorInteres
 
	reporteFinal={}
	for mesOtorgamiento in reporte:
		for renglon in reporte[mesOtorgamiento]:
			if "Monto Colocacion" in reporte[mesOtorgamiento][renglon]:
				if mesOtorgamiento not in reporteFinal:
					reporteFinal[mesOtorgamiento]={}
				reporteFinal[mesOtorgamiento][renglon]=reporte[mesOtorgamiento][renglon]

	data["renglones"]=reporteFinal
	return data

