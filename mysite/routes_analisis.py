import json
import routes_empresas as empresas
import datetime
import config
from dateutil.relativedelta import relativedelta

# Para importar desde un archivo en otra ruta
import sys
# insert at 1, 0 is the script path (or '' in REPL)
# sys.path.insert(1, 'working')
import parametricos as param
print("DEBUG PARAMETRICOS: Plazos aux 12:", param.parametricosSimuladorBuroBueno["auxiliaresCaabsaEagle"]["12"]["plazos"], flush=True)
import sys
print("DEBUG: Plazos auxiliares 12 meses:", param.parametricosSimuladorBuroBueno["auxiliaresCaabsaEagle"]["12"]["plazos"], file=sys.stderr)

def analisisSolicitud(solicitud,newData=[]):
	msg=""
	respuesta={}
	solicitud=limpiarDatosCalculados(solicitud)
	solicitud=combinarNuevaData(solicitud,newData)
	solicitud=completaDatosGenerales(solicitud)
	# -------- Inicia árbol de decisiòn de analisis de crédito

	# TIPO DE CREDITO:
	# --CN:
	# 	|----No Sindializados
	# 	     |--------------Directivo
	# 		    			|-----------CleanUp
	# 			            |-----------No CleanUp
	# 	     |--------------|No Directivo
	# 						|-----------CleanUp
	# 			            |-----------No CleanUp
	# 	|----Sindicalizados
	# 		 |--------------CleanUp
	#
	# 		 |--------------No CleanUp
	# --AN:

	if solicitud["producto"]=="Nómina":
		solicitud=obtenerCostoSeguro(solicitud)
		solicitud=completaDatosCN(solicitud)

		if solicitud["clienteSindicalizado"]=="No Aplica":
			if solicitud["clienteDirectivo"]=="Sí":
				if solicitud["solicitudEsCleanUp"]=="Sí":
					solicitud=completaDatosCleanUp(solicitud)

			if solicitud["clienteDirectivo"]=="No":
				if solicitud["solicitudEsCleanUp"]=="Sí":
					solicitud=completaDatosCleanUp(solicitud)
		else:
			if solicitud["clienteSindicalizado"]=="Chofer Caabsa Eagle":
				if solicitud["solicitudEsCleanUp"]=="Sí":
					solicitud=completaDatosCleanUp(solicitud)

			if solicitud["clienteSindicalizado"]=="Auxiliar Caabsa Eagle":
				if solicitud["solicitudEsCleanUp"]=="Sí":
					solicitud=completaDatosCleanUp(solicitud)

	if solicitud["producto"]=="Adelanto de Nómina":
		solicitud=completaDatosAN(solicitud)

	# -------- Finaliza árbol de decisiòn de analisis de crédito


	solicitud=terminaDatosAnalisis(solicitud)

	campania={}
	riesgoEmpresa={}

	campania=buscarCampania(solicitud)
	riesgoEmpresa=param.nivelRiesgo[solicitud["clienteNivelRiesgoEmpresa"]]

	if (solicitud["clientePrestarHasta"]=="No Procede"):
		respuesta["solicitud"]=solicitud
		respuesta["msg"]=msg
		return respuesta

	if campania:
		if campania["status"]=="Activa":
			msg=aplicarCampania(solicitud,campania)["msg"]
			solicitud=aplicarCampania(solicitud,campania)["solicitud"]
	else:
		msg=aplicarRiesgoEmpresa(solicitud,riesgoEmpresa)

	solicitud=calcularCapacidadPago(solicitud)
	if float(solicitud["montoCapacidadDePago"])<0:
		solicitud["montoCapacidadDePago"]="0"

	if solicitud["producto"]=="Nómina" and float(solicitud["montoCapacidadDePago"])>0:
		solicitud=calcularPagoEsperadoCN(solicitud)
	if solicitud["producto"]=="Adelanto de Nómina" and float(solicitud["montoCapacidadDePago"])>0:
		solicitud=calcularPagoEsperadoAN(solicitud)

	if (solicitud["regionNombre"]=="Guadalajara" and
		(solicitud["clienteSindicalizado"]=="" or
		 solicitud["clienteSindicalizado"]=="No Aplica")):
		if msg!="":
			msg += "| "
		msg= msg+"Verifica si el cliente es sindicalizado, en caso de serlo, define si es chofer o auxiliar y vuelve a presionar el botón 'Realizar Analisis.'"

	respuesta["solicitud"]=solicitud
	respuesta["msg"]=msg
	return respuesta

def limpiarDatosCalculados(solicitud):
	camposCalculados=config.camposCalculadosAnalisisCredito
	exceptions=["montoTransferencia"]
	for campo in camposCalculados:
		if campo not in exceptions:
			solicitud[campo]=""
	return solicitud

def obtenerCostoSeguro(solicitud):
	if ("polizaSeguro" in solicitud and
		solicitud["polizaSeguro"]!="Ninguna" and
		solicitud["frecuenciaDePago"]!=""):
		pagoSeguro=config.costoSeguros[solicitud["polizaSeguro"]]
		if solicitud["frecuenciaDePago"]=="Mensual":
			pagoSeguro=pagoSeguro*2
		if solicitud["frecuenciaDePago"]=="Quincenal" or  solicitud["frecuenciaDePago"]=="Catorcenal" :
			pagoSeguro=pagoSeguro
		if solicitud["frecuenciaDePago"]=="Semanal":
			pagoSeguro=pagoSeguro/2
		solicitud["costoSeguroParcialidad"]=str(pagoSeguro)
	return solicitud


def combinarNuevaData(solicitud,newData):
	for field in newData:
		if field not in config.camposSesion:
			solicitud[field]=newData[field].strip()
	return solicitud


