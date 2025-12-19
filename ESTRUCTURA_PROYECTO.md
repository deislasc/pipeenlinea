# 📁 Estructura del Proyecto Pipeenlinea

## 🎯 Estructura Actual (Compatible con Docker)

```
pipeenlinea/
│
├── 🐳 DOCKER & DEPLOYMENT
│   ├── docker-compose.yml          # Orquestación (PostgreSQL + Flask + pgAdmin)
│   ├── Dockerfile                  # Imagen de la aplicación Flask
│   ├── Dockerfile.migration        # Imagen para migración de datos
│   ├── .dockerignore               # Archivos a ignorar en build
│   ├── .env.example                # Template de variables de entorno
│   └── .gitignore                  # Protección de archivos sensibles
│
├── 🗄️ BASE DE DATOS
│   └── database/
│       ├── schema.sql              # Schema PostgreSQL (10 tablas)
│       └── indexes.sql             # Índices optimizados (40+)
│
├── 🔄 MIGRACIÓN
│   ├── migrate_to_postgres.py      # Script de migración JSON → PostgreSQL
│   ├── migration_logs/             # Logs de migración
│   └── logs/                       # Logs de aplicación
│
├── 🛠️ SCRIPTS DE UTILIDAD
│   ├── start.sh                    # Script interactivo de inicio
│   ├── pre_migration_check.sh      # Validación pre-migración
│   └── backup_before_migration.sh  # Backup automático
│
├── 📚 DOCUMENTACIÓN
│   ├── README.md                   # Original del proyecto
│   ├── README_MIGRACION.md         # Guía completa de migración
│   ├── QUICK_START.md              # Inicio rápido
│   └── ESTRUCTURA_PROYECTO.md      # Este archivo
│
├── 🔐 ARCHIVOS SENSIBLES (NO en git)
│   ├── secret.key                  # Clave de encriptación Fernet
│   └── .env                        # Variables de entorno (crear desde .env.example)
│
├── 📦 CÓDIGO FUENTE (mysite/)
│   ├── 🐍 BACKEND PYTHON
│   │   ├── main.py                 # Aplicación Flask principal (121KB)
│   │   ├── config.py               # Configuración y parámetros
│   │   ├── campos.py               # Definiciones de campos (150KB)
│   │   ├── update.py               # Operaciones de datos (JSON legacy)
│   │   ├── update_db.py            # Operaciones de datos (PostgreSQL NEW)
│   │   ├── database.py             # Conexión PostgreSQL (SQL raw)
│   │   ├── parametricos.py         # Parámetros de política crediticia
│   │   ├── mainmenu.py             # Estructura de menús
│   │   └── metas.py                # Metas y objetivos
│   │
│   ├── 🛣️ ROUTES (Módulos de rutas)
│   │   ├── routes_solicitudes.py   # Solicitudes de crédito (107KB)
│   │   ├── routes_analisis.py      # Análisis crediticio (43KB)
│   │   ├── routes_users.py         # Gestión de usuarios
│   │   ├── routes_empresas.py      # Gestión de empresas
│   │   ├── routes_login2.py        # Autenticación
│   │   ├── routes_logs.py          # Logging
│   │   ├── routes_agendas.py       # Agendas y citas
│   │   ├── routes_cosechas.py      # Análisis de cosechas
│   │   ├── routes_simulador.py     # Simulador de crédito
│   │   ├── routes_acl.py           # Control de acceso
│   │   ├── routes_controlexpedientes.py
│   │   ├── routes_mesaAnalisis.py
│   │   ├── routes_pagadoras.py
│   │   ├── routes_visitas.py
│   │   ├── routes_csv.py
│   │   ├── routes_correos.py
│   │   ├── routes_ROIP.py
│   │   ├── routes_BearerGenerator.py
│   │   ├── routes_OAuth2Generator.py
│   │   └── routes_downloadDbBkup.py
│   │
│   ├── 📄 TEMPLATES (HTML)
│   │   ├── base.html               # Template base
│   │   ├── login.html              # Login
│   │   ├── solicitudes.html        # Lista de solicitudes
│   │   ├── addSolicitudes.html     # Nueva solicitud
│   │   ├── analisis.html           # Análisis crediticio
│   │   ├── usuarios.html           # Gestión de usuarios
│   │   ├── empresas.html           # Gestión de empresas
│   │   ├── colocacion.html         # Colocación
│   │   ├── scorecard.html          # Scorecard
│   │   ├── pipeline.html           # Pipeline de ventas
│   │   ├── simulador.html          # Simulador
│   │   ├── cosechas.html           # Análisis de cosechas
│   │   ├── historico.html          # Histórico
│   │   ├── logs.html               # Logs de actividad
│   │   └── ... (47 templates total)
│   │
│   ├── 🎨 STATIC (Recursos estáticos)
│   │   ├── css/
│   │   │   ├── styles.css          # Estilos principales
│   │   │   └── styles_simulador.css
│   │   ├── js/
│   │   │   ├── jquery-1.11.1.min.js
│   │   │   ├── jsFunctionsFrontEnd.js (43KB)
│   │   │   └── functions_simulador.js (27KB)
│   │   ├── img/
│   │   │   ├── Logo_MiPymex.jpg
│   │   │   ├── location.png
│   │   │   └── Buzon PLD.png
│   │   └── svg/
│   │       ├── eyeOpen.svg
│   │       ├── eyeSlash.svg
│   │       └── galleriaSVG.svg
│   │
│   ├── 💾 DATOS (JSON Encriptados)
│   │   └── working/
│   │       ├── solicitudes.json     # 67MB - Solicitudes de crédito
│   │       ├── solicitudes.jsonbku  # Backup automático
│   │       ├── logs.json            # 39MB - Logs de auditoría
│   │       ├── logs.jsonbku
│   │       ├── cosechas.json        # 12MB - Análisis de cosechas
│   │       ├── geolocations.json    # 1MB - Geolocalización
│   │       ├── geolocations.jsonbku
│   │       ├── empresas.json        # 90KB - Empresas
│   │       ├── empresas.jsonbku
│   │       ├── users.json           # 62KB - Usuarios
│   │       ├── users.jsonbku
│   │       ├── acl.json             # 31KB - Permisos
│   │       ├── acl.jsonbku
│   │       ├── agendas.json         # 2KB - Agendas
│   │       ├── agendas.jsonbku
│   │       ├── pagadoras.json       # 2.6KB
│   │       ├── roips.json           # 2.2KB - Reportes SITI
│   │       ├── roips.jsonbku
│   │       └── consultas.json       # 0B (vacío)
│   │
│   ├── 📂 UPLOADS (Archivos subidos)
│   │   └── uploads/
│   │       └── *.csv, *.pdf, etc.
│   │
│   ├── 📦 ESQUEMAS Y HERRAMIENTAS
│   │   ├── esquemaReporteVentas.py
│   │   ├── esquemaReporteSolicitudesEnProceso.py
│   │   ├── esquemaReporteCobranzaReferenciada.py
│   │   ├── esquemaReporteTabularColocacion.py
│   │   ├── esquemaReporteVisitas.py
│   │   ├── plantillasReporteTexto.py
│   │   ├── qaTools.py
│   │   ├── backupCronJob.py
│   │   ├── encriptar.py
│   │   ├── correctFile.py
│   │   └── correctSolicitudesData.py
│   │
│   ├── 🔧 CONFIGURACIÓN
│   │   ├── requirements.txt         # Dependencias Python (actualizado)
│   │   ├── wsgi.py                  # WSGI entry point
│   │   └── __pycache__/             # Cache de Python
│   │
│   └── 🗑️ ARCHIVOS LEGACY/BACKUP
│       ├── __MACOSX/                # Archivos de macOS (ignorar)
│       ├── _MACOSX/                 # Archivos de macOS (ignorar)
│       ├── config_V7.py             # Versión antigua
│       ├── config_V8.py             # Versión antigua
│       ├── campos.py.backup         # Backup
│       ├── routes_analisis.py.backup
│       └── update_dev.py            # Versión de desarrollo
│
└── 📦 BACKUP DE DATOS (working/ en raíz)
    └── working/                     # COPIA IDÉNTICA de mysite/working/
        └── (mismos archivos JSON)

```

