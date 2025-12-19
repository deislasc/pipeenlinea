#-*- coding: utf-8 -*-
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import json
import os
import sys

from flask import current_app, flash, Flask, Markup, redirect, render_template
from flask import request, url_for, Response, session, escape, make_response, send_file
# from flask_login import current_user, login_required
# from flask_login import LoginManager
import collections



# 2020/04/01
# Personalizacion de la App por: Froylan David Mares Canales
# correo: fdavmares@gmail.com
# import requests
import mainmenu
import campos
import update

# **********************************************************
#                  ARCHIVOS DE FUNCIONES-->
# **********************************************************
import routes_login2,routes_solicitudes,routes_users,routes_empresas
import routes_correos,routes_logs,routes_ROIP,routes_csv
import routes_simulador
import routes_downloadDbBkup
import routes_acl
import routes_visitas
import routes_pagadoras
import routes_analisis
import routes_agendas
import config
#import cronJobShedule  #no se puede usar en PythonAnyWhere




# **********************************************************
#                  <--ARCHIVOS DE FUNCIONES
# **********************************************************



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# **********************************************************
#                    SERVICE ACCOUNT -->
# **********************************************************

# << COMENTARIOS -->
# Fuente: Autentica con un archivo de claves de cuenta de servicio
# https://cloud.google.com/bigquery/docs/authentication/service-account-file
# TODO(developer): Set key_path to the path to the service account key
#                  file.
# key_path = "path/to/service_account.json"
# # <<----TERMINAN COMENTARIOS
# from google.cloud import bigquery
# from google.oauth2 import service_account

# # key_path="serviceAccounts/panviewt2.json"
# key_path="serviceAccounts/application_default_credentials_panviewqc.json"
# credentials = service_account.Credentials.from_service_account_file(
#     key_path,
#     scopes=["https://www.googleapis.com/auth/cloud-platform"],
# )

# client = bigquery.Client(
#     credentials=credentials,
#     project=credentials.project_id,
# )

# **********************************************************
#                    <-- SERVICE ACCOUNT
# **********************************************************

# **********************************************************
#          REINICIALIZA EL SERVIDOR CON UTF-8-->
# **********************************************************


# This is only used when running locally. When running live, gunicorn runs
# the application.
# if __name__ == '__main__':
#     import sys
#     reload(sys)
    # sys.setdefaultencoding('UTF8')

# **********************************************************
#        <--REINICIALIZA EL SERVIDOR CON UTF-8
# **********************************************************


# **********************************************************
#                     IMPORT GLOBAL VARIABLES -->
# **********************************************************
homeExceptions=['/updateData','/updateArray']
menu = mainmenu.menu
menulogin = mainmenu.login
listaCamposSolicitud = campos.diccionarioCamposSolicitud
listaCamposUsuarios = campos.diccionarioCamposUsuarios
listaCamposEmpresas = campos.diccionarioCamposEmpresas
listaCamposLogs = campos.diccionarioCamposLogsSolicitudes
listaCamposSesiones=campos.diccionarioCamposLogsSesiones
listaCamposOperacionesInusuales=campos.diccionarioCamposOperacionesInusuales
listaCamposReporteVentas=campos.diccionarioCamposReporteVentas
listaCamposAgendas = campos.diccionarioCamposAgendas






# **********************************************************
#                <--  IMPORT GLOBAL VARIABLES
# **********************************************************


# **********************************************************
#                    FUNCION PARA ALERTAR -->
# **********************************************************
def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()
# **********************************************************
#                <-- FUNCION PARA ALERTAR
# **********************************************************



# [START upload_image_file]
def upload_image_file(img):
    """
    Upload the user-uploaded file to Google Cloud Storage and retrieve its
    publicly-accessible URL.
    """
    if not img:
        return None

        public_url = storage.upload_file(
            img.read(),
            img.filename,
            img.content_type
            )

        current_app.logger.info(
            'Uploaded file %s as %s.', img.filename, public_url)

        return public_url
# [END upload_image_file]


app = Flask(__name__)
app.config.update(
    SECRET_KEY='?+?.u3j?3M[?|1',
    MAX_CONTENT_LENGTH=20 * 1024 * 1024,
    ALLOWED_EXTENSIONS=set(['png', 'jpg', 'jpeg', 'gif','pdf'])
    )
app.debug = False
app.testing = False


# Se inicializan los cronJobs al iniciar el servidor
# cronJobShedule.clearJobs()
# cronJobShedule.cronJobs()


# print("static_folder:")
# print(app.static_folder)

# login_manager = LoginManager()
# login_manager.init_app(app)

# Configure logging
# if not app.testing:
#     logging.basicConfig(level=logging.INFO)
#     client = google.cloud.logging.Client()
#     # Attaches a Google Stackdriver logging handler to the root logger
#     client.setup_logging(logging.INFO)

def loginRequired(function):
    def wrapper(ownerID):
        user={}
        user=routes_users.getUser(ownerID)
        username=user['userName']

        if 'username' in session:
            # print("Usuario Autorizado.")
            return function(ownerID)
        else:
            # print("Requiere Autenticación.")
            return redirect(url_for('home'))

    return wrapper


def is_authenticated(formData):
    # print(formData)
    if not "ownerID" in formData:
        return False

    if not 'auth_token' in session:
        return False

    auth_token=session['auth_token']
    if routes_login2.isLogInBearer(session['auth_token'])==False:
        return False

    ownerID=formData["ownerID"]
    user={}
    user=routes_users.getUser(ownerID)
    username=user['userName']

    if 'username' in session:
        return True
    else:
        return False

@app.before_request
def before_request_func():
    # print("User Agent:")
    # print(request.user_agent)

    rule=str(request.url_rule)
    # print(rule)
    if rule !='/' and rule!='/logout':
        formData = request.form.to_dict(flat=True)

        if'Authorization' in request.headers:
            data={}
            data['autorizationType']=request.headers['Authorization'].split(" ")[0]
            data['hash']=request.headers['Authorization'].split(" ")[1]
            data['viewName']=rule
            data['userAgent']=request.headers['User-Agent']
            formData=routes_login2.loginCheckByToken(data)

        if 'Apikey' in request.headers:
            data={}
            data['autorizationType']='apiKey'
            data['hash']=request.headers['Apikey']
            data['viewName']=rule
            data['userAgent']=request.headers['User-Agent']
            formData=routes_login2.loginCheckByApiKey(data)

        # formData = request.form.to_dict(flat=True)
        if not is_authenticated(formData):
            # print("Requiere Autenticación.")
            if rule not in homeExceptions:
                if rule!='/static/<path:filename>':
                    # print("go to home")
                    return redirect(url_for('home'))
            else:
                # print(rule[1:])
                redirect(url_for(rule[1:]))
        # else:
        #     print("Usuario Autorizado.")
    else:
        if rule !='/':
            redirect(url_for(rule[1:]))


@app.after_request
def after_request_func(response):
    rule=str(request.url_rule)
    if 'auth_token' in session:
        auth_token=session['auth_token']
        if routes_login2.isLogInBearer(session['auth_token'])!=False:
            response.headers['Authorization']='Bearer '+session['auth_token']
    return response


# **********************************************************
#           RUTAS PARA Home y Login
# **********************************************************

@app.route('/',methods=['GET', 'POST'])
def home():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " LOG IN: "+request.method + '\x1b[0m')
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        data['userAgent']=request.headers['User-Agent']
        result=routes_login2.loginCheck(data)
        if result["code"]==403 or result["code"]==404 or result==None:
            response=make_response(render_template('login.html',
                                    viewName="Bienvenido",
                                    menu=menulogin,
                                    listaSolicitudes="undefined",
                                    listaCamposFiltro="undefined",
                                    listaEmpresas="undefined",
                                    user="undefined",
                                    feedback=result["feedback"]
                                    ))
            response.status_code=result['code']
            return response
        else:
            response=make_response(solicitudes(result["ownerID"]))
            response.headers['Authorization']='Bearer '+result['auth_token']
            response.status_code=result['code']

            return response


    else:# request.method=GET
        if 'auth_token' in session:
            if routes_login2.isLogInBearer(session['auth_token'])==False:
                feedback="Tu sesión ha expirado. \n Vuelve a ingresar."
                session.pop('auth_token', None)
                return render_template('login.html',
                        viewName="Bienvenido",
                        menu=menulogin,
                        listaSolicitudes="undefined",
                        listaCamposFiltro="undefined",
                        listaEmpresas="undefined",
                        user="undefined",
                        feedback=feedback
                        )
        return render_template('login.html',
                viewName="Bienvenido",
                menu=menulogin,
                listaSolicitudes="undefined",
                listaCamposFiltro="undefined",
                listaEmpresas="undefined",
                user="undefined"
                )

@app.route('/logout',methods=['GET', 'POST'])
def logout():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " LOG OUT: "+request.method + '\x1b[0m')
    data = request.form.to_dict(flat=True)
    user=routes_users.getUser(request.args["ownerID"])
    session.pop('userName', None)
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        printf(data);

# **********************************************************
#                   RUTAS PARA SOLICITUDES -->
# **********************************************************


# BACKEND ENDPOINTS
@app.route('/data/solicitudes/list',methods=['GET', 'POST'])
def dataSolicitudesRequest():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " DATA/SOLICITUDES/List: "+request.method + '\x1b[0m')
    data={}
    formData=request.form.to_dict(flat=True)
    data=routes_solicitudes.getSolicitudesInProcess(formData["ownerID"])
    return data

@app.route('/data/solicitudes/list/bystatus/',methods=['GET', 'POST'])
def dataSolicitudesRequestByStatus():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " DATA/SOLICITUDES/list/bystatus: "+request.method + '\x1b[0m')
    data={}
    formData=request.form.to_dict(flat=True)
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],formData["estatus"])
    return data

@app.route('/data/pipeline/',methods=['GET', 'POST'])
def dataPipeLine():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " DATA/PIPELINE: "+request.method + '\x1b[0m')
    data={}
    formData=request.form.to_dict(flat=True)
    data=routes_solicitudes.getPipeLine(formData)
    return data

@app.route('/data/scorecard/',methods=['GET', 'POST'])
def dataScoreCard():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " DATA/SCORECARD: "+request.method + '\x1b[0m')
    data={}
    formData=request.form.to_dict(flat=True)
    data=routes_solicitudes.getScoreCard(formData)
    return data

@app.route('/data/correctsolicitudes/',methods=['GET', 'POST'])
def dataCorrectSolicitudes():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " DATA/CORRECTSOLICITUDES: "+request.method + '\x1b[0m')
    data={}
    data=routes_solicitudes.correctSolicitudesData()
    return data

@app.route('/updateData',methods=['GET', 'POST'])
def updateData():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " UPDATEDATA/: "+request.method + '\x1b[0m')
    if request.method == 'GET':
        return render_template('updateData.html',
            message="Actualizando...")
    data={}
    data=request.form.to_dict(flat=True)
    if update.allowedUser(data):
        response=update.updateData(data)
        return render_template('updateData.html',
            message=response['message'],
            data=response['data'],
            messageCode=response['messageCode'])
    else:
        return render_template('updateData.html',
            message="Usuario no autorizado",
            data=[],
            messageCode="403")


@app.route('/updateArray',methods=['GET', 'POST'])
def updateArray():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " UPDATEARRAY/: "+request.method + '\x1b[0m')
    if request.method == 'GET':
        return render_template('updateArray.html',
            message="Actualizando...")
    data={}
    data=request.form.to_dict(flat=True)

    if update.allowedUser(data):
        response=update.updateArray(data)
        return render_template('updateArray.html',
            message=response['message'],
            data=response['data'],
            messageCode=response['messageCode'])
    else:
        return render_template('updateData.html',
            message="Usuario no autorizado",
            data=[],
            messageCode="403")

@app.route('/data/intervalos',methods=['GET', 'POST'])
def dataIntervalos():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " DATA/INTERVALOS: "+request.method + '\x1b[0m')
    data={}
    formData=request.form.to_dict(flat=True)
    data['intervalos']=routes_solicitudes.getIntervals(formData["fecha"],formData["fechaInicio"],formData["fechaFin"],formData["frecuencia"])
    for intervalo in data['intervalos']:
        print('{:10s}  {:10s}'.format(intervalo['inicio'],intervalo['fin']))
    return data


# FRONTEND ENDPOINTS
# @app.route('/solicitudes')
@loginRequired
def solicitudes(ownerID=None):
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES: "+request.method + '\x1b[0m')
    data={}
    # data=routes_solicitudes.getSolicitudes(ownerID)
    data=routes_solicitudes.getSolicitudesInProcess(ownerID)
    return render_template('solicitudes.html',
        viewName="Solicitudes",
        menu=menu,
        listaSolicitudes=data['listaSolicitudes'],
        listaCamposFiltro=listaCamposSolicitud,
        listaEmpresas = routes_empresas.getAsignacionEmpresas(),
        listaUsuarios = routes_users.getUsersList(),
        pagadoras=routes_pagadoras.getPagadorasList(ownerID)["list"],
        user=data['user'],
        feedback=data['user']['feedback'],
        lastUpdated="null"
        )


@app.route('/solicitudes',methods=['GET', 'POST'])
def solicitudesList():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/LIST: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    if not is_authenticated(formData):
        return redirect(url_for('home'))
    lastUpdated="null"
    if 'lastUpdatedmenuSolicitudes' in formData:
        lastUpdated=formData['lastUpdatedmenuSolicitudes']

    message=""
    reqArgs=request.args.to_dict(flat=True)

    if "message" in reqArgs:
        message=reqArgs["message"]

    ownerID=formData["ownerID"]
    data={}
    data=routes_solicitudes.getSolicitudesInProcess(ownerID)
    return render_template('solicitudes.html',
        viewName="Solicitudes",
        menu=menu,
        listaSolicitudes=data['listaSolicitudes'],
        listaCamposFiltro=listaCamposSolicitud,
        listaEmpresas = routes_empresas.getAsignacionEmpresas(),
        listaUsuarios = routes_users.getUsersList(),
        pagadoras=routes_pagadoras.getPagadorasList(formData["ownerID"])["list"],
        user=data['user'],
        feedback=data['user']['feedback'],
        message= message,
        lastUpdated=lastUpdated
        )