def completaDatosGenerales(solicitud):
	empresa=empresas.getEmpresaByName(solicitud["clienteEmpresa"])
	solicitud["clienteTipoEmpresa"]=empresa["tipo"]
	noProcedencia=""
	solicitud["clientePrestarHasta"]=""
	solicitud["lineaDeCredito"]="0.00"
	solicitud["montoMaximoPolitica"]="0.00"
	solicitud["plazoMaximoPolitica"]="0"
	solicitud["tasaPolitica"]="0.00"
	solicitud["tasaDeComisionPolitica"]="0.00"
	solicitud["tipoBuroCredito"]=""
	solicitud["montoBuenBuro"]="0.00"
	solicitud["clienteAntiguedadMeses"]="0"
	solicitud["costoSeguroParcialidad"]="0.00"
	solicitud["pagoTotalPeriodo"]="0.00"
	solicitud["capacidadDePago"]="0.00"
	solicitud["errorTransferencia"]=""

	if ("tasaDeComision" not in solicitud or
		solicitud["tasaDeComision"]==""):
		solicitud["tasaDeComision"]="0.00"

	if ("clienteAvalRequerido" not in solicitud or
		solicitud["clienteAvalRequerido"]==""):
		solicitud["clienteAvalRequerido"]=""

	if ("plazoAutorizado" not in solicitud or
		solicitud["plazoAutorizado"]==""):
		solicitud["plazoAutorizado"]="0"

	if ("montoAutorizado" not in solicitud or
		solicitud["montoAutorizado"]==""):
		solicitud["montoAutorizado"]="0"

	if "solicitudEsCleanUp" not in solicitud:
		solicitud["solicitudEsCleanUp"]="No"

	if "montoAutorizado" not in solicitud:
		solicitud["montoAutorizado"]="0.00"

	if "tasaDeComision" not in solicitud:
		solicitud["tasaDeComision"]="0.00"

	if (("frecuenciaDePago" not in solicitud) or
	   (solicitud["frecuenciaDePago"]=="")):
		solicitud["frecuenciaDePago"]="Quincenal"

	if (("plazoAutorizado" not in solicitud ) or
		(solicitud["plazoAutorizado"]=="")):
		solicitud["plazoAutorizado"]=solicitud["plazoSolicitado"]

	if "comentarios" in solicitud:
		solicitud["comentarios"]=solicitud["comentarios"].strip()

	cadenas=["No procede con la antigüedad y tipo de Buró del cliente.",
			 "No procede por antigüedad.",
			 "No procede por buró.",
			 "Requiere autorización escrita de DG por mal buró."
			]
	for cadena in cadenas:
		if ("comentarios" in solicitud and
			cadena in solicitud["comentarios"]):
			solicitud["comentarios"]=solicitud["comentarios"].replace(cadena,"")
			solicitud["comentarios"]=solicitud["comentarios"].strip()

	if "forbidden" not in solicitud:
		solicitud["forbidden"]=""

	if "nivel" not in empresa:
		empresa["nivel"]="Riesgo 1"
	solicitud["clienteNivelRiesgoEmpresa"]=empresa["nivel"]

	if (("tipoBuroCredito" not in solicitud) or
		(solicitud["tipoBuroCredito"] =="")):
		solicitud["tipoBuroCredito"]=""

	if(("clienteSindicalizado" not in solicitud) or
		solicitud["clienteSindicalizado"]==""):
		solicitud["clienteSindicalizado"]="No Aplica"

	if(("clienteDirectivo" not in solicitud) or
		solicitud["clienteDirectivo"]==""):
		solicitud["clienteDirectivo"]="No"

	if (("tipoListaNegra" not in solicitud) or
		(solicitud["tipoListaNegra"]=="")):
		solicitud["tipoListaNegra"]=""

	if (("clienteFechaIngreso" in solicitud) and
		(solicitud["clienteFechaIngreso"]!="")):
		fechaActual =datetime.datetime.today()
		fechaIngreso=datetime.datetime.strptime(solicitud["clienteFechaIngreso"]+" 23:59:59",  "%Y-%m-%d %H:%M:%S")
		solicitud["clienteAntiguedadMeses"]=diff_month(fechaActual, fechaIngreso)

		if  (solicitud["clienteAntiguedadMeses"] <6 and
			 solicitud["producto"]!="Adelanto de Nómina"):
			solicitud["clientePrestarHasta"]="No Procede"
			noProcedencia+="No procede por antigüedad.\n "
			noProcedencia+="Requiere autorización escrita de DG por falta de antigüedad.\n "
			# Verifico si aplica excepcion
			empresasExcepcion = param.empresasExcepcionASeisMeses["empresasAutorizadas"]
			if solicitud["clienteEmpresa"] in empresasExcepcion:
				if  (solicitud["clienteAntiguedadMeses"] >=3 and
					solicitud["producto"]!="Adelanto de Nómina"):
					solicitud["clientePrestarHasta"]=""
					solicitud["plazoSolicitado"]="6"
					noProcedencia=noProcedencia.replace("No procede por antigüedad.\n ", "")

		if ((solicitud["clienteAntiguedadMeses"]>=6) and
			(solicitud["clienteAntiguedadMeses"]<=12) and
			(solicitud["producto"]=="Nómina")):
			solicitud["clienteAvalRequerido"]="Requerido"
		elif((solicitud["clienteAntiguedadMeses"]>=3) and
			(solicitud["clienteAntiguedadMeses"]<=12) and
			(solicitud["producto"]=="Nómina") and
			solicitud["clienteEmpresa"] in empresasExcepcion):
			solicitud["clienteAvalRequerido"]="Requerido"
		else:
			solicitud["clienteAvalRequerido"]="No Requerido"


	if (("clienteSalario" not in solicitud) or
			(solicitud["clienteSalario"]=="")):
			solicitud["clienteSalario"]="0.00"

	if (solicitud["producto"]=="Adelanto de Nómina"):
		solicitud["tipoBuroCredito"]="No Aplica"
		solicitud["lineaDeCredito"]=(3/2)*float(solicitud["clienteSalario"])
		solicitud["lineaDeCredito"]=str(float(solicitud["lineaDeCredito"]))


	if (solicitud["producto"]=="Nómina"):
		solicitud["tipoBuroCredito"]="Bueno"

		if (("saldo1a89"  not in solicitud) or
		(solicitud["saldo1a89"]=="")):
			solicitud["saldo1a89"]="0.00"

		if (("saldoMayor90"  not in solicitud) or
		(solicitud["saldoMayor90"]=="")):
			solicitud["saldoMayor90"]="0.00"

		if (("saldoMayor120"  not in solicitud) or
		(solicitud["saldoMayor120"]=="")):
			solicitud["saldoMayor120"]="0.00"

		saldoVencido  = float(solicitud["saldo1a89"])
		saldoVencido += float(solicitud["saldoMayor90"])
		saldoVencido += float(solicitud["saldoMayor120"])
		solicitud["saldoVencido"] =str(saldoVencido)

		# print("Entrando a clasificación de Buró: ")
		# print("Salario: " + solicitud["clienteSalario"] )
		# print("Mop: " + solicitud["solicitudMop"])
		# print("Saldo Vencido: " + solicitud["saldoVencido"])

		if ( solicitud["clienteSalario"]!="" and
			 float(solicitud["clienteSalario"])>0 and
			 solicitud["solicitudMop"]!=""
			):

			solicitudMop = int(solicitud["solicitudMop"])

			if (saldoVencido >= 5 * float(solicitud["clienteSalario"]) and
				saldoVencido <  8 * float(solicitud["clienteSalario"]) and
				solicitudMop <= 5
				):
				solicitud["tipoBuroCredito"]="Regular"

			if (saldoVencido >= 5 * float(solicitud["clienteSalario"]) and
				saldoVencido <  8 * float(solicitud["clienteSalario"]) and
				solicitudMop >  5
				):
				solicitud["tipoBuroCredito"]="Malo"

			if (saldoVencido >= 8 * float(solicitud["clienteSalario"])):
				solicitud["tipoBuroCredito"]="Malo"


		if (solicitud["fechaEntregaARiesgos"]>"2023-09-30" and
		    solicitud["clienteSalario"]!="" and
			float(solicitud["clienteSalario"])>0 and
			solicitud["solicitudMop"]!=""
			):
			    # Se aplica a partir del 01 de Octubre de 2023 por instrucción de Hector Gamba
			    #solicitud["tipoBuroCredito"]=getTipoBuroV2(solicitudMop,saldoVencido,float(solicitud["clienteSalario"]))
			    # Se aplica a partir del 12 de Octubre de 2023 por instrucción de Hector Gamba
			    solicitud["tipoBuroCredito"]=getTipoBuroV3(solicitudMop,saldoVencido,float(solicitud["clienteSalario"]))


		# print("Clasificación de Buró: "+solicitud["tipoBuroCredito"])


		solicitud["saldo1a89"]=str(float(solicitud["saldo1a89"]))
		solicitud["saldoMayor90"]=str(float(solicitud["saldoMayor90"]))
		solicitud["saldoMayor120"]=str(float(solicitud["saldoMayor120"]))


		if (solicitud["tipoBuroCredito"] =="Malo"):
			solicitud["autorizacionDG"]="Requerida"
			noProcedencia+="Requiere autorización escrita de DG por mal buró.\n "

	if noProcedencia!="":
		if solicitud["comentarios"].find(noProcedencia)==-1:
			solicitud["comentarios"]= noProcedencia + solicitud["comentarios"]

		if "No procede por antigüedad" in solicitud["comentarios"]:
			solicitud["autorizacionDG"]="Requerida"

	return solicitud

