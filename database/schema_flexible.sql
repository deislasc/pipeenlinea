-- ============================================================================
-- SCHEMA FLEXIBLE PARA MIGRACIÓN COMPLETA
-- Acepta datos reales con inconsistencias
-- ============================================================================

-- Eliminar tablas existentes
DROP TABLE IF EXISTS geolocalizaciones CASCADE;
DROP TABLE IF EXISTS operaciones_internas_preocupantes CASCADE;
DROP TABLE IF EXISTS solicitudes CASCADE;
DROP TABLE IF EXISTS empresas CASCADE;
DROP TABLE IF EXISTS agendas CASCADE;
DROP TABLE IF EXISTS pagadoras CASCADE;
DROP TABLE IF EXISTS cosechas CASCADE;
DROP TABLE IF EXISTS acl CASCADE;
DROP TABLE IF EXISTS logs CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

-- ============================================================================
-- TABLA: usuarios
-- ============================================================================
CREATE TABLE usuarios (
    owner_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255),
    correo VARCHAR(255),  -- SIN UNIQUE, permite vacíos y duplicados
    hash TEXT,
    password_hash TEXT,
    random_key VARCHAR(255),
    api_key TEXT,
    region VARCHAR(100),
    puesto VARCHAR(100),
    telefono VARCHAR(50),
    celular VARCHAR(50),
    imagen_url TEXT,
    forbidden JSONB DEFAULT '[]',
    type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para búsquedas por correo (pero no UNIQUE)
CREATE INDEX idx_usuarios_correo ON usuarios(correo) WHERE correo IS NOT NULL AND correo != '';

-- ============================================================================
-- TABLA: empresas
-- ============================================================================
CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    rfc VARCHAR(20),
    owner_id VARCHAR(50),  -- SIN FOREIGN KEY, permite IDs inválidos
    asesor VARCHAR(255),
    sector VARCHAR(100),
    domicilio TEXT,
    telefono VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_empresas_owner ON empresas(owner_id);
CREATE INDEX idx_empresas_nombre ON empresas(nombre);

-- ============================================================================
-- TABLA: solicitudes
-- ============================================================================
CREATE TABLE solicitudes (
    id SERIAL PRIMARY KEY,
    cliente_nombre VARCHAR(255),
    cliente_empresa VARCHAR(255),
    cliente_rfc VARCHAR(20),
    owner_id VARCHAR(50),  -- SIN FOREIGN KEY
    inherited_id VARCHAR(50),
    region_nombre VARCHAR(100),
    asesor_nombre VARCHAR(255),

    -- Montos (permitir cualquier valor)
    monto_solicitado NUMERIC(15,2) DEFAULT 0,
    monto_autorizado NUMERIC(15,2) DEFAULT 0,
    monto_transferencia NUMERIC(15,2) DEFAULT 0,
    tasa NUMERIC(5,2),
    comision NUMERIC(15,2),
    plazo_solicitado VARCHAR(50),
    plazo_autorizado VARCHAR(50),

    -- Producto y tipo
    producto VARCHAR(100),
    tipo_operacion VARCHAR(100),
    autorizacion_dg VARCHAR(50),

    -- Estatus (SIN CHECK CONSTRAINT, acepta cualquier valor)
    solicitud_estatus VARCHAR(100),
    etapa_embudo VARCHAR(100),
    estatus_embudo VARCHAR(100),
    tipo_de_negocio VARCHAR(50),
    motivo_no_cierre TEXT,

    -- Fechas (todas opcionales)
    fecha_contacto TIMESTAMP,
    fecha_entrega_a_riesgos TIMESTAMP,
    fecha_propuesta TIMESTAMP,
    fecha_primer_solicitud_vobo TIMESTAMP,
    fecha_segunda_solicitud_vobo TIMESTAMP,
    fecha_tercer_solicitud_vobo TIMESTAMP,
    fecha_vobo TIMESTAMP,
    fecha_rechazo_riesgos TIMESTAMP,
    fecha_contrato_impreso TIMESTAMP,
    fecha_autorizacion_dg TIMESTAMP,
    fecha_rechazo_dg TIMESTAMP,
    fecha_cancelacion_cartera TIMESTAMP,
    fecha_entrega_contrato_firmado TIMESTAMP,
    fecha_fondeado TIMESTAMP,
    fecha_cancelacion_cliente TIMESTAMP,
    fecha_validacion_clabe TIMESTAMP,

    -- Otros campos
    editable VARCHAR(10),
    documentos JSONB DEFAULT '[]',
    observaciones TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_solicitudes_owner ON solicitudes(owner_id);
CREATE INDEX idx_solicitudes_estatus ON solicitudes(solicitud_estatus);
CREATE INDEX idx_solicitudes_cliente ON solicitudes(cliente_nombre);

-- ============================================================================
-- TABLA: logs
-- ============================================================================
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    objeto VARCHAR(100),
    accion VARCHAR(100),
    log_data JSONB,
    time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_timestamp ON logs(time_stamp DESC);
CREATE INDEX idx_logs_objeto ON logs(objeto);

-- ============================================================================
-- TABLA: geolocalizaciones
-- ============================================================================
CREATE TABLE geolocalizaciones (
    id SERIAL PRIMARY KEY,
    owner_id VARCHAR(50),  -- SIN FOREIGN KEY
    usuario VARCHAR(255),
    fecha TIMESTAMP,
    latitud NUMERIC(10, 7),
    longitud NUMERIC(10, 7),
    direccion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_geolocalizaciones_owner ON geolocalizaciones(owner_id);
CREATE INDEX idx_geolocalizaciones_fecha ON geolocalizaciones(fecha DESC);

-- ============================================================================
-- TABLA: acl (Access Control List)
-- ============================================================================
CREATE TABLE acl (
    id SERIAL PRIMARY KEY,
    view_name VARCHAR(255) UNIQUE,
    descripcion TEXT,
    permisos JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLA: agendas
-- ============================================================================
CREATE TABLE agendas (
    id SERIAL PRIMARY KEY,
    owner_id VARCHAR(50),  -- SIN FOREIGN KEY
    titulo VARCHAR(255),
    descripcion TEXT,
    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP,
    tipo VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agendas_owner ON agendas(owner_id);
CREATE INDEX idx_agendas_fecha ON agendas(fecha_inicio);

-- ============================================================================
-- TABLA: pagadoras
-- ============================================================================
CREATE TABLE pagadoras (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    rfc VARCHAR(20),
    datos JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLA: cosechas
-- ============================================================================
CREATE TABLE cosechas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    tipo VARCHAR(100),
    datos JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLA: operaciones_internas_preocupantes
-- ============================================================================
CREATE TABLE operaciones_internas_preocupantes (
    id SERIAL PRIMARY KEY,
    reportado_por VARCHAR(255),
    owner_id VARCHAR(50),  -- SIN FOREIGN KEY
    fecha_reporte TIMESTAMP,
    fecha_dictaminacion TIMESTAMP,
    fecha_reporte_siti TIMESTAMP,
    documentos TEXT,
    reporte_estatus VARCHAR(50),  -- SIN CHECK CONSTRAINT
    datos JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_roips_owner ON operaciones_internas_preocupantes(owner_id);
CREATE INDEX idx_roips_estatus ON operaciones_internas_preocupantes(reporte_estatus);
