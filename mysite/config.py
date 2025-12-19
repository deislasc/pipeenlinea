estatusOrden=[{
	"RECHAZADO":0,
	"CONTACTO":1,
	"ENTREGA A RIESGOS":2,
	"AUTORIZADO":3,
	"EN AUTORIZACION DG":4,
	"CONTRATO IMPRESO":5,
	"FIRMAR CONTRATO":6,
	"FONDEADO":7
},
{
	"fechaRechazoRiesgos":0,
	"fechaRechazoDG":0,
	"fechaCancelacionCliente":0,
	"fechaCancelacionCartera":0,
	"fechaContacto":1,
	"fechaEntregaARiesgos":2,
	"fechaPropuesta":3,
	"fechaAutorizacionDG":4,
	"fechaContratoImpreso":5,
	"fechaEntregaContratoFirmado":6,
	"fechaFondeado":7
},
{
	# ARREGLO PARA REPORTE DE SOLICITUDES

	"CONTACTO": {
				  "fechaReferencia":"fechaContacto",
				  "areaResponsable":"COMERCIAL",
				  "diasMax":2
				 },

	"ENTREGA A RIESGOS": {
				  "fechaReferencia":"fechaEntregaARiesgos",
				  "areaResponsable":"RIESGOS",
				  "diasMax":5
				 },
	"AUTORIZADO":{
				  "fechaReferencia":"fechaPropuesta",
				  "areaResponsable":"RIESGOS",
				  "diasMax":1
				 },
	"EN AUTORIZACION DG":{
				  "fechaReferencia":"fechaAutorizacionDG",
				  "areaResponsable":"RIESGOS",
				  "diasMax":1
				 },

	"CONTRATO IMPRESO":{
				  "fechaReferencia":"fechaContratoImpreso",
				  "areaResponsable":"COMERCIAL",
				  "diasMax":1
				 },
	"FIRMAR CONTRATO":{
				  "fechaReferencia":"fechaEntregaContratoFirmado",
				  "areaResponsable":"CARTERA",
				  "diasMax":1
				 }

}

]

diasFestivos=[	'2018-11-02','2018-11-19','2018-12-12','2018-12-25',
		  		'2019-01-01','2019-02-04','2019-03-18','2019-05-01',
		  		'2019-09-16','2019-11-18','2019-12-12','2019-12-25',
		  		'2019-12-31',
		  		'2020-01-01','2020-02-03','2020-03-16','2020-04-09',
		  		'2020-04-10','2020-05-01','2020-09-16','2020-11-02',
		  		'2020-11-16','2020-12-12','2020-12-25',
		  		'2021-01-01','2021-02-01','2021-03-15','2021-04-01',
		  		'2021-04-02','2021-05-01','2021-09-16','2021-11-02',
		  		'2021-11-15','2021-12-12','2021-12-25',
              	'2022-02-07','2022-03-21','2022-04-14','2022-04-15',
              	'2022-09-16','2022-11-02','2022-11-21','2022-12-25',
              	'2023-01-01','2023-02-06','2023-03-20','2023-04-06',
              	'2023-04-07','2023-05-01','2023-09-16','2023-11-02',
              	'2023-11-20','2023-12-12','2023-12-25'
		  	]
mesesNombres=[{
				"01":"enero",
				"02":"febrero",
				"03":"marzo",
				"04":"abril",
				"05":"mayo",
				"06":"junio",
				"07":"julio",
				"08":"agosto",
				"09":"septiembre",
				"10":"octubre",
				"11":"noviembre",
				"12":"diciembre"
			  }]
niveldeCuenta=[
		{
		 "min":0,
		 "max":75000,
		 "nivel":"Chico"
		},
		{
		 "min":75000,
		 "max":150000,
		 "nivel":"Mediano"
		},
		{
		 "min":150000,
		 "max":750000,
		 "nivel":"Grande"
		},
		{
		 "min":750000,
		 "max":100000000,
		 "nivel":"Mega"
		}
]

DB={
	 "acl":"working/acl.json",
	 "agendas":"working/agendas.json",
	 "consultas":"working/consultas.json",
	 "empresas":"working/empresas.json",
	 "geolocations":"working/geolocations.json",
	 "logs":"working/logs.json",
	 "pagadoras":"working/pagadoras.json",
	 "roips":"working/roips.json",
	 "solicitudes":"working/solicitudes.json",
	 "users":"working/users.json"
}