def completaDatosAN(solicitud):
    if "montoTransferencia" not in solicitud:
        solicitud["montoTransferencia"]="0.00"

    if "montoAutorizado" not in solicitud:
        solicitud["montoAutorizado"]="0.00"

    if solicitud["montoTransferencia"]!="" and solicitud["montoAutorizado"]!="":
        if float(solicitud["montoTransferencia"])!=float(solicitud["montoAutorizado"]):
            solicitud["errorTransferencia"]="Transferencia debe ser igual que Autorizado"

    if  (solicitud["clientePrestarHasta"]!="No Procede"):
        solicitud=getParametricosAN(solicitud)

    return solicitud


def completaDatosCN(solicitud):

	if ("solicitudTasaTipoAnterior" not in solicitud or
		solicitud["solicitudTasaTipoAnterior"]==""):
			solicitud["solicitudTasaTipoAnterior"]="Tasa Global"

	if ("solicitudSaldoActualSIACAnterior" in solicitud and
		"solicitudTotalPagadoSIACAnterior" in solicitud and
		"solicitudMontoOriginalAnterior"   in solicitud and
		"solicitudMontoOriginalAnterior"   in solicitud and
		solicitud["solicitudSaldoActualSIACAnterior"]!="" and
		solicitud["solicitudTotalPagadoSIACAnterior"]!="" and
		solicitud["solicitudMontoOriginalAnterior"]!="" and
		float(solicitud["solicitudMontoOriginalAnterior"])>0):

		solicitud["solicitudMontoOriginalAnterior"]=str(
														float(solicitud["solicitudSaldoActualSIACAnterior"]) +
														float(solicitud["solicitudTotalPagadoSIACAnterior"])
														)
		solicitud["solicitudAvanceCreditoAnterior"]=str(
														(float(solicitud["solicitudTotalPagadoSIACAnterior"]) /
														float(solicitud["solicitudMontoOriginalAnterior"]))*100
														)

	if ("solicitudSaldoParcialidadesNumeroAnterior" in solicitud and
		"solicitudSaldoParcialidadesMontoAnterior"  in solicitud and
		solicitud["solicitudSaldoParcialidadesNumeroAnterior"]!="" and
		solicitud["solicitudSaldoParcialidadesMontoAnterior"]!=""
		):
		solicitud["solicitudSaldoTotalAnterior"]=str(
													float(solicitud["solicitudSaldoParcialidadesNumeroAnterior"]) *
													float(solicitud["solicitudSaldoParcialidadesMontoAnterior"])
													)
		solicitud["montoPropuesto"]= str(float(solicitud["montoSolicitado"]) - float(solicitud["solicitudSaldoTotalAnterior"]))

	if ("montoTransferencia" in solicitud and
		"montoAutorizado" in solicitud and
		solicitud["montoTransferencia"]!="" and
		solicitud["montoAutorizado"]!=""):

		if float(solicitud["montoTransferencia"])!=float(solicitud["montoAutorizado"]):
			solicitud["errorTransferencia"]="Transferencia debe ser igual que Autorizado"

		if solicitud["montoTransferencia"]!="" and solicitud["montoAutorizado"]!="":
			if float(solicitud["montoTransferencia"])>float(solicitud["montoAutorizado"]):
				solicitud["errorTransferencia"]="Transferencia no debe ser mayor que Autorizado"

	if  (solicitud["clientePrestarHasta"]!="No Procede"):
		solicitud=getParametricos(solicitud)


	return solicitud


def completaDatosCleanUp(solicitud):
	if "montoTransferencia" not in solicitud:
		solicitud["montoTransferencia"]="0.0"

	if solicitud["montoTransferencia"]=="":
		solicitud["montoTransferencia"]="0.0"

	if ("solicitudSaldoActualSIACAnterior" in solicitud and solicitud["solicitudSaldoActualSIACAnterior"]==""):
		solicitud["solicitudSaldoActualSIACAnterior"]="0.00"
	if "solicitudSaldoActualSIACAnterior" not in solicitud:
		solicitud["solicitudSaldoActualSIACAnterior"]="0.00"

	if ("solicitudTotalPagadoSIACAnterior" in solicitud and solicitud["solicitudTotalPagadoSIACAnterior"]==""):
		solicitud["solicitudTotalPagadoSIACAnterior"]="0.00"
	if "solicitudTotalPagadoSIACAnterior" not in solicitud:
		solicitud["solicitudTotalPagadoSIACAnterior"]="0.00"

	if ("solicitudSaldoParcialidadesNumeroAnterior" in solicitud and solicitud["solicitudSaldoParcialidadesNumeroAnterior"]==""):
		solicitud["solicitudSaldoParcialidadesNumeroAnterior"]="0.00"
	if "solicitudSaldoParcialidadesNumeroAnterior" not in solicitud:
		solicitud["solicitudSaldoParcialidadesNumeroAnterior"]="0.00"


	if (solicitud["errorTransferencia"]=="Transferencia debe ser igual que Autorizado"):
		solicitud["errorTransferencia"]=""

	if ("solicitudSaldoActualSIACAnterior" in solicitud and
		solicitud["solicitudSaldoActualSIACAnterior"]!=""):

		if solicitud["solicitudTotalPagadoSIACAnterior"]!="":
			solicitud["solicitudMontoOriginalAnterior"]=(float(solicitud["solicitudSaldoActualSIACAnterior"])+
														float(solicitud["solicitudTotalPagadoSIACAnterior"]))
			if solicitud["solicitudMontoOriginalAnterior"]>0:
				solicitud["solicitudAvanceCreditoAnterior"]=(float(solicitud["solicitudTotalPagadoSIACAnterior"]) *100/
															solicitud["solicitudMontoOriginalAnterior"])
			solicitud["solicitudMontoOriginalAnterior"]=str(solicitud["solicitudMontoOriginalAnterior"])
			solicitud["solicitudAvanceCreditoAnterior"]=str(solicitud["solicitudAvanceCreditoAnterior"])

		if (solicitud["solicitudSaldoParcialidadesNumeroAnterior"] !="" and
			solicitud["solicitudSaldoParcialidadesMontoAnterior"]!="" ):
			solicitud["solicitudSaldoTotalAnterior"] = (float(solicitud["solicitudSaldoParcialidadesNumeroAnterior"]) *
														float(solicitud["solicitudSaldoParcialidadesMontoAnterior"]))
			solicitud["solicitudSaldoTotalAnterior"] = str(solicitud["solicitudSaldoTotalAnterior"])

		if (solicitud["solicitudSaldoActualSIACAnterior"]!="" and
			solicitud["montoSolicitado"]!="" and
			solicitud["solicitudSaldoTotalAnterior"]!=""):
			solicitud["montoPropuesto"]= (float(solicitud["montoSolicitado"])-
										  float(solicitud["solicitudSaldoActualSIACAnterior"])+
										  float(solicitud["solicitudSaldoTotalAnterior"]))
			solicitud["montoPropuesto"]=str(solicitud["montoPropuesto"])


		if float(solicitud["solicitudSaldoActualSIACAnterior"])>0:
			solicitud["solicitudIncrementoSaldoActual"]=float(solicitud["montoSolicitado"])* 100 / float(solicitud["solicitudSaldoActualSIACAnterior"])

		# if solicitud["solicitudTasaTipoAnterior"]=="Tasa Global":
		# 	if (float(solicitud["montoSolicitado"]) / float(solicitud["solicitudSaldoActualSIACAnterior"])<1.7):
		# 		solicitud["errorTransferencia"]="Tansferencia debe ser 70% mayor al saldo actual."

		# if solicitud["solicitudTasaTipoAnterior"]=="Tasa sobre Saldos Insolutos":
		# 	if (float (solicitud["solicitudAvanceCreditoAnterior"])<0.40):
		# 		solicitud["errorTransferencia"]="El crédito mínimo debe tener un 40% de avance."

	if float(solicitud["montoAutorizado"])>float(solicitud["montoSolicitado"]):
		solicitud["errorTransferencia"]="No se puede autorizar un monto mayor al solicitado."

	if float(solicitud["montoTransferencia"])>=float(solicitud["montoAutorizado"]):
		solicitud["errorTransferencia"]="Transferencia debe ser menor que Autorizado."

	return solicitud