@app.route('/seguimientodiario',methods=['GET', 'POST'])
def seguimientoDiario():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/REPORTE: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuSolicitudes' in formData:
        lastUpdated=formData['lastUpdatedmenuSolicitudes']
    ownerID=formData["ownerID"]
    data={}
    data=routes_solicitudes.getSolicitudesInProcessReport(ownerID)
    if "onlyData" in formData:
        if formData["onlyData"]=="True":
            return data

    return render_template('seguimientodiario.html',
        viewName="Seguimiento Diario",
        menu=menu,
        listaSolicitudes=data['listaSolicitudes'],
        listaCamposFiltro=data["headers"],
        headers=data["headers"],
        listaRegistros=data["reporte"],
        user=data['user'],
        feedback=data['user']['feedback'],
        lastUpdated=lastUpdated
        )

@app.route('/solicitudes/add',methods=['POST'])
def solicitudesAdd():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/ADD: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    if not is_authenticated(formData):
        return redirect(url_for('home'))
    message=""
    response=update.addData("",formData)
    message=response['message']
    if message=="":
        return redirect(url_for('solicitudesList'),code=307)
    else:
        return redirect(url_for('solicitudesList',message=message),code=307)


@app.route('/contactados', methods=['GET', 'POST'])
def solicitudesContactados():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/CONTACTADOS: "+request.method + '\x1b[0m')
    estatus="CONTACTO"
    viewName="Contactados"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuContactados' in formData:
        lastUpdated=formData['lastUpdatedmenuContactados']
    data={}
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    return renderSolicitudesList(data,viewName,lastUpdated,formData)

@app.route('/entregadosariesgos', methods=['GET', 'POST'])
def solicitudesentregadosRiesgos():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/ENTREGADOS A RIESGOS: "+request.method + '\x1b[0m')
    estatus="ENTREGA A RIESGOS"
    viewName="Entregados a Riesgos"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuEntregadosaRiesgos' in formData:
        lastUpdated=formData['lastUpdatedmenuEntregadosaRiesgos']
    data={}
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    return renderSolicitudesList(data,viewName,lastUpdated,formData)

@app.route('/revisionDocumental', methods=['GET', 'POST'])
def solicitudesenRevisionDocumental():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/REVISION DOCUMENTAL: "+request.method + '\x1b[0m')
    estatus="ENTREGA A RIESGOS"
    viewName="Revision Documental"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuRevisionDocumental' in formData:
        lastUpdated=formData['lastUpdatedmenuRevisionDocumental']

    data={}
    feedbackmsg=""
    continuar=False

    documentos=config.documentos
    if("accion" in formData):
        for field in documentos:
            array={}
            array["field"]=field
            array["ownerID"]=formData["ownerID"]
            if not update.allowedUser(array):
                feedbackmsg="Usuario No Autorizado."
                continuar=False
                break
            else:
                continuar=True

    if continuar:
        newData={}
        if update.updateSolicitud(formData["id"], formData, formData):#regresa un boolean
            feedbackmsg="Los cambios se guardaron con éxito."
        else:
            feedbackmsg="Operación fallida.  Vuelva a intentar"

    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    listaSolicitudes={}
    listaSolicitudes=data['listaSolicitudes']
    listaSolicitudes=list(filter(lambda d: d["fechaPrimerSolicitudVoBo"] == "", listaSolicitudes))
    listaSolicitudes=list(filter(lambda d: (
        "fechaRevisionDocumentalConluida" not in d or
        d["fechaRevisionDocumentalConluida"] == ""), listaSolicitudes))

    listaSolicitudes=filtraPorAnalista(formData,listaSolicitudes,incluirVacios=False)
    data['listaSolicitudes']=listaSolicitudes
    return render_template('revisionDocumental.html',
        viewName=viewName,
        menu=menu,
        listaSolicitudes=data['listaSolicitudes'],
        listaCamposFiltro=listaCamposSolicitud,
        listaEmpresas = routes_empresas.getAsignacionEmpresas(),
        listaUsuarios = routes_users.getUsersList(),
        pagadoras=routes_pagadoras.getPagadorasList(formData["ownerID"])["list"],
        user=data['user'],
        feedback=data['user']['feedback'],
        feedbackalert=feedbackmsg,
        lastUpdated=lastUpdated
        )

