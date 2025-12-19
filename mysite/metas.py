# El divisor indica cuantos AN equivalen a un CN
# El min indica cuantos CN se requieren como mínimo para que empiecen a contarse los AN
ponderacion={"divisor":5,
             "min":20
}


metasCN={"contactados":30,
	   "entregadosARiesgos":25,
	   "autorizados":20
}

agrupadores={
	"Nómina":"CN",
	"Vehículo":"CN",
	"Vehículos":"CN",
    "Adelanto de Nómina":"AN",
    "Seguro":"Seguros",
    "Seguro Independiente":"Seguros"
}

agrupadoresScoreCards=['CN','AN','MIX','Seguros']

comisionesAN=[0.005]

comisionesCN=[
	{"min":1.5,
	 "max":100,
	 "comision":0.02,
	 "nivel":"azul",
	 "bgcolor":"#0000FF",
	 "color":"#FFFFFF"
	},
	{"min":1.25,
	 "max":1.5,
	 "comision":0.015,
	 "nivel":"verde",
	 "bgcolor":"#00FF00",
	 "color":"#000000"
	},
	{"min":1,
	 "max":1.25,
	 "comision":0.01,
	 "nivel":"blanco",
	 "bgcolor":"#FFFFFF",
	 "color":"#000000"
	},
	{"min":0.75,
	 "max":1,
	 "comision":0.005,
	 "nivel":"amarillo",
	 "bgcolor":"#FFFF00",
	 "color":"#000000"
	},
	{"min":0,
	 "max":0.75,
	 "comision":0.000,
	 "nivel":"rojo",
	 "bgcolor":"#FF0000",
	 "color":"#FFFF00"
	}
]