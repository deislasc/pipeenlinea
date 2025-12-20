#!/bin/bash
# ============================================================================
# Script de Migración a PostgreSQL - PipeEnLinea
# Cambia de JSONs a PostgreSQL de forma automática
# ============================================================================

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}              MIGRACIÓN A POSTGRESQL - PIPEENLINEA                   ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ============================================================================
# PASO 1: Verificar prerequisitos
# ============================================================================
echo -e "${BLUE}[1/5]${NC} Verificando prerequisitos..."

# Verificar que PostgreSQL esté corriendo
if ! docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${RED}❌ PostgreSQL no está corriendo${NC}"
    echo "Ejecuta primero: ./start.sh"
    exit 1
fi

echo -e "${GREEN}✅ PostgreSQL está corriendo${NC}"

# Verificar que los datos estén migrados
row_count=$(docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -t -c "SELECT COUNT(*) FROM usuarios;" 2>/dev/null | xargs || echo "0")

if [ "$row_count" -eq "0" ]; then
    echo -e "${RED}❌ No hay datos migrados en PostgreSQL${NC}"
    echo "Ejecuta primero: docker-compose --profile migrate run --rm migration"
    exit 1
fi

echo -e "${GREEN}✅ Datos migrados: $row_count usuarios en PostgreSQL${NC}"

# ============================================================================
# PASO 2: Backup del código original
# ============================================================================
echo ""
echo -e "${BLUE}[2/5]${NC} Creando backup del código original..."

cd mysite

# Backup de update.py
if [ ! -f "update_original.py" ]; then
    cp update.py update_original.py
    echo -e "${GREEN}✅ Backup creado: update_original.py${NC}"
else
    echo -e "${YELLOW}⚠️  Backup ya existe: update_original.py${NC}"
fi

# ============================================================================
# PASO 3: Reemplazar update.py con la versión PostgreSQL
# ============================================================================
echo ""
echo -e "${BLUE}[3/5]${NC} Reemplazando update.py con versión PostgreSQL..."

# Verificar que update_postgres.py exista
if [ ! -f "update_postgres.py" ]; then
    echo -e "${RED}❌ No se encontró update_postgres.py${NC}"
    exit 1
fi

# Reemplazar
cp update_postgres.py update.py
echo -e "${GREEN}✅ update.py reemplazado con versión PostgreSQL${NC}"

cd ..

# ============================================================================
# PASO 4: Reconstruir contenedores Docker
# ============================================================================
echo ""
echo -e "${BLUE}[4/5]${NC} Reconstruyendo contenedores Docker..."

# Detener servicios
echo "Deteniendo servicios..."
docker-compose down

# Reconstruir la imagen de la app
echo "Reconstruyendo imagen de la aplicación..."
docker-compose build app

# Iniciar servicios
echo "Iniciando servicios..."
docker-compose up -d

# ============================================================================
# PASO 5: Verificar que la aplicación esté funcionando
# ============================================================================
echo ""
echo -e "${BLUE}[5/5]${NC} Verificando que la aplicación esté lista..."

# Esperar a que la app responda
echo -n "Esperando a que la aplicación esté lista"
for i in {1..30}; do
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✅ Aplicación respondiendo en http://localhost:8000${NC}"
        break
    fi
    echo -n "."
    sleep 2

    if [ $i -eq 30 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  La aplicación no responde aún${NC}"
        echo "Ver logs: docker-compose logs -f app"
        break
    fi
done

# ============================================================================
# Reporte Final
# ============================================================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                  ¡MIGRACIÓN COMPLETADA! 🎉                         ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✅ La aplicación ahora lee datos de PostgreSQL${NC}"
echo -e "${GREEN}✅ Los JSONs encriptados funcionan como respaldo${NC}"
echo ""
echo -e "${YELLOW}📋 Cambios realizados:${NC}"
echo "   • update.py reemplazado con versión híbrida PostgreSQL"
echo "   • Backup guardado en: mysite/update_original.py"
echo "   • Contenedores Docker reconstruidos"
echo ""
echo -e "${CYAN}🌐 Acceso al Sistema:${NC}"
echo "   • Aplicación Web: http://localhost:8000"
echo "   • PostgreSQL: localhost:5432"
echo ""
echo -e "${CYAN}📊 Estadísticas de datos:${NC}"
docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -c "
    SELECT
        'usuarios' as tabla, COUNT(*) as registros FROM usuarios
    UNION ALL
    SELECT 'empresas', COUNT(*) FROM empresas
    UNION ALL
    SELECT 'solicitudes', COUNT(*) FROM solicitudes
    UNION ALL
    SELECT 'logs', COUNT(*) FROM logs
    ORDER BY registros DESC;
" 2>/dev/null || echo "No se pudo obtener estadísticas"

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Sistema listo para usar - Ingresa con tu usuario y contraseña${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Mostrar logs en tiempo real (opcional)
read -p "¿Deseas ver los logs de la aplicación? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    docker-compose logs -f app
fi
