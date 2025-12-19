weekmask=[0,1,1,1,1,1,0]
diasFestivos=['2020-01-01',
              '2020-02-03',
              '2020-03-16',
              '2020-04-09',
              '2020-04-10',
              '2020-05-01',
              '2020-09-16',
              '2020-11-02',
              '2020-11-16',
              '2020-12-12',
              '2020-12-25',
              '2021-01-01',
              '2021-02-01',
              '2021-03-15',
              '2021-04-01',
              '2021-04-02',
              '2021-05-01',
              '2021-09-16',
              '2021-11-02',
              '2021-11-15',
              '2021-12-12',
              '2021-12-25',
              '2022-02-07',
              '2022-03-21',
              '2022-04-14',
              '2022-04-15',
              '2022-09-16',
              '2022-11-02',
              '2022-11-21',
              '2022-12-25',
              '2023-01-01',
              '2023-02-06',
              '2023-03-20',
              '2023-04-06',
              '2023-04-07',
              '2023-05-01',
              '2023-09-16',
              '2023-11-02',
              '2023-11-20',
              '2023-12-12',
              '2023-12-25'
             ]

function numberToCurrency(num)
{   
    return "$ "+num.replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
}

function calculaAntiguedad()
{
	var fechaIngreso=document.getElementById("fechaIngreso").value;
	if (fechaIngreso==""){
		document.getElementById("antiguedad").value=0;
		return;
	}
  	fechaIngreso=fechaIngreso+"T06:00:00";
  	var hoy = new Date();
  	var fechaIngresoDate=new Date(fechaIngreso);
  	var meses_antiguedad= monthDiff(fechaIngresoDate,hoy)+1;
  	document.getElementById("antiguedad").value=meses_antiguedad;
}


function calculaPago(data,colocaEnMontoMaximo)
{	
 	
 	var meses_antiguedad=0;
	var sueldo=0;
	var mesesSueldo=0;
	var montoMax=0;
    
    
    meses_antiguedad=parseFloat(data.antiguedad)

	if(data.montoIngresos>0)
		sueldo=parseFloat(data.montoIngresos);

	if(data.mesesSueldo>0){
		mesesSueldo=parseFloat(data.mesesSueldo);
	}

    montoMax=sueldo*mesesSueldo;

	if(data.montoMax>0)
		montoMax=parseFloat(data.montoMax);
	
  	
  	if (meses_antiguedad<6){	
  	    verPlazos(0,meses_antiguedad);
  	    getRating("",1);	
  		alert('Lo sentimos, mínimo requieres tener 6 meses de antigüedad');
        return;
    }

    var sliderMonto = document.getElementById("rangoMonto");
    if(sueldo>0 || "montoMax" in data){
		
		sliderMonto.min=3000;
		sliderMonto.max=montoMax;

		if (colocaEnMontoMaximo){
			sliderMonto.value=montoMax;
			localStorage.setItem("monto",montoMax);
		}

		document.getElementById("monto").innerHTML=numberToCurrency(sliderMonto.value);
		document.getElementById("montoMaximo").innerHTML=numberToCurrency(sliderMonto.max);
    }

 	var frecuencia = localStorage.getItem("frecuencia");
	var tiempo = localStorage.getItem("plazo")/12;
	var tasa = data.tasa * 1.014;
	var comision = data.comision*1.16;
	var redito=0.0;
	var capital = localStorage.getItem("monto")*(1.00+comision);
	var intereses=0.00;
	var totalAPagar=0.00;
	var pago=0.00;
	var intereses_periodo=0.0;
    var numero_pagos;
    var numero_pagos_al_anio;
    var tir;
        
        
	if (frecuencia=="semanal"){
		numero_pagos=52*tiempo; 
		numero_pagos_al_anio=52;    
	}

	if (frecuencia=="catorcenal"){
		numero_pagos=52*tiempo/2;
		numero_pagos_al_anio=26;
	}

	if (frecuencia=="quincenal"){
		numero_pagos=24*tiempo;
		numero_pagos_al_anio=24;
	}

	if (frecuencia=="mensual"){
		numero_pagos=12*tiempo;
		numero_pagos_al_anio=12;
	}

    localStorage.setItem("numero_pagos",numero_pagos);
    
    redito=((tasa*1.16)/(100*numero_pagos_al_anio)); 
    intereses_periodo= capital*redito;


    tir=Math.pow(1+redito,numero_pagos);
    pago=(capital*tir*redito)/(tir-1);
    	


    totalAPagar=pago*numero_pagos;
		

   
    var pago_s= "$ "+pago.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
    document.getElementById("pago").innerHTML=pago_s;
    

   
    if(localStorage.getItem("frecuencia")!=null && localStorage.getItem("frecuencia")!="")
		document.getElementById("tuPago").innerHTML="pagos "+ frecuencia +"es de:"
	else
		document.getElementById("tuPago").innerHTML="pagos quincenales de:";

	if(localStorage.getItem("numero_pagos")!=null && localStorage.getItem("numero_pagos")>0)
		document.getElementById("numPagos").innerHTML=localStorage.getItem("numero_pagos");
	else
		document.getElementById("numPagos").innerHTML=0;


	
}