documentos=[
	"solcitudDeSeguro",
	"solicitudDeCredito",
    "comprobanteDomicilio",
    "estadoDeCuenta",
    "formatoCURP",
    "identificacionOficial",
    "listasNegras",
    "solicitudBuroCredito",
    "validacionINE",
    "validacionSueldos",
    "saldo1a89",
	"saldoMayor90",
	"saldoMayor120",
	"solicitudEsCleanUp",
	"solicitudMop"
]

camposControlExpedientes=[
	'asesorNombre',
	'clienteApellidoMaterno',
	'clienteApellidoPaterno',
	'clienteEmpresa',
	'clienteNombre',
	'comentariosResguardoExpedientes',
	'documentos',
	'expedienteResguardoStatus',
	'fechaContratoImpreso',
	'fechaExpedienteDevueltoAComercial',
	'fechaExpedienteRecibidoRiesgos',
	'fechaExpedienteResguardadoEnBoveda',
	'fechaExpedienteRevisadoRiesgos',
	'id',
	'montoAutorizado',
	'montoSolicitado',
	'producto',
	'solicitudEstatus',
	'solicitudNumeroControl',
	'tipoBuroCredito',
	'usuarioExpedienteDevueltoAComercial',
	'usuarioExpedienteRecibidoRiesgos',
	'usuarioExpedienteResguardadoEnBoveda',
	'usuarioExpedienteRevisadoRiesgos'
]

camposMesaControl=[
	'asesorNombre',
	'analistaNombre',
	'buenBuroEstatus',
	'buenBuroMontoOferta',
	'buenBuroMontoAceptado',
	'clienteApellidoMaterno',
	'clienteApellidoPaterno',
	'clienteEmpresa',
	'clienteNombre',
	'comentarios',
	'documentos',
	'fechaEntregaARiesgos',
	'estatusAnalisis',
	'id',
	'montoAutorizado',
	'montoSolicitado',
	'producto',
	'solicitudNumeroControl',
	'solicitudEstatus',
	'observacionesAnalisis'
]

camposAnalisisCredito=[
	"capacidadDePago",
	"clienteAntiguedadMeses",
	"clienteAvalRequerido",
	"clienteDeduccionesMensuales",
	"clienteDeduccionesQuincenales",
	"clienteDeduccionesSemanales",
	"clienteDirectivo",
	"clienteEmpresa",
	"clienteFechaIngreso",
	"clienteNivelRiesgoEmpresa",
	"clientePrestarHasta",
	"clienteSalario",
	"clienteSindicalizado",
	"clienteTipoEmpresa",
	"comentarios",
	"costoSeguroParcialidad",
	"empresaPagadora",
	"errorTransferencia",
	"excepcionDocumentada1",
	"excepcionDocumentada2",
	"excepcionDocumentada3",
	"fechaEmisionContrato",
	"fechaPrimerCobro",
	"fechaVencimientoLineaDeCredito",
	"frecuenciaDePago",
	"lineaDeCredito",
	"montoAutorizado",
	"montoCapacidadDePago",
	"montoBuenBuro",
	"montoComision",
	"montoComisionPolitica",
	"montoMaximoPolitica",
	"montoPropuesto",
	"montoSolicitado",
	"montoTransferencia",
	"numeroPagos",
	"pagoEstimadoPeriodo",
	"pagoTotalPeriodo",
	"plazoAutorizado",
	"plazoMaximoPolitica",
	"plazoSolicitado",
	"polizaSeguro",
	"producto",
	"regionNombre",
	"saldo1a89",
	"saldoMayor90",
	"saldoMayor120",
	"solicitudEsCleanUp",
	"solicitudMop",
	"solicitudSaldoParcialidadesMontoAnterior",
	"solicitudSeguroFinanciado",
	"tasaAutorizada",
	"tasaDeComisionPolitica",
	"tasaPolitica",
	"tipoBuroCredito",
	"tipoListaNegra"
]