@app.route('/preAnalisis', methods=['GET', 'POST'])
def solicitudesenPreAnalisis():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/PRE ANALISIS: "+request.method + '\x1b[0m')
    estatus="ENTREGA A RIESGOS"
    viewName="PreAnalisis"
    formData = request.form.to_dict(flat=True)
    formData = correctNumericFields(formData)
    formData = deleteForbiddenFields(formData)
    formData = deleteCheckBoxes(formData)
    lastUpdated="null"

    # print("1:"+formData['tipoListaNegra'])

    if 'lastUpdatedmenuPreAnalisis' in formData:
        lastUpdated=formData['lastUpdatedmenuPreAnalisis']

    data={}
    solicitud={}
    feedbackmsg=""
    msg=""
    continuar=False

    if("accion" in formData):
        for field in formData:
            array={}
            array["field"]=field
            array["ownerID"]=formData["ownerID"]
            if not update.allowedUser(array):
                feedbackmsg="Usuario No Autorizado."
                continuar=False
                break
            else:
                continuar=True

    if continuar and (formData["clienteFechaIngreso"]=="" or
            formData["fechaEmisionContrato"]=="" or
            formData["fechaPrimerCobro"]=="" ):
            continuar=False
            formData["feedbackalert"]="Falta llenar alguna fecha."

    if continuar and float(formData["solicitudSaldoParcialidadesMontoAnterior"])>0:
        formData["solicitudEsCleanUp"]="Sí"


    if continuar and formData["accion"]=="Realizar Analisis":
        newData={}
        del formData["accion"]
        continuar=False
        solicitud=routes_solicitudes.getSolicitudById(int(formData["id"]))

        for campo in formData:
            if campo in config.camposAnalisisCredito:
                solicitud[campo]=formData[campo]

        if "montoSolicitado" not in formData:
            formData["montoSolicitado"]=solicitud["montoSolicitado"]

        if "plazoSolicitado" not in formData:
            formData["plazoSolicitado"]=solicitud["plazoSolicitado"]

        # Analisis para datos generales de la Solicitud
        solicitud["propuestaBuenBuro"]={}
        solicitud["propuestaSolicitud"]={}
        solicitud["propuestaRecomendacion"]={}
        solicitud["plazoAutorizado"]=""
        solicitud["montoAutorizado"]="0.00"
        solicitud["tasaAutorizada"]="0.00"
        solicitud["tasaDeComision"]="0.00"
        respuestaAnalisis=routes_analisis.analisisSolicitud(solicitud,formData)
        solicitud=respuestaAnalisis['solicitud']


        # Propuesta Original ---->
        solicitud["propuestaSolicitud"]={}
        solicitud["propuestaSolicitud"]["comentarios"]=""
        for campo in formData:
            if campo in config.camposAnalisisCredito:
                solicitud["propuestaSolicitud"][campo]=formData[campo]
        solicitud["propuestaSolicitud"]["montoAutorizado"]=formData["montoSolicitado"]
        solicitud["propuestaSolicitud"]["plazoAutorizado"]=formData["plazoSolicitado"]
        solicitud["propuestaSolicitud"]["tasaAutorizada"]=solicitud["tasaPolitica"]
        solicitud["propuestaSolicitud"]["tasaDeComision"]=solicitud["tasaDeComisionPolitica"]
        solicitud["propuestaSolicitud"]["fechaEntregaARiesgos"]=solicitud["fechaEntregaARiesgos"]

        #Primer corrida de analisis para obtener datos por política
        respuestaAnalisis=routes_analisis.analisisSolicitud(solicitud["propuestaSolicitud"],formData)
        solicitud["propuestaSolicitud"]=respuestaAnalisis['solicitud']

        # Se realizan ajustes por políticas
        if float(solicitud["montoSolicitado"])>float(solicitud["propuestaSolicitud"]["montoMaximoPolitica"]):
            solicitud["propuestaSolicitud"]["montoAutorizado"]=solicitud["propuestaSolicitud"]["montoMaximoPolitica"]

        if solicitud["producto"]=="Nómina" and float(solicitud["plazoSolicitado"])>float(solicitud["propuestaSolicitud"]["plazoMaximoPolitica"]):
            solicitud["propuestaSolicitud"]["plazoSolicitado"]=solicitud["propuestaSolicitud"]["plazoMaximoPolitica"]

        if solicitud["producto"]=="Adelanto de Nómina" and float(solicitud["plazoSolicitado"].split(" ")[0]) > float(solicitud["propuestaSolicitud"]["plazoMaximoPolitica"].split(" ")[0]):
            solicitud["propuestaSolicitud"]["plazoSolicitado"]=solicitud["propuestaSolicitud"]["plazoMaximoPolitica"]

        solicitud["propuestaSolicitud"]["plazoAutorizado"]=solicitud["propuestaSolicitud"]["plazoSolicitado"]
        solicitud["propuestaSolicitud"]["tasaAutorizada"] =solicitud["propuestaSolicitud"]["tasaPolitica"]
        solicitud["propuestaSolicitud"]["tasaDeComision"] =solicitud["propuestaSolicitud"]["tasaDeComisionPolitica"]
        solicitud["propuestaSolicitud"]["fechaEntregaARiesgos"] =solicitud["propuestaSolicitud"]["fechaEntregaARiesgos"]

        #Segunda corrida de analiis para usar datos de politica como autorizados en la propuesta
        respuestaSimulacion=routes_analisis.completarDatosSimuladorSIAC(solicitud["propuestaSolicitud"])
        respuestaAnalisis=routes_analisis.analisisSolicitud(solicitud["propuestaSolicitud"],formData)
        solicitud["propuestaSolicitud"]=respuestaAnalisis['solicitud']

        #Corrida de simulador SIAC para completar datos

        solicitud["propuestaSolicitud"]=respuestaSimulacion['solicitud']


        solicitud["propuestaSolicitud"]["montoTransferencia"]=str(float(solicitud["propuestaSolicitud"]["montoAutorizado"]) -
                                                                  float(solicitud["solicitudSaldoParcialidadesMontoAnterior"]))
        solicitud["propuestaSolicitud"]=correctNumericFields(solicitud["propuestaSolicitud"])

        if "documentos" in solicitud["propuestaSolicitud"]:
            del solicitud["propuestaSolicitud"]["documentos"]

        if "campaniaDisponible" in solicitud["propuestaSolicitud"]:
            del solicitud["propuestaSolicitud"]["campaniaDisponible"]

        # Analisis de factibilidad sobre la propuesta Original
        solicitud["propuestaSolicitud"]["factibilidad"]="Sí Procede"

        if float(solicitud["montoCapacidadDePago"])<=0:
            solicitud["propuestaSolicitud"]["factibilidad"]="No procede por no tener Capacidad de Pago."

        if float(solicitud["montoCapacidadDePago"])<float(solicitud["propuestaSolicitud"]["pagoParcialidadSimulador"]):
            solicitud["propuestaSolicitud"]["factibilidad"]="No procede porque la Parcialidad es mayor a la Capacidad de Pago."


        if float(solicitud["montoSolicitado"])>float(solicitud["propuestaSolicitud"]["montoMaximoPolitica"]):
            solicitud["propuestaSolicitud"]["factibilidad"]="No procede con el monto solicitado se ajusta a máximo por Polìtica. Verificar si existe oferta por Buen Buro"

        if solicitud["producto"]=="Nómina":
            if float(solicitud["propuestaSolicitud"]["montoTransferencia"])<5000.00:
                solicitud["propuestaSolicitud"]["factibilidad"]="No procede el monto de transferencia es menor a $5000"



        # Propuesta Original <----
        # Propuesta Buen Buro ---->
        if solicitud["producto"]=="Nómina":
            if (solicitud["tipoBuroCredito"]=="Bueno" or
                solicitud["tipoBuroCredito"]=="Regular con Capacidad" ):
                solicitud["propuestaBuenBuro"]={}
                solicitud["propuestaBuenBuro"]["comentarios"]=""
                for campo in formData:
                    if campo in config.camposAnalisisCredito:
                        solicitud["propuestaBuenBuro"][campo]=formData[campo]
                solicitud["propuestaBuenBuro"]["montoAutorizado"]=solicitud["montoBuenBuro"]
                solicitud["propuestaBuenBuro"]["plazoAutorizado"]=solicitud["propuestaSolicitud"]["plazoSolicitado"]
                solicitud["propuestaBuenBuro"]["tasaAutorizada"] =solicitud["propuestaSolicitud"]["tasaPolitica"]
                solicitud["propuestaBuenBuro"]["tasaDeComision"] =solicitud["propuestaSolicitud"]["tasaDeComisionPolitica"]
                solicitud["propuestaBuenBuro"]["fechaEntregaARiesgos"] =solicitud["propuestaSolicitud"]["fechaEntregaARiesgos"]


                respuestaAnalisis=routes_analisis.analisisSolicitud(solicitud["propuestaBuenBuro"],formData)
                solicitud["propuestaBuenBuro"]=respuestaAnalisis['solicitud']
                respuestaSimulacion=routes_analisis.completarDatosSimuladorSIAC(solicitud["propuestaBuenBuro"])
                solicitud["propuestaBuenBuro"]=respuestaSimulacion['solicitud']


                solicitud["propuestaBuenBuro"]["montoTransferencia"]=str(float(solicitud["propuestaBuenBuro"]["montoAutorizado"]) -
                                                                      float(solicitud["solicitudSaldoParcialidadesMontoAnterior"]))
                solicitud["propuestaBuenBuro"]=correctNumericFields(solicitud["propuestaBuenBuro"])



                if "documentos" in solicitud["propuestaBuenBuro"]:
                    del solicitud["propuestaBuenBuro"]["documentos"]

                if "campaniaDisponible" in solicitud["propuestaBuenBuro"]:
                    del solicitud["propuestaBuenBuro"]["campaniaDisponible"]


        # Propuesta Buen Buro <----

        # Se mejora la propuesta de Buen Buro en caso de no tener capacidad de pago
        # Se genera una opcion disminuyendo el monto
            if (solicitud["tipoBuroCredito"]=="Bueno" or
                solicitud["tipoBuroCredito"]=="Regular con Capacidad"):
                if solicitud["propuestaBuenBuro"]["capacidadDePago"]=="No Cumple":
                    if ((solicitud["tipoBuroCredito"]=="Bueno" or
                         solicitud["tipoBuroCredito"]=="Regular con Capacidad")and
                        solicitud["propuestaBuenBuro"]["capacidadDePago"]=="No Cumple"):
                        solicitud["propuestaBuenBuro"]["montoAutorizado"]=solicitud["montoBuenBuro"]
                    if int(solicitud["propuestaBuenBuro"]["plazoSolicitado"]) < int(solicitud["propuestaBuenBuro"]["plazoMaximoPolitica"]):
                        solicitud["propuestaBuenBuro"]["plazoAutorizado"]=str(int(solicitud["propuestaBuenBuro"]["plazoSolicitado"]) +6)

                    montoSolicitudTemp=solicitud["montoSolicitado"]
                    while solicitud["propuestaBuenBuro"]["capacidadDePago"]=="No Cumple":
                        respuestaAnalisis=routes_analisis.analisisSolicitud(solicitud["propuestaBuenBuro"],formData)
                        solicitud["propuestaBuenBuro"]=respuestaAnalisis['solicitud']
                        respuestaSimulacion=routes_analisis.completarDatosSimuladorSIAC(solicitud["propuestaBuenBuro"])
                        solicitud["propuestaBuenBuro"]=respuestaSimulacion['solicitud']
                        montoAutorizado=float(solicitud["propuestaBuenBuro"]["montoAutorizado"])
                        parcialidadesMontoAnterior=float(solicitud["solicitudSaldoParcialidadesMontoAnterior"])
                        montoTransferencia=montoAutorizado-parcialidadesMontoAnterior
                        solicitud["propuestaBuenBuro"]["montoTransferencia"]=str(montoTransferencia)
                        solicitud["propuestaBuenBuro"]=correctNumericFields(solicitud["propuestaBuenBuro"])

                        pagoParcialidadSimulador=float(solicitud["propuestaBuenBuro"]["pagoParcialidadSimulador"])
                        montoCapacidadDePago=float(solicitud["propuestaBuenBuro"]["montoCapacidadDePago"])

                        if pagoParcialidadSimulador < montoCapacidadDePago:
                            solicitud["propuestaBuenBuro"]["capacidadDePago"]="Ok"

                        if pagoParcialidadSimulador > montoCapacidadDePago:
                            solicitud["propuestaBuenBuro"]["capacidadDePago"]="No Cumple"
                            solicitud["propuestaBuenBuro"]["montoAutorizado"]=str(float(solicitud["propuestaBuenBuro"]["montoAutorizado"])-100)

                    if "documentos" in solicitud["propuestaBuenBuro"]:
                        del solicitud["propuestaBuenBuro"]["documentos"]

                    if "campaniaDisponible" in solicitud["propuestaBuenBuro"]:
                        del solicitud["propuestaBuenBuro"]["campaniaDisponible"]

        # Propuesta Recomendacion ---->
            solicitud["propuestaRecomendacion"]={}
            solicitud["propuestaRecomendacion"]["comentarios"]=""
            solicitud["propuestaRecomendacion"]["fechaEntregaARiesgos"] =solicitud["propuestaSolicitud"]["fechaEntregaARiesgos"]

            if solicitud["propuestaSolicitud"]["capacidadDePago"]=="No Cumple":
                solicitud["propuestaRecomendacion"]["montoAutorizado"]=solicitud["montoSolicitado"]
                if float(solicitud["propuestaRecomendacion"]["montoAutorizado"])>float(solicitud["montoMaximoPolitica"]):
                    solicitud["propuestaRecomendacion"]["montoAutorizado"]=solicitud["montoMaximoPolitica"]

                for campo in formData:
                    if campo in config.camposAnalisisCredito:
                        solicitud["propuestaRecomendacion"][campo]=formData[campo]
                solicitud["propuestaRecomendacion"]["plazoAutorizado"]=formData["plazoSolicitado"]
                solicitud["propuestaRecomendacion"]["tasaAutorizada"]=formData["tasaPolitica"]
                solicitud["propuestaRecomendacion"]["tasaDeComision"]=formData["tasaDeComisionPolitica"]
                solicitud["propuestaRecomendacion"]["capacidadDePago"]="No Cumple"

                # Se genera una opcion disminuyendo el monto
                montoSolicitudTemp=solicitud["montoSolicitado"]

                while solicitud["propuestaRecomendacion"]["capacidadDePago"]=="No Cumple":
                    respuestaAnalisis=routes_analisis.analisisSolicitud(solicitud["propuestaRecomendacion"],formData)
                    solicitud["propuestaRecomendacion"]=respuestaAnalisis['solicitud']
                    respuestaSimulacion=routes_analisis.completarDatosSimuladorSIAC(solicitud["propuestaRecomendacion"])
                    solicitud["propuestaRecomendacion"]=respuestaSimulacion['solicitud']
                    solicitud["propuestaRecomendacion"]["montoTransferencia"]=str(float(solicitud["propuestaRecomendacion"]["montoAutorizado"]) -
                                                                             float(solicitud["solicitudSaldoParcialidadesMontoAnterior"]))
                    solicitud["propuestaRecomendacion"]=correctNumericFields(solicitud["propuestaRecomendacion"])
                    if float(solicitud["propuestaRecomendacion"]["pagoParcialidadSimulador"])>float(solicitud["propuestaRecomendacion"]["montoCapacidadDePago"]):
                        solicitud["propuestaRecomendacion"]["capacidadDePago"]="No Cumple"
                        solicitud["propuestaRecomendacion"]["montoAutorizado"]=str(float(solicitud["propuestaRecomendacion"]["montoAutorizado"])-100)

                #Si el monto de transferencia el menor a 5000 se incrementa el plazo y se mejora la opcion
                if (float(solicitud["propuestaRecomendacion"]["montoTransferencia"])<5000):
                    if int(solicitud["propuestaRecomendacion"]["plazoSolicitado"]) < int(solicitud["propuestaRecomendacion"]["plazoMaximoPolitica"]):
                        solicitud["propuestaRecomendacion"]["plazoAutorizado"]=str(int(solicitud["propuestaRecomendacion"]["plazoSolicitado"]) +6)
                        solicitud["propuestaRecomendacion"]["montoAutorizado"]=montoSolicitudTemp
                        solicitud["propuestaRecomendacion"]["capacidadDePago"]="No Cumple"
                        while solicitud["propuestaRecomendacion"]["capacidadDePago"]=="No Cumple":
                            respuestaAnalisis=routes_analisis.analisisSolicitud(solicitud["propuestaRecomendacion"],formData)
                            solicitud["propuestaRecomendacion"]=respuestaAnalisis['solicitud']
                            respuestaSimulacion=routes_analisis.completarDatosSimuladorSIAC(solicitud["propuestaRecomendacion"])
                            solicitud["propuestaRecomendacion"]=respuestaSimulacion['solicitud']
                            solicitud["propuestaRecomendacion"]["montoTransferencia"]=str(float(solicitud["propuestaRecomendacion"]["montoAutorizado"]) -
                                                                                     float(solicitud["solicitudSaldoParcialidadesMontoAnterior"]))
                            solicitud["propuestaRecomendacion"]=correctNumericFields(solicitud["propuestaRecomendacion"])
                            if solicitud["propuestaRecomendacion"]["capacidadDePago"]=="No Cumple":
                                solicitud["propuestaRecomendacion"]["montoAutorizado"]=str(float(solicitud["propuestaRecomendacion"]["montoAutorizado"])-100)

                if "documentos" in solicitud["propuestaRecomendacion"]:
                    del solicitud["propuestaRecomendacion"]["documentos"]

                if "campaniaDisponible" in solicitud["propuestaRecomendacion"]:
                    del solicitud["propuestaRecomendacion"]["campaniaDisponible"]


        if solicitud["producto"]=="Adelanto de Nómina":
            solicitud["propuestaRecomendacion"]={}
            solicitud["propuestaRecomendacion"]["comentarios"]=""
            solicitud["propuestaRecomendacion"]["fechaEntregaARiesgos"] =solicitud["fechaEntregaARiesgos"]

            if solicitud["propuestaSolicitud"]["capacidadDePago"]=="No Cumple":
                solicitud["propuestaRecomendacion"]["montoAutorizado"]=solicitud["montoSolicitado"]


                for campo in formData:
                    if campo in config.camposAnalisisCredito:
                        solicitud["propuestaRecomendacion"][campo]=formData[campo]
                solicitud["propuestaRecomendacion"]["plazoAutorizado"]=formData["plazoSolicitado"]
                solicitud["propuestaRecomendacion"]["tasaAutorizada"]=formData["tasaPolitica"]
                solicitud["propuestaRecomendacion"]["tasaDeComision"]=formData["tasaDeComisionPolitica"]
                solicitud["propuestaRecomendacion"]["capacidadDePago"]="No Cumple"


                # Se genera una opcion disminuyendo el monto
                montoSolicitudTemp=solicitud["montoSolicitado"]
                propuestaPorMonto={}
                propuestaPorPlazo={}
                while solicitud["propuestaRecomendacion"]["capacidadDePago"]=="No Cumple":
                    respuestaAnalisis=routes_analisis.analisisSolicitud(solicitud["propuestaRecomendacion"],formData)
                    solicitud["propuestaRecomendacion"]=respuestaAnalisis['solicitud']
                    respuestaSimulacion=routes_analisis.completarDatosSimuladorSIAC(solicitud["propuestaRecomendacion"])
                    solicitud["propuestaRecomendacion"]=respuestaSimulacion['solicitud']
                    solicitud["propuestaRecomendacion"]["montoTransferencia"]=str(float(solicitud["propuestaRecomendacion"]["montoAutorizado"]) -
                                                                             float(solicitud["solicitudSaldoParcialidadesMontoAnterior"]))
                    solicitud["propuestaRecomendacion"]=correctNumericFields(solicitud["propuestaRecomendacion"])
                    if solicitud["propuestaRecomendacion"]["capacidadDePago"]=="No Cumple":
                        solicitud["propuestaRecomendacion"]["montoAutorizado"]=str(float(solicitud["propuestaRecomendacion"]["montoAutorizado"])-100)

                #Si el monto propuesto es menor que el 75% del montoSolicitado se incrementa el plazo y se mejora la opcion
                if float(solicitud["propuestaRecomendacion"]["montoTransferencia"])/float(solicitud["montoSolicitado"])<0.75:
                    if float(solicitud["clienteAntiguedadMeses"])>6:
                        if "1" in solicitud["plazoSolicitado"]:
                            plazoSugerido=solicitud["plazoSolicitado"].replace("1","2")
                            if "Quincena" in plazoSugerido and "2" in plazoSugerido:
                                plazoSugerido=plazoSugerido.replace("Quincena","Quincenas")

                            if "Semana" in plazoSugerido and "2" in plazoSugerido:
                                plazoSugerido=plazoSugerido.replace("Semana","Semanas")

                            solicitud["propuestaRecomendacion"]["plazoAutorizado"]=plazoSugerido
                            solicitud["propuestaRecomendacion"]["montoAutorizado"]=montoSolicitudTemp
                            solicitud["propuestaRecomendacion"]["capacidadDePago"]="No Cumple"
                            while solicitud["propuestaRecomendacion"]["capacidadDePago"]=="No Cumple":
                                respuestaAnalisis=routes_analisis.analisisSolicitud(solicitud["propuestaRecomendacion"],formData)
                                solicitud["propuestaRecomendacion"]=respuestaAnalisis['solicitud']
                                respuestaSimulacion=routes_analisis.completarDatosSimuladorSIAC(solicitud["propuestaRecomendacion"])
                                solicitud["propuestaRecomendacion"]=respuestaSimulacion['solicitud']
                                solicitud["propuestaRecomendacion"]["montoTransferencia"]=str(float(solicitud["propuestaRecomendacion"]["montoAutorizado"]) -
                                                                                         float(solicitud["solicitudSaldoParcialidadesMontoAnterior"]))
                                solicitud["propuestaRecomendacion"]=correctNumericFields(solicitud["propuestaRecomendacion"])
                                if solicitud["propuestaRecomendacion"]["capacidadDePago"]=="No Cumple":
                                    solicitud["propuestaRecomendacion"]["montoAutorizado"]=str(float(solicitud["propuestaRecomendacion"]["montoAutorizado"])-100)



        if "documentos" in solicitud["propuestaRecomendacion"]:
            del solicitud["propuestaRecomendacion"]["documentos"]

        if "campaniaDisponible" in solicitud["propuestaRecomendacion"]:
            del solicitud["propuestaRecomendacion"]["campaniaDisponible"]


        # Se vacía propuesta de buen buro si no tiene capacidad de pago
        if solicitud["producto"]=="Nómina":
            if "propuestaBuenBuro" in solicitud:
                if "capacidadDePago" in solicitud["propuestaBuenBuro"]:
                    if solicitud["propuestaBuenBuro"]["capacidadDePago"]=="No Cumple":
                        solicitud["propuestaBuenBuro"]={}
        #Se vacían propuestas cuando no hay capcidad de Pago
        if float(solicitud["montoCapacidadDePago"])<=0:
            solicitud["propuestaBuenBuro"]={}
            solicitud["propuestaRecomendacion"]={}

        # print(json.dumps(solicitud["propuestaBuenBuro"]))
        # print(json.dumps(solicitud["propuestaRecomendacion"]))
        # Propuesta Recomendacion <----

        # Se actualiza Solicitud en Base de Datos ----->
        if update.updateSolicitud(formData['id'], solicitud, formData):#regresa un boolean
            feedbackmsg="Los cambios se guardaron con éxito."
            if msg !="":
                feedbackmsg += " |"+msg
        else:
            feedbackmsg="Operación fallida.  Vuelva a intentar"
        if solicitud["errorTransferencia"]!="":
            feedbackmsg+=" |"+solicitud["errorTransferencia"]
        # Se actualiza Solicitud en Base de Datos <-----


    # Se actualiza Solicitud con Propuesta Autorizada ---->
    propuesta=""
    if continuar and formData["accion"]=="Aceptar Propuesta Solicitado":
        solicitud=routes_solicitudes.getSolicitudById(int(formData["id"]))
        propuesta= solicitud["propuestaSolicitud"].replace("\'", "\"")

    if continuar and formData["accion"]=="Aceptar Propuesta Buen Buro":
        solicitud=routes_solicitudes.getSolicitudById(int(formData["id"]))
        propuesta= solicitud["propuestaBuenBuro"].replace("\'", "\"")

    if continuar and formData["accion"]=="Aceptar Propuesta Recomendacion":
        solicitud=routes_solicitudes.getSolicitudById(int(formData["id"]))
        propuesta= solicitud["propuestaRecomendacion"].replace("\'", "\"")

    if continuar and "accion" in formData:
        if "Aceptar Propuesta"in formData["accion"]:
            propuestaAceptada = json.loads(propuesta)
            solicitud["montoAutorizado"]=propuestaAceptada["montoAutorizado"]
            solicitud["montoTransferencia"]=propuestaAceptada["montoTransferencia"]
            solicitud["tasaDeComision"]=propuestaAceptada["tasaDeComision"]
            solicitud["tasaAutorizada"]=propuestaAceptada["tasaAutorizada"]
            solicitud["plazoAutorizado"]=propuestaAceptada["plazoAutorizado"]
            respuestaAnalisis=routes_analisis.analisisSolicitud(solicitud,formData)
            solicitud=respuestaAnalisis['solicitud']
            # Se actualiza Solicitud en Base de Datos ----->
            del formData["accion"]
            if update.updateSolicitud(formData['id'], solicitud, formData):#regresa un boolean
                feedbackmsg="Los cambios se guardaron con éxito."
                if msg !="":
                    feedbackmsg += " |"+msg
            else:
                feedbackmsg="Operación fallida.  Vuelva a intentar"
            if solicitud["errorTransferencia"]!="":
                feedbackmsg+=" |"+solicitud["errorTransferencia"]
             # Se actualiza Solicitud en Base de Datos <-----
    # Se actualiza Solicitud con Propuesta Autorizada <----

    feedbackmsg.replace("| |","").replace("||","")
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    listaSolicitudes={}
    listaSolicitudes=data['listaSolicitudes']
    listaSolicitudes=list(filter(lambda d: d["fechaPrimerSolicitudVoBo"] == "", listaSolicitudes))
    listaSolicitudes=list(filter(lambda d: (
        ("fechaRevisionDocumentalConluida"  in d and
        d["fechaRevisionDocumentalConluida"] != "" )and
        ("fechaAnalisisConluido" not in d or
        d["fechaAnalisisConluido"] == "")), listaSolicitudes))

    listaSolicitudes=filtraPorAnalista(formData,listaSolicitudes,incluirVacios=False)

    #Elimino propuestas vacias
    for idx, solicitud in enumerate(listaSolicitudes):
        if "propuestaBuenBuro" in solicitud:
            if solicitud["propuestaBuenBuro"]=="{}":
                del listaSolicitudes[idx]["propuestaBuenBuro"]
        if "propuestaRecomendacion" in solicitud:
            if solicitud["propuestaRecomendacion"]=="{}":
                del listaSolicitudes[idx]["propuestaRecomendacion"]
        #..............................................
        # Vacía propuesta para clientes con menos de 6 meses
        if solicitud["producto"]=="Nómina":
            if float(solicitud["clienteAntiguedadMeses"])<6:
                if "propuestaBuenBuro" in solicitud:
                    del listaSolicitudes[idx]["propuestaBuenBuro"]
        #..............................................



    orden=config.camposPreAnalisisOrden
    listaCamposTemp=[]
    for campo in listaCamposSolicitud:
        if "preAnalisisRenderable" in campo:
            if campo["preAnalisisRenderable"]=="true":
                listaCamposTemp.append(campo.copy())

    listaCampos=[]
    for campo in listaCamposTemp:
        campo["editRenderable"]="true"
        campo["orden"]=orden.index(campo["value"])
        listaCampos.append(campo.copy())

    listaCampos=sorted(listaCampos, key=lambda k: (k['orden']))
    data["listaSolicitudes"]=listaSolicitudes

    return renderSolicitudesList(data,viewName,lastUpdated,formData,listaCampos)