function monthDiff(d1, d2) {
    var months;
    months = (d2.getFullYear() - d1.getFullYear()) * 12;
    months -= d1.getMonth() + 1;
    months += d2.getMonth();
    return months <= 0 ? 0 : months;
}

function verPlazos(plazosVisibles){
    var element;
	//Deshabilito los radio buttons
	element=document.getElementById("plazo_6");
		element.disabled=true;
		element.checked=false;
		element.hidden=true;
		document.getElementById("labelPlazo_6").hidden=true;
	element=document.getElementById("plazo_12");
		element.disabled=true;
		element.checked=false;
		element.hidden=true;
		document.getElementById("labelPlazo_12").hidden=true;
	element=document.getElementById("plazo_18");
		element.disabled=true;
		element.checked=false;
		element.hidden=true;
		document.getElementById("labelPlazo_18").hidden=true;
	element=document.getElementById("plazo_24");
		element.disabled=true;
		element.checked=false;
		element.hidden=true;
		document.getElementById("labelPlazo_24").hidden=true;
	element=document.getElementById("plazo_30");
		element.disabled=true;
		element.checked=false;
		element.hidden=true;	
		document.getElementById("labelPlazo_30").hidden=true;
	element=document.getElementById("plazo_36");
		element.disabled=true;	
		element.checked=false;
		element.hidden=true;
		document.getElementById("labelPlazo_36").hidden=true;
	element=document.getElementById("plazo_42");
		element.disabled=true;	
		element.checked=false;
		element.hidden=true;
		document.getElementById("labelPlazo_42").hidden=true;

	//Habilito conforme a políticas	
	if (plazosVisibles>=6){
		element=document.getElementById("plazo_6");
		element.disabled=false;
		element.checked=true;
		element.hidden=false;
		document.getElementById("labelPlazo_6").hidden=false;
		getRating(6,1);
	}

	if (plazosVisibles>=12){
		element=document.getElementById("plazo_12");
		element.disabled=false;
		element.checked=true;
		element.hidden=false;
		document.getElementById("labelPlazo_12").hidden=false;
		getRating(12,1);
	}

	if (plazosVisibles>=18) {
		element=document.getElementById("plazo_18");
		element.disabled=false;
		element.checked=true;
		element.hidden=false;
		document.getElementById("labelPlazo_18").hidden=false;
		getRating(18,1);
	}

	if (plazosVisibles>=24){
		element=document.getElementById("plazo_24");
		element.disabled=false;
		element.checked=true;
		element.hidden=false;
		document.getElementById("labelPlazo_24").hidden=false;
		getRating(24,1);
	}

	if (plazosVisibles >=30){
		element=document.getElementById("plazo_30");
	    element.disabled=false;
	    element.checked=true;
	    element.hidden=false;
	    document.getElementById("labelPlazo_30").hidden=false;
	    getRating(30,1);
	}	

    if (plazosVisibles >=36){
		element=document.getElementById("plazo_36");
	    element.disabled=false;
	    element.checked=true;
	    element.hidden=false;
	    document.getElementById("labelPlazo_36").hidden=false;
	    getRating(36,1);
	}	
	if (plazosVisibles >=42){
		element=document.getElementById("plazo_42");
	    element.disabled=false;
	    element.checked=true;
	    element.hidden=false;
	    document.getElementById("labelPlazo_42").hidden=false;
	    getRating(42,1);
	}	

}