def terminaDatosAnalisis(solicitud):

	if ", fechaAnalisisConluido" in solicitud["forbidden"]:
		solicitud["forbidden"]=solicitud["forbidden"].replace(", fechaAnalisisConluido","")

	if ("comentarios" in solicitud and
		"No procede" in solicitud["comentarios"]):
		solicitud["clientePrestarHasta"]="No Procede"


	if solicitud["errorTransferencia"]!="":
		solicitud["forbidden"]+=", fechaAnalisisConluido"

	if solicitud["errorTransferencia"]=="":
		if ", fechaAnalisisConluido" in solicitud["forbidden"]:
			solicitud["forbidden"]=solicitud["forbidden"].replace(", fechaAnalisisConluido","")

	pagosAlAnio=param.numPagosAlAnio[solicitud["frecuenciaDePago"]]

	if ((solicitud["plazoAutorizado"].find("Semana")==-1) and
		(solicitud["plazoAutorizado"].find("Quincena")==-1)):
		solicitud["numeroPagos"]=float(solicitud["plazoAutorizado"])/12.00 * pagosAlAnio
		solicitud["numeroPagos"]=str(int(float(solicitud["numeroPagos"])))

	solicitud["tasaDeComision"]=str(float(solicitud["tasaDeComision"]))
	solicitud["montoComision"]=float(solicitud["montoAutorizado"])*float(solicitud["tasaDeComision"])/100
	solicitud["montoComision"]=str(solicitud["montoComision"])

	if "comentarios" in solicitud :
		solicitud["comentarios"]=solicitud["comentarios"].strip()

	return(solicitud)

def diff_month(d1, d2):
	return (d1.year - d2.year) * 12 + d1.month - d2.month

def getParametricos(data):
	tipo=""
	parametros=[]

	if data["clienteTipoEmpresa"]=="Interna":
		tipo="internos"
	if data["clienteTipoEmpresa"]=="Externa":
		tipo="externos"
	if data["clienteSindicalizado"]=="Auxiliar Caabsa Eagle":
		tipo="auxiliaresCaabsaEagle"
	if data["clienteSindicalizado"]=="Chofer Caabsa Eagle":
		tipo="choferesCaabsaEagle"

	if data["tipoBuroCredito"]=="Bueno":
		parametros=param.parametricosSimuladorBuroBueno[tipo]

	if (data["tipoBuroCredito"]=="Regular" or
	    data["tipoBuroCredito"]=="Regular con Capacidad" ):
		parametros=param.parametricosSimuladorBuroRegular[tipo]

	if data["tipoBuroCredito"]=="Malo":
		parametros=param.parametricosSimuladorBuroRegular[tipo]


	if ("clienteSalario" in data):
		if (float(data["clienteSalario"])>=40000 and
			data["tipoBuroCredito"]=="Bueno" and
			data["clienteTipoEmpresa"]=="Interna" and
			data["clienteDirectivo"]=="Sí" and
			int(data["clienteAntiguedadMeses"])>=12):
			parametros=param.parametricosSimuladorBuroBueno["directivoInterno"]


	if ("clienteSalario" in data):
		if (float(data["clienteSalario"])>=40000 and
			data["tipoBuroCredito"]=="Bueno" and
			data["clienteTipoEmpresa"]=="Externa" and
			data["clienteDirectivo"]=="Sí" and
			int(data["clienteAntiguedadMeses"])>=24):
			parametros=param.parametricosSimuladorBuroBueno["directivoExterno"]


	parametricos=[]
	if ("clienteAntiguedadMeses" in data):
		antiguedad=data["clienteAntiguedadMeses"]
		# print(antiguedad)
		# print(json.dumps(parametros,indent=4))
		for item in parametros:
			if(int(item)<=int(antiguedad)):
				parametricos=parametros[item]
				# print(parametricos)

	if not parametricos:
		noProcedencia="No procede con la antigüedad y tipo de Buró del cliente.\n"
		if "No procede con la antigüedad y tipo de Buró del cliente."  not in data["comentarios"]:
			data["comentarios"]=noProcedencia+data["comentarios"]
		return data

	data["tasaPolitica"]=parametricos["tasa"]
	if data["producto"]=="Nómina":
		if "mesesSueldo" in parametricos:
			data["clientePrestarHasta"]=parametricos["mesesSueldo"]
		else:
			data["clientePrestarHasta"]="No Aplica"

	if data["producto"]=="Adelanto de Nómina":
		data["clientePrestarHasta"]="No Aplica"
	data["tasaDeComisionPolitica"]=parametricos["comision"]
	data["plazoMaximoPolitica"]=parametricos["plazos"][-1]
	data["mesesDeSueldoPolitica"]=parametricos["plazos"][-1]

	if "mesesSueldo" in parametricos:
		if data["clienteSalario"]=="":
			data["montoMaximoPolitica"]=parametricos["mesesSueldo"] * 0
		else:
			data["montoMaximoPolitica"]=parametricos["mesesSueldo"] * float(data["clienteSalario"])
	else:
		data["montoMaximoPolitica"]=str(parametricos["montoMax"])


	if (("montoAutorizado" in data) and
		(data["montoAutorizado"]!="0")):
		data["montoComisionPolitica"]=float(data["montoAutorizado"])*parametricos["comision"]
	else:
		data["montoComisionPolitica"]=float(data["montoSolicitado"])*parametricos["comision"]

	data["tasaPolitica"]=str(data["tasaPolitica"])
	data["tasaDeComisionPolitica"]= str(data["tasaDeComisionPolitica"]*100)
	data["plazoMaximoPolitica"]= str(data["plazoMaximoPolitica"])
	data["montoMaximoPolitica"]= str(data["montoMaximoPolitica"])
	data["mesesDeSueldoPolitica"]=str(data["mesesDeSueldoPolitica"])
	data["clientePrestarHasta"]= str(data["clientePrestarHasta"])
	data["clienteAntiguedadMeses"]= str(data["clienteAntiguedadMeses"])
	data["montoComisionPolitica"]=str(data["montoComisionPolitica"])

	if (("tasaAutorizada" not in data ) or
		(data["tasaAutorizada"]=="")):
		data["tasaAutorizada"]=data["tasaPolitica"]

	return data


