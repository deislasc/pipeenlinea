# -*- coding: utf-8 -*-
"""
update_db.py - Versión PostgreSQL de update.py

Este módulo reemplaza las funciones de update.py que usaban JSON encriptado
con queries SQL raw a PostgreSQL.

IMPORTANTE: Este es un ejemplo de migración. Debes:
1. Probar exhaustivamente cada función
2. Mantener update.py como backup durante la transición
3. Migrar gradualmente las funciones
"""

import json
from datetime import datetime
from flask import current_app
import config
from database import execute_query, execute_transaction, dict_to_insert, dict_to_update

# Importar funciones que aún dependen de otros módulos
from routes_users import getUser
from routes_empresas import getEmpresasRestringidas
import routes_analisis as analisis

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def is_number(s):
    """Verifica si un string es un número"""
    try:
        complex(s)
        return True
    except ValueError:
        return False

def correctNumericValue(newValue):
    """
    Corrige valores numéricos removiendo caracteres inválidos

    Args:
        newValue: Valor a corregir

    Returns:
        String con formato numérico válido
    """
    if type(newValue) != str:
        value = str(newValue)
    else:
        value = newValue

    numberStr = ""

    for c in value:
        if c.isdigit() or c == ".":
            numberStr = numberStr + c

    numberStr = numberStr.replace(",", "")

    if numberStr == "":
        numberStr = "0.00"

    numberValue = "{0:.2f}".format(float(numberStr))
    return str(numberValue)

# ============================================================================
# FUNCIONES DE SOLICITUDES
# ============================================================================