@app.route('/analisisCreditos', methods=['GET', 'POST'])
def solicitudesenAnalisisCredito():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/ANALISIS DE CREDITOS: "+request.method + '\x1b[0m')
    estatus="ENTREGA A RIESGOS"
    viewName="Analisis de Creditos"
    formData=request.form.to_dict(flat=True)
    formData = correctNumericFields(formData)
    formData = deleteForbiddenFields(formData)
    formData = deleteCheckBoxes(formData)
    lastUpdated="null"

    if 'lastUpdatedmenuAnalisisCreditos' in formData:
        lastUpdated=formData['lastUpdatedmenuAnalisisCreditos']

    data={}
    feedbackmsg=""
    continuar=False


    camposAnalisisCredito=config.camposAnalisisCredito


    if("accion" in formData):
        for field in formData:
            array={}
            array["field"]=field
            array["ownerID"]=formData["ownerID"]
            if not update.allowedUser(array):
                feedbackmsg="Usuario No Autorizado."
                continuar=False
                break
            else:
                continuar=True

    if continuar and formData["accion"]=="Realizar Analisis":
        newData={}
        del formData["accion"]
        continuar=False
        solicitud=routes_solicitudes.getSolicitudById(int(formData["id"]))
        respuestaAnalisis=routes_analisis.analisisSolicitud(solicitud,formData)
        solicitud=respuestaAnalisis['solicitud']
        msg=respuestaAnalisis['msg']

        if update.updateSolicitud(formData['id'], solicitud, formData):#regresa un boolean
            feedbackmsg="Los cambios se guardaron con éxito."
            if msg !="":
                feedbackmsg += " |"+msg
        else:
            feedbackmsg="Operación fallida.  Vuelva a intentar"
        if solicitud["errorTransferencia"]!="":
            feedbackmsg+=" |"+solicitud["errorTransferencia"]


    if continuar and formData["accion"]=="Simular":
        newData={}
        del formData["accion"]
        continuar=False
        solicitud=routes_solicitudes.getSolicitudById(int(formData["id"]))
        respuestaSimulacion=routes_analisis.completarDatosSimuladorSIAC(solicitud)
        solicitud=respuestaSimulacion['solicitud']
        msg=respuestaSimulacion['msg']

        if update.updateSolicitud(formData['id'], solicitud, formData):#regresa un boolean
            feedbackmsg="Los cambios se guardaron con éxito."
            if msg !="":
                feedbackmsg += " |"+msg
        else:
            feedbackmsg="Operación fallida.  Vuelva a intentar"
        if solicitud["errorTransferencia"]!="":
            feedbackmsg+=" |"+solicitud["errorTransferencia"]


    feedbackmsg.replace("| |","").replace("||","")
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    listaSolicitudes={}
    listaSolicitudes=data['listaSolicitudes']
    listaSolicitudes=list(filter(lambda d: d["fechaPrimerSolicitudVoBo"] == "", listaSolicitudes))
    listaSolicitudes=list(filter(lambda d: (
        ("fechaRevisionDocumentalConluida"  in d and
        d["fechaRevisionDocumentalConluida"] != "" )and
        ("fechaAnalisisConluido" not in d or
        d["fechaAnalisisConluido"] == "")), listaSolicitudes))

    for idx, solicitud in enumerate(listaSolicitudes):
        if "clientePagadora" not in solicitud:
            listaSolicitudes[idx]["clientePagadora"]=""
        if solicitud["clientePagadora"]=="":
            empresa=routes_empresas.getEmpresaByName(solicitud["clienteEmpresa"])
            if "pagadora" in empresa:
                listaSolicitudes[idx]["clientePagadora"]=empresa["pagadora"]

    listaSolicitudes=filtraPorAnalista(formData,listaSolicitudes,incluirVacios=False)

    data['listaSolicitudes']=listaSolicitudes
    return render_template('analisis.html',
        viewName=viewName,
        menu=menu,
        listaSolicitudes=data['listaSolicitudes'],
        listaCamposFiltro=listaCamposSolicitud,
        listaEmpresas = routes_empresas.getAsignacionEmpresas(),
        pagadoras=routes_pagadoras.getPagadorasList(formData["ownerID"])["list"],
        listaUsuarios = routes_users.getUsersList(),
        user=data['user'],
        feedback=data['user']['feedback'],
        feedbackalert=feedbackmsg,
        lastUpdated=lastUpdated
        )

@app.route('/autorizacionriesgos', methods=['GET', 'POST'])
def solicitudesAutorizacionRiesgos():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/AUTORIZACION RIESGOS: "+request.method + '\x1b[0m')
    estatus="ENTREGA A RIESGOS"
    viewName="Autorización Riesgos"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuAutorizacionRiesgos' in formData:
        lastUpdated=formData['lastUpdatedmenuAutorizacionRiesgos']
    data={}
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    listaSolicitudes={}
    listaSolicitudes=data['listaSolicitudes']
    listaSolicitudes=list(filter(lambda d: d["fechaVoBo"] != "", listaSolicitudes))
    listaSolicitudes=filtraPorAnalista(formData,listaSolicitudes,incluirVacios=False)
    data['listaSolicitudes']=listaSolicitudes
    return renderSolicitudesList(data,viewName,lastUpdated,formData)

@app.route('/imprimircontrato', methods=['GET', 'POST'])
def solicitudesImprimirContrato():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/IMPRIMIR CONTRATO: "+request.method + '\x1b[0m')
    estatus="AUTORIZADO"
    viewName="Imprimir Contrato"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuImprimirContrato' in formData:
        lastUpdated=formData['lastUpdatedmenuImprimirContrato']

    continuar=False
    if("accion" in formData):
        for field in formData:
            array={}
            array["field"]=field
            array["ownerID"]=formData["ownerID"]
            if not update.allowedUser(array):
                feedbackmsg="Usuario No Autorizado."
                continuar=False
                break
            else:
                continuar=True

    feedbackmsg=""
    if continuar and formData["accion"]=="Simular":
        newData={}
        del formData["accion"]
        continuar=False
        solicitud=routes_solicitudes.getSolicitudById(int(formData["id"]))
        respuestaSimulacion=routes_analisis.completarDatosSimuladorSIAC(solicitud)
        solicitud=respuestaSimulacion['solicitud']
        msg=respuestaSimulacion['msg']

        if update.updateSolicitud(formData['id'], solicitud, formData):#regresa un boolean
            feedbackmsg="Los cambios se guardaron con éxito."
            if msg !="":
                feedbackmsg += " |"+msg
        else:
            feedbackmsg="Operación fallida.  Vuelva a intentar"
        if solicitud["errorTransferencia"]!="":
            feedbackmsg+=" |"+solicitud["errorTransferencia"]


    feedbackmsg.replace("| |","").replace("||","")

    data={}
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    listaSolicitudes={}
    listaSolicitudes=data['listaSolicitudes']
    listaSolicitudes=filtraPorAnalista(formData,listaSolicitudes,incluirVacios=False)
    data['listaSolicitudes']=listaSolicitudes

    return renderSolicitudesList(data,viewName,lastUpdated,formData)

@app.route('/firmarcontrato', methods=['GET', 'POST'])
def solicitudesFirmarContrato():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/FIRMAR CONTRATO: "+request.method + '\x1b[0m')
    estatus="CONTRATO IMPRESO"
    viewName="Firmar Contrato"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuFirmarContrato' in formData:
        lastUpdated=formData['lastUpdatedmenuFirmarContrato']
    data={}
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    listaSolicitudes={}
    listaSolicitudes=data['listaSolicitudes']
    listaSolicitudes=filtraPorAnalista(formData,listaSolicitudes,incluirVacios=False)
    data['listaSolicitudes']=listaSolicitudes
    return renderSolicitudesList(data,viewName,lastUpdated,formData)

@app.route('/porfondear', methods=['GET', 'POST'])
def solicitudesPorFondear():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/POR FONDEAR: "+request.method + '\x1b[0m')
    estatus="FIRMAR CONTRATO"
    viewName="Por Fondear"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuPorFondear' in formData:
        lastUpdated=formData['lastUpdatedmenuPorFondear']
    data={}
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    listaSolicitudes={}
    listaSolicitudes=data['listaSolicitudes']
    # listaSolicitudes=filtraPorAnalista(formData,listaSolicitudes,incluirVacios=False)
    listaSolicitudes=filtraPorEstatusContrato(formData,listaSolicitudes,contratoOK=False)
    data['listaSolicitudes']=listaSolicitudes
    return renderSolicitudesList(data,viewName,lastUpdated,formData)

