# -*- coding: utf-8 -*-
"""
Database Connection Module - PostgreSQL with psycopg2
Módulo de conexión a base de datos usando SQL raw (sin ORM)
"""
import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor, Json
from contextlib import contextmanager
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://pipeenlinea_user:changeme123@localhost:5432/pipeenlinea'
)

# Pool de conexiones para mejor performance
MIN_CONNECTIONS = 2
MAX_CONNECTIONS = 20

# ============================================================================
# CONNECTION POOL
# ============================================================================

connection_pool = None

def initialize_pool():
    """
    Inicializa el pool de conexiones a PostgreSQL
    Se debe llamar al inicio de la aplicación
    """
    global connection_pool

    try:
        connection_pool = psycopg2.pool.ThreadedConnectionPool(
            MIN_CONNECTIONS,
            MAX_CONNECTIONS,
            DATABASE_URL,
            cursor_factory=RealDictCursor  # Devuelve filas como diccionarios
        )
        logger.info("✅ Pool de conexiones PostgreSQL inicializado correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error al inicializar pool de conexiones: {e}")
        return False

def close_pool():
    """
    Cierra el pool de conexiones
    Se debe llamar al cerrar la aplicación
    """
    global connection_pool

    if connection_pool:
        connection_pool.closeall()
        logger.info("Pool de conexiones cerrado")

# ============================================================================
# CONTEXT MANAGER PARA CONEXIONES
# ============================================================================

@contextmanager
def get_db_connection():
    """
    Context manager para obtener una conexión del pool

    Uso:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios")
            result = cursor.fetchall()
    """
    conn = None
    try:
        conn = connection_pool.getconn()
        yield conn
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Error de base de datos: {e}")
        raise
    finally:
        if conn:
            connection_pool.putconn(conn)

@contextmanager
def get_db_cursor(commit=True):
    """
    Context manager para obtener cursor directamente

    Parámetros:
        commit (bool): Si True, hace commit automático al finalizar

    Uso:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
            user = cursor.fetchone()
    """
    conn = None
    cursor = None
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        yield cursor
        if commit:
            conn.commit()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Error en query: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            connection_pool.putconn(conn)

# ============================================================================
# FUNCIONES DE UTILIDAD PARA QUERIES
# ============================================================================

def execute_query(query, params=None, fetch=False, fetch_one=False):
    """
    Ejecuta una query SQL

    Parámetros:
        query (str): Query SQL (usar %s para parámetros)
        params (tuple/dict): Parámetros para la query
        fetch (bool): Si True, devuelve todos los resultados
        fetch_one (bool): Si True, devuelve solo el primer resultado

    Retorna:
        - Si fetch=True: lista de diccionarios
        - Si fetch_one=True: diccionario o None
        - Si ninguno: número de filas afectadas

    Ejemplo:
        # INSERT
        execute_query(
            "INSERT INTO usuarios (name, correo) VALUES (%s, %s)",
            ("Juan Pérez", "juan@example.com")
        )

        # SELECT
        users = execute_query(
            "SELECT * FROM usuarios WHERE region = %s",
            ("Norte",),
            fetch=True
        )

        # SELECT ONE
        user = execute_query(
            "SELECT * FROM usuarios WHERE id = %s",
            (123,),
            fetch_one=True
        )
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())

        if fetch:
            return cursor.fetchall()
        elif fetch_one:
            return cursor.fetchone()
        else:
            return cursor.rowcount

def execute_many(query, params_list):
    """
    Ejecuta la misma query múltiples veces con diferentes parámetros
    Útil para inserts masivos

    Parámetros:
        query (str): Query SQL
        params_list (list): Lista de tuplas de parámetros

    Retorna:
        Número total de filas afectadas

    Ejemplo:
        execute_many(
            "INSERT INTO logs (objeto, accion) VALUES (%s, %s)",
            [
                ("Solicitud", "crear"),
                ("Usuario", "actualizar"),
                ("Empresa", "eliminar")
            ]
        )
    """
    with get_db_cursor() as cursor:
        cursor.executemany(query, params_list)
        return cursor.rowcount

def execute_transaction(queries_and_params):
    """
    Ejecuta múltiples queries en una transacción
    Si alguna falla, se hace rollback de todas

    Parámetros:
        queries_and_params (list): Lista de tuplas (query, params)

    Retorna:
        True si todo fue exitoso, False si hubo error

    Ejemplo:
        execute_transaction([
            ("UPDATE solicitudes SET monto = %s WHERE id = %s", (50000, 1)),
            ("INSERT INTO logs (objeto, accion) VALUES (%s, %s)", ("Solicitud", "actualizar"))
        ])
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            for query, params in queries_and_params:
                cursor.execute(query, params or ())
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            cursor.close()
            logger.error(f"Error en transacción: {e}")
            return False

# ============================================================================
# FUNCIONES DE MAPEO JSON <-> SQL
# ============================================================================

def dict_to_insert(table, data, returning="id"):
    """
    Convierte un diccionario en una query INSERT

    Parámetros:
        table (str): Nombre de la tabla
        data (dict): Datos a insertar
        returning (str): Campo a retornar (default: "id")

    Retorna:
        Tupla (query, params)

    Ejemplo:
        query, params = dict_to_insert("usuarios", {
            "name": "Juan",
            "correo": "juan@example.com"
        })
    """
    columns = list(data.keys())
    values = list(data.values())

    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join(columns)

    query = f"""
        INSERT INTO {table} ({columns_str})
        VALUES ({placeholders})
        RETURNING {returning}
    """

    return query, tuple(values)

def dict_to_update(table, data, where_field, where_value):
    """
    Convierte un diccionario en una query UPDATE

    Parámetros:
        table (str): Nombre de la tabla
        data (dict): Datos a actualizar
        where_field (str): Campo para WHERE
        where_value: Valor para WHERE

    Retorna:
        Tupla (query, params)

    Ejemplo:
        query, params = dict_to_update(
            "usuarios",
            {"name": "Juan Actualizado", "region": "Sur"},
            "id",
            123
        )
    """
    set_parts = [f"{key} = %s" for key in data.keys()]
    set_clause = ', '.join(set_parts)

    query = f"""
        UPDATE {table}
        SET {set_clause}
        WHERE {where_field} = %s
    """

    params = tuple(list(data.values()) + [where_value])

    return query, params

# ============================================================================
# FUNCIONES DE HEALTH CHECK
# ============================================================================

def check_database_connection():
    """
    Verifica que la conexión a la base de datos esté funcionando

    Retorna:
        True si la conexión es exitosa, False en caso contrario
    """
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        logger.error(f"Error al verificar conexión: {e}")
        return False

def get_database_stats():
    """
    Obtiene estadísticas de la base de datos

    Retorna:
        Diccionario con estadísticas
    """
    try:
        with get_db_cursor(commit=False) as cursor:
            stats = {}

            # Conteo de registros por tabla
            tables = [
                'usuarios', 'empresas', 'solicitudes', 'logs',
                'geolocalizaciones', 'acl', 'agendas', 'pagadoras',
                'operaciones_internas_preocupantes', 'cosechas'
            ]

            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                result = cursor.fetchone()
                stats[table] = result['count'] if result else 0

            # Tamaño de la base de datos
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """)
            result = cursor.fetchone()
            stats['database_size'] = result['size'] if result else 'N/A'

            return stats
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        return {}

# ============================================================================
# INICIALIZACIÓN AUTOMÁTICA
# ============================================================================

# Inicializar pool automáticamente al importar el módulo
# initialize_pool()  # Descomentar para auto-inicialización
