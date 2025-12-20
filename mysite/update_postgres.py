# -*- coding: utf-8 -*-
"""
Versión híbrida de update.py que lee de PostgreSQL primero,
y JSON como fallback si no encuentra datos.
"""
import fcntl
import json
import hashlib
import shutil
import os, binascii
from flask import jsonify,current_app
from datetime import datetime
from cryptography.fernet import Fernet

from routes_users import getUser
from routes_solicitudes import getSolicitudById
import routes_empresas
import config
import routes_analisis as analisis

# Importar módulo de database PostgreSQL
try:
    from database import execute_query, get_db_cursor, initialize_pool
    POSTGRES_AVAILABLE = True
    # Inicializar pool de conexiones al importar el módulo
    print("🔌 Inicializando pool de conexiones PostgreSQL...")
    if not initialize_pool():
        print("⚠️  No se pudo inicializar pool de PostgreSQL, usando JSON")
        POSTGRES_AVAILABLE = False
    else:
        print("✅ Pool de conexiones PostgreSQL inicializado correctamente")
except ImportError:
    POSTGRES_AVAILABLE = False
    print("⚠️  Módulo database.py no encontrado, usando solo JSON")
except Exception as e:
    POSTGRES_AVAILABLE = False
    print(f"⚠️  Error inicializando PostgreSQL: {e}, usando JSON")


# ============================================================================
# Mapeo de archivos JSON a tablas PostgreSQL
# ============================================================================
FILE_TO_TABLE_MAP = {
    'working/users.json': 'usuarios',
    'working/empresas.json': 'empresas',
    'working/solicitudes.json': 'solicitudes',
    'working/logs.json': 'logs',
    'working/cosechas.json': 'cosechas',
    'working/geolocations.json': 'geolocalizaciones',
    'working/acl.json': 'acl',
    'working/agendas.json': 'agendas',
    'working/pagadoras.json': 'pagadoras',
    'working/roips.json': 'operaciones_internas_preocupantes',
}


# ============================================================================
# Funciones de encriptación/desencriptación (mantenidas del original)
# ============================================================================
def generate_key():
    """Generates a key and save it into a file"""
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    """Loads the key named `secret.key` from the current directory."""
    return open("secret.key", "rb").read()

def encrypt_file(fileName):
    """Encrypts a message"""
    key = load_key()
    with open(fileName,'rb') as f:
        data = f.read()
    fernet = Fernet(key)
    encrypted=fernet.encrypt(data)
    with open(fileName,'wb') as f:
        f.write(encrypted)
        f.close()
    return

def decrypt_file(encrypted_data):
    """Decrypts an encrypted message"""
    key = load_key()
    f = Fernet(key)
    try:
        decrypted_data = f.decrypt(encrypted_data)
    except:
        return None
    json_str=decrypted_data.decode('utf-8')
    json_object= json.loads(json_str)
    return json_object


# ============================================================================
# FUNCIÓN HÍBRIDA: Lee de PostgreSQL primero, JSON como fallback
# ============================================================================
def reloadJSONData(fileName):
    """
    Lee datos con estrategia híbrida:
    1. Intenta leer de PostgreSQL primero
    2. Si falla o no hay datos, lee del JSON encriptado

    Retorna: Lista de diccionarios (compatible con código existente)
    """

    # Intentar leer de PostgreSQL si está disponible
    if POSTGRES_AVAILABLE and fileName in FILE_TO_TABLE_MAP:
        try:
            table_name = FILE_TO_TABLE_MAP[fileName]
            print(f"🔄 Intentando leer {table_name} desde PostgreSQL...")

            # Query para obtener todos los registros de la tabla
            query = f"SELECT * FROM {table_name}"
            results = execute_query(query, fetch=True)

            if results and len(results) > 0:
                # Convertir a lista de diccionarios (formato compatible)
                data = [dict(row) for row in results]
                print(f"✅ Leídos {len(data)} registros de PostgreSQL ({table_name})")

                # Agregar header vacío al inicio (compatibilidad con código legacy)
                data.insert(0, {})

                return data
            else:
                print(f"⚠️  No hay datos en PostgreSQL para {table_name}, usando JSON...")

        except Exception as e:
            print(f"❌ Error leyendo de PostgreSQL: {str(e)}")
            print(f"⚠️  Fallback a JSON...")

    # Fallback: leer del JSON encriptado (código original)
    print(f"📄 Leyendo desde JSON: {fileName}")
    try:
        with open(fileName,'rb') as f:
            data = f.read()
            f.close()

        json_object=decrypt_file(data)

        if json_object == None:
            print("Archivo Corrupto")
            backupFile=fileName+"bku"
            shutil.copyfile(backupFile,fileName)
            print("Se recupero de Respaldo en vivo: " + fileName)
            return reloadJSONData(fileName)
        else:
            return json_object

    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {fileName}")
        # Retornar lista vacía con header para compatibilidad
        return [{}]
    except Exception as e:
        print(f"❌ Error leyendo JSON: {str(e)}")
        return [{}]