function cleanValues(){
	
	localStorage.removeItem("frecuencia");
	localStorage.removeItem("plazo");
	localStorage.removeItem("numero_pagos");
	localStorage.removeItem("monto");
	localStorage.removeItem("monto_financiado");
	localStorage.setItem("frecuencia","quincenal");

}


function sendMail() {

    var valores="";
    var nombre=document.getElementById('name').value;
    var correo=document.getElementById('email').value;

    if (correo=="" || nombre=="" ){
    	alert("Por favor llene los campos de nombre y correo.")
    	return;
    }
    valores   = "Me interesa mayor información sobre los préstamos de MIPYMEX"
              + escape('\n\n')
              + "Nombre: "+document.getElementById('name').value
              + escape('\n')
              + "Email: "+document.getElementById('email').value
              + escape('\n\n');
              
    


    var link = "mailto:infonomina@mipymex.mx"
             + "?cc=myCCaddress@example.com"
             + "&subject=" + "Solicitud de Información de Créditos de Nómina"
            // + "&htmlBody=" valores
            // + "&body=" + escape(document.getElementById('email').value)
            + "&body=" + valores
    ;

    window.location.href = link;
}

function cerrarPanelContacto(){
	document.getElementById("panelCotizador").hidden=false;
	document.getElementById("panelContactanos").hidden=true;
	document.getElementById("panelTablaAmortizacion").hidden=true;
	
	var iframe = document.getElementById('frameFormulario');
        iframe.src = iframe.src;
        iframe.height=850;
}

function abrirPanelContacto(){
	document.getElementById("frameFormulario").height=850;
	document.getElementById("panelContactanos").hidden=false;
	document.getElementById("panelCotizador").hidden=true;
	document.getElementById("panelTablaAmortizacion").hidden=true;
}

function expandirTablaAmortizacion(switcher){
	if (switcher==true){
		document.getElementById("panelContactanos").hidden=true;
		document.getElementById("panelCotizador").hidden=true;
		document.getElementById("panelTablaAmortizacion").hidden=false;
	}
	else{
		document.getElementById("panelContactanos").hidden=true;
		document.getElementById("panelCotizador").hidden=false;
		document.getElementById("panelTablaAmortizacion").hidden=true;
	}
}

function cambiarAltura()
{
 	document.getElementById("frameFormulario").height=275;
} 

