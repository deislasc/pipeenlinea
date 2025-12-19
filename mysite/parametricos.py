#-*- coding: utf-8 -*-
empresasExcepcionASeisMeses={
	"empresasAutorizadas":[
	  	"C.A.E"
  	]
}
parametricosSimuladorBuroBueno={
	# Internos por antigûedad minima en meses
	"internos":{
		"3": {"tasa":40.20,
			  "comision":.03,
			  "mesesSueldo":0.5,
			  "plazos":[6,12,18,24,30,36,42,48]
		},
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
		"3": {"tasa":40.80,
			  "comision":.03,
			  "mesesSueldo":0.5,
			  "plazos":[6,12,18,24,30,36,42,48]
		},
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
		"12":{"tasa":23.80,
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
		"12":{"tasa":43.44,
			 "comision":.03,
			 "montoMax":12000,
			 "plazos":[6,7,8,9,10,11,12,18]
		},
		"24":{"tasa":41.04,
			 "comision":.02,
			 "montoMax":17000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30]
		},
		"36":{"tasa":41.04,
			 "comision":.02,
			 "montoMax":20000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30]
		},
		"48":{"tasa":35.04,
			 "comision":.01,
			 "montoMax":22000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36]
		},
		"60":{"tasa":35.04,
			 "comision":.01,
			 "montoMax":27000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36]
		},
		"72":{"tasa":35.04,
			 "comision":.01,
			 "montoMax":30000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36,42]
		}
	},
	"choferesCaabsaEagle":{
		"12":{"tasa":43.44,
			 "comision":.03,
			 "montoMax":14000,
			 "plazos":[6,7,8,9,10,11,12,18]
		},
		"24":{"tasa":41.04,
			 "comision":.02,
			 "montoMax":22000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30]
		},
		"36":{"tasa":41.04,
			 "comision":.02,
			 "montoMax":24000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30]
		},
		"48":{"tasa":35.04,
			 "comision":.01,
			 "montoMax":26000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36]
		},
		"60":{"tasa":35.04,
			 "comision":.01,
			 "montoMax":30000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36,42,48]
		},
		"72":{"tasa":35.04,
			 "comision":.01,
			 "montoMax":35000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36,42,48]
		}
	}
}