## 🎯 Flujo de Datos

```
┌─────────────────────────────────────────┐
│  JSON Encriptados (working/)            │
│  - solicitudes.json (67MB)              │
│  - logs.json (39MB)                     │
│  - etc.                                 │
└──────────────┬──────────────────────────┘
               │
               │ migrate_to_postgres.py
               │ (Desencripta con secret.key)
               │
               ▼
┌─────────────────────────────────────────┐
│  PostgreSQL Database                    │
│  ┌─────────────────────────────────┐   │
│  │ • usuarios                       │   │
│  │ • empresas                       │   │
│  │ • solicitudes (tabla principal)  │   │
│  │ • logs                           │   │
│  │ • cosechas                       │   │
│  │ • geolocalizaciones              │   │
│  │ • acl, agendas, pagadoras, roips│   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │
               │ psycopg2 (SQL raw)
               │ database.py
               │
               ▼
┌─────────────────────────────────────────┐
│  Flask Application (main.py)            │
│  • Routes (routes_*.py)                 │
│  • Templates (*.html)                   │
│  • Static files (css, js, img)          │
└─────────────────────────────────────────┘
```

## 🐳 Arquitectura Docker

```
┌──────────────────────────────────────────┐
│   docker-compose.yml                     │
└───┬──────────────┬───────────────────────┘
    │              │
    │              │
    ▼              ▼
┌─────────┐    ┌──────────────┐
│ postgres│    │ app (Flask)  │
│ :5432   │◄───│ :8000        │
└─────────┘    └──────────────┘
    │              │
    │              │
    ▼              ▼
[pg_data]      [uploads/]
[volumen]      [logs/]
               [working_backup/]
```

