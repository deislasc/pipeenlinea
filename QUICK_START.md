# ⚡ Quick Start - Migración PostgreSQL

## 🎯 Inicio Rápido en 5 Minutos

### 1. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tus credenciales
```

### 2. Usar el script de inicio

```bash
./start.sh
```

Selecciona opción 1 para inicio completo.

### 3. Migrar datos (opcional)

```bash
./start.sh
# Opción 3: Dry-run primero
# Opción 4: Migración real
```

### 4. Acceder

- **Aplicación**: http://localhost:8000
- **pgAdmin**: http://localhost:5050 (desarrollo)

---

## 📦 Archivos Creados

### Docker
- `docker-compose.yml` - Orquestación de servicios
- `Dockerfile` - Imagen de la aplicación Flask
- `Dockerfile.migration` - Imagen para migración de datos
- `.dockerignore` - Archivos a ignorar
- `.env.example` - Template de variables de entorno

### Base de Datos
- `database/schema.sql` - Schema PostgreSQL completo
- `database/indexes.sql` - Índices para performance
- `mysite/database.py` - Módulo de conexión (SQL raw)

### Migración
- `migrate_to_postgres.py` - Script de migración JSON → PostgreSQL
- `mysite/update_db.py` - Ejemplo de update.py con SQL raw

### Scripts
- `start.sh` - Script interactivo de inicio

### Documentación
- `README_MIGRACION.md` - Guía completa de migración
- `QUICK_START.md` - Este archivo

---

## 🗄️ Schema PostgreSQL

```
├── usuarios (users.json)
├── empresas (empresas.json)
├── solicitudes (solicitudes.json) ← Tabla principal
├── logs (logs.json)
├── cosechas (cosechas.json)
├── geolocalizaciones (geolocations.json)
├── acl (acl.json)
├── agendas (agendas.json)
├── pagadoras (pagadoras.json)
└── operaciones_internas_preocupantes (roips.json)
```

---

## 🚀 Comandos Útiles

### Docker Compose

```bash
# Levantar todo
docker-compose up -d

# Solo PostgreSQL
docker-compose up -d postgres

# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Limpiar volúmenes (¡CUIDADO!)
docker-compose down -v
```

### PostgreSQL

```bash
# Conectar a BD
docker-compose exec postgres psql -U pipeenlinea_user -d pipeenlinea

# Backup
docker-compose exec postgres pg_dump -U pipeenlinea_user pipeenlinea > backup.sql

# Restore
docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea < backup.sql
```

### Migración

```bash
# Dry-run
docker-compose --profile migrate run --rm migration --dry-run

# Migración real
docker-compose --profile migrate run --rm migration

# Con batch size específico
docker-compose --profile migrate run --rm migration --batch-size 500

# Saltar tabla específica
docker-compose --profile migrate run --rm migration --skip-table logs
```

---

## 📊 Verificar Migración

```sql
-- Conectar a PostgreSQL
docker-compose exec postgres psql -U pipeenlinea_user -d pipeenlinea

-- Contar registros
SELECT COUNT(*) FROM solicitudes;
SELECT COUNT(*) FROM usuarios;
SELECT COUNT(*) FROM logs;

-- Ver primeras solicitudes
SELECT id, cliente_nombre, solicitud_estatus, fecha_contacto
FROM solicitudes
ORDER BY fecha_contacto DESC
LIMIT 5;

-- Ver tamaño de tablas
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size('public.'||tablename) DESC;
```

---

## 🔧 Desarrollo

### Estructura de Código

```python
# ANTES (JSON)
from update import reloadJSONData

solicitudes = reloadJSONData("working/solicitudes.json")
solicitud = solicitudes[id]

# DESPUÉS (PostgreSQL)
from database import execute_query

solicitud = execute_query(
    "SELECT * FROM solicitudes WHERE id = %s",
    (id,),
    fetch_one=True
)
```

### Ejemplo de Inserción

```python
from database import execute_query

query = """
    INSERT INTO solicitudes (cliente_nombre, monto_solicitado, owner_id)
    VALUES (%s, %s, %s)
    RETURNING id
"""

result = execute_query(
    query,
    ("Juan Pérez", 50000, "USR001"),
    fetch_one=True
)

new_id = result['id']
```

---

## ☁️ Deployment en Azure

Ver `README_MIGRACION.md` sección completa de Azure.

**Resumen rápido:**

1. Crear Azure Database for PostgreSQL
2. Ejecutar schema.sql en Azure
3. Migrar datos con `migrate_to_postgres.py`
4. Build y push imagen Docker
5. Deploy en Azure Container Instances

---

## ❓ FAQ

**P: ¿Puedo usar PostgreSQL local y luego migrar a Azure?**
R: Sí, usa `pg_dump` para hacer backup y `pg_restore` en Azure.

**P: ¿Cuánto tiempo toma la migración?**
R: Depende del tamaño. Con ~10K solicitudes, ~15-20 minutos.

**P: ¿Se pierden los JSON originales?**
R: No, se mantienen como backup en `mysite/working/`.

**P: ¿Puedo volver atrás?**
R: Sí, los JSON encriptados siguen funcionando con el código original.

**P: ¿Funciona con MySQL?**
R: Sí, pero necesitas ajustar el schema (PostgreSQL → MySQL syntax).

---

## 📞 Ayuda

- **Logs de app**: `docker-compose logs app`
- **Logs de BD**: `docker-compose logs postgres`
- **Logs de migración**: Carpeta `migration_logs/`
- **Estado**: `./start.sh` → Opción 8

---

## ✅ Checklist

Antes de usar en producción:

- [ ] Backup de todos los JSON encriptados
- [ ] Backup de `secret.key`
- [ ] Dry-run exitoso
- [ ] Migración en desarrollo exitosa
- [ ] Datos verificados (conteos, samples)
- [ ] Aplicación funciona correctamente
- [ ] Login funciona
- [ ] CRUD de solicitudes funciona
- [ ] Performance aceptable
- [ ] Configuración de Azure lista
- [ ] Plan de rollback documentado

---

**¡Listo para empezar! 🚀**
