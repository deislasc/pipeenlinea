# PipeEnLinea

Sistema de gestión de créditos para PyMEs con arquitectura moderna basada en PostgreSQL y Docker.

## 🚀 Inicio Rápido (Automático)

```bash
./start.sh
```

Este script **automáticamente**:
- ✅ Verifica que Docker esté instalado y corriendo
- ✅ Crea el archivo `.env` si no existe
- ✅ Verifica archivos necesarios (secret.key, JSONs)
- ✅ Detiene servicios previos si existen
- ✅ Inicia PostgreSQL y espera a que esté listo
- ✅ Crea el esquema de base de datos si es necesario
- ✅ Construye e inicia la aplicación Flask
- ✅ Verifica que todo esté funcionando
- ✅ Muestra estadísticas y comandos útiles

**Sin intervención manual** - Solo ejecuta `./start.sh` y todo arranca automáticamente.

## 📋 Prerequisitos

- Docker Desktop instalado y corriendo
- Archivo `secret.key` en la raíz del proyecto (para desencriptar JSONs)
- Archivos JSON en el directorio `working/` (si vas a migrar datos)

## 🌐 Acceso al Sistema

Una vez iniciado:

- **Aplicación Web**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **pgAdmin** (opcional): `docker-compose --profile dev up -d pgadmin` → http://localhost:5050

## 📊 Comandos Útiles

### Ver logs en tiempo real
```bash
docker-compose logs -f
```

### Ver logs solo de la app
```bash
docker-compose logs -f app
```

### Conectar a PostgreSQL
```bash
docker-compose exec postgres psql -U pipeenlinea_user -d pipeenlinea
```

### Detener servicios
```bash
docker-compose down
```

### Reiniciar servicios
```bash
docker-compose restart
```

### Migrar datos desde JSON (Prueba - Dry Run)
```bash
docker-compose --profile migrate run --rm migration --dry-run
```

### Migrar datos desde JSON (Real)
```bash
docker-compose --profile migrate run --rm migration
```

## 🏗️ Arquitectura

```
pipeenlinea/
├── mysite/              # Aplicación Flask
│   ├── static/          # CSS, JS, imágenes
│   │   └── css/
│   │       └── modern-theme.css  # Sistema de diseño moderno
│   ├── templates/       # Templates HTML
│   │   ├── base_modern.html      # Base moderna con Bootstrap 5.3
│   │   ├── dashboard_modern.html # Dashboard ejemplo
│   │   └── componentes_ui.html   # Librería de componentes
│   ├── database.py      # Módulo de conexión PostgreSQL
│   └── ...
├── database/            # Esquemas SQL
│   ├── schema.sql       # Definición de tablas
│   └── indexes.sql      # Índices optimizados
├── working/             # JSONs encriptados (backup)
├── docker-compose.yml   # Orquestación de servicios
├── Dockerfile           # Imagen de la aplicación
├── start.sh             # Script de inicio automático ⭐
├── migrate.sh           # Script de migración interactivo ⭐
└── migrate_to_postgres.py  # Script de migración (core)
```

## 🎨 Frontend Moderno

El sistema incluye un diseño moderno y profesional:

- **Bootstrap 5.3** con componentes actualizados
- **Sistema de diseño** profesional estilo Fintech
- **Totalmente responsive** (mobile-first)
- **Paleta de colores** consistente y accesible
- **Chart.js 4.x** para visualizaciones
- **Bootstrap Icons** integrados
- **Sidebar colapsable** con menú hamburguesa

Ver documentación completa en: `FRONTEND_DESIGN_SYSTEM.md`

## 🗄️ Base de Datos

### PostgreSQL 15

10 tablas principales:
- `usuarios` - Usuarios del sistema
- `empresas` - Empresas solicitantes
- `solicitudes` - Solicitudes de crédito (tabla principal)
- `logs` - Registro de auditoría
- `cosechas` - Información agrícola
- `geolocalizaciones` - Ubicaciones
- `acl` - Control de acceso
- `agendas` - Agenda de actividades
- `pagadoras` - Entidades pagadoras
- `operaciones_internas_preocupantes` - Alertas

### Características

- ✅ Más de 40 índices optimizados
- ✅ Foreign keys y constraints
- ✅ Campos JSONB para flexibilidad
- ✅ Triggers para updated_at
- ✅ Connection pooling (2-20 conexiones)

## 🔄 Migración de Datos