# ============================================================================
# Mantener funciones originales
# ============================================================================
def appendData(varId,fileName,data,addID):
    json_object = reloadJSONData(fileName)
    if (addID and varId!=None):
        # Obtengo el ultimo id
        data[varId]=str(int(json_object[len(json_object)-1][varId])+1)
    # Agrego la data
    json_object.append(data)
    saveJsonData(fileName,json_object)
    return


def saveJsonData(fileName,json_object):
    with open(fileName,"w") as mfile:
        json.dump(json_object, mfile, indent=4)
        mfile.close()

    encrypt_file(fileName)

    with open(fileName+"bku","w") as mfile:
        json.dump(json_object, mfile, indent=4)
        mfile.close()
    encrypt_file(fileName+"bku")

def replaceJson(fileName,json_object):
    """
    Given a filename, it replaces all the data on it, for the json_object.
    """
    saveJsonData(fileName,json_object)
    return


def completaDataSolicitud(data):
    # print(data)
    datetimeObj=datetime.now()
    data["solicitudEstatus"]="CONTACTO"
    data["solicitudNumeroControl"]=""
    # data["fechaContacto"]=datetimeObj.strftime("%Y-%m-%d %H:%M:%S") #Se envia desde el template
    data["fechaEntregaARiesgos"]=""
    data["fechaPropuesta"]=""
    data["fechaPrimerSolicitudVoBo"]=""
    data["fechaSegundaSolicitudVoBo"]=""
    data["fechaTercerSolicitudVoBo"]=""
    data["fechaVoBo"]=""
    data["fechaRechazoRiesgos"]=""
    data["fechaContratoImpreso"]=""
    data["fechaAutorizacionDG"]=""
    data["fechaRechazoDG"]=""
    data["fechaCancelacionCartera"]=""
    data["fechaEntregaContratoFirmado"]=""
    data["fechaFondeado"]=""
    data["fechaCancelacionCliente"]=""
    data["autorizacionDG"]=""
    data["montoAutorizado"]="0"
    data["montoTransferencia"]="0"
    data["plazoAutorizado"]=""
    data["etapaEmbudo"]="CONTACTO"
    data["estatusEmbudo"]="CONTACTO"
    data["tipoDeNegocio"]="ACTIVO"
    data["motivoNoCierre"]=""
    data["fechaValidacionClabe"]=""
    data["clienteReferenciaCobranza"]=""
    data["fechaReferenciaCobranza"]=""

    empresasRestringidas=routes_empresas.getEmpresasRestringidas()
    data["autorizacionDG"]="Normal"
    if  data["montoSolicitado"]!="":
        if  float(data["montoSolicitado"])>=50000:
            if (data["producto"]=="Nómina" or data["producto"]=="Adelanto de Nómina" or data["producto"=="Vehículos"]):
                data["autorizacionDG"]="Requerida"
    else:
        data["montoSolicitado"]=0

    if  data["montoAutorizado"]!="":
        if  float(data["montoAutorizado"])>=50000:
            if (data["producto"]=="Nómina" or data["producto"]=="Adelanto de Nómina" or data["producto"=="Vehículos"]):
                data["autorizacionDG"]="Requerida"
    else:
        data["montoAutorizado"]=0

    if  data["clienteEmpresa"] in empresasRestringidas:
        if (data["producto"]=="Nómina" or data["producto"]=="Adelanto de Nómina" or data["producto"=="Vehículos"]):
                data["autorizacionDG"]="Requerida"

    if data["clienteEmpresa"].upper()=="MIPYMEX":
        data["autorizacionDG"]="Requerida"

    if "MIPYMEX" in data["clienteEmpresa"].upper():
        data["autorizacionDG"]="Requerida"

    if data["inheritedID"]=="":
        data["regionNombre"]=getUser(data["ownerID"])["region"]
        data["inheritedID"]=data["ownerID"]
        data["asesorNombre"]=getUser(data["ownerID"])["name"]
    else:
        data["regionNombre"]=getUser(data["inheritedID"])["region"]
        data["asesorNombre"]=getUser(data["inheritedID"])["name"]

    return data