function calculaPagoFlat(data,colocaEnMontoMaximo)
{	
	var meses_antiguedad=0;
	var sueldo=0;
	var mesesSueldo=0;
	var montoMax=0;
    
    
    meses_antiguedad=parseFloat(data.antiguedad)

	if(data.montoIngresos>0)
		sueldo=parseFloat(data.montoIngresos);

	if(data.mesesSueldo>0){
		mesesSueldo=parseFloat(data.mesesSueldo);
	}

    montoMax=sueldo*mesesSueldo;

	if(data.montoMax>0)
		montoMax=parseFloat(data.montoMax);
	
  	
  	if (meses_antiguedad<6){	
  	    verPlazos(0,meses_antiguedad);
  	    getRating("",1);	
  		alert('Lo sentimos, mínimo requieres tener 6 meses de antigüedad');
        return;
    }

    var sliderMonto = document.getElementById("rangoMonto");
    if(sueldo>0 || "montoMax" in data){
		
		sliderMonto.min=3000;
		sliderMonto.max=montoMax;

		if (colocaEnMontoMaximo){
			sliderMonto.value=montoMax;
			localStorage.setItem("monto",montoMax);
		}

		document.getElementById("monto").innerHTML=numberToCurrency(sliderMonto.value);
		document.getElementById("montoMaximo").innerHTML=numberToCurrency(sliderMonto.value);
    }

 	var frecuencia = localStorage.getItem("frecuencia");
 	var plazo=localStorage.getItem("plazo")
	var tiempo = localStorage.getItem("plazo")/12;
	var tasa = data.tasa*1.0*1.014;
	var comision = data.comision*1.16;
	var redito=0.0;
	var capital = localStorage.getItem("monto")*(1.00+comision);
	var intereses=0.00;
	var totalAPagar=0.00;
	var pago=0.00;
	var intereses_periodo=0.0;
    var numero_pagos;
    var numero_pagos_al_anio;
    var tir;
    var dias_frecuencia=0;
    var costoSeguro=data.costoSeguro*1.0;
        
    
        
	if (frecuencia=="semanal"){
		numero_pagos=52*tiempo; 
		numero_pagos_al_anio=52;  
		dias_frecuencia=7; 
		costoSeguro=costoSeguro/2;
	}

	if (frecuencia=="catorcenal"){
		numero_pagos=52*tiempo/2;
		numero_pagos_al_anio=26;
		dias_frecuencia=14;
	}

	if (frecuencia=="quincenal"){
		numero_pagos=24*tiempo;
		numero_pagos_al_anio=24;
		dias_frecuencia=15;
	}

	if (frecuencia=="mensual"){
		numero_pagos=12*tiempo;
		numero_pagos_al_anio=12;
		dias_frecuencia=30;
		costoSeguro=costoSeguro*2;
	}

	localStorage.setItem("dias_frecuencia",dias_frecuencia);
    localStorage.setItem("numero_pagos",numero_pagos);
    localStorage.setItem("numero_pagos_al_anio",numero_pagos_al_anio);
    localStorage.setItem("monto_financiado",capital);
    localStorage.setItem("costoSeguro",costoSeguro);

    
    localStorage.setItem("tasa_flat",tasa);
    tasa_diaria=(tasa/360);
    localStorage.setItem("tasa_diaria",tasa_diaria);
    tasa_mensual=tasa_diaria*30.00000;
    localStorage.setItem("tasa_mensual",tasa_mensual);
    redito=plazo*tasa_mensual*1.00/100;
    localStorage.setItem("redito",redito);
    intereses_periodo= (capital*redito*1.16);
    pago=(capital+intereses_periodo)/numero_pagos;
    localStorage.setItem("pago",pago);
    pago_capital=capital/numero_pagos;
    localStorage.setItem("pago_capital",pago_capital);
    intereses_diarios=intereses_periodo/(numero_pagos*dias_frecuencia*1.16);
    localStorage.setItem("intereses_diarios",intereses_diarios);


    pago = pago + costoSeguro;
    totalAPagar=pago*numero_pagos;
		localStorage.setItem("totalAPagar",totalAPagar);

   
    var pago_s= "$ "+pago.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
    document.getElementById("pago").innerHTML=pago_s;
    

   
    if(localStorage.getItem("frecuencia")!=null && localStorage.getItem("frecuencia")!="")
		document.getElementById("tuPago").innerHTML="pagos "+ frecuencia +"es de:"
	else
		document.getElementById("tuPago").innerHTML="pagos quincenales de:";

	if(localStorage.getItem("numero_pagos")!=null && localStorage.getItem("numero_pagos")>0)
		document.getElementById("numPagos").innerHTML=localStorage.getItem("numero_pagos");
	else
		document.getElementById("numPagos").innerHTML=0;	
}

