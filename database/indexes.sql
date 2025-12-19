-- ============================================================================
-- PIPEENLINEA - PostgreSQL Indexes for Performance
-- ============================================================================
-- Este archivo crea índices para optimizar las queries más frecuentes
-- ============================================================================

-- ============================================================================
-- ÍNDICES: usuarios
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_usuarios_owner_id ON usuarios(owner_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_correo ON usuarios(correo);
CREATE INDEX IF NOT EXISTS idx_usuarios_region ON usuarios(region);
CREATE INDEX IF NOT EXISTS idx_usuarios_active ON usuarios(active) WHERE active = true;

-- ============================================================================
-- ÍNDICES: empresas
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_empresas_nombre ON empresas(nombre);
CREATE INDEX IF NOT EXISTS idx_empresas_owner_id ON empresas(owner_id);
CREATE INDEX IF NOT EXISTS idx_empresas_restringida ON empresas(restringida) WHERE restringida = true;

-- Índice para búsqueda case-insensitive
CREATE INDEX IF NOT EXISTS idx_empresas_nombre_lower ON empresas(LOWER(nombre));

-- ============================================================================
-- ÍNDICES: solicitudes (CRÍTICOS PARA PERFORMANCE)
-- ============================================================================

-- Índices de estados y workflow
CREATE INDEX IF NOT EXISTS idx_solicitudes_estatus ON solicitudes(solicitud_estatus);
CREATE INDEX IF NOT EXISTS idx_solicitudes_etapa_estatus ON solicitudes(etapa_embudo, estatus_embudo);
CREATE INDEX IF NOT EXISTS idx_solicitudes_tipo_negocio ON solicitudes(tipo_negocio);

-- Índices de fechas (más usadas)
CREATE INDEX IF NOT EXISTS idx_solicitudes_fecha_contacto ON solicitudes(fecha_contacto DESC);
CREATE INDEX IF NOT EXISTS idx_solicitudes_fecha_entrega_riesgos ON solicitudes(fecha_entrega_riesgos DESC);
CREATE INDEX IF NOT EXISTS idx_solicitudes_fecha_fondeado ON solicitudes(fecha_fondeado DESC);
CREATE INDEX IF NOT EXISTS idx_solicitudes_created_at ON solicitudes(created_at DESC);

-- Índices de ownership
CREATE INDEX IF NOT EXISTS idx_solicitudes_owner_id ON solicitudes(owner_id);
CREATE INDEX IF NOT EXISTS idx_solicitudes_inherited_id ON solicitudes(inherited_id);

-- Índices de cliente
CREATE INDEX IF NOT EXISTS idx_solicitudes_cliente_nombre ON solicitudes(cliente_nombre);
CREATE INDEX IF NOT EXISTS idx_solicitudes_cliente_empresa ON solicitudes(cliente_empresa);
CREATE INDEX IF NOT EXISTS idx_solicitudes_numero_control ON solicitudes(numero_control);

-- Índice para búsqueda de nombre completo (case-insensitive)
CREATE INDEX IF NOT EXISTS idx_solicitudes_cliente_nombre_lower ON solicitudes(
    LOWER(cliente_nombre),
    LOWER(cliente_apellido_paterno),
    LOWER(cliente_apellido_materno)
);

-- Índice compuesto para filtros comunes
CREATE INDEX IF NOT EXISTS idx_solicitudes_owner_estatus_fecha ON solicitudes(
    owner_id,
    solicitud_estatus,
    fecha_contacto DESC
);

-- Índice para solicitudes activas (excluye fondeadas y rechazadas)
CREATE INDEX IF NOT EXISTS idx_solicitudes_activas ON solicitudes(owner_id, fecha_contacto DESC)
    WHERE solicitud_estatus NOT IN ('FONDEADO', 'RECHAZADO');

-- Índice para región y asesor
CREATE INDEX IF NOT EXISTS idx_solicitudes_region_asesor ON solicitudes(region_nombre, asesor_nombre);

-- Índice para autorización DG pendientes
CREATE INDEX IF NOT EXISTS idx_solicitudes_autorizacion_dg ON solicitudes(autorizacion_dg, fecha_propuesta DESC)
    WHERE autorizacion_dg = 'Requerida' AND fecha_autorizacion_dg IS NULL;

-- ============================================================================
-- ÍNDICES: logs (para auditoría y reportes)
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_objeto ON logs(objeto);
CREATE INDEX IF NOT EXISTS idx_logs_accion ON logs(accion);
CREATE INDEX IF NOT EXISTS idx_logs_user_id ON logs(user_id);
CREATE INDEX IF NOT EXISTS idx_logs_objeto_timestamp ON logs(objeto, timestamp DESC);

-- Índice GIN para búsqueda en JSONB
CREATE INDEX IF NOT EXISTS idx_logs_data_gin ON logs USING GIN (log_data);

-- ============================================================================
-- ÍNDICES: geolocalizaciones
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_geolocalizaciones_owner_id ON geolocalizaciones(owner_id);
CREATE INDEX IF NOT EXISTS idx_geolocalizaciones_fecha ON geolocalizaciones(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_geolocalizaciones_owner_fecha ON geolocalizaciones(owner_id, fecha DESC);

-- Índice espacial para búsquedas geográficas (requiere PostGIS si se usa)
-- CREATE INDEX IF NOT EXISTS idx_geolocalizaciones_coords ON geolocalizaciones USING GIST (
--     ll_to_earth(latitud, longitud)
-- );

-- ============================================================================
-- ÍNDICES: acl
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_acl_user_id ON acl(user_id);
CREATE INDEX IF NOT EXISTS idx_acl_resource ON acl(resource);
CREATE INDEX IF NOT EXISTS idx_acl_user_resource ON acl(user_id, resource);

-- ============================================================================
-- ÍNDICES: agendas
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_agendas_owner_id ON agendas(owner_id);
CREATE INDEX IF NOT EXISTS idx_agendas_fecha ON agendas(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_agendas_owner_fecha ON agendas(owner_id, fecha DESC);

-- ============================================================================
-- ÍNDICES: operaciones_internas_preocupantes
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_roip_estatus ON operaciones_internas_preocupantes(reporte_estatus);
CREATE INDEX IF NOT EXISTS idx_roip_fecha_reporte ON operaciones_internas_preocupantes(fecha_reporte DESC);
CREATE INDEX IF NOT EXISTS idx_roip_owner_id ON operaciones_internas_preocupantes(owner_id);

-- ============================================================================
-- ÍNDICES: cosechas
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_cosechas_periodo ON cosechas(periodo);
CREATE INDEX IF NOT EXISTS idx_cosechas_created_at ON cosechas(created_at DESC);

-- Índice GIN para búsqueda en datos JSON
CREATE INDEX IF NOT EXISTS idx_cosechas_datos_gin ON cosechas USING GIN (datos);

-- ============================================================================
-- ÍNDICES: pagadoras
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_pagadoras_nombre ON pagadoras(nombre);

-- ============================================================================
-- STATISTICS para optimización del query planner
-- ============================================================================

-- Incrementar estadísticas en columnas críticas
ALTER TABLE solicitudes ALTER COLUMN solicitud_estatus SET STATISTICS 1000;
ALTER TABLE solicitudes ALTER COLUMN owner_id SET STATISTICS 1000;
ALTER TABLE solicitudes ALTER COLUMN cliente_empresa SET STATISTICS 500;

ALTER TABLE logs ALTER COLUMN timestamp SET STATISTICS 1000;
ALTER TABLE logs ALTER COLUMN objeto SET STATISTICS 500;

-- ============================================================================
-- VACUUM y ANALYZE inicial
-- ============================================================================

-- Esto se ejecutará automáticamente después de la migración
-- VACUUM ANALYZE usuarios;
-- VACUUM ANALYZE empresas;
-- VACUUM ANALYZE solicitudes;
-- VACUUM ANALYZE logs;

-- ============================================================================
-- FIN DE ÍNDICES
-- ============================================================================
