function getWindowDim(){
        element=document.getElementById("windowInfo");
        width=window.innerWidth;
        height=window.innerHeight;
        element.setAttribute("width",width);
        element.setAttribute("height",height);
        element.setAttribute("selected","null");
    }

function showHideMainMenu(){

    element = document.getElementById("mainMenu");
    style = window.getComputedStyle(element),
    visibility = style.getPropertyValue('visibility');

    if (visibility=="hidden"){
        element.style.visibility="visible";
        element.style.width="250px";
        document.getElementById("contenedor1").style.display="none";
        document.getElementById("contenedor2").style.display="none";
        document.getElementById("contenedor3").style.display="none";
        document.getElementById("contenedor4").style.display="none";
    }
    else{
        element.style.visibility="hidden";
        element.style.width="0px";
        document.getElementById("contenedor1").style.display="inline-block";
    }
}

function hideMainMenu(){

    element = document.getElementById("mainMenu");
    style = window.getComputedStyle(element),
    visibility = style.getPropertyValue('visibility');

    if (visibility!="hidden"){
        element.style.visibility="hidden";
        element.style.width="0px";
    }

}

function expandirSolicitud(element){
    id=element.getAttribute("id");
    width=window.innerWidth;
    height=window.innerHeight;
    style = window.getComputedStyle(element);
    collapsed = element.getAttribute("collapsed");
    detalleID="detalleSolicitud_"+id;
    detalle = document.getElementById(detalleID);

    hideMainMenu();
    document.getElementById("contenedor3").style.display="none";

    winWidth=document.getElementById("windowInfo").getAttribute("width");
    oldSelectedID=document.getElementById("windowInfo").getAttribute("selected");


    if (collapsed=="true"){
            element.setAttribute("collapsed","false");
            element.style.background="#daff77"

            if (winWidth<800)
                detalle.style.display="inline-block";
            else{
                    document.getElementById("contenedor2").style.display="inline-block";
                    document.getElementById("formaSolicitudEdit").innerHTML=detalle.innerHTML;
            }

            document.getElementById("windowInfo").setAttribute("selected",id);
        }
        else{
                element.setAttribute("collapsed","true");
                element.style="";
                detalle.style.display="none";
                document.getElementById("windowInfo").setAttribute("selected","null");

                if (winWidth>=800){
                    document.getElementById("contenedor2").style.display="none";
                    document.getElementById("formaSolicitudEdit").innerHTML="";
                }

            }

    if ((oldSelectedID!=id ) && (oldSelectedID!="null")){
        contraerSolicitud(document.getElementById(oldSelectedID));

    }
    document.getElementById("contenedor4").style.display="none";
}

function contraerSolicitud(element)
{
   id=element.getAttribute("id");
   detalleID="detalleSolicitud_"+id;
   detalle = document.getElementById(detalleID);
   element.style="";
   element.setAttribute("collapsed","true");
   detalle.style.display="none";
   document.getElementById("contenedor4").style.display="none";

}

function formatDate()
{
    var d =new Date();
    var timeOffset=d.getTimezoneOffset();
    // console.log(d)
    // console.log(timeOffset);

    var MS_PER_MINUTE = 60000;
    var timeOffsetSeconds=timeOffset*MS_PER_MINUTE;
    var CDMXOffset_Invierno=360*MS_PER_MINUTE;
    var CDMXOffset_Verano=300*MS_PER_MINUTE;

    var CDMXOffset=CDMXOffset_Invierno;

    d= new Date(d - timeOffsetSeconds+CDMXOffset);


    // console.log(d);



    // dformat = [ d.getDate().padLeft(),
    //            (d.getMonth()+1).padLeft(),
    //            d.getFullYear()].join('/') +' ' +
    //           [d.getHours().padLeft(),
    //            d.getMinutes().padLeft(),
    //            d.getSeconds().padLeft()].join(':');
    dformat = [ d.getFullYear(),
               (d.getMonth()+1).padLeft(),
               d.getDate().padLeft()].join('-') +' ' +
              [d.getHours().padLeft(),
               d.getMinutes().padLeft(),
               d.getSeconds().padLeft()].join(':');
    return dformat;
}

Number.prototype.padLeft = function(base,chr)
{
    var  len = (String(base || 10).length - String(this).length)+1;
    return len > 0? new Array(len).join(chr || '0')+this : this;
}

function agregarSolicitud(trigger)
{
    collapsed = trigger.getAttribute("collapsed");
    detalle=document.getElementById("detalleSolicitudAdd");


    if (collapsed=="true"){
            trigger.setAttribute("collapsed","false");
            detalle.style.display="inline-block";
            detalle.style.height="660px";
        }
        else{
                trigger.setAttribute("collapsed","true");
                detalle.style.display="none";
            }
}


function mostrarArchivo(elemento,solicitudId)
{
    document.getElementById("contenedor3").style.display="inline-block";
    url="static/files/"+elemento.options[elemento.selectedIndex].value;
    winWidth=document.getElementById("windowInfo").getAttribute("width");
    if(winWidth<800)
        window.open(url);
    else
        document.getElementById("fileViewer").src=url;

}