@app.route('/transferencias', methods=['GET', 'POST'])
def solicitudesTransferencias():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/TRANSFERENCIAS: "+request.method + '\x1b[0m')
    estatus="FIRMAR CONTRATO"
    viewName="Transferencias"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuPorFondear' in formData:
        lastUpdated=formData['lastUpdatedmenuPorFondear']
    data={}
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    listaSolicitudes={}
    listaSolicitudes=data['listaSolicitudes']
    listaSolicitudes=filtraPorEstatusContrato(formData,listaSolicitudes,contratoOK=True)
    data['listaSolicitudes']=listaSolicitudes
    return renderSolicitudesList(data,viewName,lastUpdated,formData)

@app.route('/fondeados', methods=['GET', 'POST'])
def solicitudesFondeados():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/FONDEADOS: "+request.method + '\x1b[0m')
    estatus="FONDEADO"
    viewName="Fondeados"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuFondeados' in formData:
        lastUpdated=formData['lastUpdatedmenuFondeados']
    data={}
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    return renderSolicitudesList(data,viewName,lastUpdated,formData)

@app.route('/rechazados', methods=['GET', 'POST'])
def solicitudesRechazados():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/RECHAZADOS: "+request.method + '\x1b[0m')
    estatus="RECHAZADO"
    viewName="Rechazados"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuRechazados' in formData:
        lastUpdated=formData['lastUpdatedmenuRechazados']
    data={}
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    return renderSolicitudesList(data,viewName,lastUpdated,formData)

# @app.route('/canceladosporcliente', methods=['GET', 'POST'])
# def solicitudesCanceladosPorCliente():
#     print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/CANCELADOS POR CLIENTE: "+request.method + '\x1b[0m')
#     estatus="CANCELADO POR CLIENTE"
#     viewName="Cancelados por el Cliente"
#     formData=request.form.to_dict(flat=True)
#     lastUpdated="null"
#     if 'lastUpdatedSolicitudes' in formData:
#         lastUpdated=formData['lastUpdatedSolicitudes']
#     data={}
#     data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
#     return renderSolicitudesList(data,viewName,lastUpdated,formData)

# @app.route('/canceladosporcartera', methods=['GET', 'POST'])
# def solicitudesCanceladosPorCartera():
#     print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/CANCELADOS POR CARTERA: "+request.method + '\x1b[0m')
#     estatus="CANCELADO POR CARTERA"
#     viewName="Cancelados por Cartera"
#     formData=request.form.to_dict(flat=True)
#     lastUpdated="null"
#     if 'lastUpdatedSolicitudes' in formData:
#         lastUpdated=formData['lastUpdatedSolicitudes']
#     data={}
#     data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
#     return renderSolicitudesList(data,viewName,lastUpdated,formData)

@app.route('/autorizaciondg', methods=['GET', 'POST'])
def solicitudesAutorizacionDG():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/AUTORIZACIONDG: "+request.method + '\x1b[0m')
    estatus="EN AUTORIZACION DG"
    viewName="Autorización DG"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuAutorizacionDG' in formData:
        lastUpdated=formData['lastUpdatedmenuAutorizacionDG']
    data={}
    data=routes_solicitudes.getSolicitudesFilteredByAutorizacionDG(formData["ownerID"],estatus)
    return renderSolicitudesList(data,viewName,lastUpdated,formData)

@app.route('/solicitarvobos',methods=['GET', 'POST'])
def solicitudVoBos():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/VoBos: "+request.method + '\x1b[0m')
    estatus="ENTREGA A RIESGOS"
    viewName="Solicitar VoBo"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuSolicitarVoBos' in formData:
        lastUpdated=formData['lastUpdatedmenuSolicitarVoBos'];
    data={}
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    listaSolicitudes={}
    listaSolicitudes=data['listaSolicitudes']
    listaSolicitudes=list(filter(lambda d: (
        "fechaAnalisisConluido" in d and
        d["fechaAnalisisConluido"] != ""), listaSolicitudes))
    listaSolicitudes=list(filter(lambda d: d["fechaVoBo"] == "", listaSolicitudes))
    listaSolicitudes=filtraPorAnalista(formData,listaSolicitudes,incluirVacios=False)
    data['listaSolicitudes']=listaSolicitudes
    return render_template('vobos.html',
        viewName=viewName,
        menu=menu,
        listaSolicitudes=data['listaSolicitudes'],
        listaCamposFiltro=listaCamposSolicitud,
        listaEmpresas = routes_empresas.getAsignacionEmpresas(),
        listaUsuarios = routes_users.getUsersList(),
        pagadoras=routes_pagadoras.getPagadorasList(formData["ownerID"])["list"],
        user=data['user'],
        feedback=data['user']['feedback'],
        lastUpdated=lastUpdated
        )

@app.route('/clabes', methods=['GET', 'POST'])
def solicitudesValidacionClabes():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/CLABES: "+request.method + '\x1b[0m')
    estatus="ENTREGA A RIESGOS"
    viewName="CLABES"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuClabes' in formData:
        lastUpdated=formData['lastUpdatedmenuClabes']
    data={}
    data=routes_solicitudes.getSolicitudesFilteredByEstatus(formData["ownerID"],estatus)
    listaSolicitudes={}
    listaSolicitudes=data['listaSolicitudes']
    listaSolicitudes=list(filter(lambda d:  d["clienteNuevoRenovacion"]=="Nuevo" and d["clienteClabe"]!="", listaSolicitudes))
    data['listaSolicitudes']=listaSolicitudes
    return render_template('clabes.html',
        viewName=viewName,
        menu=menu,
        listaSolicitudes=data['listaSolicitudes'],
        listaCamposFiltro=listaCamposSolicitud,
        listaEmpresas = routes_empresas.getAsignacionEmpresas(),
        listaUsuarios = routes_users.getUsersList(),
        user=data['user'],
        feedback=data['user']['feedback'],
        lastUpdated=lastUpdated
        )

@app.route('/cobranza', methods=['GET', 'POST'])
def solicitudesCobranza():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/COBRANZA: "+request.method + '\x1b[0m')
    estatus="FONDEADO"
    viewName="Cobranza"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuCobranza' in formData:
        lastUpdated=formData['lastUpdatedmenuCobranza']
    data={}
    listaSolicitudes={}

    if "filtroCriterio" in formData:
        data=routes_solicitudes.getsolicitudesByFilter(formData["ownerID"],formData["filtroCriterio"],formData["filtroValor"])
        listaSolicitudes=data['listaSolicitudes']
        listaSolicitudes=list(filter(lambda d:  d["solicitudEstatus"]==estatus, listaSolicitudes))
        data['listaSolicitudes']=listaSolicitudes
    else:
        data['user']=routes_users.getUser(formData["ownerID"])
        data['listaSolicitudes']=listaSolicitudes

    return render_template('cobranza.html',
        viewName=viewName,
        menu=menu,
        listaSolicitudes=data['listaSolicitudes'],
        listaCamposFiltro=listaCamposSolicitud,
        listaEmpresas = routes_empresas.getAsignacionEmpresas(),
        listaUsuarios = routes_users.getUsersList(),
        user=data['user'],
        feedback=data['user']['feedback'],
        lastUpdated=lastUpdated
        )

@app.route('/controlexpedientes', methods=['GET', 'POST'])
def solicitudesControlExpediente():
    import routes_controlexpedientes

    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + "CONTROLEXPEDIENTES: "+request.method + '\x1b[0m')
    viewName="Control de Expedientes"
    feedbackmsg=""
    formData=request.form.to_dict(flat=True)
    # Actualiza en caso necesario
    if ('accion' in formData and
        formData['accion']=="Actualizar"):
        if routes_controlexpedientes.actualizaCampos(formData):
            feedbackmsg="Éxito:\nLa información fue acutalizada."
        else:
            feedbackmsg="Érror:\nLa información no pudo actualizarse.\nVuelva a intentar"
    # Devuelve la consulta
    listaSolicitudes={}
    listaSolicitudes=routes_solicitudes.getSolicitudes(formData["ownerID"])['listaSolicitudes']
    listaSolicitudes=routes_controlexpedientes.completaDatosResguardo(listaSolicitudes)
    listaSolicitudes=routes_controlexpedientes.getExpedientes(formData,listaSolicitudes)
    listaSolicitudes=limpiarCamposInecesarios(config.camposControlExpedientes, listaSolicitudes)
    listaSolicitudes=routes_solicitudes.limpiarDatosSensible(listaSolicitudes)

    usuario=routes_users.getUser(formData["ownerID"])

    return render_template('controlExpedientes.html',
        viewName=viewName,
        menu=menu,
        listaSolicitudes=listaSolicitudes,
        lastUpdated='null',
        listaCamposFiltro=listaCamposSolicitud,
        user=usuario,
        feedbackalert=feedbackmsg,
        formData=formData
        )

@app.route('/mesadeanalisis', methods=['GET', 'POST'])
def solicitudesMesaDeAnalisis():
    estatus="ENTREGA A RIESGOS"
    import routes_mesaAnalisis
    import datetime
    import numpy
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + "CONTROLEXPEDIENTES: "+request.method + '\x1b[0m')
    viewName="Mesa de Analisis"
    feedbackmsg=""
    formData=request.form.to_dict(flat=True)
    # Actualiza en caso necesario
    if ('accion' in formData and
        formData['accion']=="Actualizar"):
        if routes_mesaAnalisis.actualizaCampos(formData):
            feedbackmsg="Éxito:\nLa información fue acutalizada."
        else:
            feedbackmsg="Érror:\nLa información no pudo actualizarse.\nVuelva a intentar"
    # Devuelve la consulta
    listaSolicitudes={}
    listaSolicitudes=routes_mesaAnalisis.getSolicitudesEnMesa(formData["ownerID"])
    listaSolicitudes=routes_mesaAnalisis.getMesaControl(formData,listaSolicitudes)
    listaSolicitudes=limpiarCamposInecesarios(config.camposMesaControl, listaSolicitudes)

    for idx, solicitud in enumerate(listaSolicitudes):
        listaSolicitudes[idx]=correctNumericFields(listaSolicitudes[idx])
        listaSolicitudes[idx]["diasTranscurridos"]=""
        if listaSolicitudes[idx]["fechaEntregaARiesgos"]!="":
            fechaEntregaARiesgos=listaSolicitudes[idx]["fechaEntregaARiesgos"]
            horaEntregaARiesgos=fechaEntregaARiesgos.split(" ")[1].split(":")[0]
            diaEntregaRiesgos=fechaEntregaARiesgos.split(" ")[0]
            anio=diaEntregaRiesgos.split("-")[0]
            mes=diaEntregaRiesgos.split("-")[1]
            dia=diaEntregaRiesgos.split("-")[2]
            if(int(horaEntregaARiesgos)>16):
                date_time_obj = datetime.datetime.strptime(diaEntregaRiesgos, '%Y-%m-%d')
                date_time_obj += datetime.timedelta(days=1)
                diaEntregaRiesgos=str(date_time_obj).split(" ")[0]
            listaSolicitudes[idx]["FechaAPartirDe"]=diaEntregaRiesgos
            fechaActual = str(datetime.date.today())
            diasTranscurridos=numpy.busday_count(diaEntregaRiesgos,fechaActual,weekmask=[1,1,1,1,1,1,1])-1
            if diasTranscurridos<0:
                diasTranscurridos=0
            listaSolicitudes[idx]["diasTranscurridos"]=str(diasTranscurridos)
            if diasTranscurridos>=config.estatusOrden[2][solicitud["solicitudEstatus"]]["diasMax"]:
                listaSolicitudes[idx]["bgcolor"]="#FF0000"
                listaSolicitudes[idx]["color"]="#FFFF00"
            else:
                listaSolicitudes[idx]["bgcolor"]="#FFFFFF"
                listaSolicitudes[idx]["color"]="#000000"

    listaSolicitudes=routes_solicitudes.limpiarDatosSensible(listaSolicitudes)
    exceptionArray=['ownerID','userName','name','userEstatus','region']
    analistas={}
    analistas=routes_users.getUsersByPuesto("ANALISTA DE RIESGOS", exceptionArray)
    analistas=list(filter(lambda d:  d["userEstatus"]=="Activo", analistas))

    listaSolicitudes=filtraPorAnalista(formData,listaSolicitudes,True)
    usuario=routes_users.getUser(formData["ownerID"])

    return render_template('mesaControl.html',
        viewName=viewName,
        menu=menu,
        listaSolicitudes=listaSolicitudes,
        lastUpdated='null',
        listaCamposFiltro=listaCamposSolicitud,
        user=usuario,
        analistas=analistas,
        feedbackalert=feedbackmsg,
        formData=formData
        )