function obtenerTablaAmortizacion(){

	var tasa_diaria=localStorage.getItem("tasa_diaria")*1.0;
	var numero_pagos=localStorage.getItem("numero_pagos");
	var frecuencia=localStorage.getItem("frecuencia");
	var dias_frecuencia=parseInt(localStorage.getItem("dias_frecuencia"));
	var pago=localStorage.getItem("pago");
	var saldo_capital=localStorage.getItem("monto_financiado");
	var pago_capital=localStorage.getItem("pago_capital")*1.0;
    var intereses_diario=localStorage.getItem("intereses_diarios")*1.0;
    var costoSeguro=localStorage.getItem("costoSeguro")*1.0;
    

	var filas=[];


	var hoy = new Date();
	var diaMes=hoy.getDate();
	var dias_transcurridos=0;
	var primerPago
	var dia_inicio=hoy;
	var sdia_inicio=FormatDateSimulador(dia_inicio)
	var dia_fin=addDays(sdia_inicio,dias_frecuencia);
	var	diaSemana=dia_fin.getDay();
	var sdia_fin=FormatDateSimulador(dia_fin)
	var dia_de_pago=-1; // Default
	var pago_diario=pago/dias_frecuencia;
   

    
	
	if (frecuencia  == "semanal" ) {
		dia_de_pago=5;  //Los viernes se cobra en los pagos semanales y catorcenales
		if (diaSemana == 6){
			diaSemana=0
		}  
		diferencia=dia_de_pago-diaSemana;
		dia_fin=addDays(sdia_fin,diferencia);
		sdia_fin=FormatDateSimulador(dia_fin);
		
	}

	if(frecuencia == "catorcenal"){
		diaDelMes=sdia_fin.split("-")[2]
		if (diaDelMes<=8 ){
			//console.log("entra en 1");
			dia_fin=addDays(sdia_fin,7);
			sdia_fin=FormatDateSimulador(dia_fin);
		}
		else{			
				if (diaDelMes>=16 && diaDelMes<=23){
					//console.log("entra en 2");
					dia_fin=addDays(sdia_fin,7);
					sdia_fin=FormatDateSimulador(dia_fin);
				}
			}
		dia_de_pago=5;
		if (diaSemana == 6){
			diaSemana=0
		}  
		diferencia=dia_de_pago-diaSemana;
		dia_fin=addDays(sdia_fin,diferencia);
		sdia_fin=FormatDateSimulador(dia_fin)
	}

	if(frecuencia == "quincenal"){
		
		diaDelMes=sdia_fin.split("-")[2]

		if (diaDelMes<=8 ){
			// console.log("entra en 1");
			dia_fin=addDays(sdia_fin,7);
			sdia_fin=FormatDateSimulador(dia_fin);
		}
		else{			
				if (diaDelMes>=16 && diaDelMes<=23){
					// console.log("entra en 2");
					dia_fin=addDays(sdia_fin,7);
					sdia_fin=FormatDateSimulador(dia_fin);
				}
			}
		
		diaDelMes=sdia_fin.split("-")[2]
		if(diaDelMes<=15){
			dia_de_pago=primerQuincenaDelMes(sdia_fin);
		}

		if(diaDelMes>15 && diaDelMes<=31){
			dia_de_pago=ultimoDiaDelMes(sdia_fin);
		}

		
		dia_fin= dia_de_pago;
		sdia_fin=FormatDateSimulador(dia_fin)
	}

	
	// console.log(sdia_inicio+"---"+dia_inicio.getDay());
	// console.log(sdia_fin+"---"+dia_fin.getDay());
	// console.log("isBusinnessDay="+isBusinnessDay(sdia_fin,weekmask,diasFestivos));
		
    var suma_capital=0.0;
    var suma_intereses=0.0;
    var suma_iva=0.0;
    var suma_total=0.0;
    var suma_totalSeguro=0.0;
	for (var i=0;i<=numero_pagos-1;i++){

		 if(frecuencia=="quincenal"){
		 	//console.log("input sdia_fin---"+sdia_fin);
			diaDelMes=sdia_fin.split("-")[2];
			if(diaDelMes<=5){
				dia_de_pago=ultimoDiaDelMesAnterior(sdia_fin);
			}
			if(diaDelMes>5 && diaDelMes<=15){
				dia_de_pago=primerQuincenaDelMes(sdia_fin);
			}

			if(diaDelMes>15 && diaDelMes<=18){
				dia_de_pago=primerQuincenaDelMes(sdia_fin);
			}

			if(diaDelMes>18 && diaDelMes<=31){
				dia_de_pago=ultimoDiaDelMes(sdia_fin);
			}

			dia_fin= dia_de_pago;
			sdia_fin=FormatDateSimulador(dia_fin)
		}

		if(frecuencia=="mensual"){
		 	//console.log("input sdia_fin---"+sdia_fin);
			diaDelMes=sdia_fin.split("-")[2];
			mes=sdia_fin.split("-")[1];
			//console.log("input diaDelMes---"+diaDelMes);
			if(diaDelMes<=8){
				dia_de_pago=ultimoDiaDelMesAnterior(sdia_fin);
			}
			if(diaDelMes>8 && diaDelMes<=31){
				dia_de_pago=ultimoDiaDelMes(sdia_fin);
				//console.log("Input ultimoDiaDelMes "+FormatDateSimulador( dia_de_pago));
			}

			dia_fin= dia_de_pago;
			sdia_fin=FormatDateSimulador(dia_fin);
		}
		//console.log("Input---"+sdia_inicio+"---"+sdia_fin);
		while (isBusinnessDay(sdia_fin,weekmask,diasFestivos)==false){
			//console.log("in While")
	    	dia_fin=addDays(sdia_fin,1);
	    	sdia_fin=FormatDateSimulador(dia_fin);
	    }
		
       
		dias_transcurridos=diffDays(sdia_inicio,sdia_fin);
		// pago_dias_transcurridos=pago_diario * (dias_transcurridos);
		// pago_a_capital=(pago_dias_transcurridos)/(tasa_diaria+1.16);
		// pago_a_intereses=(pago_dias_transcurridos-pago_a_capital)/1.16;
		// pago_a_iva=pago_a_intereses*0.16
		// saldo_capital -=pago_a_capital;
		pago_dias_transcurridos=(intereses_diarios*dias_transcurridos*1.16)+pago_capital+costoSeguro;
		pago_a_capital=pago_capital;
		saldo_capital -= pago_a_capital;
		pago_a_intereses=intereses_diarios*dias_transcurridos;
		pago_a_iva=pago_a_intereses*0.16;

		var pago_s= "$ "+pago_dias_transcurridos.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
		var pago_a_capital_s= "$ "+pago_a_capital.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
		var saldo_capital_s= "$ "+saldo_capital.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
		var pago_a_intereses_s="$"+pago_a_intereses.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
		var pago_a_iva_s="$"+pago_a_iva.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
		var costoSeguro_s= "$ "+costoSeguro.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");


		
		// console.log((i+1)+"---"+sdia_inicio+"----"+sdia_fin+"----"+dias_transcurridos+"---"+pago_s);
        fila={"Num_Pago":i+1,
        		"inicio":sdia_inicio,
        		"fin":sdia_fin,
        		"dias_transcurridos":dias_transcurridos,
        		"pago_a_capital":pago_a_capital_s,
        		"pago_a_intereses":pago_a_intereses_s,
        		"pago_a_iva":pago_a_iva_s,
        		"costoSeguro":costoSeguro_s,
        		"total":pago_s,
        		"saldo_capital":saldo_capital_s			
             };

		filas.push(fila);

		suma_capital +=pago_a_capital;
    	suma_intereses +=pago_a_intereses;
    	suma_iva +=pago_a_iva;
    	suma_total +=pago_dias_transcurridos;
    	suma_totalSeguro += costoSeguro;
		
		dia_inicio=dia_fin;
		sdia_inicio=FormatDateSimulador(dia_inicio);
		dia_fin=addDays(sdia_inicio,dias_frecuencia);
		sdia_fin=FormatDateSimulador(dia_fin);

		//console.log("output "+sdia_inicio+"---"+dia_inicio.getDate());
		//console.log("output "+sdia_fin+"---"+dia_fin.getDate());
		// console.log("isBusinnessDay="+isBusinnessDay(sdia_fin,weekmask,diasFestivos));
	}

// console.log(filas);
var suma_capital_s= "$ "+suma_capital.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
var suma_intereses_s= "$ "+suma_intereses.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
var suma_iva_s= "$ "+suma_iva.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
var suma_total_s= "$ "+suma_total.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
var suma_totalSeguro_s="$ "+suma_totalSeguro.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
totales={
		"capital":suma_capital_s,
		"intereses":suma_intereses_s,
		"iva":suma_iva_s,
		"total":suma_total_s,
		"totalCostoSeguro":suma_totalSeguro_s
	  };
muestra_tabla(filas,totales);


}

