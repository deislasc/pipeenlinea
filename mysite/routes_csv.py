import json

def jsontocsv(headers,reporte):
	csv=""
	for i,campo in enumerate(headers):
		csv += campo
		if i< len(headers)-1:
			csv += ","
		else:
			csv += "\n"

	for renglon in reporte:
		for i,campo in enumerate(headers):
		    newstring=""
		    newstring=renglon[campo]
		    newstring=newstring.replace('\n\n\n','')
		    newstring=newstring.replace('\n\n','')
		    newstring=newstring.replace('\n','')
		    newstring=newstring.replace('\r','')
		    newstring=newstring.replace("  ","")
		    newstring=newstring.replace(",","")
		    newstring=newstring.upper()
		    newstring=newstring.strip()


		    csv += newstring
		    if i< len(headers)-1:
		        csv += ","
		    else:
		        csv += "\n"
	return(csv)

def jsontotxt(headers,reporte,delimitador=","):
	csv=""
	for i,campo in enumerate(headers):
		csv += campo
		if i< len(headers)-1:
			csv += ","
		else:
			csv += "\n"

	for renglon in reporte:
		for i,campo in enumerate(headers):
			if (delimitador in renglon[campo] and
				'"' not in renglon[campo]) :
				renglon[campo]='"'+renglon[campo]+'"'
			csv += renglon[campo].replace("\n"," ").replace("  ","").strip().upper()
			if i< len(headers)-1:
				csv += delimitador
			else:
				csv += "\n"
	return(csv)


def csvtojson(csvData):
	csvData=csvData.replace("\ufeff", "")
	csvData=csvData.replace(",,",", ,")
	renglones=csvData.split("\r\n")
	encabezados=[]
	encabezados=renglones[0].split(",")
	data=[]


	del renglones[0]

	for renglon in renglones:
		dataRow={}
		values=renglon.split(",")
		for i,value in enumerate(values):
			value=value.strip()
			dataRow[encabezados[i]]=value
			data.append(dataRow)

	return data

def cosechastocsv(data,formData):
	if "Periodo/Otorgamiento" in formData["accion"]:
		headers=["PERÍODO","OTORGAMIENTO","COLOCACION",
        		 "CV 30","CV 60","CV 90","CV 120","CV 150","CV >150","CV TOTAL",
        		 "IV 30","IV 60","IV 90","IV 120","IV 150","IV >150","IV TOTAL",
        		 "TV 30","TV 60","TV 90","TV 120","TV 150","TV >150","TV TOTAL"]

	if "Otorgamiento/Periodo" in formData["accion"]:
		headers=["OTORGAMIENTO","PERÍODO","COLOCACION",
        		 "CV 30","CV 60","CV 90","CV 120","CV 150","CV >150","CV TOTAL",
        		 "IV 30","IV 60","IV 90","IV 120","IV 150","IV >150","IV TOTAL",
        		 "TV 30","TV 60","TV 90","TV 120","TV 150","TV >150","TV TOTAL"]

	reporte=data["renglones"]
	csv=""
	csv+="DESDE:,HASTA,PRODUCTO,TIPO,"
	for i,campo in enumerate(headers):
		csv += campo
		if i< len(headers)-1:
			csv += ","
		else:
			csv += "\n"

	for grupo in reporte:
		for renglon in reporte[grupo]:
			csv+=str(formData["fechaInicio"])+","
			csv+=str(formData["fechaFin"])+","
			csv+=str(formData["producto"])+","
			csv+=str(formData["accion"])+","
			csv+=grupo +","
			csv+=renglon +","
			csv+='{:.2f}'.format(reporte[grupo][renglon]["Monto Colocacion"])+","
			for campo in reporte[grupo][renglon]:
				valor=reporte[grupo][renglon][campo]
				if type(valor) == dict:
					for dictField in valor:
						dictValue=valor[dictField]
						csv+= '{:.2f}'.format(dictValue)+","
			csv += "\n"
	csv=csv.replace(",\n","\n")
	return(csv)