@app.route('/historico', methods=['GET', 'POST'])
def solicitudesHistorico():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/HISTORICO: "+request.method + '\x1b[0m')
    viewName="Historico"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuHistorico' in formData:
        lastUpdated=formData['lastUpdatedmenuHistorico']
    data={}
    listaSolicitudes={}


    notRenderException=["solicitudNumeroControl",
                        "montoSolicitado","montoAutorizado","montoTransferencia",
                        "plazoSolicitado","plazoAutorizado",
                        "tasaAutorizada","tasaPolitica",
                        "tasaDeComision","tasaDeComisionPolitica",
                        "montoComision","montoComisionPolitica","tipoBuroCredito"]

    renderExceptions=[]
    for campo in campos.diccionarioCamposSolicitud:
        if campo["analisisRenderable"]=="true":
            if "class" in campo:
                    if campo["class"]=="roundInputCalc" or campo["class"]=="roundInputVerde":
                        if "value" in campo:
                            if campo["value"] not in notRenderException:
                                renderExceptions.append(campo["value"])

    if "filtroCriterio" in formData:
        data=routes_solicitudes.getsolicitudesByFilter(formData["ownerID"],formData["filtroCriterio"],formData["filtroValor"])
        if data['user']['acl']=="asesor" or  data['user']['acl']=="gerenteComercial":
            for idx, solicitud in enumerate(data['listaSolicitudes']):
                solicitud=data['listaSolicitudes'][idx]
                for campo in renderExceptions:
                    if campo in solicitud:
                        del solicitud[campo]
                data['listaSolicitudes'][idx]=solicitud
    else:
        data['user']=routes_users.getUser(formData["ownerID"])
        data['listaSolicitudes']=listaSolicitudes

    listaCamposUnicos=[]
    listaCamposSolicitudOrdenada=[]

    listaCamposSolicitud2=[]
    for idx, campo in enumerate(listaCamposSolicitud):
        campo["index_order"]=idx
        listaCamposSolicitud2.append(campo.copy())

    listaCamposSolicitudOrdenada=sorted(listaCamposSolicitud2, key=lambda k: (k['label'].upper()))
    for idx, campo in enumerate(listaCamposSolicitudOrdenada):
        if "value" in campo and "value" in listaCamposSolicitudOrdenada[idx-1]:
            if campo["value"]!=listaCamposSolicitudOrdenada[idx-1]["value"]:
                if campo["value"]=="solicitudNumeroControl":
                    campo["editRenderable"]="true"
                if campo["label"]!="":
                    listaCamposUnicos.append(campo.copy())

    listaCamposUnicos=sorted(listaCamposUnicos, key=lambda k: (k['index_order']))

    listaCamposFinal=[]
    for campo in listaCamposUnicos:
        if "addRenderable" in campo and campo["addRenderable"]=="true":
            campo["viewOrder"]=1
            listaCamposFinal.append(campo.copy())
        else:
            if "editRenderable" in campo and campo["editRenderable"]=="true":
                campo["viewOrder"]=1
                listaCamposFinal.append(campo.copy())
            else:
                if "revisionDocumentalRenderable" in campo and campo["revisionDocumentalRenderable"]=="true":
                    campo["viewOrder"]=2
                    listaCamposFinal.append(campo.copy())
                else:
                    if "analisisRenderable" in campo and campo["analisisRenderable"]=="true":
                        campo["viewOrder"]=3
                        listaCamposFinal.append(campo.copy())
                    else:
                        if "voboRenderable" in campo and campo["voboRenderable"]=="true":
                            campo["viewOrder"]=4
                            listaCamposFinal.append(campo.copy())
                        else:
                            if "clabeRenderable" in campo and campo["clabeRenderable"]=="true":
                                campo["viewOrder"]=5
                                listaCamposFinal.append(campo.copy())
                            else:
                                if "cobranzaRenderable" in campo and campo["cobranzaRenderable"]=="true":
                                    campo["viewOrder"]=6
                                    listaCamposFinal.append(campo.copy())
                                else:
                                    if "mesaAnalisisRenderable" in campo and campo["mesaAnalisisRenderable"]=="true":
                                        campo["viewOrder"]=7
                                        listaCamposFinal.append(campo.copy())

    listaCamposFinal=sorted(listaCamposFinal, key=lambda k: (k['index_order']))

    acl=data['user']['acl']
    aclRestricted=["asesor","gerenteComercial","gerenteCartera","supervisorContable"]

    for idx, campo in enumerate(listaCamposFinal):
        if acl in aclRestricted:
            if campo["value"] in renderExceptions:
                listaCamposFinal[idx]["addRenderable"]="false"
                listaCamposFinal[idx]["editRenderable"]="false"
                listaCamposFinal[idx]["revisionDocumentalRenderable"]="false"
                listaCamposFinal[idx]["analisisRenderable"]="false"
                listaCamposFinal[idx]["preAnalisisisRenderable"]="false"
                listaCamposFinal[idx]["mesaAnalisisisRenderable"]="false"
            if campo["value"]=="solicitudNumeroControl":
                listaCamposFinal[idx]["filterOption"]="true"
                listaCamposFinal[idx]["editRenderable"]="true"
                listaCamposFinal[idx]["class"]="roundInput"


    return render_template('historico.html',
        viewName=viewName,
        menu=menu,
        listaSolicitudes=data['listaSolicitudes'],
        listaCamposFiltro=listaCamposFinal,
        listaEmpresas = routes_empresas.getAsignacionEmpresas(),
        pagadoras=routes_pagadoras.getPagadorasList(formData["ownerID"])["list"],
        listaUsuarios = routes_users.getUsersList(),
        user=data['user'],
        feedback=data['user']['feedback'],
        lastUpdated=lastUpdated
        )

@app.route('/reporteCobranzaReferenciadaCSV',methods=['POST'])
def reporteCobranzaReferenciadaCSV():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SOLICITUDES/REPORTE DE COBRANZA REFERENCIADA: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    if(formData["accion"]=="Cobranza Referenciada"):
        data=routes_solicitudes.reporteCobranza(formData["ownerID"])
        data['user']=routes_users.getUser(formData["ownerID"])
        csv=routes_csv.jsontocsv(data["headers"],data["reporte"])
        return Response(csv,
            mimetype="text/csv",
            headers={"Content-disposition":
            "attachment; filename=CobranzaReferenciada.csv"})
    if(formData["accion"]=="Consultar"):
        return redirect(url_for('solicitudesCobranza'),code=307)


def renderSolicitudesList(data={},viewName=None,lastUpdated="null",formData={},listaCampos=None):
    if listaCampos==None:
        listaCamposFiltro=campos.diccionarioCamposSolicitud
    else:
        if viewName=="PreAnalisis":
            listaCamposFiltro=listaCampos

    feedbackalert=None
    if "feedbackalert" in formData:
        feedbackalert=formData["feedbackalert"]

    return render_template('solicitudes.html',
        viewName=viewName,
        menu=menu,
        listaSolicitudes=data['listaSolicitudes'],
        listaCamposFiltro=listaCamposFiltro,
        listaEmpresas = routes_empresas.getAsignacionEmpresas(),
        listaUsuarios= routes_users.getUsersList(),
        pagadoras=routes_pagadoras.getPagadorasList(formData["ownerID"])["list"],
        user=data['user'],
        feedback=data['user']['feedback'],
        feedbackalert=feedbackalert,
        lastUpdated=lastUpdated
        )



@app.route('/pipeline',methods=['GET', 'POST'])
def PipeLine():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " PIPELINE: "+request.method + '\x1b[0m')
    data={}
    viewName="PipeLine"
    formData=request.form.to_dict(flat=True)
    data=routes_solicitudes.getPipeLine(formData)
    return render_template('pipeline.html',
        viewName=viewName,
        menu=menu,
        pipelines=data['pipelines'],
        columnas=data['columnas'],
        lastUpdated='null',
        listaCamposFiltro=listaCamposSolicitud,
        listaEmpresas = routes_empresas.getAsignacionEmpresas(),
        user=data['user'],
        formData=formData

        )

@app.route('/scorecard',methods=['GET', 'POST'])
def scorecard():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SCORECARD: "+request.method + '\x1b[0m')
    data={}
    viewName="ScoreCard"
    formData=request.form.to_dict(flat=True)
    data=routes_solicitudes.getScoreCard(formData)
    return render_template('scorecard.html',
        viewName=viewName,
        menu=menu,
        scorecards=data['scorecards'],
        lastUpdated='null',
        listaCamposFiltro=listaCamposSolicitud,
        listaEmpresas = routes_empresas.getAsignacionEmpresas(),
        user=data['user'],
        formData=formData

        )




# **********************************************************
#               <-- RUTAS PARA SOLICITUDES
# **********************************************************


# **********************************************************
#                   RUTAS PARA USUARIOS -->
# **********************************************************
def usuarios(ownerID=None,lastUpdated="null"):
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " USUARIOS: "+request.method + '\x1b[0m')
    data={}
    data=routes_users.getUsers(ownerID)
    return render_template('usuarios.html',
        viewName="Usuarios",
        menu=menu,
        listaUsuarios=data['listaUsuarios'],
        listaCamposFiltro=listaCamposUsuarios,
        lastUpdated=lastUpdated,
        user=data['user']
        )

@app.route('/usuarios',methods=['GET', 'POST'])
def usuariosList():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " USUARIOS/List: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    ownerID=formData["ownerID"]
    lastUpdated="null"
    if 'lastUpdatedmenuUsuarios' in formData:
        lastUpdated=formData['lastUpdatedmenuUsuarios'];
    return usuarios(ownerID, lastUpdated)

@app.route('/usuarios/add', methods=['POST'])
def usuariosAdd():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " USUARIOS/Add: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True);
    update.addData("",formData)
    return redirect(url_for('usuariosList'),code=307)

@app.route('/perfil', methods=['POST'])
def usuariosPerfil():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " USUARIOS/Perfil: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    ownerID=formData["ownerID"]
    data={}
    data=routes_users.getUserProfile(ownerID)
    return render_template('usuarios.html',
        viewName="Perfil de Usuario",
        menu=menu,
        listaUsuarios=data['listaUsuarios'],
        listaCamposFiltro=listaCamposUsuarios,
        user=data['user']
        )

# **********************************************************
#               <-- RUTAS PARA USUARIOS
# **********************************************************

# **********************************************************
#                   RUTAS PARA ACL -->
# **********************************************************

@app.route('/acl', methods=['POST'])
def ACL():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " ACL: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    ownerID=formData["ownerID"]

    data={}
    data=routes_acl.getACLList(ownerID)

    if "acl" in formData:
        if formData["acl"] =="":
            return render_template('acl.html',
            viewName="ACL",
            menu=menu,
            listaACL=data['list'],
            user=data['user']
            )
        else:
            data=routes_acl.saveACLList(formData["ownerID"],formData["acl"])



    return render_template('acl.html',
        viewName="ACL",
        menu=menu,
        listaACL=data['list'],
        user=data['user']
        )

# **********************************************************
#               <-- RUTAS PARA ACL
# **********************************************************

# **********************************************************
#                   RUTAS PARA PAGADORAS -->
# **********************************************************

@app.route('/pagadoras', methods=['POST'])
def pagadoras():
    import routes_pagadoras
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " PAGADORAS: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    ownerID=formData["ownerID"]

    data={}
    data=routes_pagadoras.getPagadorasList(ownerID)


    if ("accion" in formData and
        formData["accion"]=="Guardar"):
        if formData["contenido"] =="":
            return render_template('pagadoras.html',
            viewName="Pagadoras",
            menu=menu,
            contenido=data['list'],
            user=data['user']
            )
        else:
            data=routes_pagadoras.savePagadorasList(formData["ownerID"],formData)



    return render_template('pagadoras.html',
        viewName="Pagadoras",
        menu=menu,
        contenido=data['list'],
        user=data['user']
        )

# **********************************************************
#               <-- RUTAS PARA PAGADORAS
# **********************************************************

# **********************************************************
#                   RUTAS PARA EMPRESAS -->
# **********************************************************

# BACKEND ENDPOINTS
@app.route('/data/correctempresas/',methods=['GET', 'POST'])
def dataCorrectEmpresas():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " DATA/CORRECTEMPRESAS: "+request.method + '\x1b[0m')
    data={}
    data=routes_empresas.correctEmpresasData()
    return data


# FRONTEND ENDPOINTS

def empresas(ownerID=None,lastUpdated="null"):
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " EMPRESAS: "+request.method + '\x1b[0m')
    data={}
    data=routes_empresas.getEmpresas(ownerID)
    return render_template('empresas.html',
        viewName="Empresas",
        menu=menu,
        listaEmpresas=data['listaEmpresas'],
        listaAsesores=data['listaAsesores'],
        listaCamposFiltro=listaCamposEmpresas,
        pagadoras=routes_pagadoras.getPagadorasList(ownerID)["list"],
        lastUpdated=lastUpdated,
        user=data['user']
        )

@app.route('/empresas',methods=['GET', 'POST'])
def empresasList():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " EMPRESAS/List: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    ownerID=formData["ownerID"]
    lastUpdated="null"
    if 'lastUpdatedmenuEmpresas' in formData:
        lastUpdated=formData['lastUpdatedmenuEmpresas'];
    return empresas(ownerID,lastUpdated)


@app.route('/empresas/add',methods=['POST'])
def empresasAdd():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " EMPRESAS/ADD: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    update.addData("",formData)
    return redirect(url_for('empresasList'),code=307)


@app.route('/asignaciones',methods=['GET', 'POST'])
def asignaciones():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " ASIGNACIONES/List: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    ownerID=formData["ownerID"]
    lastUpdated="null"
    if 'lastUpdatedmenuAsignaciones' in formData:
        lastUpdated=formData['lastUpdatedmenuAsignaciones'];
    data={}
    data=routes_empresas.getEmpresas(ownerID)

    asesores={}
    asesores=routes_users.getUsers(ownerID)['listaUsuarios']
    asesores=list(filter(lambda d:  d["acl"]=="asesor" and d["userEstatus"]=="Activo", asesores))

    return render_template('asignaciones.html',
        viewName="Asignaciones",
        menu=menu,
        listaEmpresas=data['listaEmpresas'],
        listaUsuarios=asesores,
        listaCamposFiltro=listaCamposEmpresas,
        lastUpdated=lastUpdated,
        user=data['user']
        )



# @app.route('/usuarios/add', methods=['POST'])
# def usuariosAdd():
#     print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " USUARIOS/Add: "+request.method + '\x1b[0m')
#     formData=request.form.to_dict(flat=True);
#     update.addData("",formData)
#     return redirect(url_for('usuariosList'),code=307)