### Método Recomendado: Script Interactivo ⭐

```bash
./migrate.sh
```

Este script **interactivo** te permite elegir entre:

1. **Dry-Run (Prueba)** - Simula la migración sin guardar
2. **Migración Real** - Migra todos los datos a PostgreSQL
3. **Batch Size Personalizado** - Ajusta el tamaño de lote (100-5000)
4. **Omitir Tablas** - Migra solo las tablas que necesites
5. **Ver Estado** - Estadísticas de registros por tabla
6. **Limpiar DB** - Reinicia la base de datos desde cero

### Método Manual:

```bash
# 1. Verificación pre-migración
./pre_migration_check.sh

# 2. Backup automático
./backup_before_migration.sh

# 3. Prueba (Dry-Run)
docker-compose --profile migrate run --rm migration --dry-run

# 4. Migración real
docker-compose --profile migrate run --rm migration
```

Documentación completa: `README_MIGRACION.md`

## 🔐 Seguridad

- ✅ Encriptación Fernet para JSONs
- ✅ Variables de entorno para credenciales
- ✅ `.gitignore` protege datos sensibles
- ✅ Connection pooling seguro
- ✅ SQL parametrizado (previene SQL injection)

## 🐳 Docker

### Servicios

- **postgres**: PostgreSQL 15 Alpine
- **app**: Aplicación Flask con Gunicorn (4 workers)
- **pgadmin** (opcional): Interfaz web para PostgreSQL
- **migration** (one-time): Contenedor de migración

### Volúmenes persistentes

- `postgres_data`: Datos de PostgreSQL
- `./uploads`: Archivos subidos
- `./working`: Backup de JSONs
- `./logs`: Logs de la aplicación

## 📚 Documentación

- `README.md` - Este archivo (inicio rápido)
- `README_MIGRACION.md` - Guía completa de migración
- `QUICK_START.md` - Guía de 5 minutos
- `ESTRUCTURA_PROYECTO.md` - Estructura del proyecto
- `FRONTEND_DESIGN_SYSTEM.md` - Sistema de diseño UI

## 🆘 Troubleshooting

### PostgreSQL no inicia
```bash
docker-compose logs postgres
# Verificar que el puerto 5432 esté libre
lsof -i :5432
```

### Aplicación no responde
```bash
docker-compose logs -f app
# Verificar variables de entorno
cat .env
```

### Error de desencriptación
```bash
# Verificar que secret.key sea el correcto
ls -la secret.key
```

### Limpiar todo y empezar de cero
```bash
docker-compose down -v --remove-orphans
docker system prune -f
./start.sh
```

## 🔧 Variables de Entorno (.env)

```env
# PostgreSQL
DB_HOST=postgres
DB_PORT=5432
DB_NAME=pipeenlinea
DB_USER=pipeenlinea_user
DB_PASSWORD=tu_password_seguro

# Flask
FLASK_ENV=development
SECRET_KEY=tu_secret_key_generado

# pgAdmin (opcional)
PGADMIN_EMAIL=admin@pipeenlinea.com
PGADMIN_PASSWORD=admin123
```

## 📈 Stack Tecnológico

### Backend
- Python 3.9
- Flask 2.3.3
- PostgreSQL 15
- psycopg2 (SQL raw, sin ORM)
- Gunicorn
- Cryptography (Fernet)

### Frontend
- Bootstrap 5.3
- jQuery 3.7.1
- Chart.js 4.x
- Bootstrap Icons
- CSS Custom Properties

### DevOps
- Docker & Docker Compose
- PostgreSQL Alpine
- Nginx (producción)

## 🚀 Despliegue en Azure

Para producción en Azure Database for PostgreSQL:

1. Crear Azure Database for PostgreSQL
2. Configurar variables de entorno en `.env`:
   ```env
   AZURE_DB_HOST=your-server.postgres.database.azure.com
   AZURE_DB_USER=your-user@your-server
   AZURE_DB_PASSWORD=your-password
   AZURE_DB_SSLMODE=require
   ```
3. Ejecutar migración
4. Desplegar contenedor de la app

Documentación completa: `README_MIGRACION.md` (sección Azure)

## 📝 Licencia

Privado - MiPymex

## 👥 Soporte

Para preguntas o problemas, contactar al equipo de desarrollo.

---

**¿Listo para empezar?** Solo ejecuta:

```bash
./start.sh
```

¡Todo lo demás es automático! 🚀
