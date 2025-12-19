import config
import sys
import datetime
import json
import os
import zipfile
import shutil
from flask import Response

import update
from routes_csv import jsontocsv as jsontocsv
from routes_solicitudes import correctSolicitudesData  as correctSolicitudesData
from routes_empresas import correctEmpresasData as correctEmpresasData
from routes_logs import correctLogsData as correctLogsData



'''
Este script se corre en la terminal
python3 respaldar

Se genera un archivo año_mes_dia_backup
'''
# **********************************************************
#             SE OBTIENEN TODAS LAS SOLICITUDES-->
# **********************************************************


workingDir="/home/pipeenlinea/"
specificDir="working/solicitudes.json"

listaSolicitudes = update.reloadJSONData(specificDir)
listaSolicitudes.pop(0)
listaSolicitudes = sorted(listaSolicitudes, key=lambda k: (k['fechaContacto']))

headers=[]
solicitud={"ownerID": "30",
        "inheritedID": "30",
        "viewName": "Solicitudes",
        "producto": "N\u00f3mina",
        "clienteNombre": "H\u00e9ctor Alejandro",
        "clienteApellidoPaterno": "P\u00e9rez",
        "clienteApellidoMaterno": "Navarro",
        "clienteNuevoRenovacion": "Renovaci\u00f3n",
        "clienteEmpresa": "Cajilota",
        "clientePuesto": "Chofer",
        "clienteAntiguedad": "M\u00e1s de 2 a\u00f1os",
        "clienteClabe": "",
        "clienteNombreJefe": "Omar Romero",
        "clienteCorreoJefe": "Omar Romero",
        "clienteSeEnteroPor": "Presentacion del Asesor",
        "montoSolicitado": "25000",
        "plazoSolicitado": "18",
        "polizaSeguro": "50000",
        "fechaContacto": "2022-05-18 09:13:11",
        "solicitudEstatus": "FONDEADO",
        "solicitudNumeroControl": "CN-3807",
        "fechaEntregaARiesgos": "2022-05-18 14:01:42",
        "fechaPropuesta": "2022-05-20 18:37:57",
        "fechaPrimerSolicitudVoBo": "",
        "fechaSegundaSolicitudVoBo": "",
        "fechaTercerSolicitudVoBo": "",
        "fechaVoBo": "2022-05-20 18:37:54",
        "fechaRechazoRiesgos": "",
        "fechaContratoImpreso": "2022-05-20 18:49:10",
        "fechaAutorizacionDG": "",
        "fechaRechazoDG": "",
        "fechaCancelacionCartera": "",
        "fechaEntregaContratoFirmado": "2022-05-25 11:13:24",
        "fechaFondeado": "2022-05-26 15:47:28",
        "fechaCancelacionCliente": "",
        "autorizacionDG": "Normal",
        "montoAutorizado": "25000",
        "montoTransferencia": "12696.54",
        "plazoAutorizado": "18",
        "etapaEmbudo": "CIERRE",
        "estatusEmbudo": "FONDEADO",
        "tipoDeNegocio": "GANADO",
        "motivoNoCierre": "",
        "fechaValidacionClabe": "",
        "clienteReferenciaCobranza": "",
        "fechaReferenciaCobranza": "",
        "regionNombre": "Guadalajara",
        "asesorNombre": "Alma Nayeli Gonzalez Robles",
        "id": "6778",
        "documentos": "https://drive.google.com/drive/folders/1RhDw-Mle3nwMw5vpTzu62tbUd_Z3r_RR",
        "editable": "true",
        "montoComision": "750.00",
        "usuarioAutorizacionRiesgos": "Brenda Benito Escudero"}

for campo in solicitud:
	headers.append(campo)
	print(campo)


csv=""
for i,campo in enumerate(headers):
	csv += campo
	if i< len(headers)-1:
		csv += "|"
	else:
		csv += "\n"

for renglon in listaSolicitudes:
	for i,campo in enumerate(headers):

		if campo in renglon:
			if type(renglon[campo])==list:
				renglon[campo]=""
			csv += renglon[campo] 
		if i< len(headers)-1:
			csv += "|"
		else:
			csv += "\n"

text_file = open("SolicitudesQuery.txt", "wt")
n = text_file.write(csv)
text_file.close()



# **********************************************************
#            <-- SE GENERAN ARCHIVOS DE BACK UP
# **********************************************************