def completeDataUsuario(data):
    data["password"]="12345"
    return data

def completeDataEmpresa(data):
    asesor={}
    if "asesor" in data:
        asesor=getUser(data['asesor'])
        data["ownerID"]=data['asesor']
        data["asesor"]=asesor['name']
    return data

def completeDataROIP(data):
    datetimeObj=datetime.now()
    usuario={}
    if "ownerID" in data:
        usuario=getUser(data['ownerID'])
        data["reportadoPor"]=usuario['name']
        data["fechaReporte"]=datetimeObj.strftime("%Y-%m-%d %H:%M:%S")
        data["fechaDictaminacion"]=""
        data["fechaReporteSITI"]=""
        data["documentos"]=""
        data["reporteEstatus"]="abierto"

    return data

def completeDataGeolocation(data):
    datetimeObj=datetime.now()
    usuario={}
    if "ownerID" in data:
        usuario=getUser(data['ownerID'])
        data["usuario"]=usuario['name']
        data["fecha"]=datetimeObj.strftime("%Y-%m-%d %H:%M:%S")
    return data


def setEstatusSolicitud(data):
    data["editable"]="true"
    if data["fechaContacto"]!="":
        data["solicitudEstatus"]="CONTACTO"

        data["etapaEmbudo"]="CONTACTO"
        data["estatusEmbudo"]="CONTACTO"
        data["tipoDeNegocio"]="ACTIVO"

    if data["fechaEntregaARiesgos"]!="":
        data["solicitudEstatus"]="ENTREGA A RIESGOS"

        data["etapaEmbudo"]="ENTREGA A RIESGOS"
        data["estatusEmbudo"]="EN ANALISIS"
        data["tipoDeNegocio"]="ACTIVO"

    if data["fechaPropuesta"]!="":
        if data["autorizacionDG"]=="Normal":
            data["solicitudEstatus"]="AUTORIZADO"

            data["etapaEmbudo"]="ENTREGA A RIESGOS"
            data["estatusEmbudo"]="AUTORIZADO"
            data["tipoDeNegocio"]="GANADO"

        if data["autorizacionDG"]=="Requerida":
            data["solicitudEstatus"]="EN AUTORIZACION DG"

            data["etapaEmbudo"]="ENTREGA A RIESGOS"
            data["estatusEmbudo"]="EN ANALISIS"
            data["tipoDeNegocio"]="ACTIVO"


    if data["fechaAutorizacionDG"]!="":
        if data["autorizacionDG"]=="Requerida":
            data["solicitudEstatus"]="AUTORIZADO"

            data["etapaEmbudo"]="ENTREGA A RIESGOS"
            data["estatusEmbudo"]="AUTORIZADO"
            data["tipoDeNegocio"]="GANADO"

    if data["fechaContratoImpreso"]!="":
        data["solicitudEstatus"]="CONTRATO IMPRESO"

        data["etapaEmbudo"]="ENTREGA A RIESGOS"
        data["estatusEmbudo"]="CONTRATO IMPRESO"
        data["tipoDeNegocio"]="GANADO"

    if data["fechaEntregaContratoFirmado"]!="":
        # if ("contratoDocumento" in data and
        # 	data["contratoDocumento"]=="Ok"):
        data["solicitudEstatus"]="FIRMAR CONTRATO"
        data["etapaEmbudo"]="CIERRE"
        data["estatusEmbudo"]="FIRMAR CONTRATO"
        data["tipoDeNegocio"]="GANADO"

    if data["fechaFondeado"]!="":
        data["solicitudEstatus"]="FONDEADO"
        # data["editable"]="false"

        data["etapaEmbudo"]="CIERRE"
        data["estatusEmbudo"]="FONDEADO"
        data["tipoDeNegocio"]="GANADO"


    if data["fechaRechazoRiesgos"]!="":
        data["fechaRechazo"]=data["fechaRechazoRiesgos"]
        data["solicitudEstatus"]="RECHAZADO"
        # data["editable"]="false"

        data["etapaEmbudo"]="ENTREGA A RIESGOS"
        data["estatusEmbudo"]="EN ANALISIS"
        data["tipoDeNegocio"]="PERDIDO"
        data["motivoNoCierre"]="Rechazado por Riesgos"

        if data["fechaEntregaARiesgos"]=="":
            data["etapaEmbudo"]="CONTACTO"
            data["estatusEmbudo"]="CANCELADO"
            data["motivoNoCierre"]="Cancelado por el Cliente"
            data["tipoDeNegocio"]="PERDIDO"

        if data["fechaEntregaARiesgos"]=="":
            data["etapaEmbudo"]="CONTACTO"
            data["estatusEmbudo"]="CANCELADO"
            data["motivoNoCierre"]="Cancelado por el Cliente"
            data["tipoDeNegocio"]="PERDIDO"

        if data["fechaPropuesta"]!="":
            data["etapaEmbudo"]="ENTREGA A RIESGOS"
            data["estatusEmbudo"]="AUTORIZADO"
            data["motivoNoCierre"]="Cancelado por el Cliente"
            data["tipoDeNegocio"]="PERDIDO"

        if data["fechaContratoImpreso"]!="":
            data["etapaEmbudo"]="ENTREGA A RIESGOS"
            data["estatusEmbudo"]="CONTRATO IMPRESO"
            data["motivoNoCierre"]="Cancelado por el Cliente"
            data["tipoDeNegocio"]="PERDIDO"

        if data["fechaEntregaContratoFirmado"]!="":
            data["etapaEmbudo"]="CIERRE"
            data["estatusEmbudo"]="FIRMAR CONTRATO"
            data["motivoNoCierre"]="Cancelado por el Cliente"
            data["tipoDeNegocio"]="PERDIDO"

        if data["fechaFondeado"]!="":
            data["etapaEmbudo"]="CIERRE"
            data["estatusEmbudo"]="FONDEADO"
            data["motivoNoCierre"]="Cancelado por el Cliente"
            data["tipoDeNegocio"]="PERDIDO"


    if data["fechaRechazoDG"]!="":
        data["solicitudEstatus"]="RECHAZADO"
        data["fechaRechazo"]=data["fechaRechazoDG"]
        data["editable"]="false"

        data["etapaEmbudo"]="ENTREGA A RIESGOS"
        data["estatusEmbudo"]="EN ANALISIS"
        data["tipoDeNegocio"]="PERDIDO"
        data["motivoNoCierre"]="Rechazado por DG"


    if data["fechaCancelacionCliente"]!="":
        estatusActual=data["solicitudEstatus"]
        data["solicitudEstatus"]="RECHAZADO"
        data["fechaRechazo"]=data["fechaCancelacionCliente"]
        data["tipoDeNegocio"]="PERDIDO"
        # data["editable"]="false"

        if estatusActual=="CONTACTO":
            data["etapaEmbudo"]="CONTACTO"
            data["estatusEmbudo"]="CANCELADO"
            data["tipoDeNegocio"]="PERDIDO"
            data["motivoNoCierre"]="Cancelado por el Cliente"

        if estatusActual=="FIRMAR CONTRATO":
            data["etapaEmbudo"]="CIERRE"
            data["estatusEmbudo"]="CANCELADO"
            data["tipoDeNegocio"]="PERDIDO"
            data["motivoNoCierre"]="Cancelado por el Cliente"


    if data["fechaCancelacionCartera"]!="":
        data["solicitudEstatus"]="RECHAZADO"
        data["fechaRechazo"]=data["fechaCancelacionCartera"]
        data["editable"]="false"

        data["etapaEmbudo"]="CIERRE"
        data["estatusEmbudo"]="RECHAZADO"
        data["tipoDeNegocio"]="PERDIDO"
        data["motivoNoCierre"]="Contrato Cancelado por Cartera"

    data["autorizacionDG"]="Normal"
    empresasRestringidas=routes_empresas.getEmpresasRestringidas()

    if  data["montoSolicitado"]!="":
        if  float(data["montoSolicitado"])>=50000:
            if (data["producto"]=="Nómina" or data["producto"]=="Adelanto de Nómina" or data["producto"]=="Vehículos"):
                data["autorizacionDG"]="Requerida"
    else:
        data["montoSolicitado"]=0

    if  data["montoAutorizado"]!="":
        if  float(data["montoAutorizado"])>=50000:
            if (data["producto"]=="Nómina" or data["producto"]=="Adelanto de Nómina" or data["producto"=="Vehículos"]):
                data["autorizacionDG"]="Requerida"
    else:
        data["montoAutorizado"]=0

    if  data["clienteEmpresa"] in empresasRestringidas:
        if (data["producto"]=="Nómina" or data["producto"]=="Adelanto de Nómina" or data["producto"]=="Vehículos"):
                data["autorizacionDG"]="Requerida"

    if data["clienteEmpresa"].upper()=="MIPYMEX":
        data["autorizacionDG"]="Requerida"

    if "MIPYMEX" in data["clienteEmpresa"].upper():
        data["autorizacionDG"]="Requerida"

    # print(data)

    return data