function listaEmpresasUpdate(element,id){
    nuevoAsesor=element.options[element.selectedIndex];
    nuevoAsesor=element.options[element.selectedIndex].getAttribute("nombreAsesor");
    if (id="add") {
        selected=element.options[element.selectedIndex];
        nombreElemento="clienteEmpresa";
        elementInheritedID=document.getElementById("inheritedID");
        elementInheritedID.value=selected.getAttribute("ownerID");
    }
    else nombreElemento="clienteEmpresa_"+id;
    elementoLista=document.getElementById(nombreElemento);
    elementoLista.innerHTML="";
    for (var i = 0; i<= asignaciones.length - 1; i++) {
        asesor=asignaciones[i].asesor;
        if(nuevoAsesor==asesor){
            empresas=asignaciones[i].empresas.sort();
            for (var j = 0; j<= empresas.length-1; ++j) {
                empresa=empresas[j];
                var opt = document.createElement('option');
                opt.value = empresa;
                opt.innerHTML = empresa;
                elementoLista.appendChild(opt);
            }
        }

    }
}

function updateDate(solicitudId,element,checkbox)
{

    if (forbidden.indexOf(element.name)>-1){
        try{
            throw new Error("No autorizado para cambiar:" + element.name);
        }
        catch(e){
            alert(e.message);

        }
        return;
    }

    if(checkbox.checked)
       element.value=formatDate();
    else
       element.value="";

    updateData(element,solicitudId)
}

function updateData(element,id)
{
    if (forbidden.indexOf(element.name)>-1){
        alert("No autorizado para cambiar:" + element.name);
        return;
    }

    if (viewName=="PreAnalisis" && element.name!="comentarios")  return;

    updateDataShow(true);
    frame=document.getElementById("updateDataFrame").contentWindow;
    form=frame.document.getElementById("updateDataForm");
    frame.document.getElementById("field").value=element.name;
    frame.document.getElementById("value").value=element.value;
    frame.document.getElementById("id").value=id;
    frame.document.getElementById("viewName").value=viewName;
    frame.document.getElementById("userName").value=user.name;
    frame.document.getElementById("ownerID").value=user.ownerID;

    if(element.getAttribute("type")=="checkbox")
        {
            frame.document.getElementById("value").value=element.checked;
        }

    frame.document.getElementById("updateDataForm").submit();



    updateDataShow(false);

    setTimeout(() => {
    if(element.name=="asesorNombre"){
            selected=element.options[element.selectedIndex];
            updateDataShow(true);
            frame=document.getElementById("updateDataFrame").contentWindow;
            form=frame.document.getElementById("updateDataForm");
            frame.document.getElementById("field").value="inheritedID";
            frame.document.getElementById("value").value=selected.getAttribute("ownerID");
            frame.document.getElementById("id").value=id;
            frame.document.getElementById("viewName").value=viewName;
            frame.document.getElementById("userName").value=user.name;
            frame.document.getElementById("ownerID").value=user.ownerID;
            frame.document.getElementById("updateDataForm").submit();
            updateDataShow(false);
        }
    }, 3000);


}

function updateDataShow(visible)
{
    if (visible){
        document.getElementById("updateDataDiv").style.visibility="visible";
        document.getElementById("updateDataDiv").style.display="inline-block";
    }
    else{

        intervalID=setInterval(function(){
        opacity=document.getElementById("updateDataDiv").style.opacity;
        // opacity=opacity-.01;
            document.getElementById("updateDataDiv").style.opacity=opacity;
        }, 30);


        setTimeout(function(){
            clearInterval(intervalID);
            document.getElementById("updateDataDiv").style.visibility="hidden";
            document.getElementById("updateDataDiv").style.display="none";
            document.getElementById("updateDataDiv").style.opacity="50%";
        }, 1500);
    }

}

function updateArray(array,field)
{
    if (forbidden.indexOf(element.name)>-1){
        alert("No autorizado para cambiar:" + element.name);
        return;
    }

    updateArrayShow(true);
    frame=document.getElementById("updateArrayFrame").contentWindow;
    form=frame.document.getElementById("updateArrayForm");
    frame.document.getElementById("field").value=field;
    frame.document.getElementById("dataArray").value=array;
    frame.document.getElementById("viewName").value=viewName;
    frame.document.getElementById("userName").value=user.name;
    frame.document.getElementById("ownerID").value=user.ownerID;
    frame.document.getElementById("updateArrayForm").submit();
    updateArrayShow(false);

    setTimeout(() => {
    if(element.name=="asesorNombre"){
            selected=element.options[element.selectedIndex];
            updateArrayShow(true);
            frame=document.getElementById("updateArrayFrame").contentWindow;
            form=frame.document.getElementById("updateArrayForm");
            frame.document.getElementById("field").value="inheritedID";
            frame.document.getElementById("value").value=selected.getAttribute("ownerID");
            frame.document.getElementById("id").value=id;
            frame.document.getElementById("viewName").value=viewName;
            frame.document.getElementById("userName").value=user.name;
            frame.document.getElementById("ownerID").value=user.ownerID;
            frame.document.getElementById("updateArrayForm").submit();
            updateArrayShow(false);
        }
    }, 1000);


}

function updateArrayShow(visible)
{
    if (visible){
        document.getElementById("updateArrayDiv").style.visibility="visible";
        document.getElementById("updateArrayDiv").style.display="inline-block";
    }
    else{

        intervalID=setInterval(function(){
        opacity=document.getElementById("updateArrayDiv").style.opacity;
        // opacity=opacity-.01;
            document.getElementById("updateArrayDiv").style.opacity=opacity;
        }, 30);


        setTimeout(function(){
            clearInterval(intervalID);
            document.getElementById("updateArrayDiv").style.visibility="hidden";
            document.getElementById("updateArrayDiv").style.display="none";
            document.getElementById("updateArrayDiv").style.opacity="50%";
        }, 1500);
    }

}