def getParametricosAN(solicitud):
	plazo=""
	if solicitud["plazoSolicitado"]!="":
		plazo = solicitud["plazoSolicitado"]
	if (solicitud["plazoAutorizado"]!="" and
		solicitud["plazoAutorizado"]!="0"):
		plazo = solicitud["plazoAutorizado"]

	solicitud["numeroPagos"]=plazo.split(" ")[0]
	periodo=plazo.split(" ")[1]
	if "mes" in periodo.lower():
		periodo="Mes"
	if "quincena" in periodo.lower():
		periodo="Quincena"
	if "semana" in periodo.lower():
		periodo="Semana"
	if "catorcena" in periodo.lower():
		periodo="Catorcena"

	solicitud["plazoMaximoPolitica"]="2 "+periodo+"s"
	solicitud["clientePrestarHasta"]="1 "+periodo

	capacidadDePago=0
	if periodo.lower()=="semana":
		capacidadDePago=str((1/4)*float(solicitud["clienteSalario"]))
	if periodo.lower()=="quincena":
		capacidadDePago=str((1/2)*float(solicitud["clienteSalario"]))
	if periodo.lower()=="mes":
		capacidadDePago=str(float(solicitud["clienteSalario"]))
	solicitud["montoMaximoPolitica"]=capacidadDePago

	if solicitud["numeroPagos"]=="1":
		solicitud["tasaDeComisionPolitica"]="6"

	if solicitud["numeroPagos"]=="2":
		solicitud["tasaDeComisionPolitica"]="10"

	if float(solicitud["clienteAntiguedadMeses"])<6:
		solicitud["tasaDeComisionPolitica"]="10"
		solicitud["plazoMaximoPolitica"]="1 "+periodo

	if ("montoSolicitado" in solicitud and
		solicitud["montoSolicitado"]!="" and
		float(solicitud["montoSolicitado"])>0):
		solicitud["montoComisionPolitica"]= ((float(solicitud["tasaDeComisionPolitica"])/100) *
											 float(solicitud["montoSolicitado"]))
		solicitud["montoComisionPolitica"]= str(solicitud["montoComisionPolitica"])

	if ("montoAutorizado" in solicitud and
		solicitud["montoAutorizado"]!="" and
		float(solicitud["montoAutorizado"])>0):
		solicitud["montoComisionPolitica"]= ((float(solicitud["tasaDeComisionPolitica"])/100) *
											 float(solicitud["montoAutorizado"]))
		solicitud["montoComisionPolitica"]= str(solicitud["montoComisionPolitica"])
		solicitud["montoAutorizado"]=str(solicitud["montoAutorizado"])

	return solicitud


def calcularCapacidadPago(solicitud):
	if "clienteDeduccionesSemanales" not in solicitud or solicitud["clienteDeduccionesSemanales"]=="":
		solicitud["clienteDeduccionesSemanales"]="0"

	if "clienteDeduccionesQuincenales" not in solicitud or solicitud["clienteDeduccionesQuincenales"]=="":
		solicitud["clienteDeduccionesQuincenales"]="0"

	if "clienteDeduccionesMensuales" not in solicitud or solicitud["clienteDeduccionesMensuales"]=="":
		solicitud["clienteDeduccionesMensuales"]="0"

	if "clienteDeduccionesPeriodo" not in solicitud or solicitud["clienteDeduccionesPeriodo"]=="":
		solicitud["clienteDeduccionesPeriodo"]="0"

	if("clienteSalario" not in solicitud or
		solicitud["clienteSalario"]==""):
		return solicitud

	deducciones=0.00


	if solicitud["frecuenciaDePago"]=="Mensual":
		solicitud["montoCapacidadDePago"]=str(solicitud["clienteSalario"])
		deducciones = float(solicitud["clienteDeduccionesSemanales"]) * 4.33
		deducciones+= float(solicitud["clienteDeduccionesQuincenales"]) * 2.00
		deducciones+= float(solicitud["clienteDeduccionesMensuales"]) * 1.00


	if solicitud["frecuenciaDePago"]=="Quincenal" or  solicitud["frecuenciaDePago"]=="Catorcenal" :
		solicitud["montoCapacidadDePago"]=str(float(solicitud["clienteSalario"])/2.0)
		deducciones = float(solicitud["clienteDeduccionesSemanales"]) * 2.00
		deducciones+= float(solicitud["clienteDeduccionesQuincenales"]) * 1.00
		deducciones+= float(solicitud["clienteDeduccionesMensuales"]) / 2.00

	if solicitud["frecuenciaDePago"]=="Semanal":
		solicitud["montoCapacidadDePago"]=str(float(solicitud["clienteSalario"])/4.33)
		deducciones = float(solicitud["clienteDeduccionesSemanales"]) * 1.00
		deducciones+= float(solicitud["clienteDeduccionesQuincenales"]) / 2.00
		deducciones+= float(solicitud["clienteDeduccionesMensuales"]) / 4.33

	solicitud["clienteDeduccionesPeriodo"]=str(deducciones)

	if solicitud["producto"]=="Adelanto de Nómina":
		solicitud["montoCapacidadDePago"]=str(float(solicitud["montoCapacidadDePago"])-deducciones)
		solicitud["montoPropuesto"]=str(float(solicitud["montoCapacidadDePago"])-deducciones)


	if solicitud["producto"]=="Nómina":
		if ("clienteSindicalizado" not in solicitud or
			 solicitud["clienteSindicalizado"]!="Auxiliar Caabsa Eagle" and
			 solicitud["clienteSindicalizado"]!="Chofer Caabsa Eagle"
			):
			solicitud["montoCapacidadDePago"]=str((float(solicitud["montoCapacidadDePago"])-deducciones)*param.factorCapacidadDePago["No Sindicalizados"])


		if ("clienteSindicalizado" in solicitud and
			 (solicitud["clienteSindicalizado"]=="Auxiliar Caabsa Eagle" or
			 solicitud["clienteSindicalizado"]=="Chofer Caabsa Eagle")
			):
			solicitud["montoCapacidadDePago"]=str(float(solicitud["montoCapacidadDePago"])*param.factorCapacidadDePago["Sindicalizados"])
			solicitud["montoCapacidadDePago"]=str(float(solicitud["montoCapacidadDePago"])-deducciones)


	return solicitud