def setEstatusROI(data):
    if data["fechaReporte"]!="":
        data["reporteEstatus"]="abierto"

    if data["fechaDictaminacion"]!="":
        data["reporteEstatus"]="dictaminado"

    if data["fechaReporteSITI"]!="":
        data["reporteEstatus"]="reportado"

    return data

def addData(fileName="",data=[]):
    varId=""
    viewName=data["viewName"]

    for field in data:
        if field in config.camposNumericos:
            if str(data[field])=="":
                data[field]=correctNumericValue("0")
            else:
                value=correctNumericValue(data[field])
                if  is_number(value):
                    data[field]=value
                else:
                    response={}
                    response['data']=[]
                    response['message']="Valores Inválidos."
                    response['messageCode']="403"
                    return(response)



    if fileName!="":
        fileName=fileName+".json"
    else:
        if viewName=="Solicitudes":
            fileName="working/solicitudes.json"
            data=completaDataSolicitud(data)
            varId="id"

        elif viewName=="Usuarios":
            fileName="working/users.json"
            data=completeDataUsuario(data)
            varId="ownerID"

        elif viewName=="Empresas":
            fileName="working/empresas.json"
            data=completeDataEmpresa(data)
            varId="id"

        elif viewName=="Operaciones Internas Preocupantes":
            fileName="working/roips.json"
            data=completeDataROIP(data)
            varId="id"

        elif viewName=="Geolocalizacion":
            fileName="working/geolocations.json"
            data=completeDataGeolocation(data)
            varId="id"


    appendData(varId,fileName,data,True)

    response={}
    response['data']=[]
    response['message']=""
    response['messageCode']="200"
    addLog(data,"agregar")
    return response