# @app.route('/perfil', methods=['POST'])
# def usuariosPerfil():
#     print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " USUARIOS/Perfil: "+request.method + '\x1b[0m')
#     formData=request.form.to_dict(flat=True)
#     ownerID=formData["ownerID"]
#     data={}
#     data=routes_users.getUserProfile(ownerID)
#     return render_template('usuarios.html',
#         viewName="Perfil de Usuario",
#         menu=menu,
#         listaUsuarios=data['listaUsuarios'],
#         listaCamposFiltro=listaCamposUsuarios,
#         user=data['user']
#         )

# **********************************************************
#               <-- RUTAS PARA EMPRESAS
# **********************************************************

# **********************************************************
#                   RUTAS PARA LOGS -->
# **********************************************************
# BACKEND ENDPOINTS
@app.route('/data/correctlogs/',methods=['GET', 'POST'])
def dataCorrectLogs():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " DATA/CORRECTLOGS: "+request.method + '\x1b[0m')
    data={}
    data=routes_logs.correctLogsData()
    return data
# FRONTEND ENDPOINTS

def logs(formData,ownerID=None,lastUpdated="null"):
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " LOGS: "+request.method + '\x1b[0m')
    data={}
    data=routes_logs.getLogs(ownerID,formData)
    return render_template('logs.html',
        viewName="Logs",
        menu=menu,
        formData=formData,
        listaLogs=data['listaLogs'],
        listaCamposFiltro=listaCamposLogs,
        lastUpdated=lastUpdated,
        user=data['user']
        )

@app.route('/logs',methods=['GET', 'POST'])
def logsList():
    import datetime
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " LOGS/List: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)

    if 'fechaInicio' not in formData:
        hoy=datetime.date.today()
        dInicio='{:02d}'.format(1)
        mInicio='{:02d}'.format(hoy.month-1)
        yInicio=hoy.year
        inicio=str(yInicio)+"-"+str(mInicio)+"-"+str(dInicio)
        formData['fechaInicio']=inicio

    ownerID=formData["ownerID"]
    lastUpdated="null"
    if 'lastUpdatedmenuLogs' in formData:
        lastUpdated=formData['lastUpdatedmenuLogs'];
    return logs(formData,ownerID,lastUpdated)

@app.route('/sesiones',methods=['GET', 'POST'])
def sesionsList():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SESIONES/List: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    ownerID=formData["ownerID"]
    lastUpdated="null"
    if 'lastUpdatedmenuSesiones' in formData:
        lastUpdated=formData['lastUpdatedmenuSesiones'];

    data=routes_logs.getLogins(ownerID)
    return render_template('sesiones.html',
        viewName="Sesiones",
        menu=menu,
        listaLogs=data['sesiones'],
        listaCamposFiltro=listaCamposSesiones,
        lastUpdated=lastUpdated,
        user=data['user']
        )

# **********************************************************
#               <-- RUTAS PARA LOGS
# **********************************************************

# **********************************************************
#                   RUTAS PARA OPERACIONES INTERNAS PREOCUPANTES -->
# **********************************************************
@app.route('/reporteOIP',methods=['GET', 'POST'])
def roipsList():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " ROIPS: "+request.method + '\x1b[0m')
    estatus="ENTREGA A RIESGOS"
    viewName="Operaciones Internas Preocupantes"
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if 'lastUpdatedmenuOIP' in formData:
        lastUpdated=formData['lastUpdatedmenuOIP'];
    data={}
    data=routes_ROIP.getReportesOperacionesInternasPreocupantes(formData["ownerID"])
    listaSolicitudes={}
    return render_template('roips.html',
        viewName=viewName,
        menu=menu,
        listaSolicitudes=data['listaSolicitudes'],
        listaCamposFiltro=listaCamposOperacionesInusuales,
        user=data['user'],
        feedback=data['user']['feedback'],
        lastUpdated=lastUpdated
        )
@app.route('/reporteOIP/add',methods=['POST'])
def roipsAdd():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " ROIPS/ADD: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    update.addData("",formData)
    return redirect(url_for('roipsList'),code=307)

# **********************************************************
#               <-- RUTAS PARA OPERACIONES INTERNAS PREOCUPANTES
# **********************************************************

# **********************************************************
#                   RUTAS PARA CORREOS -->
# **********************************************************

@app.route('/correos/send',methods=['POST'])
def correosSend():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " CORREOS/SEND: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    result=routes_correos.enviarCorreo(formData)
    return result
    # return render_template('empresas.html',
    #     viewName="Empresas",
    #     menu=menu,
    #     listaEmpresas=data['listaEmpresas'],
    #     listaAsesores=data['listaAsesores'],
    #     listaCamposFiltro=listaCamposEmpresas,
    #     user=data['user']
    #     )


# **********************************************************
#               <-- RUTAS PARA CORREOS
# **********************************************************

# **********************************************************
#                   RUTAS PARA REPORTE DE VENTAS -->
# **********************************************************
@app.route('/reporteVentas',methods=['POST'])
def reporteVentas():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " REPORTE DE VENTAS: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    data=routes_solicitudes.reporteVentas(formData)
    lastUpdated="null"
    data['user']=routes_users.getUser(formData["ownerID"])
    return render_template('reporteVentas.html',
        viewName="Reporte de Ventas",
        menu=menu,
        headers=data["headers"],
        listaRegistros=data["reporte"],
        listaCamposFiltro=listaCamposReporteVentas,
        lastUpdated=lastUpdated,
        user=data['user'],
        formData=formData
        )

@app.route('/reporteVentasCSV',methods=['POST'])
def reporteVentasCSV():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " REPORTE DE VENTAS: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    lastUpdated="null"
    if(formData["accion"]=="Descargar"):
        data=routes_solicitudes.reporteVentas(formData)
        data['user']=routes_users.getUser(formData["ownerID"])
        csv=routes_csv.jsontocsv(data["headers"],data["reporte"])
        return Response(csv,
            mimetype="text/csv",
            headers={"Content-disposition":
            "attachment; filename=ReportedeVentas.csv"})
    if(formData["accion"]=="Consultar"):
        return redirect(url_for('reporteVentas'),code=307)


# **********************************************************
#               <-- RUTAS PARA REPORTE DE VENTAS
# **********************************************************

# **********************************************************
#                   RUTAS PARA SIMULADOR EN LINEA-->
# **********************************************************

@app.route('/simulador',methods=['GET','POST'])
def simulador():
    from datetime import datetime
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " SIMULADOR: "+request.method + '\x1b[0m')
    data={}
    viewName="Simulador"
    formData=request.form.to_dict(flat=True)
    if("tipoConvenio" in formData):
        data=routes_simulador.getSimulacion(formData)
    if("seguro" not in formData):
        data["seguro"]="25000"
    data["maxDate"]=datetime.today().strftime('%Y-%m-%d')
    data['user']=routes_users.getUser(formData["ownerID"])
    return render_template('simulador.html',
        viewName=viewName,
        menu=menu,
        lastUpdated='null',
        user=data['user'],
        responseData=data
        )



# **********************************************************
#                <-- RUTAS PARA SIMULADOR EN LINEA
# **********************************************************

# **********************************************************
#                   RUTAS PARA REPORTE DE COLOCACION-->
# **********************************************************
@app.route('/colocacion',methods=['GET','POST'])
def colocacion():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " COLOCACION: "+request.method + '\x1b[0m')
    data={}
    viewName="Colocación"
    formData=request.form.to_dict(flat=True)
    if ("accion" not in formData):
        formData["accion"]="Graficar"

    if formData["accion"]=="Graficar":
        if "frecuencia" not in formData:
            formData["frecuencia"]="1"
        data=routes_solicitudes.getColocacion(formData)

    if formData["accion"]=="Tabular":
        formData['frecuencia']="1"
        data=routes_solicitudes.getTabularColocacion(formData)


    if "accion" in formData and formData["accion"]=="Subir Colocacion.csv":
        print(formData["accion"])

    return render_template('colocacion.html',
        viewName=viewName,
        menu=menu,
        series=data['series'],
        etiquetas=data['etiquetas'],
        productos=data['productos'],
        headers=data['headers'],
        listaAsesores=data['asesores'],
        seguros=data['seguros'],
        accion=formData['accion'],
        lastUpdated='null',
        listaCamposFiltro=listaCamposSolicitud,
        user=data['user'],
        formData=formData
        )



# **********************************************************
#                <-- RUTAS PARA REPORTE DE COLOCACION
# **********************************************************

# **********************************************************
#                   RUTAS PARA REPORTE DE CUMPLIMIENTO-->
# **********************************************************
@app.route('/cumplimiento',methods=['GET','POST'])
def cumplimiento():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " CUMPLIMIENTO: "+request.method + '\x1b[0m')
    data={}
    viewName="Cumplimiento"
    formData=request.form.to_dict(flat=True)

    if ("accion" not in formData):
        # formData["accion"]="Tabular Cumplimiento"
        formData["accion"]="Excepciones a Políticas"

    if formData["accion"]=="Excepciones a Políticas":
        formData['frecuencia']="1"
        data=routes_solicitudes.getTabularColocacion(formData)
        formData=data['formData']
        plantillaHTML='excepciones.html'

    if formData["accion"]=="Expedientes Faltantes":
        formData['frecuencia']="1"
        data=routes_solicitudes.getTabularColocacion(formData)
        formData=data['formData']

        plantillaHTML='expedientesFaltantes.html'


    return render_template(plantillaHTML,
        viewName=viewName,
        menu=menu,
        series=data['series'],
        anios=data['años'],
        etiquetas=data['etiquetas'],
        productos=data['productos'],
        headers=data['headers'],
        listaAsesores=data['asesores'],
        resumenProducto=data['resumenProducto'],
        resumenAsesor=data['resumenAsesor'],
        resumenEntregados=data["resumenEntregados"],
        seguros=data['seguros'],
        accion=formData['accion'],
        lastUpdated='null',
        listaCamposFiltro=listaCamposSolicitud,
        user=data['user'],
        formData=formData
        )



# **********************************************************
#                <-- RUTAS PARA REPORTE DE COLOCACION
# **********************************************************

# **********************************************************
#                 RUTAS PARA REPORTES DE TEXTO -->
# **********************************************************

@app.route('/reporteDeTexto',methods=['GET','POST'])
def reporteDeTexto():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " REPORT DE TEXTO: "+request.method + '\x1b[0m')
    data={}
    listanombresCamposSolicitud=[]
    camposUnicos={}


    for campo in listaCamposSolicitud:
        campoActual={}
        if "value" in campo:
            campoActual["value"]=campo["value"]
            campoActual["label"]=campo["label"]
            if campo["label"]=="":
                campoActual["label"]=campo["value"]

            if ("FECHA" in campoActual["value"].upper() and
                "fecha" not in  campoActual["label"].upper()):
                campoActual["label"]="Fecha "+campoActual["label"]

            if ("CLIENTE" in campoActual["value"].upper() and
                "CLIENTE" not in  campoActual["label"].upper()):
                campoActual["label"]="Cliente "+campoActual["label"]

            if ("SOLICITUD" in campoActual["value"].upper() and
                "SOLICITUD" not in  campoActual["label"].upper()):
                campoActual["label"]="Solicitud "+campoActual["label"]

            campoActual["label"]=campoActual["label"].title()
            if "Dg" in campoActual["label"]:
                campoActual["label"]=campoActual["label"].replace("Dg", "DG")

            if campoActual not in listanombresCamposSolicitud:
                listanombresCamposSolicitud.append(campoActual.copy())

    listanombresCamposSolicitud=sorted(listanombresCamposSolicitud, key=lambda k: (k['label'].upper()))
    camposUnicos["Solicitudes"]=listanombresCamposSolicitud



    listanombresCamposSolicitud=[]
    for campo in listaCamposEmpresas:
        campoActual={}
        if "value" in campo:
            campoActual["value"]=campo["value"]
            campoActual["label"]=campo["label"]
            if campo["label"]=="":
                campoActual["label"]=campo["value"]

            if ("FECHA" in campoActual["value"].upper() and
                "fecha" not in  campoActual["label"].upper()):
                campoActual["label"]="Fecha "+campoActual["label"]

            if ("CLIENTE" in campoActual["value"].upper() and
                "CLIENTE" not in  campoActual["label"].upper()):
                campoActual["label"]="Cliente "+campoActual["label"]

            if ("SOLICITUD" in campoActual["value"].upper() and
                "SOLICITUD" not in  campoActual["label"].upper()):
                campoActual["label"]="Solicitud "+campoActual["label"]

            campoActual["label"]=campoActual["label"].title()
            if "Dg" in campoActual["label"]:
                campoActual["label"]=campoActual["label"].replace("Dg", "DG")

            if campoActual not in listanombresCamposSolicitud:
                listanombresCamposSolicitud.append(campoActual.copy())

    listanombresCamposSolicitud=sorted(listanombresCamposSolicitud, key=lambda k: (k['label'].upper()))

    camposUnicos["Empresas"]=listanombresCamposSolicitud

    listanombresCamposSolicitud=[]
    for campo in listaCamposAgendas:
        campoActual={}
        if "value" in campo:
            campoActual["value"]=campo["value"]
            campoActual["label"]=campo["label"]
            if campo["label"]=="":
                campoActual["label"]=campo["value"]

            campoActual["label"]=campoActual["label"].title()

            if campoActual not in listanombresCamposSolicitud:
                listanombresCamposSolicitud.append(campoActual.copy())

    listanombresCamposSolicitud=sorted(listanombresCamposSolicitud, key=lambda k: (k['label'].upper()))

    camposUnicos["Agendas"]=listanombresCamposSolicitud


    viewName="Reporte de Texto"
    formData=request.form.to_dict(flat=True)


    if "accion" in formData:
        contenido=""
        if formData["accion"]=="Descargar":
            if formData["viewName"]=="Transferencias":
                import plantillasReporteTexto
                plantilla=plantillasReporteTexto.transferencias[0]
                plantilla["ownerID"]=formData["ownerID"]
                data=routes_solicitudes.reporteTexto(plantilla)
                for registro in data["reporte"]:
                    registro["Monto Autorizado ($)"]='${:0,.2f}'.format(float(registro["Monto Autorizado ($)"]))
                    registro["Monto Transferencia ($)"]='${:0,.2f}'.format(float(registro["Monto Transferencia ($)"]))
                    contenido=routes_csv.jsontotxt(data["headers"],data["reporte"],",")

            if formData["viewName"]=="Reporte de Texto":
                if formData["catalogo"]=="Solicitudes":
                    data=routes_solicitudes.reporteTexto(formData)
                if formData["catalogo"]=="Empresas":
                    data=routes_empresas.reporteTexto(formData)
                if formData["catalogo"]=="Agendas":
                    data=routes_agendas.reporteTexto(formData)
                contenido=routes_csv.jsontocsv(data["headers"],data["reporte"])

            return Response(contenido,
                mimetype="text/csv",
                headers={"Content-disposition":
                "attachment; filename=ReporteTexto.csv"})

    data['user']=routes_users.getUser(formData["ownerID"])

    return render_template('reporteTexto.html',
        viewName=viewName,
        menu=menu,
        lastUpdated='null',
        user=data['user'],
        formData=formData,
        camposUnicos=camposUnicos
        )