parametricosSimuladorBuroRegular={
	# Internos por antigûedad minima en meses
	"internos":{
		"3": {"tasa":45.00,
			  "comision":.03,
			  "mesesSueldo":0.5,
			  "plazos":[6,12,18,24,30,36,42,48]
		},
		"6": {"tasa":45.00,
			  "comision":.03,
			  "mesesSueldo":1,
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
		"3": {"tasa":45.60,
			  "comision":.03,
			  "mesesSueldo":0.5,
			  "plazos":[6,12,18,24,30,36,42,48]
		},
		"6": {"tasa":45.60,
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
		"12":{"tasa":67.44,
			 "comision":.03,
			 "montoMax":12000,
			 "plazos":[6,7,8,9,10,11,12]
		},
		"24":{"tasa":65.04,
			 "comision":.04,
			 "montoMax":17000,
			 "plazos":[6,7,8,9,10,11,12,18,24]
		},
		"36":{"tasa":65.04,
			 "comision":.04,
			 "montoMax":20000,
			 "plazos":[6,7,8,9,10,11,12,18,24]
		},
		"48":{"tasa":59.04,
			 "comision":.03,
			 "montoMax":22000,
			 "plazos":[6,7,8,9,10,11,12,18,24]
		},
		"60":{"tasa":59.04,
			 "comision":.03,
			 "montoMax":27000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36]
		},
		"72":{"tasa":59.04,
			 "comision":.03,
			 "montoMax":30000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36,42]
		}
	},
	"choferesCaabsaEagle":{
		"12":{"tasa":67.44,
			 "comision":.03,
			 "montoMax":14000,
			 "plazos":[6,7,8,9,10,11,12]
		},
		"24":{"tasa":65.04,
			 "comision":.04,
			 "montoMax":22000,
			 "plazos":[6,7,8,9,10,11,12,18,24]
		},
		"36":{"tasa":65.04,
			 "comision":.04,
			 "montoMax":24000,
			 "plazos":[6,7,8,9,10,11,12,18,24]
		},
		"48":{"tasa":59.04,
			 "comision":.03,
			 "montoMax":26000,
			 "plazos":[6,7,8,9,10,11,12,18,24]
		},
		"60":{"tasa":59.04,
			 "comision":.03,
			 "montoMax":30000,
			 "plazos":[6,7,8,9,10,11,12,18,24,30,36,42,48]
		},
		"72":{"tasa":59.04,
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


# Clasificacion MOP
MOP={
	"MOP-00":"Cuenta muy reciente para ser calificada.",
	"MOP-01":"Pago puntual y adecuado.",
	"MOP-02":"Retraso de 1 a 29 días.",
	"MOP-03":"Retraso de 30 a 59 días.",
	"MOP-04":"Retraso de 60 a 89 días.",
	"MOP-05":"Retraso de 90 a 119 días.",
	"MOP-06":"Retraso de 120 a 179 días.",
	"MOP-07":"Retraso de 180 o más.",
	"MOP-97":"Cuenta con deuda parcial o total sin recuperar. Este MOP aplica al otorgarse 'quita' o cuando no ha sido posible cobrar el crédito.",
	"MOP-99":"Fraude cometido por el consumidor."
}

# Capacidad de Pago
factorCapacidadDePago={
	"No Sindicalizados":0.30,
	"Sindicalizados":1.00

}

# Campañas
campanias=[
			{
			 "nombre":"50% Más por Buen Buro",
			 "del":"2022-03-01",
			 "hasta":"2022-03-31",
			 "nivelesRiesgoAplican":["Riesgo 1","Riesgo 2","Riesgo 3"],
			 "productos":["Nómina"],
			 "tipoBuroCredito":["Bueno"],
			 "tipoEmpresaAplica":["Interna","Externa"],
			 "clienteSindicalizadoAplicar":["","No Aplica","Auxiliar Caabsa Eagle", "Chofer Caabsa Eagle"],
			 "clienteDirectivoAplicar":"true",
			 "aplicarComisionCero":"true",
			 "factorCredito":"1.50",
			 "status":"Activa" #"Activa","Vencida"
			},
			{
			 "nombre":"50% Más por Buen Buro",
			 "del":"2023-10-01",
			 "hasta":"2022-03-31",
			 "nivelesRiesgoAplican":["Riesgo 1","Riesgo 2","Riesgo 3"],
			 "productos":["Nómina"],
			 "tipoBuroCredito":["Regular con Capacidad"],
			 "tipoEmpresaAplica":["Interna","Externa"],
			 "clienteSindicalizadoAplicar":["","No Aplica","Auxiliar Caabsa Eagle", "Chofer Caabsa Eagle"],
			 "clienteDirectivoAplicar":"true",
			 "aplicarComisionCero":"true",
			 "factorCredito":"1.50",
			 "status":"Activa" #"Activa","Vencida"
			}
]
# Niveles de Riesgo
nivelRiesgo={
	"Riesgo 1":{
		"nombre": "Riesgo 1",
		"mesesSueldoExtra":0,
		"mesesAntiguedadMinimaMalBuro":0,
		"factorBuenBuro":2.0,
		"requiereAvalMalBuró":"No",
		"excepcionesBuroMalo":"Regular",  #Se consideran como regular
		"maxMeses":0,
		"descripcion":"Empresas con baja mora y con quien seremos más laxos (prestar un mes más de lo que dicen las políticas y no rechazar créditos por mal buró, a éstos considerarlos de regular buró). Se podrán prestar hasta 5 meses"
	},
	"Riesgo 2":{
		"nombre": "Riesgo 2",
		"mesesSueldoExtra":0.5,
		"mesesAntiguedadMinimaMalBuro":24,
		"factorBuenBuro":1.0,
		"requiereAvalMalBuró":"Sí",
		"excepcionesBuroMalo":"Regular",  #Se consideran como regular
		"maxMeses":5,
		"descripcion":"Empresas con mora controlada y con quien seremos un poco más laxos (prestar medio mes más y para los que tengan mal burò y más de dos años pedir aval para prestarles conforme a la politicas)."
	},
	"Riesgo 3":{
		"nombre": "Riesgo 3",
		"mesesSueldoExtra": 0,
		"mesesAntiguedadMinimaMalBuro":24,
		"factorBuenBuro":1.0,
		"requiereAvalMalBuró":"Sí",
		"excepcionesBuroMalo":"Malo",
		"maxMeses":5,
		"descripcion":"Continuar políticas actuales, los que tengan mal buró y más de dos años prestar conforme a política 'Criterio para prestar a rechazados'"
	},
	"Riesgo 4":{
		"nombre": "Riesgo 4",
		"mesesSueldoExtra": -1,
		"mesesAntiguedadMinimaMalBuro":0,
		"factorBuenBuro":1.0,
		"requiereAvalMalBuró":"Sí",
		"excepcionesBuroMalo":"Malo",
		"maxMeses":5,
		"plazosPorAntiguedad":{
			"12":{
				"Regular":6,
				"Bueno": 12
			},
			"24":{
				"Regular":12,
				"Bueno": 18
			},
			"48":{
				"Regular":18,
				"Bueno":24
			}
		},
		"descripcion":"Prestar un mes menos de lo que dicen las políticas.  1r6, 1b12, 2r12,2b18,4r18,4b24"
	},
	"Riesgo 5":{
		"nombre": "Riesgo 5",
		"mesesSueldoExtra": 0,
		"mesesAntiguedadMinimaMalBuro":"",
		"requiereAvalMalBuró":"Sí",
		"excepcionesBuroMalo":"Malo",
		"factorBuenBuro":1.0,
		"maxMeses":1,
		"plazosPorAntiguedad":{
			"12":{
				"Regular":0,
				"Bueno": 6
			},
			"24":{
				"Regular":6,
				"Bueno": 12
			},
			"48":{
				"Regular":12,
				"Bueno": 12
			}
		},
		"descripcion":"Prestar máximo un mes de sueldo (1r0 préstamos), plazos 1b6meses, 2r6, 2b12,4r12,4b12"
	}

}

# SEGURO FINANCIADO
impactoSeguroCapitalPermitido ={ 'limite':0.1 }
