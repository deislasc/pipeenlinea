#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE MIGRACIÓN V2: JSON Encriptado → PostgreSQL
====================================================
Migra datos usando los nombres EXACTOS de las columnas del schema_completo.sql
Sin transformaciones - mapeo directo de JSON a PostgreSQL
"""

import sys
import os
import json
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

# Mapeo de archivos JSON a tablas y sus columnas exactas
MIGRATIONS = {
    'users.json': {
        'table': 'usuarios',
        'pk': 'ownerID',
        'columns': ['ownerID', 'acl', 'apiKey', 'correo', 'hash', 'name',
                   'password', 'puesto', 'randomKey', 'region',
                   'tipoUsuario', 'userEstatus', 'userName']
    },
    'empresas.json': {
        'table': 'empresas',
        'pk': 'id',
        'columns': ['id', 'agrupacion', 'asesor', 'autorizacionDG', 'empresaPagadora',
                   'empresaSegmentacionCobranza', 'estatus', 'nombre', 'ownerID',
                   'region', 'tipo', 'userID_10', 'userID_14', 'userID_30',
                   'userID_52', 'userID_59', 'userID_65', 'userID_9', 'voboRequerido']
    },
    'solicitudes.json': {
        'table': 'solicitudes',
        'pk': 'id',
        'columns': ['id', 'asesorNombre', 'autorizacionDG', 'clienteAntiguedad',
                   'clienteApellidoMaterno', 'clienteApellidoPaterno', 'clienteClabe',
                   'clienteCorreoJefe', 'clienteEmpresa', 'clienteNombre',
                   'clienteNombreJefe', 'clienteNuevoRenovacion', 'clientePuesto',
                   'clienteReferenciaCobranza', 'clienteSalario', 'clienteSeEnteroPor',
                   'comentarios', 'documentos', 'editable', 'estatusEmbudo',
                   'etapaEmbudo', 'fechaAutorizacionDG', 'fechaCancelacionCartera',
                   'fechaCancelacionCliente', 'fechaContacto', 'fechaContratoImpreso',
                   'fechaEntregaARiesgos', 'fechaEntregaContratoFirmado', 'fechaFondeado',
                   'fechaPrimerSolicitudVoBo', 'fechaPropuesta', 'fechaRechazo',
                   'fechaRechazoDG', 'fechaRechazoRiesgos', 'fechaReferenciaCobranza',
                   'fechaSegundaSolicitudVoBo', 'fechaTercerSolicitudVoBo',
                   'fechaValidacionClabe', 'fechaVoBo', 'inheritedID',
                   'montoAutorizado', 'montoSolicitado', 'montoTransferencia',
                   'motivoNoCierre', 'oldID', 'ownerID', 'plazoAutorizado',
                   'plazoSolicitado', 'polizaSeguro', 'producto', 'regionNombre',
                   'solicitudEstatus', 'solicitudNumeroControl', 'tipoDeNegocio',
                   'usuarioAutorizacionRiesgos', 'viewName']
    },
    'logs.json': {
        'table': 'logs',
        'pk': None,  # SERIAL auto-generado
        'columns': ['Objeto', 'accion', 'logData', 'timeStamp']
    },
    'geolocations.json': {
        'table': 'geolocalizaciones',
        'pk': 'id',
        'columns': ['id', 'coords', 'fecha', 'ownerID', 'usuario', 'viewName', 'visita']
    },
    'acl.json': {
        'table': 'acl',
        'pk': None,  # SERIAL auto-generado
        'columns': ['acl', 'forbidden', 'scope']
    },
    'agendas.json': {
        'table': 'agendas',
        'pk': None,  # SERIAL auto-generado
        'columns': ['actividad', 'clienteNombre', 'clienteNuevoRenovacion',
                   'comentarios', 'empresa', 'fecha', 'hora', 'ownerID',
                   'ubicacion', 'userName']
    },
    'roips.json': {
        'table': 'operaciones_internas_preocupantes',
        'pk': 'id',
        'columns': ['id', 'documentos', 'fechaDictaminacion', 'fechaReporte',
                   'fechaReporteSITI', 'inheritedID', 'ownerID', 'reportadoPor',
                   'reporteEstatus', 'roi', 'viewName']
    }
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
    """Desencripta y carga un archivo JSON"""
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
# FUNCIONES DE MIGRACIÓN
# ============================================================================

def convert_value(value, column_name):
    """Convierte valores al tipo apropiado para PostgreSQL"""
    # Si es None o vacío, retornar None
    if value is None or value == '':
        return None

    # Manejar campos de fecha primero (antes de listas/dicts)
    if 'fecha' in column_name.lower() or column_name == 'timeStamp':
        # Si es lista o dict en campo de fecha, retornar None (datos inválidos)
        if isinstance(value, (list, dict)):
            return None

        if isinstance(value, str):
            # Intentar parsear diferentes formatos de fecha
            for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                try:
                    return datetime.strptime(value, fmt)
                except:
                    continue
            # Si no pudo parsear, retornar None
            return None
        elif isinstance(value, datetime):
            return value
        # Si es otro tipo en campo de fecha, retornar None
        return None

    # Si es lista o dict (y NO es campo de fecha), convertir a JSON
    if isinstance(value, (list, dict)):
        return json.dumps(value)

    # Retornar el valor tal cual
    return value

def migrate_table(file_name, config, batch_size=500):
    """
    Migra datos de un archivo JSON a una tabla PostgreSQL

    Args:
        file_name: Nombre del archivo JSON
        config: Configuración de la migración (tabla, columnas, etc.)
        batch_size: Tamaño del batch para inserción

    Returns:
        Tupla (éxitos, errores)
    """
    table_name = config['table']
    columns = config['columns']
    pk_column = config.get('pk')

    print(f"\n📦 Migrando {file_name} → {table_name}")

    # Cargar datos del JSON
    file_path = os.path.join(WORKING_DIR, file_name)
    if not os.path.exists(file_path):
        print(f"   ⚠️  Archivo no encontrado, omitiendo...")
        return 0, 0

    json_data = decrypt_json_file(file_path)
    if json_data is None:
        print(f"   ❌ Error al cargar {file_name}")
        return 0, 0

    # Saltar el primer elemento si es un objeto vacío (header)
    records = json_data[1:] if len(json_data) > 0 and json_data[0] == {} else json_data

    if len(records) == 0:
        print(f"   ⚠️  Sin registros para migrar")
        return 0, 0

    print(f"   Total de registros: {len(records)}")

    # Procesar en batches
    success_count = 0
    error_count = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_values = []

        for record in batch:
            if not isinstance(record, dict):
                continue

            # Extraer valores en el orden de las columnas
            values = []
            for col in columns:
                raw_value = record.get(col)
                converted_value = convert_value(raw_value, col)
                values.append(converted_value)

            batch_values.append(tuple(values))

        if not batch_values:
            continue

        # Construir query de inserción
        # PostgreSQL convierte nombres a lowercase automáticamente, usar sin comillas
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join([col.lower() for col in columns])  # Convertir a lowercase

        query = f"""
            INSERT INTO {table_name} ({columns_str})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """

        # Ejecutar batch
        try:
            execute_many(query, batch_values)
            success_count += len(batch_values)
            print(f"   ✅ Batch {i//batch_size + 1}: {len(batch_values)} registros")
        except Exception as e:
            error_count += len(batch_values)
            print(f"   ❌ Error en batch {i//batch_size + 1}: {e}")

    print(f"   📊 Resultado: {success_count} exitosos, {error_count} errores")
    return success_count, error_count

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal"""

    print("=" * 70)
    print("  MIGRACIÓN DE DATOS V2: JSON Encriptado → PostgreSQL")
    print("=" * 70)

    # Verificar conexión a PostgreSQL
    print("🔌 Verificando conexión a PostgreSQL...")
    if not initialize_pool():
        print("❌ No se pudo conectar a PostgreSQL")
        sys.exit(1)

    if not check_database_connection():
        print("❌ La base de datos no está disponible")
        sys.exit(1)

    print("✅ Conexión exitosa\n")

    # Migrar cada tabla
    total_success = 0
    total_errors = 0

    for file_name, config in MIGRATIONS.items():
        success, errors = migrate_table(file_name, config)
        total_success += success
        total_errors += errors

    # Reporte final
    print("\n" + "=" * 70)
    print("✅ MIGRACIÓN COMPLETADA")
    print(f"   Total de registros migrados: {total_success}")
    if total_errors > 0:
        print(f"   ⚠️  Total de errores: {total_errors}")
    print("=" * 70)

    return 0 if total_errors == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