function displayLastUpdated(){
        if ( typeof lastUpdated  === 'undefined')
           return;
        document.getElementById(lastUpdated).click();
}


function filtrarSolicitudes(lista,elementoFiltro,value)
{
    oldSelectedID=document.getElementById("windowInfo").getAttribute("selected");
    if (oldSelectedID != "null")
        contraerSolicitud(document.getElementById(oldSelectedID));
    document.getElementById("windowInfo").setAttribute("selected","null");
    document.getElementById("contenedor2").style.display="none";
    document.getElementById("formaSolicitudEdit").innerHTML="";

    elemento=document.getElementById(elementoFiltro);
    filtro=elemento.options[elemento.selectedIndex].value;
    filtro=filtro+"";
    for (var i=0;i<=lista.length-1;i++){
        array=lista[i];
        id=lista[i].id;
        if(viewName=="Usuarios")
            id=lista[i].ownerID;
        currentElement=document.getElementById(id);
        if(typeof(array[filtro])=="undefined")
            currentElement.style.display="none";
        else{
                if(filtro!="clienteNombre"){
                    if (array[filtro].toUpperCase().includes(value.toUpperCase())){
                            currentElement.style.display="inline-block";
                        }
                    else{
                            currentElement.style.display="none";
                        }
                }

                if(filtro=="clienteNombre"){
                    nombreCompleto=array['clienteNombre'].trim()+" "+array['clienteApellidoPaterno'].trim()+" "+array['clienteApellidoMaterno'].trim();
                    nombreCompleto.trim();
                    if (nombreCompleto.toUpperCase().includes(value.toUpperCase())){
                        currentElement.style.display="inline-block";
                        }
                    else{
                            currentElement.style.display="none";
                        }

                }
            }
    }


}

function limpiarFiltroSolicitudes()
{
    document.getElementById("filtroValor").value="";
    lista=solicitudes;
    if(viewName=="Por Fondear") lista=solicitudes;
    if(viewName=="Usuarios") lista=usuarios;
    if(viewName=="Perfil de Usuario") lista=usuarios;
    if(viewName=="Empresas") lista=asignaciones;

    filtrarSolicitudes(lista,'filtroCriterio',"");
}

function filtrarLogs(lista,elementoFiltro,value){


    elemento=document.getElementById(elementoFiltro);
    filtro=elemento.options[elemento.selectedIndex].value;
    filtro=filtro+"";
    table=document.getElementById("tablaLogs");
    table.innerHTML="";

    contenido="";
    contenido+="<tr>";
    contenido+="<th> # </th>";
    contenido+="<th> Objeto </th>";
    contenido+="<th> Acción </th>";
    contenido+="<th> Momento </th>";
    contenido+="<th> Usuario </th>";
    contenido+="<th> Número de Control </th>";
    contenido+="<th> Nombre del Cliente </th>";
    contenido+="<th> Campo </th>";
    contenido+="<th> De </th>";
    contenido+="<th> A </th>";
    contenido+="</tr>";

    for (log in lista){
         if(filtro in lista[log]){
            if(lista[log][filtro].toUpperCase().includes(value.toUpperCase())){
            contenido+="<tr>";
            contenido+="<td>"+lista[log]["id"]+"</td>";
            contenido+="<td>"+lista[log]["Objeto"]+"</td>";
            contenido+="<td>"+lista[log]["accion"]+"</td>";
            contenido+="<td>"+lista[log]["timeStamp"]+"</td>";
            contenido+="<td>"+lista[log]["userName"]+"</td>";
            contenido+="<td>"+lista[log]["solicitudNumeroControl"]+"</td>";
            contenido+="<td>"+lista[log]["clienteNombre"]+"</td>";
            if (lista[log]["accion"]!="agregar"){
                contenido+="<td>"+lista[log]["logData"]["field"]+"</td>";
                contenido+="<td style='word-break: break-all;'>"+lista[log]["logData"]["oldValue"]+"</td>";
                contenido+="<td style='word-break: break-all;'>"+lista[log]["logData"]["value"]+"</td>";
            }
            if (lista[log]["accion"]=="agregar"){
                contenido+="<td colspan='3'>"+JSON. stringify(lista[log]["logData"],undefined,4)+"</td>";
            }

            contenido+="</tr>";
         }

         }

    }




    table.innerHTML=contenido;
    ajustarEncabezadosLogs();

}


function limpiarFiltroLogs(){

    document.getElementById("filtroValor").value="";
    lista=logs;
    filtrarLogs(lista,'filtroCriterio',"");

}

function ajustarEncabezadosLogs(){

    t1=document.getElementById("tablaLogs");
    t2=document.getElementById("tablaEncabezadoLogs");

    t1.rows[0].height="0";

    for (i = 0; i<=9;i++){
        t2.rows[0].cells[i].width=t1.rows[0].cells[i].offsetWidth-4;
    }
}