## 🔄 Volúmenes Docker

```yaml
volumes:
  - ./mysite/uploads:/app/uploads           # Archivos subidos
  - ./mysite/working:/app/working_backup    # Backup JSON
  - ./secret.key:/app/secret.key:ro         # Clave (read-only)
  - ./logs:/app/logs                        # Logs de aplicación
  - postgres_data:/var/lib/postgresql/data  # Datos PostgreSQL
```

## ⚙️ Variables de Entorno (.env)

```bash
# PostgreSQL
DB_PASSWORD=tu_password_seguro

# Flask
SECRET_KEY=tu_flask_secret_key
FLASK_ENV=production

# Paths
ENCRYPTION_KEY_PATH=/app/secret.key
DATABASE_URL=postgresql://pipeenlinea_user:password@postgres:5432/pipeenlinea
```

## 📊 Tamaños de Archivos Clave

| Archivo | Tamaño | Descripción |
|---------|--------|-------------|
| solicitudes.json | 67MB | Solicitudes de crédito |
| logs.json | 39MB | Auditoría completa |
| cosechas.json | 12MB | Análisis de cohorts |
| main.py | 121KB | App Flask principal |
| routes_solicitudes.py | 107KB | Lógica de solicitudes |
| campos.py | 150KB | Definiciones de campos |
| routes_analisis.py | 43KB | Análisis crediticio |

## 🚦 Comandos Rápidos

```bash
# 1. Verificar estructura
./pre_migration_check.sh

# 2. Crear backup
./backup_before_migration.sh

# 3. Iniciar servicios
./start.sh

# 4. Ver logs
docker-compose logs -f

# 5. Conectar a PostgreSQL
docker-compose exec postgres psql -U pipeenlinea_user -d pipeenlinea
```

## ✅ Checklist de Archivos Críticos

- [x] `secret.key` - En raíz (44 bytes)
- [x] `mysite/working/*.json` - Todos presentes
- [x] `working/*.json` - Copia de respaldo
- [x] `docker-compose.yml` - Configurado
- [x] `database/schema.sql` - Schema listo
- [x] `migrate_to_postgres.py` - Script de migración
- [x] `.gitignore` - Protege datos sensibles
- [ ] `.env` - **CREAR desde .env.example**

## 🎯 Próximos Pasos

1. ✅ Estructura verificada
2. ✅ Docker configurado
3. ✅ Scripts de utilidad listos
4. ⏭️ Crear `.env` desde `.env.example`
5. ⏭️ Ejecutar `./pre_migration_check.sh`
6. ⏭️ Ejecutar `./start.sh`

---

**Última actualización**: 2024-12-19
**Versión**: 1.0 - Migración PostgreSQL
