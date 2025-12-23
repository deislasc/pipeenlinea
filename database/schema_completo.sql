-- =====================================================
-- Schema Completo - Generado desde estructura real JSON
-- Generado: 2025-12-23 00:03:49
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


-- Tabla: usuarios (66 registros)
CREATE TABLE usuarios (
    ownerID INTEGER PRIMARY KEY,
    acl VARCHAR(255),
    apiKey VARCHAR(255),
    correo VARCHAR(255),
    hash VARCHAR(255),
    name VARCHAR(255),
    password VARCHAR(255),
    puesto VARCHAR(255),
    randomKey VARCHAR(255),
    region VARCHAR(255),
    tipoUsuario VARCHAR(255),
    userEstatus VARCHAR(255),
    userName VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usuarios_correo ON usuarios(correo);
CREATE INDEX idx_usuarios_userName ON usuarios(userName);


-- Tabla: empresas (156 registros)
CREATE TABLE empresas (
    agrupacion VARCHAR(255),
    asesor VARCHAR(255),
    autorizacionDG VARCHAR(255),
    empresaPagadora VARCHAR(255),
    empresaSegmentacionCobranza VARCHAR(255),
    estatus VARCHAR(255),
    id VARCHAR(255) PRIMARY KEY,
    nombre VARCHAR(255),
    ownerID VARCHAR(255),
    region VARCHAR(255),
    tipo VARCHAR(255),
    userID_10 VARCHAR(255),
    userID_14 VARCHAR(255),
    userID_30 VARCHAR(255),
    userID_52 VARCHAR(255),
    userID_59 VARCHAR(255),
    userID_65 VARCHAR(255),
    userID_9 VARCHAR(255),
    voboRequerido VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_empresas_ownerID ON empresas(ownerID);
CREATE INDEX idx_empresas_userID_10 ON empresas(userID_10);
CREATE INDEX idx_empresas_userID_14 ON empresas(userID_14);


-- Tabla: solicitudes (11090 registros)
CREATE TABLE solicitudes (
    asesorNombre VARCHAR(255),
    autorizacionDG VARCHAR(255),
    clienteAntiguedad VARCHAR(255),
    clienteApellidoMaterno VARCHAR(100),
    clienteApellidoPaterno VARCHAR(100),
    clienteClabe TEXT,
    clienteCorreoJefe TEXT,
    clienteEmpresa VARCHAR(255),
    clienteNombre VARCHAR(255),
    clienteNombreJefe TEXT,
    clienteNuevoRenovacion TEXT,
    clientePuesto VARCHAR(255),
    clienteReferenciaCobranza TEXT,
    clienteSalario TEXT,
    clienteSeEnteroPor TEXT,
    comentarios TEXT,
    documentos VARCHAR(255),
    editable VARCHAR(255),
    estatusEmbudo VARCHAR(255),
    etapaEmbudo VARCHAR(255),
    fechaAutorizacionDG TIMESTAMP,
    fechaCancelacionCartera TIMESTAMP,
    fechaCancelacionCliente TIMESTAMP,
    fechaContacto TIMESTAMP,
    fechaContratoImpreso TIMESTAMP,
    fechaEntregaARiesgos TIMESTAMP,
    fechaEntregaContratoFirmado TIMESTAMP,
    fechaFondeado TIMESTAMP,
    fechaPrimerSolicitudVoBo TIMESTAMP,
    fechaPropuesta TIMESTAMP,
    fechaRechazo TIMESTAMP,
    fechaRechazoDG TIMESTAMP,
    fechaRechazoRiesgos TIMESTAMP,
    fechaReferenciaCobranza TIMESTAMP,
    fechaSegundaSolicitudVoBo TIMESTAMP,
    fechaTercerSolicitudVoBo TIMESTAMP,
    fechaValidacionClabe TIMESTAMP,
    fechaVoBo TIMESTAMP,
    id VARCHAR(255) PRIMARY KEY,
    inheritedID VARCHAR(100),
    montoAutorizado VARCHAR(255),
    montoSolicitado VARCHAR(255),
    montoTransferencia VARCHAR(255),
    motivoNoCierre TEXT,
    oldID VARCHAR(255),
    ownerID VARCHAR(255),
    plazoAutorizado TEXT,
    plazoSolicitado TEXT,
    polizaSeguro VARCHAR(255),
    producto VARCHAR(255),
    regionNombre VARCHAR(255),
    solicitudEstatus VARCHAR(255),
    solicitudNumeroControl VARCHAR(255),
    tipoDeNegocio VARCHAR(255),
    usuarioAutorizacionRiesgos TEXT,
    viewName TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_solicitudes_clienteApellidoMaterno ON solicitudes(clienteApellidoMaterno);
CREATE INDEX idx_solicitudes_clienteApellidoPaterno ON solicitudes(clienteApellidoPaterno);
CREATE INDEX idx_solicitudes_fechaValidacionClabe ON solicitudes(fechaValidacionClabe);


-- Tabla: logs (35087 registros)
CREATE TABLE logs (
    log_id SERIAL PRIMARY KEY,
    Objeto VARCHAR(255),
    accion VARCHAR(255),
    logData JSONB,
    timeStamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_timeStamp ON logs(timeStamp);
CREATE INDEX idx_logs_Objeto ON logs(Objeto);



-- Tabla: geolocalizaciones (2614 registros)
CREATE TABLE geolocalizaciones (
    coords VARCHAR(255),
    fecha TIMESTAMP,
    id VARCHAR(255) PRIMARY KEY,
    ownerID VARCHAR(255),
    usuario VARCHAR(255),
    viewName VARCHAR(255),
    visita VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_geolocalizaciones_ownerID ON geolocalizaciones(ownerID);


-- Tabla: acl (12 registros)
CREATE TABLE acl (
    acl_id SERIAL PRIMARY KEY,
    acl VARCHAR(255),
    forbidden JSONB,
    scope VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_acl_acl ON acl(acl);
CREATE INDEX idx_acl_scope ON acl(scope);


-- Tabla: agendas (4 registros)
CREATE TABLE agendas (
    agenda_id SERIAL PRIMARY KEY,
    actividad VARCHAR(255),
    clienteNombre TEXT,
    clienteNuevoRenovacion VARCHAR(255),
    comentarios VARCHAR(255),
    empresa VARCHAR(255),
    fecha TIMESTAMP,
    hora VARCHAR(255),
    ownerID VARCHAR(255),
    ubicacion TEXT,
    userName VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agendas_ownerID ON agendas(ownerID);
CREATE INDEX idx_agendas_fecha ON agendas(fecha);


-- Tabla: operaciones_internas_preocupantes (4 registros)
CREATE TABLE operaciones_internas_preocupantes (
    documentos TEXT,
    fechaDictaminacion TIMESTAMP,
    fechaReporte TIMESTAMP,
    fechaReporteSITI TIMESTAMP,
    id VARCHAR(255) PRIMARY KEY,
    inheritedID VARCHAR(100),
    ownerID VARCHAR(255),
    reportadoPor VARCHAR(255),
    reporteEstatus VARCHAR(255),
    roi VARCHAR(255),
    viewName VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_operaciones_internas_preocupantes_inheritedID ON operaciones_internas_preocupantes(inheritedID);
CREATE INDEX idx_operaciones_internas_preocupantes_ownerID ON operaciones_internas_preocupantes(ownerID);

