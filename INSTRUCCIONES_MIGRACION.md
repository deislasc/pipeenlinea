# 🚀 Instrucciones de Migración a PostgreSQL

## ✅ Cambios Aplicados (ya están en la rama)

1. ✅ **update_postgres.py** - Versión híbrida que lee PostgreSQL primero, JSON como fallback
2. ✅ **docker-compose.yml** - Quitado `:ro` del volumen working para permitir escritura de logs
3. ✅ **Corrección de bugs** - Parámetro `fetch=True` corregido

---

## 📋 Pasos para Completar la Migración

### Opción A: Usando el Script Automático (Recomendado)

```bash
./switch_to_postgres.sh
```

El script hace todo automáticamente:
- ✅ Verifica que PostgreSQL esté corriendo
- ✅ Verifica que los datos estén migrados
- ✅ Hace backup de `update.py` original
- ✅ Reemplaza con versión PostgreSQL
- ✅ Reconstruye contenedores
- ✅ Verifica que la app funcione

---

### Opción B: Proceso Manual (Paso a paso)

#### 1️⃣ Detener los contenedores actuales
```bash
docker compose down
```

#### 2️⃣ Hacer backup y reemplazar update.py
```bash
cd mysite
cp update.py update_original.py
cp update_postgres.py update.py
cd ..
```

#### 3️⃣ Reconstruir la imagen de la aplicación
```bash
docker compose build app
```

#### 4️⃣ Iniciar los servicios
```bash
docker compose up -d
```

#### 5️⃣ Verificar que la aplicación funcione
```bash
docker compose logs -f app
```

Deberías ver mensajes como:
```
✅ Leídos 15 registros de PostgreSQL (usuarios)
✅ Leídos 1234 registros de PostgreSQL (solicitudes)
```

---

## 🎯 Verificación Final

### Abrir el navegador y acceder a:
```
http://localhost:8000
```

### Iniciar sesión con tu usuario y contraseña

Si ves la pantalla de login y puedes iniciar sesión → **¡Migración exitosa!** 🎉

---

## 🔍 Solución de Problemas

### Error: "execute_query() got an unexpected keyword argument"
**Solución:** Ya está corregido en la versión actual. Asegúrate de hacer `git pull` para obtener la última versión.

### Error: "Read-only file system: 'working/logs.json'"
**Solución:** Ya está corregido en `docker-compose.yml`. Necesitas:
```bash
docker compose down
docker compose up -d
```

### La aplicación no inicia
**Ver logs:**
```bash
docker compose logs -f app
```

### PostgreSQL no tiene datos
**Verificar:**
```bash
docker compose exec postgres psql -U pipeenlinea_user -d pipeenlinea -c "SELECT COUNT(*) FROM usuarios;"
```

Si retorna 0, necesitas migrar los datos primero:
```bash
docker compose --profile migrate run --rm migration
```

---

## 📊 Estadísticas de la Base de Datos

Para ver cuántos registros hay en cada tabla:

```bash
docker compose exec postgres psql -U pipeenlinea_user -d pipeenlinea -c "
    SELECT
        'usuarios' as tabla, COUNT(*) as registros FROM usuarios
    UNION ALL
    SELECT 'empresas', COUNT(*) FROM empresas
    UNION ALL
    SELECT 'solicitudes', COUNT(*) FROM solicitudes
    UNION ALL
    SELECT 'logs', COUNT(*) FROM logs
    ORDER BY registros DESC;
"
```

---

## 🔄 Cómo Funciona el Sistema Híbrido

La nueva versión de `update.py` (que es `update_postgres.py` renombrado) funciona así:

1. **Intenta leer de PostgreSQL primero**
   - Si encuentra datos → los retorna ✅

2. **Si PostgreSQL falla → lee del JSON**
   - Fallback automático a JSON encriptado 🔄

3. **Escrituras:**
   - Por ahora se escriben solo a JSON (logs, etc.)
   - En futuras versiones se migrarán también a PostgreSQL

### Ventajas:
- ✅ **Cero cambios** en el código existente (routes_login2.py, etc.)
- ✅ **Seguro** - si PostgreSQL falla, usa JSON
- ✅ **Gradual** - puedes migrar tabla por tabla
- ✅ **Compatible** - todo el código legacy funciona igual

---

## 🎉 ¡Listo!

Tu sistema ahora está usando PostgreSQL para leer datos, con JSON como respaldo.

**Próximos pasos (opcional):**
- Migrar escrituras a PostgreSQL (logs, nuevas solicitudes)
- Eliminar dependencia de JSON completamente
- Optimizar queries con índices