function muestra_tabla(filas,totales){
	var hoy = new Date();
	var hoy_s=FormatDateSimulador(hoy);
	var monto_solicitado=localStorage.getItem("monto")*1.0;
	var monto_solicitado_s="$"+monto_solicitado.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
	var monto_financiado=localStorage.getItem("monto_financiado")*1.0;
	var monto_financiado_s="$"+monto_financiado.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
	var monto_comision= monto_financiado-monto_solicitado;
	var monto_comision_s="$"+monto_comision.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");

	var tabla_s="";
		
	esquema={	"Num_Pago":"#",
        		"inicio":"Desde",
        		"fin":"Al",
        		"dias_transcurridos":"Días",
        		"pago_a_capital":"Pago a Capital",
        		"pago_a_intereses":"Pago a Intereses",
        		"pago_a_iva":"IVA Sobre Intereses",
        		"costoSeguro":"Seguro",
        		"total":"Total del Periodo",
        		"saldo_capital":"Saldo Capital"		 		
             }
    tabla_s +="<center>";
    tabla_s +="<Table border=1 cellspacing=0 id='tabla_amortizacion' name='tabla_amortizacion' style='font-size:10px;'>";
    tabla_s +="<tr><td colspan=10>";
    tabla_s +='<img src="static/img/Logo_MiPymex.jpg" height="50" style="position:absolute;">';
    tabla_s +="<center> <p style='font-weight:bold; line-heigth:10px;'>MIPYMEX S.A. DE C.V. SOFOM ENR </p>";
    tabla_s +="SIMULADOR DE TABLA DE AMORTIZACIÓN <br/>";
    tabla_s +="DE USO EXCLUSIVO PARA PERSONAL DE MIPYMEX</center><br/>";
    tabla_s +="<p style='font-weight:bold; font-size:12px;'> Los datos presentados en esta simulación pueden diferir conforme a las condiciones reales del crédtio</p>"
    
    tabla_s +="Fecha de Inicio: "+hoy_s +"<br/>";
    tabla_s +="Monto Solicitado: "+monto_solicitado_s +"<br/>";
    tabla_s +="Plazo: "+localStorage.getItem("plazo")+" meses"+"<br/>";
    tabla_s +="Frecuencia de pago: "+localStorage.getItem("frecuencia")+"<br/>";
    tabla_s +="Número de pagos: "+localStorage.getItem("numero_pagos")+"<br/>";
    tabla_s +="Monto Financiado: "+monto_financiado_s +"<br/>";
    var tasa_s=localStorage.getItem("tasa_flat");
    tasa_s=(Math.round(tasa_s*100)/100).toFixed(2);
    tabla_s +="Tasa de Interés Simple: "+tasa_s +"% Anual<br/>";

    tabla_s +="El Monto Financiado incluye una comisión de: "+monto_comision_s +" IVA incluido";
    tabla_s +="</td> </tr>"
    tabla_s +="<tr>";
    for (campo in esquema){
    	tabla_s += "<th>";
    	tabla_s += esquema[campo];
    	tabla_s += "</th>";
    }
    tabla_s +="</tr>";
   
    for(fila in filas){
		tabla_s +="<tr>";
	    for (campo in esquema){
	    	tabla_s += "<td style='text-align:right;'>";
	    	tabla_s += filas[fila][campo];
	    	tabla_s += "</td>";
    	}
    	tabla_s +="</tr>";
    }   

    tabla_s +="<tr>";
    tabla_s +="<td colspan=4 style='text-align:right;'> Total </td>";
    tabla_s +="<td style='text-align:right;'>" + totales["capital"] +"</td>";
    tabla_s +="<td style='text-align:right;'>" + totales["intereses"] +"</td>";
    tabla_s +="<td style='text-align:right;'>" + totales["iva"] +"</td>";
    tabla_s +="<td style='text-align:right;'>" + totales["totalCostoSeguro"] +"</td>";
    tabla_s +="<td style='text-align:right;'>" + totales["total"] +"</td>";
    tabla_s +="<td style='text-align:center;'>-------</td>";


    tabla_s +="</tr>";
    tabla_s +="</Table>";
     tabla_s +="</center>"

    element=document.getElementById("divTablaAmortizacion");
    element.innerHTML=tabla_s;
    expandirTablaAmortizacion(true);
}