def addLog(data=[],accion=""):
    endData={}
    viewName=data["viewName"]
    if (viewName=="Solicitudes"  or
        viewName=="Contactados"   or
        viewName=="Entregados a Riesgos" or
        viewName=="Solicitar VoBo" or
        viewName=="Autorización Riesgos" or
        viewName=="Autorización DG" or
        viewName=="Imprimir Contrato" or
        viewName=="Firmar Contrato" or
        viewName=="Por Fondear" or
        viewName=="Transferencias" or
        viewName=="Fondeados" or
        viewName=="Rechazados"  or
        viewName=="CLABES"	or
        viewName=="Cobranza" or
        viewName=="Historico" or
        viewName=="PreAnalisis" or
        viewName=="Analisis de Creditos" or
        viewName=="Revision Documental"
        ):
        endData["Objeto"]="Solicitudes"
    elif viewName=="Usuarios":
        endData["Objeto"]="Usuarios"
    elif viewName=="Perfil de Usuario":
        endData["Objeto"]="Usuarios"
    elif viewName=="Log In":
        endData["Objeto"]="Ingreso"
    elif viewName=="Empresas":
        endData["Objeto"]="Empresas"
    elif viewName=="Operacion Interna Preocupante":
        endData["Objeto"]="Operacion Interna Preocupante"
    elif viewName=="Operaciones Internas Preocupantes":
        endData["Objeto"]="Operacion Interna Preocupante"
    elif viewName=="Geolocalizacion":
        endData["Objeto"]="Geolocalizacion"
    elif viewName=="Asignaciones":
        endData["Objeto"]="Empresas"

    endData["logData"]=data
    endData["accion"]=accion
    datetimeObj=datetime.now();
    endData["timeStamp"]=str(datetimeObj)
    fileName="working/logs.json"
    appendData(None,fileName,endData,False)
    return