def calcularPagoEsperadoCN(solicitud):
	redito=0.0
	capital=0.0
	tiempo=0.0
	interes=0.0
	parcialidad=0.0

	if "tasaPolitica" in solicitud:
		redito=solicitud["tasaPolitica"]
	if "tasaAutorizada" in solicitud:
		redito=solicitud["tasaAutorizada"]

	if "montoSolicitado" in solicitud:
		capital=solicitud["montoSolicitado"]
	if "montoAutorizado" in solicitud:
		capital=solicitud["montoAutorizado"]

	if "plazoSolicitado" in solicitud:
		tiempo=solicitud["plazoSolicitado"]
	if "plazoAutorizado" in solicitud:
		tiempo=solicitud["plazoAutorizado"]

	try:
		float(redito)
	except ValueError:
		return solicitud

	try:
		float(capital)
	except ValueError:
		return solicitud

	try:
		float(tiempo)
	except ValueError:
		return solicitud


	capital=float(capital)
	redito=(float(redito)/100)*(1.16)
	tiempo=float(tiempo)/12

	interes=capital*redito*tiempo

	total_a_pagar=capital+interes
	if (solicitud["numeroPagos"]!="" and
		solicitud["numeroPagos"]!="0"):
		parcialidad=total_a_pagar/float(solicitud["numeroPagos"])

	solicitud["pagoEstimadoPeriodo"]=str(parcialidad)
	parcialidad += float(solicitud["costoSeguroParcialidad"])
	solicitud["pagoTotalPeriodo"]=str(parcialidad)

	solicitud["capacidadDePago"] = "No Cumple"

	if parcialidad > float(solicitud["montoCapacidadDePago"]):
		solicitud["capacidadDePago"] = "No Cumple"
	else:
		solicitud["capacidadDePago"] = "Ok"



	return solicitud

def calcularPagoEsperadoAN(solicitud):

	parcialidad=0.00

	if "montoSolicitado" in solicitud:
		capital=solicitud["montoSolicitado"]
	if ("montoAutorizado" in solicitud and
		solicitud["montoAutorizado"] != ""):
		capital=solicitud["montoAutorizado"]

	if "plazoSolicitado" in solicitud:
		tiempo=solicitud["plazoSolicitado"]

	if ("plazoAutorizado" in solicitud and
		solicitud["plazoAutorizado"] != ""):
		tiempo=solicitud["plazoAutorizado"]

	capital=float(capital)
	numeroPagos=float(solicitud["numeroPagos"])

	if numeroPagos==1.0:
		interes=capital*.06*1.16
		total_a_pagar=capital + interes
		parcialidad=total_a_pagar

	if numeroPagos==2.0:
		interes=capital*.10*1.16
		total_a_pagar=capital + interes
		parcialidad=total_a_pagar/2

	if float(solicitud["clienteAntiguedadMeses"])<6:
		interes=capital*.10*1.16
		total_a_pagar=capital + interes
		parcialidad=total_a_pagar



	solicitud["pagoEstimadoPeriodo"]=str(parcialidad)
	parcialidad += float(solicitud["costoSeguroParcialidad"])
	solicitud["pagoTotalPeriodo"]=str(parcialidad)

	if parcialidad > float(solicitud["montoCapacidadDePago"]):
		solicitud["capacidadDePago"] = "No Cumple"
	else:
		solicitud["capacidadDePago"] = "Ok"

	return solicitud

def buscarCampania (solicitud):
	campanias=param.campanias
	campaniaFinal={}
	for campania in campanias:
		if (campania ["status"]=="Activa" and
			solicitud["clienteTipoEmpresa"] in campania["tipoEmpresaAplica"] and
			solicitud["clienteNivelRiesgoEmpresa"] in campania["nivelesRiesgoAplican"] and
			solicitud["tipoBuroCredito"] in campania["tipoBuroCredito"] and
			solicitud["producto"] in campania["productos"] and
			solicitud["clienteSindicalizado"] in campania["clienteSindicalizadoAplicar"]
		):
			campaniaFinal=campania

	return campaniaFinal

def aplicarCampania(solicitud,campania):
	solicitud["montoBuenBuro"]="0.00"
	msg=""
	if campania:
		solicitud["campaniaDisponible"]=json.dumps(campania,indent=4)
		if (campania["nombre"]=="50% Más por Buen Buro" and
			(solicitud["tipoBuroCredito"]=="Bueno" or
			solicitud["tipoBuroCredito"]=="Regular con Capacidad")):
			montoCampania=float(solicitud["montoMaximoPolitica"])*float(campania['factorCredito'])
			montoCampania=int(montoCampania/100)*100
			solicitud["montoBuenBuro"]=str(montoCampania)
			nombre=solicitud['clienteNombre']+" "+solicitud['clienteApellidoPaterno']+" "+solicitud['clienteApellidoMaterno']
			nombre=nombre.upper()
			msg  = nombre+" es sujeto de Campaña de Buen Buro.\n"
			msg += "Monto de credito preautorizado: "+'${:0,.2f}'.format(montoCampania)+"\n"
			msg += "Informalo al Gerente Comercial."
	result={}
	result["msg"]=msg
	result["solicitud"]=solicitud

	return result

def aplicarRiesgoEmpresa(solicitud,riesgo):
	msg=""
	if riesgo['nombre']=="Riesgo 5":
		nombre=solicitud['clienteNombre']+" "+solicitud['clienteApellidoPaterno']+" "+solicitud['clienteApellidoMaterno']
		nombre=nombre.upper()
		msg = nombre+" colabora en una empresa catalogada como: "+riesgo['nombre'] +"\n"
		msg += "por lo que se recomienda no prestar más de: "+str(riesgo["maxMeses"])+" mes(es) de sueldo.\n"
		msg += "Informalo al Gerente Comercial"

	return msg

