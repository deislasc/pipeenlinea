#!/bin/bash
# ============================================================================
# RESET Y MIGRACIÓN COMPLETA A POSTGRESQL
# Elimina datos actuales, recrea schema completo desde JSON real, migra TODO
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
echo -e "${CYAN}       RESET Y MIGRACIÓN COMPLETA A POSTGRESQL                       ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ============================================================================
# PASO 1: Verificar que PostgreSQL esté corriendo
# ============================================================================
echo -e "${BLUE}[1/5]${NC} Verificando PostgreSQL..."

if ! docker compose ps | grep -q "postgres.*Up"; then
    echo -e "${YELLOW}PostgreSQL no está corriendo. Iniciando...${NC}"
    docker compose up -d postgres
    sleep 5
fi

echo -e "${GREEN}✅ PostgreSQL está corriendo${NC}"

# ============================================================================
# PASO 2: Hacer BACKUP de datos actuales (por si acaso)
# ============================================================================
echo ""
echo -e "${BLUE}[2/5]${NC} Creando backup de PostgreSQL actual..."

mkdir -p backups
backup_file="backups/backup_$(date +%Y%m%d_%H%M%S).sql"

docker compose exec -T postgres pg_dump -U pipeenlinea_user pipeenlinea > "$backup_file" 2>/dev/null || true

if [ -f "$backup_file" ]; then
    echo -e "${GREEN}✅ Backup creado: $backup_file${NC}"
else
    echo -e "${YELLOW}⚠️  No se pudo crear backup (base vacía o error)${NC}"
fi

# ============================================================================
# PASO 3: Eliminar schema actual y recrear con schema completo
# ============================================================================
echo ""
echo -e "${BLUE}[3/5]${NC} Aplicando schema completo (generado desde estructura JSON real)..."

# Aplicar schema completo
docker compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea < database/schema_completo.sql

echo -e "${GREEN}✅ Schema completo creado${NC}"

# ============================================================================
# PASO 4: Ejecutar migración completa
# ============================================================================
echo ""
echo -e "${BLUE}[4/5]${NC} Migrando TODOS los datos de JSON a PostgreSQL..."

# Reconstruir imagen de migración
echo "Reconstruyendo imagen de migración..."
docker compose build migration

# Ejecutar migración completa
echo "Iniciando migración completa..."
docker compose --profile migrate run --rm migration

# ============================================================================
# PASO 5: Verificar resultados
# ============================================================================
echo ""
echo -e "${BLUE}[5/5]${NC} Verificando resultados de la migración..."

echo ""
echo -e "${CYAN}📊 Registros migrados:${NC}"
docker compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -c "
    SELECT
        'usuarios' as tabla, COUNT(*) as registros FROM usuarios
    UNION ALL
    SELECT 'empresas', COUNT(*) FROM empresas
    UNION ALL
    SELECT 'solicitudes', COUNT(*) FROM solicitudes
    UNION ALL
    SELECT 'logs', COUNT(*) FROM logs
    UNION ALL
    SELECT 'geolocalizaciones', COUNT(*) FROM geolocalizaciones
    UNION ALL
    SELECT 'acl', COUNT(*) FROM acl
    UNION ALL
    SELECT 'agendas', COUNT(*) FROM agendas
    UNION ALL
    SELECT 'operaciones_internas_preocupantes', COUNT(*) FROM operaciones_internas_preocupantes
    ORDER BY registros DESC;
"

# ============================================================================
# Reporte Final
# ============================================================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}              ¡MIGRACIÓN COMPLETA FINALIZADA! 🎉                     ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✅ Todos los datos han sido migrados a PostgreSQL${NC}"
echo -e "${GREEN}✅ Backup guardado en: $backup_file${NC}"
echo ""
echo -e "${YELLOW}📋 Siguiente paso:${NC}"
echo "   Ejecuta: ./migracion_completa.sh"
echo "   Para actualizar la aplicación y usar PostgreSQL"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