camposCalculadosAnalisisCredito = [
	"capacidadDePago",
	"clienteAntiguedadMeses",
	"clienteAvalRequerido",
	"clienteDeduccionesPeriodo",
	"clienteNivelRiesgoEmpresa",
	"clientePrestarHasta",
	"clienteTipoEmpresa",
	"costoSeguroParcialidad",
	"empresaPagadora",
	"errorTransferencia",
	"lineaDeCredito",
	"montoBuenBuro",
	"montoCapacidadDePago",
	"montoComision",
	"montoComisionPolitica",
	"montoMaximoPolitica",
	"montoTransferencia",
	"montoPropuesto",
	"numeroPagos",
	"pagoEstimadoPeriodo",
	"pagoTotalPeriodo",
	"plazoMaximoPolitica",
	"solicitudAvanceCreditoAnterior",
	"solicitudIncrementoSaldoActual"
	"solicitudMontoOriginalAnterior",
	"solicitudSaldoTotal",
	"tasaDeComisionPolitica",
	"tasaPolitica",
	"tipoBuroCredito"
]

accionesDeProceso=[
	"Guardar Revision",
	"Realizar Analisis"
]

camposSesion=[
	"ownerID",
    "inheritedID",
    "viewName",
    "accion",
    "name",
    "userName",
    "lastUpdatedmenuRevisionDocumental",
    "lastUpdatedmenuAnalisisCreditos"
]

camposNumericos=[
	"clienteDeduccionesMensuales",
	"clienteDeduccionesPeriodo",
	"clienteDeduccionesQuincenales",
	"clienteDeduccionesSemanales",
	"clienteSalario",
	"costoSeguroParcialidad",
	"ivaInteresesSimulador",
	"lineaDeCredito",
	"montoAutorizado",
	"montoBuenBuro",
	"montoCapacidadDePago",
	"montoComision",
	"montoComisionPolitica",
	"montoMaximoPolitica",
	"montoMinistracion",
	"montoPropuesto",
	"montoSeguro",
	"montoIvaComision",
	"montoIVASeguro",
	"montoSolicitado",
	"montoTransferencia",
	"pagoEstimadoPeriodo",
	"pagoParcialidadSimulador",
	"pagoTotalPeriodo",
	"pagoTotalSimulador",
	"saldo1a89",
	"saldoMayor90",
	"saldoMayor120",
	"solicitudAvanceCreditoAnterior",
	"solicitudIncrementoSaldoActual",
	"solicitudMontoOriginalAnterior",
	"solicitudSaldoActualSIACAnterior",
	"solicitudSaldoParcialidadesMontoAnterior",
	"solicitudSaldoParcialidadesNumeroAnterior",
	"solicitudSaldoTotalAnterior",
	"solicitudSeguroFinanciado",
	"solicitudTotalPagadoSIACAnterior",
	"tasaPolitica",
	"totalInteresesSimulador"
]

camposPreAnalisisOrden=[
	"regionNombre",
	"clienteEmpresa",
	"clienteNombre",
	"clienteApellidoPaterno",
	"clienteApellidoMaterno",
	"producto",
	"montoSolicitado",
	"plazoSolicitado",
	"documentos",
	"polizaSeguro",
	"clienteDirectivo",
	"clienteSindicalizado",
	"clienteFechaIngreso",
	"frecuenciaDePago",
	"clienteSalario",
	"clienteDeduccionesMensuales",
	"clienteDeduccionesQuincenales",
	"clienteDeduccionesSemanales",
	"tipoListaNegra",
	"saldo1a89",
	"saldoMayor90",
	"saldoMayor120",
	"solicitudMop",
	"solicitudEsCleanUp",
	"solicitudSaldoParcialidadesMontoAnterior",
	"fechaEmisionContrato",
	"fechaPrimerCobro",
	"accionRealizarAnalisis",
	"clientePagadora",
	"voboRequerido",
	"clienteAntiguedadMeses",
	"tipoBuroCredito",
	"montoCapacidadDePago",
	"montoMaximoPolitica",
	"montoBuenBuro",
	"montoPropuesto",
	"tasaPolitica",
	"plazoMaximoPolitica",
	"tasaDeComisionPolitica",
	"montoComisionPolitica",
	"comentarios"
	]