function filtrarReporte(lista,elementoFiltro,value){

    elemento=document.getElementById(elementoFiltro);
    filtro=elemento.options[elemento.selectedIndex].value;
    filtro=filtro+"";
    table=document.getElementById("tablaReporte");
    table.innerHTML="";

    contenido="";
    contenido+='<tr style="height: 54px;">';
    for (i = 0; i<=headers.length-1;i++){
        contenido+='<th style="font-weight: bold; font-size: 9px">';
        contenido+= headers[i];
        contenido+='</th>';
    }
    contenido+="</tr>";

    for (registro in reporte){
        if(reporte[registro][filtro].toUpperCase().includes(value.toUpperCase()))
        {
            contenido +='<tr>';
            for (i = 0; i<=headers.length-1;i++){
                contenido +='    <td style="font-weight: bold; font-size: 9px">';
                contenido +=        reporte[registro][headers[i]];
                contenido +='    </td>';
            }
            contenido +='</tr>';
        }
    }

    table.innerHTML=contenido;
    ajustarEncabezadosReporteCSV();

}


function limpiarFiltroReporte(){

    document.getElementById("filtroValor").value="";
    lista=reporte;
    filtrarReporte(lista,'filtroCriterio',"");

}

function ajustarEncabezadosReporteCSV(){
    t1=document.getElementById("tablaReporte");
    t2=document.getElementById("tablaEncabezadoReporte");

    t1.rows[0].height="0";
    for (i = 0; i<=headers.length-1;i++){
        t2.rows[0].cells[i].width=t1.rows[0].cells[i].offsetWidth;
    }
}

function mostrarDetallePipeLine(fecha,producto,asesor,columna){
    // console.log(pipelines);
    solicitudes=[];
    for (pipeline in pipelines){
        if(pipelines[pipeline].fecha==fecha){
            for(productoNombre in pipelines[pipeline].productos){
                if(productoNombre==producto){
                   asesores=pipelines[pipeline].productos[productoNombre]
                   for (asesorNombre in asesores){
                        if(asesorNombre==asesor){
                            columnas=asesores[asesorNombre]
                            for(columnaNombre in columnas){
                                if(columnaNombre==columna){
                                     solicitudes=columnas[columnaNombre].solicitudes;

                                }
                            }


                        }
                   }
                }
            }
        }

    }

    // console.clear();
    tabla=document.getElementById("detallePipeLine");
    tabla.innerHTML="";
    contenidoTabla='<table id="detallePipeLine" border="1" cellspacing="0" style="table-layout: fixed; width: calc(100% - 8px)">'
    contenidoTabla+="<tr>";
    contenidoTabla+='<th class="encabezadoTabla">Datos</th>';

    for (campo in filtros){
        if(filtros[campo].pipeLineRenderable=="true"){
            contenidoTabla+='<th class="encabezadoTabla">'+filtros[campo].label+'</th>';
        }

    }
    contenidoTabla+="</tr>";
    for (solicitud in solicitudes){
        // console.log(solicitudes[solicitud]);
        contenidoTabla+="<tr>";
        renglon="<>";
        renglon="<td class='linkTabla' onclick='mostrarSolicitudPipeLine("+solicitudes[solicitud].id+");'><u>Ver</u></td>";
        for (campo in filtros){
            if(filtros[campo].pipeLineRenderable=="true"){
                valor=solicitudes[solicitud][filtros[campo].value]
                if(valor==undefined){
                    valor="";
                }
                renglon+='<td class="cuerpoTabla">'+valor+'</td>';
            }
        }
        contenidoTabla+=renglon;
        contenidoTabla+="</tr>";
    }


    contenidoTabla+='</table>';
    tabla.innerHTML=contenidoTabla;

    element=document.getElementById(id="detalleSolicitud");
    element.innerHTML="";


}


function mostrarSolicitudPipeLine(id)
{
    solicitud=[]
    for (pipeline in pipelines){
            for(productoNombre in pipelines[pipeline].productos){
                   asesores=pipelines[pipeline].productos[productoNombre]
                   for (asesorNombre in asesores){
                            columnas=asesores[asesorNombre]
                            for(columnaNombre in columnas){
                                     solicitudes=columnas[columnaNombre].solicitudes;
                                     for (solicitudID in solicitudes){
                                        if(solicitudes[solicitudID].id==id){
                                            solicitud=solicitudes[solicitudID]
                                            break;
                                        }

                                     }


                            }
                   }
            }
    }


    element=document.getElementById(id="detalleSolicitud");
    element.innerHTML="";
    contenidoTabla="";
    for (filtro in filtros){
        contenidoTabla+="<tr>";
        if(filtros[filtro].editRenderable=="true"){
            campo=filtros[filtro].value;
            if (campo in solicitud){
                contenidoTabla+='<td class="cuerpoTablaDer">'+filtros[filtro].label+': </td>';

                valor=solicitud[campo];
                if (valor === undefined){
                    valor="";
                }
                if(campo=="documentos"){
                    valor  =  '<input type="button" name="documentos_{{solicitud.id}}"';
                    valor += 'onclick="openWindow(' ;
                    valor += "'" +solicitud[campo] +"'";
                    valor += ');"';
                    valor += 'value="Ver Documentos">';
                }
                contenidoTabla+='<td class="cuerpoTablaIzq">'+valor+'</td>';
            }
        }
        contenidoTabla+="</tr>";
    }
    element.innerHTML=contenidoTabla;
}