def is_number(s):
    try:
        complex(s) # for int, long, float and complex
    except ValueError:
        return False

    return True

def updateData(data):
    app = current_app
    viewName=data['viewName']

    if str(data["field"]) in config.camposNumericos:
        if str(data["value"])=="":
            data["value"]=correctNumericValue("0")
        else:
            value=correctNumericValue(data["value"])
            if  is_number(value):
                data["value"]=value
            else:
                response={}
                response['data']=[]
                response['message']="Valor Inválido."
                response['messageCode']="403"
                return(response)

    if (viewName=="Solicitudes" or
        viewName=="Contactados" or
        viewName=="Entregados a Riesgos" or
        viewName=="Solicitar VoBo" or
        viewName=="Autorización Riesgos" or
        viewName=="Autorización DG" or
        viewName=="Imprimir Contrato" or
        viewName=="Firmar Contrato" or
        viewName=="Por Fondear" or
        viewName=="Transferencias" or
        viewName=="Fondeados" or
        viewName=="Rechazados" or
        viewName=="Cancelados por el Cliente" or
        viewName=="Cancelados por Cartera" or
        viewName=="CLABES" or
        viewName=="Cobranza" or
        viewName=="Historico" or
        viewName=="PreAnalisis" or
        viewName=="Analisis de Creditos" or
        viewName=="Revision Documental" or
        viewName=="Control de Expedientes"
        ):
        fileName="working/solicitudes.json"

    elif (viewName=="Usuarios" or
        viewName=="Perfil de Usuario"):
        fileName="working/users.json"

    elif viewName=="Empresas" :
        fileName="working/empresas.json"

    elif viewName=="Asignaciones" :
        fileName="working/empresas.json"

    elif viewName=="Operaciones Internas Preocupantes":
        fileName="working/roips.json"


    json_object=reloadJSONData(fileName)

    indice=int(data["id"])
    field=str(data["field"])
    newValue=str(data["value"])

    try:
        oldValue=json_object[indice][field]
    except KeyError:
        oldValue=""



    if viewName=="Usuarios" or viewName=="Perfil de Usuario":
        if field=="newPassword":
            user=getUser(data['id'])
            hashed=data["value"]+user["correo"]
            hash_object = hashlib.sha512(hashed.encode())
            newValue = hash_object.hexdigest()
            field="hash"
            # if "password" in json_object[indice]:
                # del json_object[indice]["password"]
            apiKey=binascii.hexlify(os.urandom(24)).decode("utf-8")
            json_object[indice]["randomKey"]=apiKey
            apiKey +="."+user["correo"]+"."+user["ownerID"]+app.config['SECRET_KEY']
            apiKey=hashlib.sha512(apiKey.encode()).hexdigest()
            json_object[indice]["apiKey"]=apiKey
            json_object[indice]["password"]=hashlib.sha512(data["value"].encode()).hexdigest()
            oldValue="Valor Secreto"
            data["value"]="Nuevo Valor Secreto"


    json_object[indice][field]=newValue

    if (viewName=="Solicitudes" or
        viewName=="Contactados" or
        viewName=="Entregados a Riesgos" or
        viewName=="Solicitar VoBo" or
        viewName=="Autorización Riesgos" or
        viewName=="Autorización DG" or
        viewName=="Imprimir Contrato" or
        viewName=="Firmar Contrato" or
        viewName=="Por Fondear" or
        viewName=="Transferencias" or
        viewName=="Fondeados" or
        viewName=="Rechazados" or
        viewName=="Cancelados por el Cliente" or
        viewName=="Cancelados por Cartera" or
        viewName=="CLABES" or
        viewName=="Cobranza" or
        viewName=="Historico" or
        viewName=="Revision Documental" or
        viewName=="PreAnalisis" or
        viewName=="Analisis de Creditos" or
        viewName=="Control de Expedientes"

        ):

        if field=="ownerID":
            if json_object[indice]["inheritedID"]=="":
                json_object[indice]["inheritedID"]=data["value"]

        if field=="inheritedID":
            json_object[indice]["asesorNombre"]=getUser(data["value"])["name"]

        if field=="fechaPropuesta":
            json_object[indice]["usuarioAutorizacionRiesgos"]=data["userName"]
            if data["value"]=="":
                json_object[indice]["fechaPrimerSolicitudVoBo"]=""
                json_object[indice]["fechaSegundaSolicitudVoBo"]=""
                json_object[indice]["fechaTercerSolicitudVoBo"]=""
                json_object[indice]["fechaVoBo"]=""

        if field=="fechaRechazoRiesgos":
            json_object[indice]["usuarioAutorizacionRiesgos"]=data["userName"]

        # Se valida si se puede o no actualizar el campo
        permitido=True
        if field in config.estatusOrden[1]:
            newfieldNumber=config.estatusOrden[1][field]
            currentfieldNumber=config.estatusOrden[0][json_object[indice]["solicitudEstatus"]]
            if newfieldNumber>currentfieldNumber +1 and newValue!="":
                permitido=False

            if newfieldNumber==5 and currentfieldNumber==3:
                permitido=False
                if json_object[indice]["autorizacionDG"]=="Normal":
                    permitido=True
                else:
                    if json_object[indice]["fechaAutorizacionDG"]!="":
                        permitido=True

            if newfieldNumber>=5:
                if json_object[indice]["autorizacionDG"]=="Requerida":
                    if json_object[indice]["fechaAutorizacionDG"]=="":
                        permitido=False

            if viewName=="Historico":
                permitido=True


            # print(permitido)
            if permitido==False:
                response={}
                response['data']=[]
                response['message']="Operación no permitida."
                response['messageCode']="403"
                return(response)

        json_object[indice]=setEstatusSolicitud(json_object[indice])
        json_object[indice]=deleteCheckBoxes(json_object[indice])

    if viewName=="Usuarios":
        data["usuarioModificado"]=json_object[indice]["name"]

    if viewName=="Empresas":
        if data["field"]=="asesor":
            asesor=getUser(data['value'])
            json_object[indice]["ownerID"]=data['value']
            json_object[indice]["asesor"]=asesor['name']

    if viewName=="Asignaciones":
        if(field in json_object[indice]):
            json_object[indice][field]=newValue
        else:
            asesorNuevo={}
            asesorNuevo[field]=newValue
            json_object[indice].append(asesorNuevo)

    if viewName=="Operaciones Internas Preocupantes":
        json_object[indice]=setEstatusROI(json_object[indice])

    if viewName=="Revision Documental":
        if (field == "fechaRevisionDocumentalConluida" and
            newValue!=""):
            solicitud=analisis.analisisSolicitud(json_object[indice],newData=[])['solicitud']
            updateSolicitud(solicitud["id"], solicitud, data)


    if (viewName=="Analisis de Creditos" or
        viewName=="PreAnalisis"):
        if "forbidden" in json_object[indice]:
            if (field in json_object[indice]["forbidden"] and
                field not in config.camposAnalisisCredito):
                response={}
                response['data']=[]
                response['message']="Operación no permitida."
                response['messageCode']="403"
                return(response)
        newData={}
        newData[field]=newValue
        solicitud=analisis.analisisSolicitud(json_object[indice],newData)['solicitud']
        updateSolicitud(solicitud["id"], solicitud, data)


    if (viewName!="Analisis de Creditos" and
        viewName!="PreAnalisis" and
        viewName!="Revision Documental"):
        saveJsonData(fileName,json_object)
        data["oldValue"]=oldValue
        addLog(data,"actualización")

    response={}
    response['data']=json_object[indice]
    response['message']="Información actualizada."
    response['messageCode']="200"
    return(response)


