# 🚀 MIGRACIÓN A POSTGRESQL - INSTRUCCIONES SIMPLES

## ⚡ EJECUTA UN SOLO COMANDO

```bash
./migracion_completa.sh
```

Eso es todo. El script hace **TODO automáticamente**:

1. ✅ Descarga las correcciones de Git
2. ✅ Inicia PostgreSQL
3. ✅ Migra los datos de JSON a PostgreSQL
4. ✅ Reemplaza el código con la versión corregida
5. ✅ Reconstruye los contenedores
6. ✅ Inicia la aplicación
7. ✅ Verifica que todo funcione

---

## 📝 Si el script no existe, ejecútalo así:

```bash
# 1. Traer los cambios de Git
git pull origin claude/analyze-code-LMuAp

# 2. Dar permisos de ejecución
chmod +x migracion_completa.sh

# 3. Ejecutar
./migracion_completa.sh
```

---

## 🎯 Después de la migración

1. Abre tu navegador en: **http://localhost:8000**
2. Ingresa con tu usuario y contraseña
3. ✅ **¡Listo! El sistema está usando PostgreSQL**

---

## 🔍 Verificar que todo funcione

Deberías ver en los logs:
```
✅ Leídos 15 registros de PostgreSQL (usuarios)
✅ Leídos 1234 registros de PostgreSQL (solicitudes)
```

En lugar de:
```
❌ Error leyendo de PostgreSQL: ...
📄 Leyendo desde JSON: ...
```

---

## 🆘 Si algo falla

Ver los logs:
```bash
docker compose logs -f app
```

Ver datos en PostgreSQL:
```bash
docker compose exec postgres psql -U pipeenlinea_user -d pipeenlinea -c "SELECT COUNT(*) FROM usuarios;"
```

---

## 📁 Archivos Importantes

- **migracion_completa.sh** ← El script maestro (USA ESTE)
- **update_postgres.py** ← Versión híbrida PostgreSQL/JSON
- **docker-compose.yml** ← Configuración de contenedores
- **mysite/update.py** ← Se reemplaza automáticamente

---

## ✅ ¿Qué hace el sistema híbrido?

**Lee de PostgreSQL primero**, si falla lee del JSON:

```python
# Intenta PostgreSQL
usuarios = leer_de_postgres("usuarios")  # ✅ Rápido
if no_funciona:
    usuarios = leer_de_json("users.json")  # 🔄 Fallback
```

**Ventajas:**
- ✅ Más rápido (PostgreSQL es más eficiente)
- ✅ Seguro (si PostgreSQL falla, usa JSON)
- ✅ Sin cambios en el código (compatible 100%)
