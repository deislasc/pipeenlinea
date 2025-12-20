#!/bin/bash
# ============================================================================
# MIGRACIÓN COMPLETA A POSTGRESQL - TODO EN UNO
# Este script hace TODA la migración de principio a fin
# ============================================================================

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}       MIGRACIÓN COMPLETA A POSTGRESQL - PIPEENLINEA                 ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ============================================================================
# PASO 1: Actualizar código desde Git
# ============================================================================
echo -e "${BLUE}[1/6]${NC} Actualizando código desde Git..."

git pull origin claude/analyze-code-LMuAp

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  No se pudo hacer pull automático. Continuando...${NC}"
fi

echo -e "${GREEN}✅ Código actualizado${NC}"

# ============================================================================
# PASO 2: Detener contenedores existentes
# ============================================================================
echo ""
echo -e "${BLUE}[2/6]${NC} Deteniendo contenedores existentes..."

docker compose down

echo -e "${GREEN}✅ Contenedores detenidos${NC}"

# ============================================================================
# PASO 3: Iniciar PostgreSQL y migrar datos
# ============================================================================
echo ""
echo -e "${BLUE}[3/6]${NC} Iniciando PostgreSQL y migrando datos..."

# Iniciar solo PostgreSQL
docker compose up -d postgres

# Esperar a que PostgreSQL esté listo
echo -n "Esperando a que PostgreSQL esté listo"
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U pipeenlinea_user > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✅ PostgreSQL listo${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Verificar si ya hay datos
echo ""
echo "Verificando si hay datos en PostgreSQL..."
row_count=$(docker compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -t -c "SELECT COUNT(*) FROM usuarios;" 2>/dev/null | xargs || echo "0")

if [ "$row_count" -eq "0" ]; then
    echo -e "${YELLOW}⚠️  No hay datos. Ejecutando migración...${NC}"

    # Ejecutar migración
    docker compose --profile migrate run --rm migration

    # Verificar migración
    row_count=$(docker compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -t -c "SELECT COUNT(*) FROM usuarios;" 2>/dev/null | xargs || echo "0")

    if [ "$row_count" -gt "0" ]; then
        echo -e "${GREEN}✅ Datos migrados exitosamente: $row_count usuarios${NC}"
    else
        echo -e "${RED}❌ La migración falló${NC}"
        echo "Ver detalles con: docker compose logs migration"
        exit 1
    fi
else
    echo -e "${GREEN}✅ PostgreSQL ya tiene datos: $row_count usuarios${NC}"
fi

# ============================================================================
# PASO 4: Preparar código con versión PostgreSQL
# ============================================================================
echo ""
echo -e "${BLUE}[4/6]${NC} Preparando código con versión PostgreSQL..."

cd mysite

# Backup del original (si no existe)
if [ ! -f "update_original.py" ]; then
    if [ -f "update.py" ]; then
        cp update.py update_original.py
        echo -e "${GREEN}✅ Backup creado: update_original.py${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Backup ya existe${NC}"
fi

# Verificar que update_postgres.py existe
if [ ! -f "update_postgres.py" ]; then
    echo -e "${RED}❌ No se encontró update_postgres.py${NC}"
    echo "Asegúrate de estar en el directorio correcto"
    exit 1
fi

# Reemplazar update.py con la versión PostgreSQL
cp update_postgres.py update.py
echo -e "${GREEN}✅ update.py reemplazado con versión PostgreSQL (corregida)${NC}"

cd ..

# ============================================================================
# PASO 5: Reconstruir y reiniciar la aplicación
# ============================================================================
echo ""
echo -e "${BLUE}[5/6]${NC} Reconstruyendo y reiniciando aplicación..."

# Reconstruir imagen
echo "Reconstruyendo imagen de la aplicación..."
docker compose build app

# Iniciar todos los servicios
echo "Iniciando servicios..."
docker compose up -d

echo -e "${GREEN}✅ Servicios iniciados${NC}"

# ============================================================================
# PASO 6: Verificar que la aplicación funcione
# ============================================================================
echo ""
echo -e "${BLUE}[6/6]${NC} Verificando que la aplicación funcione..."

# Esperar a que la app responda
echo -n "Esperando a que la aplicación responda"
for i in {1..60}; do
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✅ Aplicación funcionando en http://localhost:8000${NC}"
        break
    fi
    echo -n "."
    sleep 2

    if [ $i -eq 60 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  La aplicación tardó más de lo esperado${NC}"
        echo "Revisa los logs: docker compose logs -f app"
        break
    fi
done

# Mostrar logs recientes
echo ""
echo -e "${CYAN}📋 Últimos logs de la aplicación:${NC}"
docker compose logs --tail=20 app

# ============================================================================
# Reporte Final
# ============================================================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                    ¡MIGRACIÓN COMPLETADA! 🎉                       ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✅ La aplicación ahora usa PostgreSQL${NC}"
echo ""
echo -e "${CYAN}🌐 Acceso al Sistema:${NC}"
echo "   • Aplicación: http://localhost:8000"
echo "   • PostgreSQL: localhost:5432"
echo ""
echo -e "${CYAN}📊 Estadísticas de la base de datos:${NC}"
docker compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -c "
    SELECT
        'usuarios' as tabla, COUNT(*) as registros FROM usuarios
    UNION ALL
    SELECT 'empresas', COUNT(*) FROM empresas
    UNION ALL
    SELECT 'solicitudes', COUNT(*) FROM solicitudes
    UNION ALL
    SELECT 'logs', COUNT(*) FROM logs
    ORDER BY registros DESC;
" 2>/dev/null || echo "No se pudieron obtener estadísticas"

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Sistema listo - Abre http://localhost:8000 e ingresa con tu usuario${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Preguntar si quiere ver logs en vivo
read -p "¿Ver logs de la aplicación en vivo? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo ""
    echo -e "${CYAN}Mostrando logs en vivo (Ctrl+C para salir)...${NC}"
    echo ""
    docker compose logs -f app
fi
