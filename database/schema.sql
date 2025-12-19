-- ============================================================================
-- PIPEENLINEA - PostgreSQL Database Schema
-- ============================================================================
-- Encoding: UTF8
-- Locale: es_MX.UTF-8
-- PostgreSQL Version: 15+
-- ============================================================================

-- Set timezone
SET timezone = 'America/Mexico_City';

-- ============================================================================
-- TABLA: usuarios
-- Almacena información de usuarios del sistema
-- Migrado de: users.json (62KB)
-- ============================================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    owner_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    correo VARCHAR(255) UNIQUE NOT NULL,
    hash TEXT NOT NULL,
    password_hash TEXT,
    api_key TEXT,
    random_key VARCHAR(100),
    region VARCHAR(100),
    scope VARCHAR(50) DEFAULT 'self',
    forbidden JSONB DEFAULT '[]'::jsonb,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE usuarios IS 'Usuarios del sistema con autenticación y permisos';
COMMENT ON COLUMN usuarios.owner_id IS 'ID único del usuario (legacy)';
COMMENT ON COLUMN usuarios.scope IS 'Alcance de visibilidad: self o all';
COMMENT ON COLUMN usuarios.forbidden IS 'Array JSON de campos prohibidos para el usuario';

-- ============================================================================
-- TABLA: empresas
-- Almacena información de empresas/compañías
-- Migrado de: empresas.json (91KB)
-- ============================================================================
CREATE TABLE IF NOT EXISTS empresas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    owner_id VARCHAR(50),
    asesor VARCHAR(255),
    nivel_riesgo VARCHAR(50),
    restringida BOOLEAN DEFAULT false,
    datos_adicionales JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_empresas_owner FOREIGN KEY (owner_id)
        REFERENCES usuarios(owner_id) ON DELETE SET NULL
);

COMMENT ON TABLE empresas IS 'Empresas y compañías en el sistema';
COMMENT ON COLUMN empresas.restringida IS 'Indica si la empresa requiere autorización DG';
COMMENT ON COLUMN empresas.datos_adicionales IS 'Campos adicionales variables en formato JSON';