function printElem(elem)
{
    logofile="\"{{ url_for('static', filename='static/img/Logo_MiPymex.jpg') }}\"";

    titulo="";
    if(viewName=="PipeLine"){
      titulo="SOLICITUDES EN PROCESO";
    }
    if(viewName=="ScoreCard"){
      titulo="ScoreCard";
    }
    if(viewName=="Seguimiento Diario"){
      titulo="Seguimiento Diario";
    }

    tablaEncabezado="";
    tablaEncabezado+='<table ';
    tablaEncabezado+='border="2" ';
    tablaEncabezado+='cellspacing="0" ';
    tablaEncabezado+='width="100%" ';
    tablaEncabezado+='<tr>';
    tablaEncabezado+='<td rowspan=2 width="150px" style="text-align: center; vertical-align: middle;">';
    tablaEncabezado+='<img src="static/img/Logo_MiPymex.jpg" alt=""';
    tablaEncabezado+='     style="width: 140px; height: auto;">';
    tablaEncabezado+='</td>';
    tablaEncabezado+='<td style="word-wrap: break-word; border-bottom:0px ';
    tablaEncabezado+='       font-family: Arial, Helvetica, sans-serif; ';
    tablaEncabezado+='       font-size: 24px;';
    tablaEncabezado+='       font-weight: bold;';
    tablaEncabezado+='       background-color:#ffffff;';
    tablaEncabezado+='       text-align: center;" ';
    tablaEncabezado+='>'+titulo+'</td>';
    tablaEncabezado+='</tr>';
    tablaEncabezado+='<tr>';
    tablaEncabezado+='<td style="text-align: right; vertical-align:bottom; border-top:0px;">';
    tablaEncabezado+= formatDate().split(" ")[0];
    tablaEncabezado+='</td>';
    tablaEncabezado+='</tr>';
    tablaEncabezado+='</table>';


    contenido="";
    contenido+='<html><head>';
    contenido+='<title>'+viewName+'</title>';
    // contenido+=tablaEncabezado;
    contenido+='</head>';
    contenido+='<body>';
    contenido+='<header>'
    contenido+=tablaEncabezado;
    contenido+='</header>'
    contenido+=document.getElementById(elem).innerHTML
    contenido+='</body></html>';
    var mywindow = window.open('', 'PRINT', 'height=400,width=600');
    mywindow.document.write(contenido);
    mywindow.document.close(); // necessary for IE >= 10
    mywindow.focus(); // necessary for IE >= 10*/

    mywindow.print();
    mywindow.close();

    return true;
}

function openWindow(url)
{
    var mywindow = window.open(url, "_blank");
}

function mostrarVisorSolicitudes(button){
    visor=document.getElementById("visorSolicitudes");
    style = window.getComputedStyle(visor);
    visibility = style.getPropertyValue('visibility');
    // console.log(visor.visibility);
    if(visibility=="hidden"){
        visor.style.visibility="visible";
        document.getElementById("visorSolicitudes").style.display="inline-block";
        document.getElementById("panelPipeLine").style.setProperty('height',"calc(100% - 320px)")
        button.value="Ocultar Solicitudes";

    }
    else{
        visor.style.visibility="hidden";
        document.getElementById("visorSolicitudes").style.display="none";
        document.getElementById("panelPipeLine").style.setProperty('height',"100%");
        button.value="Ver Solicitudes";
    }
}


function onSignIn(googleUser) {
    // Useful data for your client-side scripts:
    var profile = googleUser.getBasicProfile();
    // console.log("ID: " + profile.getId()); // Don't send this directly to your server!
    // console.log('Full Name: ' + profile.getName());
    // console.log('Given Name: ' + profile.getGivenName());
    // console.log('Family Name: ' + profile.getFamilyName());
    // console.log("Image URL: " + profile.getImageUrl());
    // console.log("Email: " + profile.getEmail());

    // The ID token you need to pass to your backend:
    var id_token = googleUser.getAuthResponse().id_token;
    // console.log("ID Token: " + id_token);
}

function viewVoBoTable(){
    document.getElementById("contenedor2").style.display="none";
    container=document.getElementById('contenedor4');
    panel=document.getElementById('fillPanel');

    winWidth=document.getElementById("windowInfo").getAttribute("width");
    if  (winWidth>=800){
            container.visibility="visible";
            container.style.display="inline-block";
            panel.innerHTML="";
            contenido="<table border=1 cellspacing=0 width='100%'>";
            contenido+='<th class="encabezadoTabla"> Fecha de Solicitud </th>';
            contenido+='<th class="encabezadoTabla"> Entregado a Riesgos </th>';
            contenido+='<th class="encabezadoTabla"> Empresa </th>';
            contenido+='<th class="encabezadoTabla"> Cliente </th>';
            contenido+='<th class="encabezadoTabla"> Monto Autorizado </th>';
            contenido+='<th class="encabezadoTabla"> Plazo </th>';
            contenido+='<th class="encabezadoTabla"> 1ro </th>';
            contenido+='<th class="encabezadoTabla"> 2do </th>';
            contenido+='<th class="encabezadoTabla"> 3ro </th>';
            contenido+='<th class="encabezadoTabla"> Último Envío </th>';

            for (solicitud in solicitudes){
                ultimoEnvio="";
                contenido+="<tr>";
                contenido+="<td class='cuerpoTabla2Izq'>"+solicitudes[solicitud]["fechaContacto"]+"</td>";
                contenido+="<td class='cuerpoTabla2Izq'>"+solicitudes[solicitud]["fechaEntregaARiesgos"]+"</td>";
                contenido+="<td class='cuerpoTabla2Izq'>"+solicitudes[solicitud]["clienteEmpresa"]+"</td>";
                contenido+="<td class='cuerpoTabla2Izq'>"+solicitudes[solicitud]["clienteNombre"]+" "+solicitudes[solicitud]["clienteApellidoPaterno"]+ " "+ solicitudes[solicitud]["clienteApellidoMaterno"] +"</td>";
                contenido+="<td class='cuerpoTabla2Der'>"+solicitudes[solicitud]["montoAutorizado"]+"</td>";
                contenido+="<td class='cuerpoTabla2Izq'>"+solicitudes[solicitud]["plazoAutorizado"]+"</td>";

                if (solicitudes[solicitud]["fechaPrimerSolicitudVoBo"]!=""){
                    contenido+="<td class='cuerpoTabla2'>Sí</td>";
                    ultimoEnvio=solicitudes[solicitud]["fechaPrimerSolicitudVoBo"]
                }

                else
                     contenido+="<td class='cuerpoTabla2Izq'></td>";

                if (solicitudes[solicitud]["fechaSegundaSolicitudVoBo"]!=""){
                    contenido+="<td class='cuerpoTabla2'>Sí</td>";
                    ultimoEnvio=solicitudes[solicitud]["fechaSegundaSolicitudVoBo"]
                }
                else
                     contenido+="<td class='cuerpoTabla2Izq'></td>";

                if (solicitudes[solicitud]["fechaTercerSolicitudVoBo"]!=""){
                    contenido+="<td class='cuerpoTabla2'>Sí</td>";
                    ultimoEnvio=solicitudes[solicitud]["fechaTercerSolicitudVoBo"]
                }
                else
                     contenido+="<td class='cuerpoTabla2'></td>";

                contenido+="<td class='cuerpoTabla2Izq'>"+ultimoEnvio+"</td>";




                contenido+="</tr>";


            }
            contenido += "</table>";
            panel.innerHTML=contenido;

        }

}