def updateArray(data):
    viewName=data['viewName']
    field=str(data["field"])

    badresponse={}
    badresponse['data']=data
    badresponse['message']="Información incorrecta."
    badresponse['messageCode']="400"

    valuedataArray=json.loads(data["dataArray"]);

    if (viewName!="Solicitar VoBo"):
        return badresponse;


    # Aqui debe iniciara a iterar con el arrego de datos
    if (viewName=="Solicitar VoBo" and field=="fechasVoBos"):
        for itemID in valuedataArray:
            if valuedataArray[itemID]==True:
                newData=data
                newData['id']=itemID
                newData['value']=valuedataArray["date"]
                if "dataArray" in newData:
                    del newData["dataArray"]
                if "date" in newData:
                    del newData["date"]
                solicitud=getSolicitudById(int(itemID))
                field=searchDateToUpdate(solicitud)
                newData["field"]=field
                itemResponse=updateData(newData)

    response={}
    response['viewName']=data['viewName']
    response['data']="Conjunto de datos"
    response['message']="Información actualizada."
    response['messageCode']="200"
    return(response);

def updateSolicitud(id, data, formData=None):
    # print(json.dumps(formData,indent=4))
    # print(json.dumps(data,indent=4))
    response=True
    solicitud=getSolicitudById(int(id))
    # Obtengo los valores originales de la solicitud
    oldData={}
    for field in data:
        if 	field in solicitud:
            oldData[field]=solicitud[field]
        else:
            oldData[field]=""
            solicitud[field]=""

    # Verifico cuales valores cambiaron
    newData={}
    newitem={}
    for field in data:
        if field in config.camposNumericos:
            if str(data[field])=="":
                data[field]=correctNumericValue("0")
            else:
                value=correctNumericValue(data[field])
                if  is_number(value):
                    data[field]=value
                else:
                    response={}
                    response['data']=[]
                    response['message']="Valor Inválido."
                    response['messageCode']="403"
                    return(response)

        if str(data[field]).strip()!=str(oldData[field]).strip():
            newData[field]=str(data[field]).strip()
            if field not in config.camposSesion:
                solicitud[field]=str(data[field]).strip()
                newitem["id"]=data["id"]
                newitem["field"]=field
                newitem["value"]=str(data[field]).strip()

    solicitud=deleteCheckBoxes(solicitud)


    fileName="working/solicitudes.json"
    json_object=reloadJSONData(fileName)
    json_object[int(data["id"])]=solicitud
    try:
        saveJsonData(fileName,json_object)
    except Exception as e:
        response=False
        # print(e)
    else:
        response=True
        logData={}
        logData["ownerID"]=data["ownerID"]
        logData["userName"]=formData["userName"]
        logData["field"]=""
        logData["value"]=""
        logData["id"]=data["id"]
        logData["viewName"]=formData["viewName"]
        logData["oldValue"]=""
        for field in newData:
            if field not in config.camposSesion:
                logData["field"] += field + ", "
                logData["value"] += newData[field] + ", "
                logData["oldValue"] += oldData[field] + ", "
        addLog(logData,"actualización")

    return response