empresasExternas=[
	"CREDICONFIA",
	"SUNSET",
	"SERVSAT",
	"MABRATEX",
	"ADNA",
	"GRUPO CANARIOS ANTARA",
	"CANARIOS",
	"GPO CANARIOS",
	"GRUPO PISA",
	"PISA",
	"KING FISH",
	"GLOBAL MED",
	"CIPRIANI",
	"CARVALLO Y CICERON SOLIDEZ LEGAL Y CONTABLE S.C.",
	"COFIPYME",
	"BALANCE INNOVADOR SERVICIOS SA DE CV",
	"DCCN",
	"ELI LILLY DE MEXICO SA DE CV",
	"EXTERNO",
	"RESTAURANTES GROGI",
	"GROGI",
	"T&T SOLUCIONES PROFESIONALES EN ADMINISTRACION",
	"IMAGEN COMERCIAL SUNSET S.A. DE C.V.",
	"LUXUS",
	"MABRATEX S.A. DE C.V.",
	"INTELUXE, S.A. DE C.V.",
	"INTELUXE",
	"ROLINAVA, S.A. DE C.V.",
	"ROLINAVA",
	"SERVICIOS ADMINISTRATIVOS E INDUSTRIALES ILEKUN, S.A. DE C.V.",
	"ILEKUN",
	"GRUPO SORDO MADALENO",
	"SORDO MADALENO",
	"SERVSAT COMMUNICATIONS S.A. DE C.V.",
	"TELLES MENESES Y ASOCIADOS SC",
	"DMC SANTA FE S.A. DE C.V.",
	"DMC",
	"VALUE SHORE ADVISORS",
	"VALUE SHORE",
	"VIALIDADES DELAC SA DE CV"
]


parametricosSimuladorBuroBueno={
	# 2024-03-04 Se regresa a tasas y comisiones de las politicas V7.01 (últimas autorizadas por el comité)
	# Internos por antigûedad minima en meses
	"internos":{
		"6": {"tasa":40.20,
			  "comision":.03,
			  "mesesSueldo":1,
			  "plazos":[6,12,18,24,30,36,42,48]
		},

		"12":{"tasa":36.00,
			 "comision":.03,
			 "mesesSueldo":2,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
		"24":{"tasa":31.80,
			 "comision":.03,
			 "mesesSueldo":3,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
		"48":{"tasa":28.20,
			 "comision":.03,
			 "mesesSueldo":4,
			 "plazos":[6,12,18,24,30,36,42,48]
		}
	},
	"externos":{
		"6": {"tasa":40.80,
			  "comision":.03,
			  "mesesSueldo":1,
			  "plazos":[6,12,18,24,30,36,42,48]
		},

		"12":{"tasa":37.20,
			 "comision":.03,
			 "mesesSueldo":2,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
		"24":{"tasa":32.40,
			 "comision":.03,
			 "mesesSueldo":3,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
		"48":{"tasa":28.80,
			 "comision":.03,
			 "mesesSueldo":4,
			 "plazos":[6,12,18,24,30,36,42,48]
		}
	},

	"directivoInterno":{
        "6":{"tasa":24.00,
			 "comision":.03,
			 "mesesSueldo":1,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
		"12":{"tasa":22.80,
			 "comision":.03,
			 "mesesSueldo":3,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
		"24":{"tasa":22.20,
			 "comision":.03,
			 "mesesSueldo":4,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
		"48":{"tasa":21.60,
			 "comision":.03,
			 "mesesSueldo":5,
			 "plazos":[6,12,18,24,30,36,42,48]
		}
	},
	"directivoExterno":{
        "6":{"tasa":24.00,
			 "comision":.03,
			 "mesesSueldo":1,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
        "12":{"tasa":23.40,
			 "comision":.03,
			 "mesesSueldo":3,
			 "plazos":[6,12,18,24,30,36,42,48]
		},

		"24":{"tasa":22.80,
			 "comision":.03,
			 "mesesSueldo":4,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
		"48":{"tasa":22.20,
			 "comision":.03,
			 "mesesSueldo":5,
			 "plazos":[6,12,18,24,30,36,42,48]
		}
	},
	"auxiliaresCaabsaEagle":{
		"12":{"tasa":35.05,
			 "comision":.03,
			 "montoMax":12000,
			 "plazos":[6,7,8,9,10,11,12,18]
		},
		"24":{"tasa":32.65,
			 "comision":.02,
			 "montoMax":17000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30]
		},
		"36":{"tasa":32.65,
			 "comision":.02,
			 "montoMax":20000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30]
		},
		"48":{"tasa":26.65,
			 "comision":.01,
			 "montoMax":22000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36]
		},
		"60":{"tasa":26.65,
			 "comision":.01,
			 "montoMax":27000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36]
		},
		"72":{"tasa":26.65,
			 "comision":.01,
			 "montoMax":30000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36,42]
		}
	},
	"choferesCaabsaEagle":{
		"12":{"tasa":35.05,
			 "comision":.03,
			 "montoMax":14000,
			 "plazos":[6,7,8,9,10,11,12,18]
		},
		"24":{"tasa":32.65,
			 "comision":.02,
			 "montoMax":22000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30]
		},
		"36":{"tasa":32.65,
			 "comision":.02,
			 "montoMax":24000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30]
		},
		"48":{"tasa":26.65,
			 "comision":.01,
			 "montoMax":26000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36]
		},
		"60":{"tasa":26.65,
			 "comision":.01,
			 "montoMax":30000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36,42,48]
		},
		"72":{"tasa":26.65,
			 "comision":.01,
			 "montoMax":35000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36,42,48]
		}
	}
}