def completarDatosSimuladorSIAC(solicitud):
	respuesta={}
	msg=""
	impactoSeguroCapitalPermitido=param.impactoSeguroCapitalPermitido['limite']
	valorImpactoSeguroCapital=0
	solicitud['montoSeguro']="0.0"
	solicitud['montoIVASeguro']="0.0"
	solicitud['solicitudSeguroFinanciado']="0.0"
	solicitud['montoMinistracion']="0.0"
	solicitud['montoIvaComision']="0.0"
	solicitud['tipoPagoSeguro']='Prorrateado'

	if solicitud["producto"]=="Adelanto de Nómina":
		solicitud['tipoPagoSeguro']='No Aplica'
		solicitud['montoSeguro']="0.0"
		solicitud['montoIVASeguro']="0.0"

	if ('costoSeguroParcialidad' in solicitud and
		solicitud['costoSeguroParcialidad']!="" and
		solicitud['costoSeguroParcialidad']!="''" and
		float(solicitud['costoSeguroParcialidad'])>0):
		if 'numeroPagos' in solicitud:
			if ('montoAutorizado' in solicitud and float(solicitud['montoAutorizado'])>0):
				totalSeguro=float(solicitud["numeroPagos"])*float(solicitud['costoSeguroParcialidad'])
				solicitud['totalSeguro']=str(totalSeguro)
				if solicitud['montoAutorizado']!="" and solicitud['montoAutorizado']!="0":
					valorImpactoSeguroCapital = totalSeguro / float(solicitud['montoAutorizado'])
					if valorImpactoSeguroCapital>impactoSeguroCapitalPermitido:
						solicitud['tipoPagoSeguro']='Prorrateado'
						solicitud['montoSeguro']=str(totalSeguro)
						solicitud['montoIVASeguro']=str(totalSeguro*0.16)
					else:
						solicitud['tipoPagoSeguro']='Financiado'
						solicitud['montoSeguro']=calculaSeguroFinanciado(solicitud)
						solicitud['montoIVASeguro']=str(float(solicitud['montoSeguro'])*0.16)
						solicitud['solicitudSeguroFinanciado']=solicitud['montoSeguro']


	solicitud['montoMinistracion'] = calculaMinistracion(solicitud)
	solicitud['montoIvaComision']=str(float(solicitud["montoComision"])*0.16)
	solicitud['fechaUltimoPago']=calculaFechaUlitmoPago(solicitud)
	solicitud=calcularPagoParcialidadSIAC(solicitud)

	# if solicitud['tipoPagoSeguro']=='Prorrateado':
	# 	solicitud['montoSeguro']="0.0"
	# 	solicitud['montoIVASeguro']="0.0"


	respuesta["solicitud"]=solicitud
	respuesta["msg"]=msg

	return respuesta

def calculaSeguroFinanciado(solicitud):
	seguroFinanciado="0"

	if "totalSeguro" in solicitud:
		totalSeguro=float(solicitud['totalSeguro'])
	else:
		return seguroFinanciado

	if "plazoAutorizado" in solicitud:
		tiempo=float(solicitud["plazoAutorizado"])/12
	else:
		return seguroFinanciado

	if "tasaAutorizada" in solicitud:
		tasa=round(float(solicitud['tasaAutorizada'])/100,4)
	else:
		return seguroFinanciado



	seguroFinanciado=totalSeguro/(1+(tiempo*tasa))
	seguroFinanciado=round(seguroFinanciado,2)
	seguroFinanciado=str(seguroFinanciado)

	return seguroFinanciado

def calculaMinistracion(solicitud):
	montoMinistracion="0"
	montoSeguroTotal=0
	if ("montoAutorizado" not in solicitud or
		"tasaDeComision" not in solicitud or
		"montoSeguro" not in solicitud
		):
		return montoMinistracion

	montoAutorizado=float(solicitud['montoAutorizado'])
	tasaDeComision = float(solicitud['tasaDeComision'])*1.16/100
	montoSeguro=0
	if solicitud['tipoPagoSeguro'] == 'Financiado':
		montoSeguroTotal=float(solicitud['montoSeguro'])*1.16
		montoSeguroTotal=round(montoSeguroTotal,2)

	montoMinistracion=montoAutorizado * (1+tasaDeComision) + montoSeguroTotal
	montoMinistracion=round(montoMinistracion,2)
	montoMinistracion=str(montoMinistracion)

	return montoMinistracion

def calculaFechaUlitmoPago(solicitud):
	fechaUltimoPago=""
	if ('fechaPrimerCobro' not in solicitud or
		'plazoAutorizado' not in solicitud or
		'frecuenciaDePago' not in solicitud ):
		return fechaUltimoPago

	if solicitud['fechaPrimerCobro']=="":
		return fechaUltimoPago

	frecuencia=solicitud['frecuenciaDePago']
	fechaPrimerPago=solicitud['fechaPrimerCobro']
	if(solicitud["plazoAutorizado"].isnumeric()):
		plazo=int(solicitud["plazoAutorizado"])
		if frecuencia=="Semanal":
			plazo = int((plazo)*7*4.33)
	else:
		if("quincena" in solicitud["plazoAutorizado"].lower()):
			plazo=int(solicitud["plazoAutorizado"].split(" ")[0])*0.5
		if("semana" in solicitud["plazoAutorizado"].lower()):
			plazo=int(solicitud["plazoAutorizado"].split(" ")[0])*7  #Se convierte a dias

	fechaArray=fechaPrimerPago.split("-")


	if frecuencia =="Mensual" :
		fechaUltimoPago=datetime.date(int(fechaArray[0]),int(fechaArray[1]),1) + relativedelta(months=+plazo) + relativedelta(days=-1)


	if frecuencia=="Quincenal":
		if int(fechaArray[2])==15:
		    if plazo==0.5:
		        fechaUltimoPago=datetime.date(int(fechaArray[0]),int(fechaArray[1]),1) + relativedelta(days=15-1)
		    else:
			    fechaUltimoPago=datetime.date(int(fechaArray[0]),int(fechaArray[1]),1) + relativedelta(months=+plazo) + relativedelta(days=-1)

		if int(fechaArray[2])>=28:
		    if plazo==0.5:
		    	#Se calcula el ùltimo dia del mes
		    	if int(fechaArray[1])<12:
		    	    fechaUltimoPago=datetime.date(int(fechaArray[0]),int(fechaArray[1])+1,1) + relativedelta(days=-1)
		    	else:
		    	    fechaUltimoPago=datetime.date(int(fechaArray[0]),int(fechaArray[1]),1) + relativedelta(days=15-1)






		    else:
		        fechaUltimoPago=datetime.date(int(fechaArray[0]),int(fechaArray[1]),15) + relativedelta(months=+plazo)

	if frecuencia=="Catorcenal":
		fechaUltimoPago=datetime.date(int(fechaArray[0]),int(fechaArray[1]),int(fechaArray[2]))  + relativedelta(days=(float(solicitud['numeroPagos'])-1)*14)

	if frecuencia=="Semanal":
		# =FECHA(AÑO(C3),MES(C3)+C6,DIA(C3)-8)+(6-DIASEM(FECHA(AÑO(C3),MES(C3)+C6,DIA(C3)-8)))
		diaSemana=datetime.date(int(fechaArray[0]),int(fechaArray[1]),int(fechaArray[2])) + relativedelta(days=+plazo) + relativedelta(days=-8)
		delta= 4 - diaSemana.weekday()
		fechaUltimoPago=datetime.date(int(fechaArray[0]),int(fechaArray[1]),int(fechaArray[2])) + relativedelta(days=+(plazo)) + relativedelta(days=-8+delta)


	fechaUltimoPago=fechaUltimoPago.strftime('%Y-%m-%d')

	return fechaUltimoPago