def actualizarDataControlExpedientes(dataExpedientes,formData):
    response=True
    fileName="working/solicitudes.json"
    solicitudes=reloadJSONData(fileName)

    for idx in dataExpedientes:
        for field in dataExpedientes[idx]:
            solicitudes[int(idx)][field]=dataExpedientes[idx][field]

    try:
        saveJsonData(fileName,solicitudes)
    except Exception as e:
        response=False

    return response

def correctNumericValue(newValue):
    if type(newValue)!=str:
        value=str(newValue)
    else:
        value=newValue

    numberStr=""

    for c in value:
        if(c.isdigit or c=="."):
            numberStr  = numberStr +c
    numberStr=numberStr.replace(",", "")

    if numberStr=="":
        numberStr="0.00"

    numberValue="{0:.2f}".format(float(numberStr))
    return str(numberValue)

def deleteCheckBoxes(data):
    checkBoxes=[]
    for field in data:
        if "check_" in field:
            checkBoxes.append(field)
    for field in checkBoxes:
        del data[field]
    return data

def searchDateToUpdate(data):
    updateDate="null"
    if data["fechaPrimerSolicitudVoBo"]=="":
        updateDate="fechaPrimerSolicitudVoBo"

    elif data["fechaSegundaSolicitudVoBo"]=="":
        updateDate="fechaSegundaSolicitudVoBo"

    elif data["fechaTercerSolicitudVoBo"]=="":
        updateDate="fechaTercerSolicitudVoBo"

    return updateDate

def allowedUser(data):
    field=str(data["field"])
    user=getUser(data['ownerID'])
    if field in user["forbidden"]:
        return False
    else:
        return True

def actualizarDataSolicitudes(data,formData):
    response=True
    fileName="working/solicitudes.json"
    solicitudes=reloadJSONData(fileName)

    for idx in data:
        for field in data[idx]:
            if is_number(idx):
                solicitudes[int(idx)][field]=data[idx][field]

    try:
        saveJsonData(fileName,solicitudes)
    except Exception as e:
        response=False

    return response

def replaceJson(fileName,json_object):
    """
    Given a filename, it replaces all the data on it, for the json_object.
    """
    saveJsonData(fileName,json_object)
    return