def getSolicitudById(solicitud_id):
    """
    Obtiene una solicitud por ID

    Args:
        solicitud_id: ID de la solicitud

    Returns:
        Diccionario con datos de la solicitud o None
    """
    query = """
        SELECT
            id,
            numero_control,
            cliente_nombre,
            cliente_apellido_paterno,
            cliente_apellido_materno,
            cliente_empresa,
            cliente_salario,
            producto,
            monto_solicitado,
            monto_autorizado,
            solicitud_estatus,
            fecha_contacto,
            fecha_entrega_riesgos,
            fecha_fondeado,
            owner_id,
            inherited_id,
            asesor_nombre,
            region_nombre,
            autorizacion_dg,
            -- Agregar todos los campos necesarios
            created_at,
            updated_at
        FROM solicitudes
        WHERE id = %s
    """

    result = execute_query(query, (solicitud_id,), fetch_one=True)

    if result:
        # Convertir RealDictRow a dict regular y formatear fechas
        solicitud = dict(result)

        # Convertir fechas a strings para compatibilidad
        for key, value in solicitud.items():
            if isinstance(value, datetime):
                solicitud[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            elif value is None:
                solicitud[key] = ""

        return solicitud

    return None

def addSolicitud(data):
    """
    Agrega una nueva solicitud

    Args:
        data: Diccionario con datos de la solicitud

    Returns:
        Diccionario con response (data, message, messageCode)
    """
    # Completar datos de solicitud
    data = completaDataSolicitud(data)

    # Validar campos numéricos
    for field in data:
        if field in config.camposNumericos:
            if str(data[field]) == "":
                data[field] = correctNumericValue("0")
            else:
                value = correctNumericValue(data[field])
                if is_number(value):
                    data[field] = value
                else:
                    return {
                        'data': [],
                        'message': "Valores Inválidos.",
                        'messageCode': "403"
                    }

    # Mapear campos de camelCase a snake_case para SQL
    sql_data = {
        'numero_control': data.get('solicitudNumeroControl', ''),
        'cliente_nombre': data.get('clienteNombre', ''),
        'cliente_apellido_paterno': data.get('clienteApellidoPaterno', ''),
        'cliente_apellido_materno': data.get('clienteApellidoMaterno', ''),
        'cliente_empresa': data.get('clienteEmpresa', ''),
        'cliente_salario': data.get('clienteSalario', 0),
        'producto': data.get('producto', ''),
        'monto_solicitado': data.get('montoSolicitado', 0),
        'solicitud_estatus': data.get('solicitudEstatus', 'CONTACTO'),
        'fecha_contacto': data.get('fechaContacto'),
        'owner_id': data.get('ownerID'),
        'inherited_id': data.get('inheritedID'),
        'asesor_nombre': data.get('asesorNombre', ''),
        'region_nombre': data.get('regionNombre', ''),
        'autorizacion_dg': data.get('autorizacionDG', 'Normal'),
        'view_name': data.get('viewName', 'Solicitudes')
        # Agregar todos los campos necesarios...
    }

    # Construir query de inserción
    query, params = dict_to_insert('solicitudes', sql_data, returning='id')

    try:
        result = execute_query(query, params, fetch_one=True)
        new_id = result['id']

        # Agregar log
        addLog(data, "agregar")

        return {
            'data': {'id': new_id},
            'message': "Solicitud creada correctamente",
            'messageCode': "200"
        }
    except Exception as e:
        return {
            'data': [],
            'message': f"Error al crear solicitud: {str(e)}",
            'messageCode': "500"
        }

def updateSolicitud(solicitud_id, data, formData=None):
    """
    Actualiza una solicitud existente

    Args:
        solicitud_id: ID de la solicitud
        data: Nuevos datos
        formData: Datos del formulario para logging

    Returns:
        True si exitoso, False si error
    """
    # Obtener solicitud actual
    solicitud = getSolicitudById(solicitud_id)
    if not solicitud:
        return False

    # Obtener valores originales para logging
    oldData = {}
    for field in data:
        oldData[field] = solicitud.get(field, "")

    # Verificar cambios y validar numéricos
    newData = {}
    for field in data:
        if field in config.camposNumericos:
            if str(data[field]) == "":
                data[field] = correctNumericValue("0")
            else:
                value = correctNumericValue(data[field])
                if is_number(value):
                    data[field] = value
                else:
                    return False

        if str(data[field]).strip() != str(oldData[field]).strip():
            newData[field] = str(data[field]).strip()

    if not newData:
        return True  # No hay cambios

    # Construir query de actualización
    # Mapear campos de camelCase a snake_case
    sql_updates = {}
    for field, value in newData.items():
        # Convertir camelCase a snake_case
        # Esta es una simplificación, necesitarías un mapeo completo
        snake_field = field.replace('Cliente', 'cliente_').replace('Monto', 'monto_')
        sql_updates[snake_field] = value

    # Agregar updated_at
    sql_updates['updated_at'] = datetime.now()

    query, params = dict_to_update('solicitudes', sql_updates, 'id', solicitud_id)

    try:
        execute_query(query, params)

        # Logging
        if formData:
            logData = {
                "ownerID": data.get("ownerID"),
                "userName": formData.get("userName"),
                "field": "",
                "value": "",
                "id": solicitud_id,
                "viewName": formData.get("viewName"),
                "oldValue": ""
            }

            for field in newData:
                logData["field"] += field + ", "
                logData["value"] += newData[field] + ", "
                logData["oldValue"] += oldData.get(field, "") + ", "

            addLog(logData, "actualización")

        return True
    except Exception as e:
        print(f"Error actualizando solicitud: {e}")
        return False

# ============================================================================
# FUNCIONES DE COMPLETADO DE DATOS
# ============================================================================

def completaDataSolicitud(data):
    """
    Completa datos de una nueva solicitud con valores por defecto

    Args:
        data: Diccionario con datos parciales

    Returns:
        Diccionario con todos los campos completados
    """
    datetimeObj = datetime.now()

    # Estado inicial
    data["solicitudEstatus"] = "CONTACTO"
    data["solicitudNumeroControl"] = ""

    # Fechas del workflow (todas vacías inicialmente)
    data["fechaEntregaARiesgos"] = ""
    data["fechaPropuesta"] = ""
    data["fechaPrimerSolicitudVoBo"] = ""
    data["fechaSegundaSolicitudVoBo"] = ""
    data["fechaTercerSolicitudVoBo"] = ""
    data["fechaVoBo"] = ""
    data["fechaRechazoRiesgos"] = ""
    data["fechaContratoImpreso"] = ""
    data["fechaAutorizacionDG"] = ""
    data["fechaRechazoDG"] = ""
    data["fechaCancelacionCartera"] = ""
    data["fechaEntregaContratoFirmado"] = ""
    data["fechaFondeado"] = ""
    data["fechaCancelacionCliente"] = ""
    data["autorizacionDG"] = "Normal"
    data["montoAutorizado"] = "0"
    data["montoTransferencia"] = "0"
    data["plazoAutorizado"] = ""
    data["etapaEmbudo"] = "CONTACTO"
    data["estatusEmbudo"] = "CONTACTO"
    data["tipoDeNegocio"] = "ACTIVO"
    data["motivoNoCierre"] = ""
    data["fechaValidacionClabe"] = ""
    data["clienteReferenciaCobranza"] = ""
    data["fechaReferenciaCobranza"] = ""

    # Determinar si requiere autorización DG
    empresasRestringidas = getEmpresasRestringidas()
    data["autorizacionDG"] = "Normal"

    if data.get("montoSolicitado", "") != "":
        if float(data["montoSolicitado"]) >= 50000:
            if data.get("producto") in ["Nómina", "Adelanto de Nómina", "Vehículos"]:
                data["autorizacionDG"] = "Requerida"
    else:
        data["montoSolicitado"] = 0

    if data.get("clienteEmpresa", "") in empresasRestringidas:
        if data.get("producto") in ["Nómina", "Adelanto de Nómina", "Vehículos"]:
            data["autorizacionDG"] = "Requerida"

    if data.get("clienteEmpresa", "").upper() == "MIPYMEX" or "MIPYMEX" in data.get("clienteEmpresa", "").upper():
        data["autorizacionDG"] = "Requerida"

    # Asignar región y asesor
    if data.get("inheritedID", "") == "":
        usuario = getUser(data["ownerID"])
        data["regionNombre"] = usuario["region"]
        data["inheritedID"] = data["ownerID"]
        data["asesorNombre"] = usuario["name"]
    else:
        usuario = getUser(data["inheritedID"])
        data["regionNombre"] = usuario["region"]
        data["asesorNombre"] = usuario["name"]

    return data

# ============================================================================
# FUNCIONES DE LOGGING
# ============================================================================

def addLog(data, accion=""):
    """
    Agrega un registro de log

    Args:
        data: Diccionario con datos del evento
        accion: Tipo de acción (agregar, actualización, etc.)
    """
    endData = {}
    viewName = data.get("viewName", "")

    # Determinar objeto
    if viewName in ["Solicitudes", "Contactados", "Entregados a Riesgos",
                    "Solicitar VoBo", "Autorización Riesgos", "Autorización DG",
                    "Imprimir Contrato", "Firmar Contrato", "Por Fondear",
                    "Transferencias", "Fondeados", "Rechazados", "CLABES",
                    "Cobranza", "Historico", "PreAnalisis",
                    "Analisis de Creditos", "Revision Documental"]:
        objeto = "Solicitudes"
    elif viewName in ["Usuarios", "Perfil de Usuario"]:
        objeto = "Usuarios"
    elif viewName == "Log In":
        objeto = "Ingreso"
    elif viewName == "Empresas":
        objeto = "Empresas"
    else:
        objeto = viewName

    query = """
        INSERT INTO logs (objeto, accion, log_data, timestamp, user_id)
        VALUES (%s, %s, %s, %s, %s)
    """

    params = (
        objeto,
        accion,
        json.dumps(data),
        datetime.now(),
        data.get("ownerID")
    )

    try:
        execute_query(query, params)
    except Exception as e:
        print(f"Error agregando log: {e}")

# ============================================================================
# FUNCIONES DE BÚSQUEDA
# ============================================================================

def getSolicitudes(owner_id, scope='self'):
    """
    Obtiene solicitudes según el scope del usuario

    Args:
        owner_id: ID del usuario
        scope: 'self' o 'all'

    Returns:
        Lista de solicitudes
    """
    if scope == 'self':
        query = """
            SELECT *
            FROM solicitudes
            WHERE owner_id = %s OR inherited_id = %s
            ORDER BY asesor_nombre, fecha_contacto
        """
        params = (owner_id, owner_id)
    else:
        query = """
            SELECT *
            FROM solicitudes
            ORDER BY asesor_nombre, fecha_contacto
        """
        params = ()

    results = execute_query(query, params, fetch=True)

    # Convertir a dict y formatear fechas
    solicitudes = []
    for row in results:
        solicitud = dict(row)
        for key, value in solicitud.items():
            if isinstance(value, datetime):
                solicitud[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            elif value is None:
                solicitud[key] = ""
        solicitudes.append(solicitud)

    return solicitudes

def getSolicitudesByEstatus(estatus):
    """
    Obtiene solicitudes por estatus

    Args:
        estatus: Estatus de la solicitud

    Returns:
        Lista de solicitudes
    """
    query = """
        SELECT *
        FROM solicitudes
        WHERE solicitud_estatus = %s
        ORDER BY fecha_contacto DESC
    """

    results = execute_query(query, (estatus,), fetch=True)

    solicitudes = []
    for row in results:
        solicitud = dict(row)
        for key, value in solicitud.items():
            if isinstance(value, datetime):
                solicitud[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            elif value is None:
                solicitud[key] = ""
        solicitudes.append(solicitud)

    return solicitudes

# ============================================================================
# FUNCIONES DE ESTADÍSTICAS
# ============================================================================

def getEstadisticasSolicitudes():
    """
    Obtiene estadísticas generales de solicitudes

    Returns:
        Diccionario con estadísticas
    """
    queries = {
        'total': "SELECT COUNT(*) as count FROM solicitudes",
        'contacto': "SELECT COUNT(*) as count FROM solicitudes WHERE solicitud_estatus = 'CONTACTO'",
        'en_proceso': "SELECT COUNT(*) as count FROM solicitudes WHERE solicitud_estatus NOT IN ('FONDEADO', 'RECHAZADO')",
        'fondeadas': "SELECT COUNT(*) as count FROM solicitudes WHERE solicitud_estatus = 'FONDEADO'",
        'rechazadas': "SELECT COUNT(*) as count FROM solicitudes WHERE solicitud_estatus = 'RECHAZADO'",
        'monto_total_autorizado': "SELECT COALESCE(SUM(monto_autorizado), 0) as total FROM solicitudes WHERE solicitud_estatus = 'FONDEADO'"
    }

    stats = {}
    for key, query in queries.items():
        result = execute_query(query, fetch_one=True)
        if key == 'monto_total_autorizado':
            stats[key] = float(result['total'])
        else:
            stats[key] = result['count']

    return stats

# ============================================================================
# NOTA: Este es solo un ejemplo de migración
# ============================================================================
# Falta migrar muchas otras funciones de update.py:
# - setEstatusSolicitud
# - updateData
# - updateArray
# - allowedUser
# - Funciones de empresas
# - Funciones de usuarios
# - Funciones de ROIPs
# - etc.
#
# La migración completa debe ser gradual y bien testeada
# ============================================================================
