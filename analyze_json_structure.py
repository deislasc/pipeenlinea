#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analizar la estructura real de los archivos JSON encriptados
y generar un schema SQL completo.
"""

import json
import os
from cryptography.fernet import Fernet
from datetime import datetime
from decimal import Decimal

def load_key():
    """Carga la clave de encriptación"""
    return open("secret.key", "rb").read()

def decrypt_file(encrypted_data):
    """Desencripta datos encriptados"""
    key = load_key()
    f = Fernet(key)

    try:
        decrypted_data = f.decrypt(encrypted_data)
    except:
        return None

    json_str = decrypted_data.decode('utf-8')
    json_object = json.loads(json_str)
    return json_object

def reloadJSONData(fileName):
    """Lee y desencripta un archivo JSON"""
    with open(fileName, 'rb') as f:
        data = f.read()
        f.close()

    json_object = decrypt_file(data)

    if json_object is None:
        print(f"❌ Error: Archivo corrupto {fileName}")
        return None
    else:
        return json_object

def infer_sql_type(value, key_name=""):
    """Infiere el tipo SQL desde un valor Python"""
    if value is None or value == "":
        # Para campos vacíos, intentar inferir del nombre
        if "fecha" in key_name.lower() or "date" in key_name.lower():
            return "TIMESTAMP"
        if "id" in key_name.lower():
            return "VARCHAR(100)"
        return "TEXT"

    if isinstance(value, bool):
        return "BOOLEAN"
    elif isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float) or isinstance(value, Decimal):
        return "DECIMAL(15,2)"
    elif isinstance(value, list):
        return "JSONB"
    elif isinstance(value, dict):
        return "JSONB"
    elif isinstance(value, str):
        # Intentar detectar si es fecha
        if "fecha" in key_name.lower() or "timestamp" in key_name.lower():
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
                return "TIMESTAMP"
            except:
                pass

        # Por longitud
        if len(value) > 500:
            return "TEXT"
        elif len(value) > 255:
            return "VARCHAR(500)"
        else:
            return "VARCHAR(255)"
    else:
        return "TEXT"

def analyze_json_structure(file_path, table_name):
    """Analiza la estructura de un archivo JSON"""
    print(f"\n{'='*80}")
    print(f"📋 Analizando: {file_path} → Tabla: {table_name}")
    print(f"{'='*80}")

    data = reloadJSONData(file_path)

    if data is None:
        print("❌ No se pudo leer el archivo")
        return None

    if len(data) <= 1:
        print("⚠️  Archivo vacío o solo tiene header")
        return None

    # Saltar el primer elemento (header vacío)
    records = data[1:] if data[0] == {} else data

    if len(records) == 0:
        print("⚠️  No hay registros")
        return None

    print(f"✅ Total de registros: {len(records)}")

    # Analizar múltiples registros para obtener todos los campos
    all_keys = set()
    sample_values = {}

    # Analizar los primeros 10 registros (o todos si hay menos)
    sample_size = min(10, len(records))
    for record in records[:sample_size]:
        if isinstance(record, dict):
            for key in record.keys():
                all_keys.add(key)
                # Guardar un valor de ejemplo no vacío
                if key not in sample_values and record[key] not in [None, "", [], {}]:
                    sample_values[key] = record[key]

    # Si no tenemos valores de ejemplo, tomar del primer registro
    if not sample_values and len(records) > 0:
        sample_values = records[0]

    # Generar definición de columnas
    columns = []
    for key in sorted(all_keys):
        value = sample_values.get(key, "")
        sql_type = infer_sql_type(value, key)
        columns.append({
            'name': key,
            'type': sql_type,
            'sample': value
        })

    print(f"\n📊 Campos encontrados ({len(columns)}):")
    print(f"{'Campo':<30} {'Tipo SQL':<20} {'Valor de ejemplo':<30}")
    print(f"{'-'*80}")
    for col in columns:
        sample_str = str(col['sample'])[:50] if col['sample'] not in [None, ""] else "(vacío)"
        print(f"{col['name']:<30} {col['type']:<20} {sample_str:<30}")

    return {
        'table_name': table_name,
        'columns': columns,
        'total_records': len(records)
    }

def generate_sql_schema(analyses):
    """Genera el schema SQL completo basado en los análisis"""

    sql_parts = []

    sql_parts.append("""-- =====================================================