function viewEnviarVoBoTable(){
    document.getElementById("contenedor2").style.display="none";
    container=document.getElementById('contenedor4');
    panel=document.getElementById('fillPanel');

    winWidth=document.getElementById("windowInfo").getAttribute("width");
    if  (winWidth>=800){
            container.visibility="visible";
            container.style.display="inline-block";
            panel.innerHTML="";
            contenido="<table border=1 cellspacing=0 width='100%'>";
            contenido+='<th class="encabezadoTabla"> Empresa </th>';
            contenido+='<th class="encabezadoTabla"> Cliente </th>';
            contenido+='<th class="encabezadoTabla"> Monto Autorizado </th>';
            contenido+='<th class="encabezadoTabla"> Plazo </th>';
            contenido+='<th class="encabezadoTabla"> Jefe Inmediato </th>';
            contenido+='<th class="encabezadoTabla"> Correo Jefe </th>';
            contenido+='<th class="encabezadoTabla"> Enviar </th>';


            for (solicitud in solicitudes){
                ultimoEnvio="";
                if (solicitudes[solicitud]["fechaPrimerSolicitudVoBo"]!="")
                    ultimoEnvio=solicitudes[solicitud]["fechaPrimerSolicitudVoBo"]

                if (solicitudes[solicitud]["fechaSegundaSolicitudVoBo"]!="")
                    ultimoEnvio=solicitudes[solicitud]["fechaSegundaSolicitudVoBo"]

                if (solicitudes[solicitud]["fechaTercerSolicitudVoBo"]!="")
                    ultimoEnvio=solicitudes[solicitud]["fechaTercerSolicitudVoBo"]

                ultimoEnvio=ultimoEnvio.split(" ")[0];
                todayDate=formatDate().split(" ")[0];

                if (ultimoEnvio!=todayDate && solicitudes[solicitud]["fechaTercerSolicitudVoBo"]==""){
                    contenido+="<tr>";

                    contenido+="<td class='cuerpoTabla2Izq'>"+solicitudes[solicitud]["clienteEmpresa"]+"</td>";
                    contenido+="<td class='cuerpoTabla2Izq'>"+solicitudes[solicitud]["clienteNombre"]+" "+solicitudes[solicitud]["clienteApellidoPaterno"]+ " "+ solicitudes[solicitud]["clienteApellidoMaterno"] +"</td>";
                    contenido+="<td class='cuerpoTabla2Der'>"+solicitudes[solicitud]["montoAutorizado"]+"</td>";
                    contenido+="<td class='cuerpoTabla2Izq'>"+solicitudes[solicitud]["plazoAutorizado"]+"</td>";
                    contenido+="<td class='cuerpoTabla2Izq'>"+solicitudes[solicitud]["clienteNombreJefe"]+"</td>";
                    contenido+="<td class='cuerpoTabla2Izq'>"+solicitudes[solicitud]["clienteCorreoJefe"]+"</td>";
                    contenido+="<td class='cuerpoTabla2'>";
                    contenido+="<label id='labelEnviarVoBo_"+solicitudes[solicitud].id+"'";
                    contenido+=" name=labelEnviarVoBo_"+solicitudes[solicitud].id+"'";
                    contenido+=" >Sí</label>";
                    contenido+="<input type='checkbox'";
                    contenido+=" name='cbEnviarVoBo_" + solicitudes[solicitud].id+"' checked=true";
                    contenido+=" id='cbEnviarVoBo_" + solicitudes[solicitud].id+"'";
                    contenido+=' onchange="updateEnvio(';
                    contenido+="'labelEnviarVoBo_"+solicitudes[solicitud].id+"'";
                    contenido+=',this.id);"';
                    contenido+=">"
                    contenido+="</td>";

                    contenido+="</tr>";
                }
            }
            contenido += "<tr>";
            contenido += "<td colspan=7 class='cuerpoTabla2'>";
            contenido += '<button class="buttonSubmit" onclick="postEnvioVoBos();">Confirmar Envio</button>';
            contenido += "</td>";
            // contenido += "<td colspan=2 class='cuerpoTabla2'>";
            // contenido += "<form action='/solicitarvobos' method='post'>";
            // contenido += '<input  class="buttonSubmit" type="submit" value="Descargar" name="accion" id="accion">';
            // contenido += '<input type="hidden" name="ownerID" value='+user.ownerID+'>';
            // contenido += '<input type="hidden" name="viewName" value="'+viewName+'">';
            // contenido += "</form>"
            // contenido += "</td>";
            contenido += "</tr>";
            contenido += "</table>";
            panel.innerHTML=contenido;

        }

}