def calcularPagoParcialidadSIAC(solicitud):
	pagoParcialidadSimulador="0"

	if ('montoMinistracion' not in solicitud or
		solicitud['montoMinistracion']=="0"
		):
		return solicitud

	if ('numeroPagos' not in solicitud or
		solicitud['numeroPagos']=="0"
		):
		return solicitud

	if (float(solicitud['montoMinistracion'])>0 and
		float(solicitud['numeroPagos'])>0):
		pagoParcialidadSimulador= float(solicitud['montoMinistracion']) / float(solicitud['numeroPagos'])


	diaInicio=solicitud['fechaEmisionContrato']
	fechaArray=diaInicio.split("-")
	fechaInicio=datetime.date(int(fechaArray[0]),int(fechaArray[1]),int(fechaArray[2]))

	diaFin= solicitud['fechaUltimoPago']
	fechaArray=diaFin.split("-")
	fechaFin=datetime.date(int(fechaArray[0]),int(fechaArray[1]),int(fechaArray[2]))

	delta=abs((fechaFin-fechaInicio).days)
	plazoReal=delta/360

	if "tasaAutorizada" in solicitud:
		tasa=round(float(solicitud['tasaAutorizada'])/100,4)
		capital=float(solicitud['montoMinistracion'])
		intereses=capital*tasa*plazoReal
		intereses=round(intereses,2)
		ivaIntereses=intereses*0.16

		ivaIntereses=round(ivaIntereses,2)
		if solicitud['tipoPagoSeguro']=='Prorrateado':
			if solicitud['montoIVASeguro']!="":
				ivaIntereses+= float(solicitud['montoIVASeguro'])

		totalAPagar=capital+intereses+ivaIntereses
		if solicitud['tipoPagoSeguro']=='Prorrateado':
			if solicitud['montoSeguro']!="":
				totalAPagar += float(solicitud['montoSeguro'])

		totalAPagar=round(totalAPagar,2)
		pagoParcialidadSimulador=totalAPagar/float(solicitud["numeroPagos"])
		pagoParcialidadSimulador=round(pagoParcialidadSimulador,2)
		pagoParcialidadSimulador=str(pagoParcialidadSimulador)
		solicitud["pagoParcialidadSimulador"]=pagoParcialidadSimulador
		solicitud["totalInteresesSimulador"]=str(intereses)
		solicitud["ivaInteresesSimulador"]=str(ivaIntereses)
		solicitud["pagoTotalSimulador"]=str(totalAPagar)
	return solicitud

def preAnalisis(solicitud):
	msg=""
	respuesta={}
	solicitud=limpiarDatosCalculados(solicitud)
	solicitud=combinarNuevaData(solicitud,newData)
	solicitud=completaDatosGenerales(solicitud)
	return solicitud

def getTipoBuroV2(solicitudMop,saldoVencido,salario):
	# Se aplica a partir del 01 de Octubre de 2023 por instrucción de Hector Gamba
	tipoBuro=""
	buroBuenoArray=["0,0","1,0"]
	buroRegularConCapacidadArray =["2,0",
	                   "0,1","1,1","2,1",
	                   "0,2","1,2","2,2"]

	buroRegularArray=["2,0","3,0","4,0","5,0","6,0","7,0","96,0","97,0",
	                  "0,1","1,1","2,1","3,1","4,1","5,1","6,1","7,1","96,1","97,1",
	                  "0,2","1,2","2,2","3,2","4,2","5,2","6,2","7,2","96,2","97,2",
	                  "0,3","1,3","2,3","3,3","4,3","5,3","6,3","7,3","96,3","97,3",
	                  "0,3","1,3","2,3","3,3","4,3","5,3","6,3","7,3","96,3","97,3",
	                  "0,4","1,4","2,4","3,4","4,4","5,4","6,4",
	                  "0,5","1,5","2,5","3,5","4,5","5,5",
	                  "0,6","1,6","2,6","3,6","4,6","5,6",
	                  "0,7","1,7","2,7","3,7","4,7","5,7"
	]
	buroMaloArray=[      "7,4","96,4","97,4",
	               "6,5","7,5","96,5","97,5",
	               "6,6","7,6","96,6","97,6",
	               "6,7","7,7","96,7","97,7"
	               ]

	vecesSalario=int(saldoVencido/salario)
	buroSolicitud=str(int(solicitudMop))+","+str(vecesSalario)

	if buroSolicitud in buroBuenoArray:
		tipoBuro="Bueno"
	if buroSolicitud in buroRegularArray:
		tipoBuro="Regular"

	if buroSolicitud in buroRegularConCapacidadArray:
		tipoBuro="Regular con Capacidad"

	if (buroSolicitud in buroMaloArray or
		vecesSalario >= 8 ):
		tipoBuro="Malo"

	return tipoBuro

def getTipoBuroV3(solicitudMop,saldoVencido,salario):
	# Se aplica a partir del 01 de Octubre de 2023 por instrucción de Hector Gamba
	tipoBuro=""
	buroBuenoArray=["0,0","1,0"]
	buroRegularConCapacidadArray =["2,0","3,0","4,0","5,0","6,0","7,0","96,0","97,0",
	                   "0,1","1,1","2,1","3,1","4,1","5,1","6,1","7,1","96,1","97,1",
	                   "0,2","1,2","2,2","3,2","4,2","5,2","6,2","7,2","96,2","97,2",]

	buroRegularArray=["2,0","3,0","4,0","5,0","6,0","7,0","96,0","97,0",
	                  "0,1","1,1","2,1","3,1","4,1","5,1","6,1","7,1","96,1","97,1",
	                  "0,2","1,2","2,2","3,2","4,2","5,2","6,2","7,2","96,2","97,2",
	                  "0,3","1,3","2,3","3,3","4,3","5,3","6,3","7,3","96,3","97,3",
	                  "0,3","1,3","2,3","3,3","4,3","5,3","6,3","7,3","96,3","97,3",
	                  "0,4","1,4","2,4","3,4","4,4","5,4","6,4",
	                  "0,5","1,5","2,5","3,5","4,5","5,5",
	                  "0,6","1,6","2,6","3,6","4,6","5,6",
	                  "0,7","1,7","2,7","3,7","4,7","5,7"
	]
	buroMaloArray=[      "7,4","96,4","97,4",
	               "6,5","7,5","96,5","97,5",
	               "6,6","7,6","96,6","97,6",
	               "6,7","7,7","96,7","97,7"
	               ]

	vecesSalario=int(saldoVencido/salario)
	buroSolicitud=str(int(solicitudMop))+","+str(vecesSalario)

	if buroSolicitud in buroBuenoArray:
		tipoBuro="Bueno"
	if buroSolicitud in buroRegularArray:
		tipoBuro="Regular"

	if buroSolicitud in buroRegularConCapacidadArray:
		tipoBuro="Regular con Capacidad"

	if (buroSolicitud in buroMaloArray or
		vecesSalario >= 8 ):
		tipoBuro="Malo"

	return tipoBuro