-- Schema Completo - Generado desde estructura real JSON
-- Generado: {}
-- =====================================================

-- Eliminar tablas existentes
DROP TABLE IF EXISTS geolocalizaciones CASCADE;
DROP TABLE IF EXISTS acl CASCADE;
DROP TABLE IF EXISTS agendas CASCADE;
DROP TABLE IF EXISTS logs CASCADE;
DROP TABLE IF EXISTS solicitudes CASCADE;
DROP TABLE IF EXISTS operaciones_internas_preocupantes CASCADE;
DROP TABLE IF EXISTS empresas CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    # Generar CREATE TABLE para cada tabla
    for analysis in analyses:
        if analysis is None:
            continue

        table_name = analysis['table_name']
        columns = analysis['columns']

        sql_parts.append(f"-- Tabla: {table_name} ({analysis['total_records']} registros)")
        sql_parts.append(f"CREATE TABLE {table_name} (")

        col_definitions = []
        primary_key = None

        for col in columns:
            col_name = col['name']
            col_type = col['type']

            # Determinar si es PRIMARY KEY
            if col_name in ['owner_id', 'id', 'empresa_id', 'solicitud_id', 'log_id', 'roip_id', 'geo_id', 'acl_id', 'agenda_id']:
                if primary_key is None:  # Solo una PK por tabla
                    primary_key = col_name
                    col_definitions.append(f"    {col_name} {col_type} PRIMARY KEY")
                else:
                    col_definitions.append(f"    {col_name} {col_type}")
            else:
                col_definitions.append(f"    {col_name} {col_type}")

        # Agregar timestamps si no existen
        has_created = any(c['name'] in ['created_at', 'createdAt'] for c in columns)
        has_updated = any(c['name'] in ['updated_at', 'updatedAt'] for c in columns)

        if not has_created:
            col_definitions.append(f"    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        if not has_updated:
            col_definitions.append(f"    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

        sql_parts.append(",\n".join(col_definitions))
        sql_parts.append(");\n")

        # Crear índices para campos comunes
        index_fields = [c['name'] for c in columns if 'id' in c['name'].lower() and c['name'] != primary_key]
        for field in index_fields[:3]:  # Máximo 3 índices por tabla
            sql_parts.append(f"CREATE INDEX idx_{table_name}_{field} ON {table_name}({field});")

        sql_parts.append("\n")

    return "\n".join(sql_parts)

def main():
    """Función principal"""

    print("""
╔════════════════════════════════════════════════════════════════╗
║  Análisis de Estructura JSON → Schema PostgreSQL Completo     ║
╚════════════════════════════════════════════════════════════════╝
""")

    # Archivos a analizar
    files_to_analyze = [
        ('working/users.json', 'usuarios'),
        ('working/empresas.json', 'empresas'),
        ('working/solicitudes.json', 'solicitudes'),
        ('working/logs.json', 'logs'),
        ('working/geolocations.json', 'geolocalizaciones'),
        ('working/acl.json', 'acl'),
        ('working/agendas.json', 'agendas'),
        ('working/roips.json', 'operaciones_internas_preocupantes'),
    ]

    analyses = []

    for file_path, table_name in files_to_analyze:
        if os.path.exists(file_path):
            analysis = analyze_json_structure(file_path, table_name)
            analyses.append(analysis)
        else:
            print(f"\n⚠️  Archivo no encontrado: {file_path}")
            analyses.append(None)

    # Generar schema SQL
    print("\n" + "="*80)
    print("🔧 Generando schema SQL completo...")
    print("="*80)

    sql_schema = generate_sql_schema(analyses)

    # Guardar a archivo
    output_file = "database/schema_completo.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_schema)

    print(f"\n✅ Schema SQL generado: {output_file}")
    print(f"📝 Total de tablas: {sum(1 for a in analyses if a is not None)}")

    # Mostrar resumen
    print("\n" + "="*80)
    print("📊 RESUMEN DE REGISTROS POR TABLA:")
    print("="*80)
    for analysis in analyses:
        if analysis:
            print(f"  • {analysis['table_name']:<40} {analysis['total_records']:>10} registros")

    print("\n✨ Proceso completado. Ahora puedes usar schema_completo.sql para la migración.")

if __name__ == "__main__":
    main()