function updateEnvio(labelId, checkboxId){
    cb=document.getElementById(checkboxId);
    label=document.getElementById(labelId);
    if(cb.checked)
        label.innerHTML="Sí";
    else
        label.innerHTML="No";
}

function postEnvioVoBos(){
    array="{";
    for (solicitud in solicitudes){
                ultimoEnvio="";
                if (solicitudes[solicitud]["fechaPrimerSolicitudVoBo"]!="")
                    ultimoEnvio=solicitudes[solicitud]["fechaPrimerSolicitudVoBo"]

                if (solicitudes[solicitud]["fechaSegundaSolicitudVoBo"]!="")
                    ultimoEnvio=solicitudes[solicitud]["fechaSegundaSolicitudVoBo"]

                if (solicitudes[solicitud]["fechaTercerSolicitudVoBo"]!="")
                    ultimoEnvio=solicitudes[solicitud]["fechaTercerSolicitudVoBo"]

                ultimoEnvio=ultimoEnvio.split(" ")[0];
                todayDate=formatDate().split(" ")[0];
                if(ultimoEnvio!=todayDate && solicitudes[solicitud]["fechaTercerSolicitudVoBo"]==""){
                    // console.log(solicitudes[solicitud].id);
                    cb=document.getElementById("cbEnviarVoBo_"+solicitudes[solicitud].id);

                    array+= '"'+solicitudes[solicitud].id+'":';
                    array+=cb.checked+', ';
                }

            }
    array+='"date":"'+ formatDate()+'"';
    array+="}";
    field="fechasVoBos"
    updateArray(array,field);

}

function agregarROIP(trigger)
{
    collapsed = trigger.getAttribute("collapsed");
    detalle=document.getElementById("detalleSolicitudAdd");


    if (collapsed=="true"){
            trigger.setAttribute("collapsed","false");
            detalle.style.display="inline-block";
            detalle.style.height="620px";
        }
        else{
                trigger.setAttribute("collapsed","true");
                detalle.style.display="none";
            }
}

function mostrarDetalleScoreCard(fecha,agrupador,asesor,columna){
    allsolicitudes=[]
    for (scorecard in scorecards){
        if (scorecards[scorecard].fecha==fecha) {
            set=scorecards[scorecard]['scoreCard'][agrupador]['asesores'][asesor][columna].set;
            allsolicitudes=scorecards[scorecard]['solicitudes']
        }
    }

    solicitudes=[]
    for(item in set){
        idx=set[item][0];
        for (solicitud in allsolicitudes){
            if (allsolicitudes[solicitud]['id']==idx){
                solicitudes.push(allsolicitudes[solicitud])
            }
        }
    }



    tabla=document.getElementById("detallePipeLine");
    tabla.innerHTML="";
    contenidoTabla='<table id="detallePipeLine" border="1" cellspacing="0" style="table-layout: fixed; width: calc(100% - 8px)">'
    contenidoTabla+="<tr>";
    contenidoTabla+='<th class="encabezadoTabla">Datos</th>';

    for (campo in filtros){
        if(filtros[campo].pipeLineRenderable=="true"){
            contenidoTabla+='<th class="encabezadoTabla">'+filtros[campo].label+'</th>';
        }

    }
    contenidoTabla+="</tr>";
    for (solicitud in solicitudes){
        // console.log(solicitudes[solicitud]);
        contenidoTabla+="<tr>";
        renglon="<>";
        renglon="<td class='linkTabla' onclick='mostrarSolicitudScoreCard(";
        renglon+=fecha+","+solicitudes[solicitud].id
        renglon+=");'><u>Ver</u></td>";
        for (campo in filtros){
            if(filtros[campo].pipeLineRenderable=="true"){
                valor=solicitudes[solicitud][filtros[campo].value]
                if(valor==undefined){
                    valor="";
                }
                renglon+='<td class="cuerpoTabla">'+valor+'</td>';
            }
        }
        contenidoTabla+=renglon;
        contenidoTabla+="</tr>";
    }


    contenidoTabla+='</table>';
    tabla.innerHTML=contenidoTabla;
}

function mostrarSolicitudScoreCard(fecha,idx){
    solicitud=[];
    for (scorecard in scorecards){
        if (scorecards[scorecard].fecha==fecha) {
            allsolicitudes=scorecards[scorecard]['solicitudes']
        }
    }

    for (solicitud in allsolicitudes){
        if (allsolicitudes[solicitud]['id']==idx){
            solicitud=(allsolicitudes[solicitud]);
            break;
        }
    }


    element=document.getElementById(id="detalleSolicitud");
    element.innerHTML="";
    contenidoTabla="";
    for (filtro in filtros){
        contenidoTabla+="<tr>";
        if(filtros[filtro].editRenderable=="true"){
            campo=filtros[filtro].value;
            if (campo in solicitud){
                contenidoTabla+='<td class="cuerpoTablaDer">'+filtros[filtro].label+': </td>';

                valor=solicitud[campo];
                if (valor === undefined){
                    valor="";
                }
                if(campo=="documentos"){
                    valor  =  '<input type="button" name="documentos_{{solicitud.id}}"';
                    valor += 'onclick="openWindow(' ;
                    valor += "'" +solicitud[campo] +"'";
                    valor += ');"';
                    valor += 'value="Ver Documentos">';
                }
                contenidoTabla+='<td class="cuerpoTablaIzq">'+valor+'</td>';
            }
        }
        contenidoTabla+="</tr>";
    }
    element.innerHTML=contenidoTabla;
}