# **********************************************************
#                 RUTAS PARA REPORTES DE TEXTO <--
# **********************************************************
# **********************************************************
#                   RUTAS PARA DESCARGAR BACKUPS-->
# **********************************************************

@app.route('/backups',methods=['GET','POST'])
def backups():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " BACKUPS: "+request.method + '\x1b[0m')
    data={}
    viewName="BackUps"
    formData=request.form.to_dict(flat=True)

    workingDir="/home/pipeenlinea/"

    if "delete" in formData:

        fileName=workingDir+'working/backup/'+formData['delete']
        # fileName='/home/fdavmares/working/backup/'+formData['delete']  # Para servidor fdavmares
        fileName='/home/pipeenlinea/working/backup/'+formData['delete'] #Para servidor pipeenlinea

        if os.path.exists(fileName):
            os.remove(fileName)

    if "backup" in formData:
        return send_file(workingDir+'working/backup/'+formData['backup'],
            attachment_filename=formData['backup'],
            as_attachment=True)
    data['backups']=routes_downloadDbBkup.getBackUpFiles()
    data['user']=routes_users.getUser(formData["ownerID"])

    return render_template('backups.html',
        viewName=viewName,
        menu=menu,
        lastUpdated='null',
        user=data['user'],
        backups=data['backups']['archivos']
        )




# **********************************************************
#                <-- RUTAS PARA DESCARGAR BACKUPS
# **********************************************************


# **********************************************************
#                   RUTAS PARA SUBIR ARCHIVOS-->
# **********************************************************
@app.route('/uploadFile',methods=['GET','POST'])
def uploadFile():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " UPLOADFILE: "+request.method + '\x1b[0m')
    data={}

    formData=request.form.to_dict(flat=True)
    viewName=formData("viewName")
    templates={
    "Cosechas":"cosechas.html",
    "Pagos":"pagos.html"
    }
    viewNameTemplate=templates[viewName]
    workingDir="/home/pipeenlinea/working/uploads/"



    return render_template(viewNameTemplate,
        viewName=viewName,
        menu=menu,
        lastUpdated='null',
        user=data['user']
        )

# **********************************************************
#                <-- RUTAS PARA SUBIR ARCHIVOS
# **********************************************************


# **********************************************************
#                   RUTAS PARA COSECHAS-->
# **********************************************************

@app.route('/cosechas',methods=['GET', 'POST'])
def cosechas():
    import routes_csv, routes_cosechas
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " COSECHAS: "+request.method + '\x1b[0m')
    data={}
    viewName="Cosechas"
    feedbackmsg=""
    uploadsDir="uploads/"
    formData=request.form.to_dict(flat=True)
    if ('archivo' in request.files and
        'accion' not in formData):
        archivo=request.files['archivo']
        fileName=archivo.filename
        if(fileName)=="":
            feedbackmsg="Archivo no seleccionado."

        if(fileName)!="":
            fileName = secure_filename(fileName)
            fileName = uploadsDir + fileName
            fileExt=fileName.split(".").pop()
            if fileExt.lower()=="csv":
                archivo.save(fileName)
                csvData=esperarYLeerArchivo(fileName)
                if csvData==False:
                    feedbackmsg="No se pudo leer el archivo: "+fileName
                else:
                    jsonData=[]
                    jsonData=routes_csv.csvtojson(csvData.decode("utf-8"))
                    if routes_cosechas.actualizarCosechas(jsonData):
                        feedbackmsg="La información de cosechas ha sido actualizada."
                    else:
                        feedbackmsg="Error: Algo sucedió y las cosechas no fueron actualizadas."


            else:
                feedbackmsg="Archivo inválido.  Se requiere un archivo 'csv'"


    # print(json.dumps(request.form,indent=4))

    if ("producto" not in formData or
        formData['producto']==""):
        formData['producto']="General"

    if ("contenidoTipo" not in formData or
        formData['contenidoTipo']==""):
        formData['contenidoTipo']="Total Vencido"

    if ("accion" not in formData):
        formData["accion"]="Tabular Periodo/Otorgamiento"

    if formData["accion"]=="Graficar":
        data=routes_cosechas.getGraficaCosechas(formData)


    if "Tabular" in formData["accion"]:
        data=routes_cosechas.getTabularCosechas(formData)

    if "csv" in formData["accion"]:
        data=routes_cosechas.getTabularCosechas(formData)
        csv=routes_csv.cosechastocsv(data,formData)
        return Response(csv,
                mimetype="text/csv",
                headers={"Content-disposition":
                "attachment; filename=Reporte_Cosechas.csv"})

    usuario=routes_users.getUser(formData["ownerID"])

    return render_template('cosechas.html',
        viewName=viewName,
        menu=menu,
        accion=formData['accion'],
        lastUpdated='null',
        listaCamposFiltro=listaCamposSolicitud,
        user=usuario,
        feedbackalert=feedbackmsg,
        reporte=data,
        formData=formData
        )

# **********************************************************
#                <-- RUTAS PARA COSECHAS
# **********************************************************

# **********************************************************
#          RUTAS PARA REGISTRAR GEOLOCALIZACION-->
# **********************************************************
def visitas(formData):
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " VISITAS: "+request.method + '\x1b[0m')
    data={}
    data=routes_visitas.getVisitas(formData)
    return data

@app.route('/geoLocalizar',methods=['GET','POST'])
def geoLocalizar():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " GEOLOCALIZAR: "+request.method + '\x1b[0m')
    data={}
    viewName="Geolocalizacion"
    formData=request.form.to_dict(flat=True)
    data['user']=routes_users.getUser(formData["ownerID"])
    if "coords" not in formData:
        return render_template('geoLocation.html',
            viewName=viewName,
            menu=menu,
            lastUpdated='null',
            user=data['user']
            )
    else:
        response=update.addData("",formData)
        return redirect(url_for('solicitudesList'),code=307)

@app.route('/visitas',methods=['GET','POST'])
def visitasList():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " VISITAS/List: "+request.method + '\x1b[0m')
    data={}
    viewName="Visitas"
    formData=request.form.to_dict(flat=True)
    ownerID=formData["ownerID"]
    lastUpdated="null"
    data=visitas(formData)
    if "accion" not in formData:
        return render_template('visitas.html',
            viewName=viewName,
            menu=menu,
            lastUpdated=lastUpdated,
            user=data['user'],
            headers=data["headers"],
            listaRegistros=data['listaVisitas'],
            formData=formData
            )

    if(formData["accion"]=="Consultar"):
        return render_template('visitas.html',
            viewName=viewName,
            menu=menu,
            lastUpdated=lastUpdated,
            user=data['user'],
            headers=data["headers"],
            listaRegistros=data['listaVisitas'],
            formData=formData
            )

    if(formData["accion"]=="Descargar"):
        data=visitas(formData)
        csv=routes_csv.jsontocsv(data["headers"],data["listaVisitas"])
        return Response(csv,
            mimetype="text/csv",
            headers={"Content-disposition":
            "attachment; filename=ReportedeVisitas.csv"})




# **********************************************************
#          <-- RUTAS PARA REGISTRAR GEOLOCALIZACION
# **********************************************************

# **********************************************************
#                   RUTAS PARA AGENDAS -->
# **********************************************************
@app.route('/agendas',methods=['GET', 'POST'])
def agendas():
    if app.debug:
        print('\x1b[6;30;42m' + "               "+ '\x1b[0m' +'\033[92m' + " AGENDAS/List: "+request.method + '\x1b[0m')
    formData=request.form.to_dict(flat=True)
    ownerID=formData["ownerID"]
    lastUpdated="null"
    if 'lastUpdatedmenuAgendas' in formData:
        lastUpdated=formData['lastUpdatedmenuAgendas'];
    data={}

    data=routes_agendas.getAgendas(ownerID,formData)

    return render_template('agendas.html',
        viewName="Agendas",
        menu=menu,
        listaEmpresas=routes_empresas.getAsignacionEmpresas(),
        listaCitas=data["citas"],
        listaUsuarios=data["asesores"],
        listaCamposFiltro=listaCamposAgendas,
        diasAgenda=data["diasAgenda"],
        lastUpdated=lastUpdated,
        formData=data["formData"],
        user=data['user']
        )
# **********************************************************
#               <-- RUTAS PARA AGENDAS
# **********************************************************

# **********************************************************
#           FUNCIONES DE MISCELANEA ---->
# **********************************************************

def correctNumericFields(newData):
    for field in newData:
        if field in config.camposNumericos:
            numberStr=""
            for c in newData[field]:
                if(c.isdigit or c=="."):
                    numberStr  = numberStr +c
            numberStr=numberStr.replace(",", "")
            resultantValue=numberStr.replace('.', '', 1).isdigit()
            if not resultantValue:
                 numberStr="0.00"
            if numberStr=="":
                numberStr="0.00"
            newData[field]="{0:.2f}".format(float(numberStr))
    return newData

def deleteForbiddenFields(data):
    user=routes_users.getUser(data['ownerID'])
    for field in user["forbidden"]:
        if field in data:
           del data[field]
    return data

def deleteCheckBoxes(data):
    checkBoxes=[]
    for field in data:
        if "check_" in field:
            checkBoxes.append(field)
    for field in checkBoxes:
        del data[field]
    return data

def secure_filename(fileName=""):
    fileExt=fileName.split(".").pop()
    fileName=fileName.replace(".","").replace(" ","_")
    fileName = ''.join(ch for ch in fileName if (ch.isalnum() or ch=="_"))
    fileName=fileName.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ü","u")
    fileName=fileName.replace(fileExt,"."+fileExt)
    return fileName

def esperarYLeerArchivo(fileName=""):
    import time
    while not os.path.exists(fileName):
        print(fileName+ " ...Sigo eperando al archivo... ")
        time.sleep(1)

    if os.path.isfile(fileName):
        with open(fileName,'rb') as f:
            data = f.read()
            f.close()
        return data
    else:
        return False

def limpiarCamposInecesarios(camposNecesarios, solicitudes):
    for idx, solicitud in enumerate(solicitudes):
        solicitudLimpia={}
        for campo in camposNecesarios:
            solicitudLimpia[campo]=""
            if campo in solicitud:
                solicitudLimpia[campo]=solicitud[campo]
                if campo =="comentarios":
                    solicitudLimpia[campo]=solicitud[campo].strip()
        solicitudes[idx]=solicitudLimpia


    return solicitudes

def filtraPorAnalista(formData,listaSolicitudes,incluirVacios=False):
    usuario=routes_users.getUser(formData["ownerID"])
    for solicitud in listaSolicitudes:
        if "analistaNombre" not in solicitud:
            solicitud['analistaNombre']=""
    if incluirVacios:
        if usuario["puesto"].lower()=="analista de riesgos":
            listaSolicitudes=list(filter(lambda d:  d["analistaNombre"]==usuario['userName'] or
                                                    d["analistaNombre"]=="", listaSolicitudes))
    else:
        if usuario["puesto"].lower()=="analista de riesgos":
            listaSolicitudes=list(filter(lambda d:  d["analistaNombre"]==usuario['userName'],
                                                    listaSolicitudes))

    return listaSolicitudes

def filtraPorEstatusContrato(formData,listaSolicitudes,contratoOK=False):
    usuario=routes_users.getUser(formData["ownerID"])
    for solicitud in listaSolicitudes:
        if "contratoDocumento" not in solicitud:
            solicitud['contratoDocumento']=""
        if solicitud["contratoDocumento"]=="No Cumple":
            solicitud["color"]="#FFFFFF"
            solicitud["bgcolor"]="#FF0000"
        if solicitud["contratoDocumento"]=="Ok":
            solicitud["color"]="#000000"
            solicitud["bgcolor"]="#00FF00"
    if contratoOK==False:
        listaSolicitudes=list(filter(lambda d:  d["contratoDocumento"]!='Ok', listaSolicitudes))
    if contratoOK==True:
        listaSolicitudes=list(filter(lambda d:  d["contratoDocumento"]=='Ok', listaSolicitudes))

    return listaSolicitudes

def days_between(d1, d2):
    from datetime import datetime
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

# **********************************************************
#          <------ FUNCIONES DE MISCELANEA
# **********************************************************


# Add an error handler that reports exceptions to Stackdriver Error
# Reporting. Note that this error handler is only used when debug
# is False
@app.errorhandler(500)
def server_error(e):
    client = error_reporting.Client()
    client.report_exception(
        http_context=error_reporting.build_flask_context(request))
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


# This is only used when running locally. When running live, gunicorn runs
# the application.
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
    # para que se pueda ver desde una red externa el puerto debe ser 8000
    # app.run(host='192.168.1.69', port=8000, debug=True)
    ALLOWED_HOSTS = ['*']