function isBusinnessDay(dia_fin,weekmask,diasFestivos){
	if (dia_fin in diasFestivos){
		return false;
	}
	d= new Date();
	d.setFullYear(dia_fin.split("-")[0]);
	d.setMonth(dia_fin.split("-")[1]-1);
	d.setDate(dia_fin.split("-")[2]);
	//console.log(d);
	diaSemana=d.getDay();
	//console.log(dia_fin+"--->"+FormatDateSimulador(d)+" diaSemana="+diaSemana);
	if(weekmask[diaSemana]==0)
		return false;
	else
		return true;

}

function addDays(sdia_inicio,dias){
	var newDate=new Date(sdia_inicio.split("-")[0], sdia_inicio.split("-")[1]-1, sdia_inicio.split("-")[2]);
	newDate.setDate(newDate.getDate()+dias)	

	return newDate;
}

function diffDays(sdia_inicio,sdia_fin){
	
	dia_inicio=new Date(sdia_inicio.split("-")[0], sdia_inicio.split("-")[1]-1, sdia_inicio.split("-")[2]);
	dia_fin=new Date(sdia_fin.split("-")[0], sdia_fin.split("-")[1]-1, sdia_fin.split("-")[2]);

	var diffTime=Math.abs(dia_fin-dia_inicio);
	var daysDiff=Math.ceil(diffTime/(1000*60*60*24));
	return daysDiff;
} 