parametricosSimuladorBuroRegular={
	# Internos por antigûedad minima en meses
	"internos":{
        "6":{"tasa":45.00,
			 "comision":.03,
			 "mesesSueldo":0.5,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
		"12":{"tasa":43.80,
			 "comision":.03,
			 "mesesSueldo":1,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
		"24":{"tasa":42.60,
			 "comision":.03,
			 "mesesSueldo":2,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
		"48":{"tasa":41.40,
			 "comision":.03,
			 "mesesSueldo":2,
			 "plazos":[6,12,18,24,30,36,42,48]
		}
	},
	"externos":{
        "6":{"tasa":45.60,
			 "comision":.03,
			 "mesesSueldo":0.5,
			 "plazos":[6,12,18,24,30,36,42,48]
		},

		"12":{"tasa":44.40,
			 "comision":.03,
			 "mesesSueldo":1,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
		"24":{"tasa":43.20,
			 "comision":.03,
			 "mesesSueldo":2,
			 "plazos":[6,12,18,24,30,36,42,48]
		},
		"48":{"tasa":42.00,
			 "comision":.03,
			 "mesesSueldo":2,
			 "plazos":[6,12,18,24,30,36,42,48]
		}
	},
	"auxiliaresCaabsaEagle":{
		"12":{"tasa":59.05,
			 "comision":.03,
			 "montoMax":6000,
			 "plazos":[6,7,8,9,10,11,12]
		},
		"24":{"tasa":56.65,
			 "comision":.04,
			 "montoMax":13000,
			 "plazos":[6,7,8,9,10,11,12,18,24]
		},
		"36":{"tasa":56.65,
			 "comision":.04,
			 "montoMax":15000,
			 "plazos":[6,7,8,9,10,11,12,18,24]
		},
		"48":{"tasa":50.65,
			 "comision":.03,
			 "montoMax":17000,
			 "plazos":[6,7,8,9,10,11,12,18,24]
		},
		"60":{"tasa":50.65,
			 "comision":.03,
			 "montoMax":22000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36]
		},
		"72":{"tasa":50.65,
			 "comision":.03,
			 "montoMax":25000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36,42]
		}
	},
	"choferesCaabsaEagle":{
		"12":{"tasa":59.05,
			 "comision":.03,
			 "montoMax":14000,
			 "plazos":[6,7,8,9,10,11,12]
		},
		"24":{"tasa":56.65,
			 "comision":.04,
			 "montoMax":22000,
			 "plazos":[6,7,8,9,10,11,12,18,24]
		},
		"36":{"tasa":56.65,
			 "comision":.04,
			 "montoMax":24000,
			 "plazos":[6,7,8,9,10,11,12,18,24]
		},
		"48":{"tasa":50.65,
			 "comision":.03,
			 "montoMax":26000,
			 "plazos":[6,7,8,9,10,11,12,18,24]
		},
		"60":{"tasa":50.65,
			 "comision":.03,
			 "montoMax":30000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36,42,48]
		},
		"72":{"tasa":50.65,
			 "comision":.03,
			 "montoMax":35000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36,42,48]
		}
	}
}

# Pagos al año segùn frecuencia
numPagosAlAnio={
	"Semanal":52,
	"Quincenal":24,
	"Catorcenal":24,
	"Mensual":12
}

# Costo Quincenal del Seguro
costoSeguros={
	"25000":44.50,
	"50000":79.50,
	"75000":119.50,
	"100000":144.50
}