-- ============================================================================
-- TABLA: solicitudes
-- Almacena solicitudes de crédito (tabla principal)
-- Migrado de: solicitudes.json (67MB - ~miles de registros)
-- ============================================================================
CREATE TABLE IF NOT EXISTS solicitudes (
    id SERIAL PRIMARY KEY,
    numero_control VARCHAR(100),

    -- ====================
    -- INFORMACIÓN DEL CLIENTE
    -- ====================
    cliente_nombre VARCHAR(255),
    cliente_apellido_paterno VARCHAR(255),
    cliente_apellido_materno VARCHAR(255),
    cliente_empresa VARCHAR(255),
    cliente_salario DECIMAL(12,2) DEFAULT 0,
    cliente_deducciones_mensuales DECIMAL(12,2) DEFAULT 0,
    cliente_deducciones_periodo DECIMAL(12,2) DEFAULT 0,
    cliente_deducciones_quincenales DECIMAL(12,2) DEFAULT 0,
    cliente_deducciones_semanales DECIMAL(12,2) DEFAULT 0,

    -- ====================
    -- INFORMACIÓN DE LA SOLICITUD
    -- ====================
    producto VARCHAR(100),
    monto_solicitado DECIMAL(12,2) DEFAULT 0,
    monto_autorizado DECIMAL(12,2) DEFAULT 0,
    monto_transferencia DECIMAL(12,2) DEFAULT 0,
    plazo_autorizado INTEGER,
    linea_credito DECIMAL(12,2) DEFAULT 0,

    -- ====================
    -- ANÁLISIS CREDITICIO
    -- ====================
    monto_buen_buro DECIMAL(12,2) DEFAULT 0,
    monto_capacidad_pago DECIMAL(12,2) DEFAULT 0,
    monto_comision DECIMAL(12,2) DEFAULT 0,
    monto_comision_politica DECIMAL(12,2) DEFAULT 0,
    monto_maximo_politica DECIMAL(12,2) DEFAULT 0,
    monto_seguro DECIMAL(12,2) DEFAULT 0,
    monto_iva_comision DECIMAL(12,2) DEFAULT 0,
    monto_iva_seguro DECIMAL(12,2) DEFAULT 0,
    monto_propuesto DECIMAL(12,2) DEFAULT 0,
    monto_ministracion DECIMAL(12,2) DEFAULT 0,
    costo_seguro_parcialidad DECIMAL(12,2) DEFAULT 0,
    iva_intereses_simulador DECIMAL(12,2) DEFAULT 0,

    -- ====================
    -- WORKFLOW Y ESTADOS
    -- ====================
    solicitud_estatus VARCHAR(50) NOT NULL DEFAULT 'CONTACTO',
    etapa_embudo VARCHAR(50),
    estatus_embudo VARCHAR(50),
    tipo_negocio VARCHAR(50),
    motivo_no_cierre TEXT,
    autorizacion_dg VARCHAR(50) DEFAULT 'Normal',
    editable BOOLEAN DEFAULT true,

    -- ====================
    -- FECHAS DEL WORKFLOW
    -- ====================
    fecha_contacto TIMESTAMP WITH TIME ZONE,
    fecha_entrega_riesgos TIMESTAMP WITH TIME ZONE,
    fecha_propuesta TIMESTAMP WITH TIME ZONE,
    fecha_primer_solicitud_vobo TIMESTAMP WITH TIME ZONE,
    fecha_segunda_solicitud_vobo TIMESTAMP WITH TIME ZONE,
    fecha_tercera_solicitud_vobo TIMESTAMP WITH TIME ZONE,
    fecha_vobo TIMESTAMP WITH TIME ZONE,
    fecha_rechazo_riesgos TIMESTAMP WITH TIME ZONE,
    fecha_contrato_impreso TIMESTAMP WITH TIME ZONE,
    fecha_autorizacion_dg TIMESTAMP WITH TIME ZONE,
    fecha_rechazo_dg TIMESTAMP WITH TIME ZONE,
    fecha_cancelacion_cartera TIMESTAMP WITH TIME ZONE,
    fecha_entrega_contrato_firmado TIMESTAMP WITH TIME ZONE,
    fecha_fondeado TIMESTAMP WITH TIME ZONE,
    fecha_cancelacion_cliente TIMESTAMP WITH TIME ZONE,
    fecha_validacion_clabe TIMESTAMP WITH TIME ZONE,
    fecha_rechazo TIMESTAMP WITH TIME ZONE,
    fecha_revision_documental_concluida TIMESTAMP WITH TIME ZONE,

    -- ====================
    -- OWNERSHIP Y ASIGNACIÓN
    -- ====================
    owner_id VARCHAR(50) NOT NULL,
    inherited_id VARCHAR(50),
    asesor_nombre VARCHAR(255),
    region_nombre VARCHAR(100),
    usuario_autorizacion_riesgos VARCHAR(255),

    -- ====================
    -- COBRANZA
    -- ====================
    cliente_referencia_cobranza VARCHAR(255),
    fecha_referencia_cobranza TIMESTAMP WITH TIME ZONE,

    -- ====================
    -- METADATOS
    -- ====================
    view_name VARCHAR(100),
    forbidden JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_solicitudes_owner FOREIGN KEY (owner_id)
        REFERENCES usuarios(owner_id) ON DELETE RESTRICT,
    CONSTRAINT fk_solicitudes_inherited FOREIGN KEY (inherited_id)
        REFERENCES usuarios(owner_id) ON DELETE SET NULL,
    CONSTRAINT chk_solicitud_estatus CHECK (solicitud_estatus IN (
        'RECHAZADO', 'CONTACTO', 'ENTREGA A RIESGOS', 'AUTORIZADO',
        'EN AUTORIZACION DG', 'CONTRATO IMPRESO', 'FIRMAR CONTRATO', 'FONDEADO'
    )),
    CONSTRAINT chk_autorizacion_dg CHECK (autorizacion_dg IN ('Normal', 'Requerida')),
    CONSTRAINT chk_tipo_negocio CHECK (tipo_negocio IN ('ACTIVO', 'GANADO', 'PERDIDO'))
);

COMMENT ON TABLE solicitudes IS 'Solicitudes de crédito - tabla principal del sistema';
COMMENT ON COLUMN solicitudes.solicitud_estatus IS 'Estado actual en el workflow de aprobación';
COMMENT ON COLUMN solicitudes.autorizacion_dg IS 'Indica si requiere autorización de Dirección General';
COMMENT ON COLUMN solicitudes.forbidden IS 'Campos prohibidos para edición en análisis crediticio';