function FormatDateSimulador(date){
	var d=new Date(date);
	dformat=[  d.getFullYear(),
			  (d.getMonth()+1).padLeft(),
			   d.getDate().padLeft()
			].join('-');
	return dformat;
}

function ultimoDiaDelMesAnterior(sdia_fin){
	dia_fin=new Date(sdia_fin.split("-")[0], sdia_fin.split("-")[1]-1, 0);
	return dia_fin;

}

function ultimoDiaDelMes(sdia_fin){
	dia_fin=new Date(sdia_fin.split("-")[0], sdia_fin.split("-")[1], 0);
	return dia_fin;
}

function primerQuincenaDelMes(sdia_fin){
	dia_fin=new Date(sdia_fin.split("-")[0], sdia_fin.split("-")[1]-1, 15);
	return dia_fin;
}

Number.prototype.padLeft=function(base,chr){
	var len=(String(base ||10).length - String(this).length)+1;
	return len >0 ? new Array (len).join(chr || '0')+this : this;
}

function printElemSimulador(elementId){
	element=document.getElementById(elementId);
	contenido ="<html> <body>";
	contenido += element.innerHTML;
	contenido +="</body></html>";
	var myWindow= window.open('','PRINT','height=400,width=600');
	myWindow.document.write(contenido);
	myWindow.document.close();
	myWindow.focus();
	myWindow.print();
	myWindow.close();
	return true;
}