function viewClabesTable(){
    document.getElementById("contenedor2").style.display="none";
    container=document.getElementById('contenedor4');
    panel=document.getElementById('fillPanel');

    winWidth=document.getElementById("windowInfo").getAttribute("width");
    if  (winWidth>=800){
            container.visibility="visible";
            container.style.display="inline-block";
            panel.innerHTML="";
            contenido="<table border=1 cellspacing=0 width='100%'>";
            contenido+='<th class="encabezadoTabla"> Clabe</th>';
            contenido+='<th class="encabezadoTabla"> Clave de Rastreo </th>';
            contenido+='<th class="encabezadoTabla"> Nombre Beneficiario </th>';
            contenido+='<th class="encabezadoTabla"> Referencia Numérica </th>';



            for (solicitud in solicitudes){

                if(solicitudes[solicitud]["fechaValidacionClabe"]==""){

                    contenido+="<tr>";

                    id=parseFloat(solicitudes[solicitud]["id"])
                    referencia="MIPYMEX"+pad(id,8)

                    referenciaNumerica=formatSixDigitsDate()+"1";

                    contenido+="<td class='cuerpoTabla2Izq'>"+solicitudes[solicitud]["clienteClabe"]+"</td>";
                    contenido+="<td class='cuerpoTabla2Izq'>"+referencia+"</td>";
                    contenido+="<td class='cuerpoTabla2Izq'>"+solicitudes[solicitud]["clienteNombre"].toUpperCase()+" "+solicitudes[solicitud]["clienteApellidoPaterno"].toUpperCase()+ " "+ solicitudes[solicitud]["clienteApellidoMaterno"].toUpperCase() +"</td>";
                    contenido+="<td class='cuerpoTabla2Izq'>"+referenciaNumerica+"</td>";
                    contenido+="</tr>";
                }

            }

            contenido += "</table>";
            panel.innerHTML=contenido;

        }

}

function pad(num, size) {
    num = num.toString();
    while (num.length < size) num = "0" + num;
    return num;
}

function formatSixDigitsDate()
{
    var d =new Date();
    var timeOffset=d.getTimezoneOffset();
    // console.log(d)
    // console.log(timeOffset);

    var MS_PER_MINUTE = 60000;
    var timeOffsetSeconds=timeOffset*MS_PER_MINUTE;
    var CDMXOffset=360*MS_PER_MINUTE;
    d= new Date(d - timeOffsetSeconds+CDMXOffset);


    // console.log(d);



    // dformat = [ d.getDate().padLeft(),
    //            (d.getMonth()+1).padLeft(),
    //            d.getFullYear()].join('/') +' ' +
    //           [d.getHours().padLeft(),
    //            d.getMinutes().padLeft(),
    //            d.getSeconds().padLeft()].join(':');
    dformat = [ d.getFullYear().toString().substr(-2),
               (d.getMonth()+1).padLeft(),
               d.getDate().padLeft()].join('');
    return dformat;
}

function getLocation(){
    if (viewName=="Geolocalizacion")
    {
        var x = document.getElementById("coords");
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(showPosition);
            } else {
            x.innerHTML = "Geolocation is not supported by this browser.";
            }
    }
}

function showPosition(position) {
    var x = document.getElementById("coords");
    x.value = position.coords.latitude + "," + position.coords.longitude;
    // getReverseGeocodingData(position.coords.latitude, position.coords.longitude);

}


function getReverseGeocodingData(lat, lng) {
    var latlng = new google.maps.LatLng(lat, lng);
    // This is making the Geocode request
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({ 'latLng': latlng },  (results, status) =>{
        if (status !== google.maps.GeocoderStatus.OK) {
            alert(status);
        }
        // This is checking to see if the Geoeode Status is OK before proceeding
        if (status == google.maps.GeocoderStatus.OK) {
            console.log(results);
            var address = (results[0].formatted_address);
        }
    });
}

function agregarAListaDeCampos(checkbox,value,label,idListaDestino,catalogo){

    listaDestino=document.getElementById(idListaDestino);
    if (checkbox.checked){
        var li = document.createElement("li");
        li.appendChild(document.createTextNode(label));
        li.setAttribute("class", "roundListItem");
        li.setAttribute("name", value);
        li.setAttribute("id", label);
        listaDestino.appendChild(li);
    }else{
        var li= document.getElementById(label)
        listaDestino.removeChild(li)
    }

    var lis = listaDestino.getElementsByTagName("li");
    camposSolicitados=document.getElementById("camposSolicitados")
    camposSolicitados.innerHTML="";
    var innerHTML=""
    for(let i=0; i < lis.length; i++) {
        var li=lis[i]
        innerHTML += li.getAttribute("name")+":"+li.getAttribute("id")+"|";
    }
    camposSolicitados.innerHTML=innerHTML;
}