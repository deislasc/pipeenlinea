#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE MIGRACIÓN: JSON Encriptado → PostgreSQL
==================================================
Migra todos los datos de archivos JSON encriptados a PostgreSQL

Uso:
    python migrate_to_postgres.py [--dry-run] [--batch-size 1000]

Opciones:
    --dry-run: Simula la migración sin guardar datos
    --batch-size: Número de registros por batch (default: 1000)
    --skip-table: Tabla a omitir (puede usar múltiples veces)
"""

import sys
import os
import json
import argparse
from datetime import datetime
from cryptography.fernet import Fernet

# Agregar path de mysite
sys.path.insert(0, 'mysite')

# Importar módulo de base de datos
from database import initialize_pool, execute_query, execute_many, check_database_connection

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

WORKING_DIR = "working"
SECRET_KEY_PATH = os.getenv('ENCRYPTION_KEY_PATH', 'secret.key')

# Mapeo de archivos JSON a tablas
FILE_TO_TABLE_MAP = {
    'users.json': 'usuarios',
    'empresas.json': 'empresas',
    'solicitudes.json': 'solicitudes',
    'logs.json': 'logs',
    'cosechas.json': 'cosechas',
    'geolocations.json': 'geolocalizaciones',
    'acl.json': 'acl',
    'agendas.json': 'agendas',
    'pagadoras.json': 'pagadoras',
    'roips.json': 'operaciones_internas_preocupantes'
}

# ============================================================================
# FUNCIONES DE DESENCRIPTACIÓN
# ============================================================================

def load_key():
    """Carga la clave de encriptación"""
    try:
        with open(SECRET_KEY_PATH, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error al cargar clave de encriptación: {e}")
        sys.exit(1)

def decrypt_json_file(file_path):
    """
    Desencripta y carga un archivo JSON

    Args:
        file_path: Ruta al archivo encriptado

    Returns:
        Lista/diccionario con datos JSON
    """
    try:
        key = load_key()
        fernet = Fernet(key)

        with open(file_path, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = fernet.decrypt(encrypted_data)
        json_data = json.loads(decrypted_data.decode('utf-8'))

        return json_data
    except Exception as e:
        print(f"❌ Error al desencriptar {file_path}: {e}")
        return None

# ============================================================================
# FUNCIONES DE TRANSFORMACIÓN DE DATOS
# ============================================================================

def transform_usuario(item):
    """Transforma datos de usuario de JSON a formato SQL"""
    return {
        'owner_id': item.get('ownerID', ''),
        'name': item.get('name', ''),
        'correo': item.get('correo', ''),
        'hash': item.get('hash', ''),
        'password_hash': item.get('password', ''),
        'api_key': item.get('apiKey', ''),
        'random_key': item.get('randomKey', ''),
        'region': item.get('region', ''),
        'scope': item.get('scope', 'self'),
        'forbidden': json.dumps(item.get('forbidden', [])),
        'active': item.get('active', True)
    }

def transform_empresa(item):
    """Transforma datos de empresa de JSON a formato SQL"""
    return {
        'nombre': item.get('nombre', ''),
        'owner_id': item.get('ownerID', None),
        'asesor': item.get('asesor', ''),
        'nivel_riesgo': item.get('nivelRiesgo', ''),
        'restringida': item.get('restringida', False),
        'datos_adicionales': json.dumps({k: v for k, v in item.items()
                                        if k not in ['id', 'nombre', 'ownerID', 'asesor', 'nivelRiesgo', 'restringida']})
    }

def transform_solicitud(item):
    """Transforma datos de solicitud de JSON a formato SQL"""

    # Función helper para convertir fechas vacías en NULL
    def fecha_or_null(fecha_str):
        if not fecha_str or fecha_str == '':
            return None
        try:
            return datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None

    # Función helper para convertir números
    def decimal_or_zero(value):
        if not value or value == '':
            return 0
        try:
            return float(str(value).replace(',', ''))
        except:
            return 0

    return {
        'numero_control': item.get('solicitudNumeroControl', ''),

        # Cliente
        'cliente_nombre': item.get('clienteNombre', ''),
        'cliente_apellido_paterno': item.get('clienteApellidoPaterno', ''),
        'cliente_apellido_materno': item.get('clienteApellidoMaterno', ''),
        'cliente_empresa': item.get('clienteEmpresa', ''),
        'cliente_salario': decimal_or_zero(item.get('clienteSalario')),
        'cliente_deducciones_mensuales': decimal_or_zero(item.get('clienteDeduccionesMensuales')),
        'cliente_deducciones_periodo': decimal_or_zero(item.get('clienteDeduccionesPeriodo')),
        'cliente_deducciones_quincenales': decimal_or_zero(item.get('clienteDeduccionesQuincenales')),
        'cliente_deducciones_semanales': decimal_or_zero(item.get('clienteDeduccionesSemanales')),

        # Solicitud
        'producto': item.get('producto', ''),
        'monto_solicitado': decimal_or_zero(item.get('montoSolicitado')),
        'monto_autorizado': decimal_or_zero(item.get('montoAutorizado')),
        'monto_transferencia': decimal_or_zero(item.get('montoTransferencia')),
        'plazo_autorizado': int(item.get('plazoAutorizado', 0)) if item.get('plazoAutorizado') else None,
        'linea_credito': decimal_or_zero(item.get('lineaDeCredito')),

        # Análisis
        'monto_buen_buro': decimal_or_zero(item.get('montoBuenBuro')),
        'monto_capacidad_pago': decimal_or_zero(item.get('montoCapacidadDePago')),
        'monto_comision': decimal_or_zero(item.get('montoComision')),
        'monto_comision_politica': decimal_or_zero(item.get('montoComisionPolitica')),
        'monto_maximo_politica': decimal_or_zero(item.get('montoMaximoPolitica')),
        'monto_seguro': decimal_or_zero(item.get('montoSeguro')),
        'monto_iva_comision': decimal_or_zero(item.get('montoIvaComision')),
        'monto_iva_seguro': decimal_or_zero(item.get('montoIVASeguro')),
        'monto_propuesto': decimal_or_zero(item.get('montoPropuesto')),
        'monto_ministracion': decimal_or_zero(item.get('montoMinistracion')),
        'costo_seguro_parcialidad': decimal_or_zero(item.get('costoSeguroParcialidad')),
        'iva_intereses_simulador': decimal_or_zero(item.get('ivaInteresesSimulador')),

        # Workflow
        'solicitud_estatus': item.get('solicitudEstatus', 'CONTACTO'),
        'etapa_embudo': item.get('etapaEmbudo', ''),
        'estatus_embudo': item.get('estatusEmbudo', ''),
        'tipo_negocio': item.get('tipoDeNegocio', ''),
        'motivo_no_cierre': item.get('motivoNoCierre', ''),
        'autorizacion_dg': item.get('autorizacionDG', 'Normal'),
        'editable': item.get('editable', 'true') == 'true',

        # Fechas
        'fecha_contacto': fecha_or_null(item.get('fechaContacto')),
        'fecha_entrega_riesgos': fecha_or_null(item.get('fechaEntregaARiesgos')),
        'fecha_propuesta': fecha_or_null(item.get('fechaPropuesta')),
        'fecha_primer_solicitud_vobo': fecha_or_null(item.get('fechaPrimerSolicitudVoBo')),
        'fecha_segunda_solicitud_vobo': fecha_or_null(item.get('fechaSegundaSolicitudVoBo')),
        'fecha_tercera_solicitud_vobo': fecha_or_null(item.get('fechaTercerSolicitudVoBo')),
        'fecha_vobo': fecha_or_null(item.get('fechaVoBo')),
        'fecha_rechazo_riesgos': fecha_or_null(item.get('fechaRechazoRiesgos')),
        'fecha_contrato_impreso': fecha_or_null(item.get('fechaContratoImpreso')),
        'fecha_autorizacion_dg': fecha_or_null(item.get('fechaAutorizacionDG')),
        'fecha_rechazo_dg': fecha_or_null(item.get('fechaRechazoDG')),
        'fecha_cancelacion_cartera': fecha_or_null(item.get('fechaCancelacionCartera')),
        'fecha_entrega_contrato_firmado': fecha_or_null(item.get('fechaEntregaContratoFirmado')),
        'fecha_fondeado': fecha_or_null(item.get('fechaFondeado')),
        'fecha_cancelacion_cliente': fecha_or_null(item.get('fechaCancelacionCliente')),
        'fecha_validacion_clabe': fecha_or_null(item.get('fechaValidacionClabe')),
        'fecha_rechazo': fecha_or_null(item.get('fechaRechazo')),
        'fecha_revision_documental_concluida': fecha_or_null(item.get('fechaRevisionDocumentalConluida')),

        # Ownership
        'owner_id': item.get('ownerID', ''),
        'inherited_id': item.get('inheritedID', None),
        'asesor_nombre': item.get('asesorNombre', ''),
        'region_nombre': item.get('regionNombre', ''),
        'usuario_autorizacion_riesgos': item.get('usuarioAutorizacionRiesgos', ''),

        # Cobranza
        'cliente_referencia_cobranza': item.get('clienteReferenciaCobranza', ''),
        'fecha_referencia_cobranza': fecha_or_null(item.get('fechaReferenciaCobranza')),

        # Metadata
        'view_name': item.get('viewName', ''),
        'forbidden': json.dumps(item.get('forbidden', []))
    }

def transform_log(item):
    """Transforma datos de log de JSON a formato SQL"""
    timestamp = item.get('timeStamp', '')
    try:
        timestamp_dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
    except:
        try:
            timestamp_dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except:
            timestamp_dt = datetime.now()

    return {
        'objeto': item.get('Objeto', ''),
        'accion': item.get('accion', ''),
        'log_data': json.dumps(item.get('logData', {})),
        'timestamp': timestamp_dt,
        'user_id': item.get('logData', {}).get('ownerID', None)
    }

def transform_geolocalizacion(item):
    """Transforma datos de geolocalización de JSON a formato SQL"""
    def fecha_or_null(fecha_str):
        if not fecha_str:
            return None
        try:
            return datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None

    return {
        'usuario': item.get('usuario', ''),
        'owner_id': item.get('ownerID', None),
        'latitud': float(item.get('latitud', 0)) if item.get('latitud') else None,
        'longitud': float(item.get('longitud', 0)) if item.get('longitud') else None,
        'fecha': fecha_or_null(item.get('fecha')),
        'datos_adicionales': json.dumps({k: v for k, v in item.items()
                                        if k not in ['id', 'usuario', 'ownerID', 'latitud', 'longitud', 'fecha']})
    }

def transform_acl(item):
    """Transforma datos de ACL de JSON a formato SQL"""
    return {
        'user_id': item.get('userID', None),
        'resource': item.get('resource', ''),
        'permission': item.get('permission', ''),
        'datos': json.dumps({k: v for k, v in item.items()
                           if k not in ['id', 'userID', 'resource', 'permission']})
    }

def transform_agenda(item):
    """Transforma datos de agenda de JSON a formato SQL"""
    def fecha_or_null(fecha_str):
        if not fecha_str:
            return None
        try:
            return datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None

    return {
        'owner_id': item.get('ownerID', None),
        'titulo': item.get('titulo', ''),
        'descripcion': item.get('descripcion', ''),
        'fecha': fecha_or_null(item.get('fecha')),
        'datos': json.dumps({k: v for k, v in item.items()
                           if k not in ['id', 'ownerID', 'titulo', 'descripcion', 'fecha']})
    }

def transform_pagadora(item):
    """Transforma datos de pagadora de JSON a formato SQL"""
    return {
        'nombre': item.get('nombre', ''),
        'datos': json.dumps({k: v for k, v in item.items() if k not in ['id', 'nombre']})
    }

def transform_roip(item):
    """Transforma datos de ROIP de JSON a formato SQL"""
    def fecha_or_null(fecha_str):
        if not fecha_str:
            return None
        try:
            return datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None

    return {
        'reportado_por': item.get('reportadoPor', ''),
        'owner_id': item.get('ownerID', None),
        'fecha_reporte': fecha_or_null(item.get('fechaReporte')),
        'fecha_dictaminacion': fecha_or_null(item.get('fechaDictaminacion')),
        'fecha_reporte_siti': fecha_or_null(item.get('fechaReporteSITI')),
        'documentos': item.get('documentos', ''),
        'reporte_estatus': item.get('reporteEstatus', 'abierto'),
        'datos': json.dumps({k: v for k, v in item.items()
                           if k not in ['id', 'reportadoPor', 'ownerID', 'fechaReporte',
                                       'fechaDictaminacion', 'fechaReporteSITI', 'documentos', 'reporteEstatus']})
    }

def transform_cosecha(item):
    """Transforma datos de cosecha de JSON a formato SQL"""
    return {
        'periodo': item.get('periodo', ''),
        'datos': json.dumps(item)
    }

# Mapeo de transformadores
TRANSFORMERS = {
    'usuarios': transform_usuario,
    'empresas': transform_empresa,
    'solicitudes': transform_solicitud,
    'logs': transform_log,
    'geolocalizaciones': transform_geolocalizacion,
    'acl': transform_acl,
    'agendas': transform_agenda,
    'pagadoras': transform_pagadora,
    'operaciones_internas_preocupantes': transform_roip,
    'cosechas': transform_cosecha
}

# ============================================================================
# FUNCIONES DE MIGRACIÓN
# ============================================================================

def build_insert_query(table, data):
    """Construye query INSERT dinámicamente"""
    columns = list(data.keys())
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join(columns)

    query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
    return query, tuple(data.values())

def migrate_table(json_file, table_name, batch_size=1000, dry_run=False):
    """
    Migra una tabla específica

    Args:
        json_file: Nombre del archivo JSON
        table_name: Nombre de la tabla destino
        batch_size: Tamaño del batch para inserts
        dry_run: Si es True, solo simula sin guardar

    Returns:
        Número de registros migrados
    """
    file_path = os.path.join(WORKING_DIR, json_file)

    if not os.path.exists(file_path):
        print(f"⚠️  Archivo no encontrado: {file_path}")
        return 0

    print(f"\n📦 Migrando {json_file} → {table_name}")

    # Cargar datos
    data = decrypt_json_file(file_path)
    if data is None:
        print(f"❌ Error al cargar {json_file}")
        return 0

    # Si data es una lista vacía o el primer elemento está vacío, skip
    if not data or (isinstance(data, list) and len(data) > 0 and not data[0]):
        # Saltar primer elemento vacío si existe
        if isinstance(data, list) and len(data) > 0 and not data[0]:
            data = data[1:]

    if not data:
        print(f"⚠️  {json_file} está vacío")
        return 0

    print(f"   Total de registros: {len(data)}")

    # Obtener transformador
    transformer = TRANSFORMERS.get(table_name)
    if not transformer:
        print(f"❌ No hay transformador para {table_name}")
        return 0

    # Transformar y migrar en batches
    migrated = 0
    errors = 0

    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        batch_queries = []

        for item in batch:
            try:
                transformed = transformer(item)
                query, params = build_insert_query(table_name, transformed)
                batch_queries.append((query, params))
            except Exception as e:
                errors += 1
                if errors <= 5:  # Mostrar solo primeros 5 errores
                    print(f"   ⚠️  Error transformando registro: {e}")

        # Ejecutar batch
        if not dry_run and batch_queries:
            try:
                for query, params in batch_queries:
                    execute_query(query, params)
                migrated += len(batch_queries)
                print(f"   ✅ Migrados {migrated}/{len(data)} registros", end='\r')
            except Exception as e:
                print(f"\n   ❌ Error ejecutando batch: {e}")
                errors += len(batch_queries)
        elif dry_run:
            migrated += len(batch_queries)
            print(f"   [DRY-RUN] Procesados {migrated}/{len(data)} registros", end='\r')

    print()  # Nueva línea

    if errors > 0:
        print(f"   ⚠️  {errors} registros con errores")

    return migrated

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Migración de JSON a PostgreSQL')
    parser.add_argument('--dry-run', action='store_true', help='Simular migración sin guardar')
    parser.add_argument('--batch-size', type=int, default=1000, help='Tamaño del batch')
    parser.add_argument('--skip-table', action='append', help='Tabla a omitir')
    args = parser.parse_args()

    print("=" * 70)
    print("  MIGRACIÓN DE DATOS: JSON Encriptado → PostgreSQL")
    print("=" * 70)

    if args.dry_run:
        print("\n🔍 MODO DRY-RUN: No se guardarán cambios\n")

    # Verificar conexión
    print("🔌 Verificando conexión a PostgreSQL...")
    if not initialize_pool():
        print("❌ No se pudo conectar a la base de datos")
        sys.exit(1)

    if not check_database_connection():
        print("❌ La base de datos no responde")
        sys.exit(1)

    print("✅ Conexión exitosa\n")

    # Migrar cada tabla
    total_migrated = 0
    skip_tables = args.skip_table or []

    for json_file, table_name in FILE_TO_TABLE_MAP.items():
        if table_name in skip_tables:
            print(f"\n⏭️  Saltando {table_name}")
            continue

        try:
            count = migrate_table(json_file, table_name, args.batch_size, args.dry_run)
            total_migrated += count
        except Exception as e:
            print(f"❌ Error migrando {table_name}: {e}")

    # Resumen
    print("\n" + "=" * 70)
    print(f"✅ MIGRACIÓN COMPLETADA")
    print(f"   Total de registros migrados: {total_migrated}")

    if args.dry_run:
        print("\n⚠️  RECUERDA: Esto fue un dry-run. Ejecuta sin --dry-run para guardar.")

    print("=" * 70)

if __name__ == '__main__':
    main()