-- ============================================================================
-- TABLA: logs
-- Almacena auditoría de todas las acciones
-- Migrado de: logs.json (39MB)
-- ============================================================================
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    objeto VARCHAR(100),
    accion VARCHAR(50),
    log_data JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    user_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE logs IS 'Auditoría completa de acciones en el sistema';
COMMENT ON COLUMN logs.objeto IS 'Tipo de objeto: Solicitudes, Usuarios, Empresas, etc.';
COMMENT ON COLUMN logs.accion IS 'Acción realizada: agregar, actualización, etc.';

-- ============================================================================
-- TABLA: cosechas
-- Almacena análisis de cohorts/cosechas
-- Migrado de: cosechas.json (12MB)
-- ============================================================================
CREATE TABLE IF NOT EXISTS cosechas (
    id SERIAL PRIMARY KEY,
    periodo VARCHAR(50),
    datos JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE cosechas IS 'Análisis de cohorts por periodo';

-- ============================================================================
-- TABLA: geolocalizaciones
-- Almacena ubicaciones GPS de usuarios
-- Migrado de: geolocations.json (1MB)
-- ============================================================================
CREATE TABLE IF NOT EXISTS geolocalizaciones (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(255),
    owner_id VARCHAR(50),
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    fecha TIMESTAMP WITH TIME ZONE,
    datos_adicionales JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_geolocalizaciones_owner FOREIGN KEY (owner_id)
        REFERENCES usuarios(owner_id) ON DELETE CASCADE
);

COMMENT ON TABLE geolocalizaciones IS 'Geolocalización de usuarios para tracking de visitas';

-- ============================================================================
-- TABLA: acl
-- Access Control Lists - permisos granulares
-- Migrado de: acl.json (32KB)
-- ============================================================================
CREATE TABLE IF NOT EXISTS acl (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    resource VARCHAR(255),
    permission VARCHAR(100),
    datos JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_acl_user FOREIGN KEY (user_id)
        REFERENCES usuarios(owner_id) ON DELETE CASCADE
);

COMMENT ON TABLE acl IS 'Listas de control de acceso granular';

-- ============================================================================
-- TABLA: agendas
-- Citas y eventos agendados
-- Migrado de: agendas.json (2KB)
-- ============================================================================
CREATE TABLE IF NOT EXISTS agendas (
    id SERIAL PRIMARY KEY,
    owner_id VARCHAR(50),
    titulo VARCHAR(255),
    descripcion TEXT,
    fecha TIMESTAMP WITH TIME ZONE,
    datos JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_agendas_owner FOREIGN KEY (owner_id)
        REFERENCES usuarios(owner_id) ON DELETE CASCADE
);

COMMENT ON TABLE agendas IS 'Agendas y citas de usuarios';

-- ============================================================================
-- TABLA: pagadoras
-- Empresas pagadoras de nómina
-- Migrado de: pagadoras.json (2.7KB)
-- ============================================================================
CREATE TABLE IF NOT EXISTS pagadoras (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    datos JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE pagadoras IS 'Empresas pagadoras de nómina';

-- ============================================================================
-- TABLA: operaciones_internas_preocupantes
-- ROIPs - Reportes de Operaciones Internas Preocupantes
-- Migrado de: roips.json (2.3KB)
-- ============================================================================
CREATE TABLE IF NOT EXISTS operaciones_internas_preocupantes (
    id SERIAL PRIMARY KEY,
    reportado_por VARCHAR(255),
    owner_id VARCHAR(50),
    fecha_reporte TIMESTAMP WITH TIME ZONE,
    fecha_dictaminacion TIMESTAMP WITH TIME ZONE,
    fecha_reporte_siti TIMESTAMP WITH TIME ZONE,
    documentos TEXT,
    reporte_estatus VARCHAR(50) DEFAULT 'abierto',
    datos JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_roip_owner FOREIGN KEY (owner_id)
        REFERENCES usuarios(owner_id) ON DELETE SET NULL,
    CONSTRAINT chk_reporte_estatus CHECK (reporte_estatus IN ('abierto', 'dictaminado', 'reportado'))
);

COMMENT ON TABLE operaciones_internas_preocupantes IS 'Reportes de Operaciones Internas Preocupantes (ROIP)';

-- ============================================================================
-- TRIGGER: updated_at automático
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger a tablas relevantes
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_empresas_updated_at BEFORE UPDATE ON empresas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_solicitudes_updated_at BEFORE UPDATE ON solicitudes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cosechas_updated_at BEFORE UPDATE ON cosechas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- FIN DEL SCHEMA
-- ============================================================================
