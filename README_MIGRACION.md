# 🚀 Guía de Migración a PostgreSQL

## 📋 Tabla de Contenidos
1. [Pre-requisitos](#pre-requisitos)
2. [Configuración Inicial](#configuración-inicial)
3. [Migración en Desarrollo](#migración-en-desarrollo)
4. [Migración a Producción (Azure)](#migración-a-producción-azure)
5. [Rollback](#rollback)
6. [Troubleshooting](#troubleshooting)

---

## ✅ Pre-requisitos

### Locales
- Docker y Docker Compose instalados
- Git
- 10GB de espacio en disco disponible
- Acceso a los archivos JSON encriptados
- Archivo `secret.key` de encriptación

### Azure (Producción)
- Azure Database for PostgreSQL - Flexible Server
- Azure Container Registry (ACR) o Docker Hub
- Azure Container Instances o Azure App Service
- 2 horas de ventana de mantenimiento

---

## 🔧 Configuración Inicial

### 1. Clonar y preparar el repositorio

```bash
cd /home/user/pipeenlinea
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```bash
# PostgreSQL
DB_PASSWORD=tu_password_seguro_aqui

# Flask
SECRET_KEY=tu_flask_secret_key_aqui

# pgAdmin (opcional, solo desarrollo)
PGADMIN_PASSWORD=tu_pgadmin_password
```

**⚠️ IMPORTANTE:** Nunca commits el archivo `.env` al repositorio.

### 3. Verificar archivos JSON

```bash
ls -lh mysite/working/
```

Deberías ver:
- `solicitudes.json` (~67MB)
- `logs.json` (~39MB)
- `cosechas.json` (~12MB)
- `users.json` (~62KB)
- `empresas.json` (~91KB)
- Otros archivos JSON encriptados

---

## 🧪 Migración en Desarrollo

### Paso 1: Levantar PostgreSQL

```bash
docker-compose up -d postgres
```

Verificar que esté corriendo:

```bash
docker-compose ps
docker-compose logs postgres
```

Deberías ver: `database system is ready to accept connections`

### Paso 2: Verificar el schema

El schema se crea automáticamente al iniciar PostgreSQL por primera vez gracias a:
- `database/schema.sql`
- `database/indexes.sql`

Para verificar:

```bash
docker-compose exec postgres psql -U pipeenlinea_user -d pipeenlinea -c "\dt"
```

Deberías ver todas las tablas:
- usuarios
- empresas
- solicitudes
- logs
- etc.

### Paso 3: Ejecutar migración (DRY-RUN primero)

```bash
# Dry-run para verificar sin guardar datos
docker-compose --profile migrate run --rm migration --dry-run
```

Esto mostrará:
- Cuántos registros se migrarán de cada tabla
- Errores potenciales
- Sin modificar la base de datos

### Paso 4: Migración REAL

```bash
# Migración completa
docker-compose --profile migrate run --rm migration
```

Esto tomará varios minutos dependiendo del tamaño de datos.

### Paso 5: Verificar datos migrados

```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U pipeenlinea_user -d pipeenlinea
```

Queries de verificación:

```sql
-- Contar registros
SELECT COUNT(*) FROM usuarios;
SELECT COUNT(*) FROM solicitudes;
SELECT COUNT(*) FROM logs;

-- Ver algunas solicitudes
SELECT id, cliente_nombre, solicitud_estatus, fecha_contacto
FROM solicitudes
LIMIT 5;

-- Salir
\q
```

### Paso 6: Levantar la aplicación

```bash
docker-compose up -d app
```

Verificar logs:

```bash
docker-compose logs -f app
```

### Paso 7: Probar la aplicación

Abrir en navegador: http://localhost:8000

O usar curl:

```bash
curl http://localhost:8000/health
```

### Paso 8: pgAdmin (Opcional)

```bash
docker-compose --profile dev up -d pgadmin
```

Abrir en navegador: http://localhost:5050

Credenciales:
- Email: admin@pipeenlinea.com
- Password: (el que configuraste en .env)

Agregar servidor PostgreSQL:
- Host: postgres
- Port: 5432
- Database: pipeenlinea
- Username: pipeenlinea_user
- Password: (el que configuraste en .env)

---

## ☁️ Migración a Producción (Azure)

### Arquitectura Recomendada

```
┌─────────────────────────────────────────┐
│   Azure Container Instances / App Service │
│   (Flask App)                           │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│   Azure Database for PostgreSQL        │
│   (Flexible Server)                     │
└─────────────────────────────────────────┘
```

### Paso 1: Crear Azure Database for PostgreSQL

```bash
# Crear resource group
az group create \
  --name pipeenlinea-rg \
  --location eastus

# Crear PostgreSQL Flexible Server
az postgres flexible-server create \
  --resource-group pipeenlinea-rg \
  --name pipeenlinea-db \
  --location eastus \
  --admin-user pipeenlinea_admin \
  --admin-password 'TuPasswordSeguro!' \
  --sku-name Standard_B2s \
  --storage-size 128 \
  --version 15

# Crear base de datos
az postgres flexible-server db create \
  --resource-group pipeenlinea-rg \
  --server-name pipeenlinea-db \
  --database-name pipeenlinea

# Configurar firewall (permitir Azure services)
az postgres flexible-server firewall-rule create \
  --resource-group pipeenlinea-rg \
  --name pipeenlinea-db \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### Paso 2: Obtener connection string

```bash
az postgres flexible-server show-connection-string \
  --server-name pipeenlinea-db \
  --database-name pipeenlinea \
  --admin-user pipeenlinea_admin
```

Formato:
```
postgresql://pipeenlinea_admin:TuPasswordSeguro!@pipeenlinea-db.postgres.database.azure.com:5432/pipeenlinea?sslmode=require
```

### Paso 3: Ejecutar schema en Azure

```bash
# Opción A: Desde tu máquina local
psql "postgresql://pipeenlinea_admin:TuPasswordSeguro!@pipeenlinea-db.postgres.database.azure.com:5432/pipeenlinea?sslmode=require" \
  -f database/schema.sql

psql "postgresql://pipeenlinea_admin:TuPasswordSeguro!@pipeenlinea-db.postgres.database.azure.com:5432/pipeenlinea?sslmode=require" \
  -f database/indexes.sql

# Opción B: Copiar schema y ejecutar interactivamente
psql "postgresql://..." < database/schema.sql
```

### Paso 4: Migrar datos a Azure

Modificar `.env` con la connection string de Azure:

```bash
DATABASE_URL=postgresql://pipeenlinea_admin:TuPasswordSeguro!@pipeenlinea-db.postgres.database.azure.com:5432/pipeenlinea?sslmode=require
```

Ejecutar migración:

```bash
python migrate_to_postgres.py
```

O usando Docker:

```bash
docker-compose --profile migrate run --rm \
  -e DATABASE_URL="postgresql://..." \
  migration
```

### Paso 5: Build y push de imagen Docker

```bash
# Build
docker build -t pipeenlinea:latest .

# Tag para Azure Container Registry
docker tag pipeenlinea:latest yourregistry.azurecr.io/pipeenlinea:latest

# Login a ACR
az acr login --name yourregistry

# Push
docker push yourregistry.azurecr.io/pipeenlinea:latest
```

### Paso 6: Deploy en Azure Container Instances

```bash
az container create \
  --resource-group pipeenlinea-rg \
  --name pipeenlinea-app \
  --image yourregistry.azurecr.io/pipeenlinea:latest \
  --cpu 2 \
  --memory 4 \
  --registry-login-server yourregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --dns-name-label pipeenlinea \
  --ports 8000 \
  --environment-variables \
    DATABASE_URL="postgresql://..." \
    FLASK_ENV=production \
    SECRET_KEY="your-secret-key"
```

### Paso 7: Verificar deployment

```bash
# Obtener URL pública
az container show \
  --resource-group pipeenlinea-rg \
  --name pipeenlinea-app \
  --query ipAddress.fqdn

# Test
curl http://<fqdn>:8000/health
```

---

## 🔄 Rollback

Si algo sale mal durante la migración:

### Rollback Local

```bash
# Detener servicios
docker-compose down

# Eliminar volúmenes de base de datos
docker volume rm pipeenlinea_postgres_data

# Volver a levantar con JSON (modo legacy)
# (Restaurar versión anterior del código)
```

### Rollback Azure

```bash
# Restaurar backup de base de datos
az postgres flexible-server restore \
  --resource-group pipeenlinea-rg \
  --name pipeenlinea-db-restored \
  --source-server pipeenlinea-db \
  --restore-time "2024-01-01T10:00:00Z"

# Revertir a imagen anterior
az container update \
  --resource-group pipeenlinea-rg \
  --name pipeenlinea-app \
  --image yourregistry.azurecr.io/pipeenlinea:previous
```

---

## 🐛 Troubleshooting

### Error: "No se puede conectar a PostgreSQL"

```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps

# Ver logs
docker-compose logs postgres

# Reiniciar
docker-compose restart postgres
```

### Error: "Permission denied" en migración

```bash
# Verificar permisos de archivos
ls -la mysite/working/

# Verificar secret.key
ls -la secret.key
```

### Error: "Tabla ya existe"

```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U pipeenlinea_user -d pipeenlinea

# Drop schema y recrear
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
\q

# Re-ejecutar schema
docker-compose restart postgres
```

### Error: "Out of memory" durante migración

```bash
# Aumentar batch size
docker-compose --profile migrate run --rm migration --batch-size 500
```

### Verificar datos migrados vs JSON

```python
# Script de verificación
python3 << 'EOF'
import sys
sys.path.insert(0, 'mysite')

from database import initialize_pool, execute_query
from cryptography.fernet import Fernet
import json

initialize_pool()

# Contar en BD
count_db = execute_query("SELECT COUNT(*) as count FROM solicitudes", fetch_one=True)
print(f"Solicitudes en BD: {count_db['count']}")

# Contar en JSON
with open('secret.key', 'rb') as f:
    key = f.read()
fernet = Fernet(key)

with open('mysite/working/solicitudes.json', 'rb') as f:
    encrypted = f.read()

data = json.loads(fernet.decrypt(encrypted).decode('utf-8'))
# Restar 1 si el primer elemento está vacío
count_json = len(data) - 1 if not data[0] else len(data)
print(f"Solicitudes en JSON: {count_json}")

if count_db['count'] == count_json:
    print("✅ Conteos coinciden!")
else:
    print(f"⚠️  Diferencia: {abs(count_db['count'] - count_json)}")
EOF
```

---

## 📊 Monitoreo Post-Migración

### Queries útiles

```sql
-- Ver actividad actual
SELECT pid, usename, state, query
FROM pg_stat_activity
WHERE datname = 'pipeenlinea';

-- Ver tamaño de tablas
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Ver índices más usados
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC
LIMIT 10;

-- Ver queries lentas (requiere pg_stat_statements)
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs: `docker-compose logs`
2. Verifica la conexión: `docker-compose exec postgres psql ...`
3. Ejecuta dry-run: `--dry-run`
4. Consulta este README

---

## ✅ Checklist de Migración

### Pre-Migración
- [ ] Backups de todos los JSON encriptados
- [ ] Backup de secret.key
- [ ] Variables de entorno configuradas
- [ ] PostgreSQL corriendo y accesible
- [ ] Schema creado correctamente
- [ ] Dry-run exitoso

### Migración
- [ ] Usuarios migrados
- [ ] Empresas migradas
- [ ] Solicitudes migradas (tabla más grande)
- [ ] Logs migrados
- [ ] Otras tablas migradas
- [ ] Conteos verificados
- [ ] Datos spot-check (verificar algunos registros)

### Post-Migración
- [ ] Aplicación levantada y respondiendo
- [ ] Login funciona
- [ ] Solicitudes se pueden crear
- [ ] Reportes funcionan
- [ ] Performance aceptable
- [ ] Logs de aplicación limpios
- [ ] Monitoreo configurado

---

¡Buena suerte con la migración! 🚀
