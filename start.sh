#!/bin/bash
# ============================================================================
# Script de Inicio Automático - Pipeenlinea
# Arranca todo el sistema sin intervención manual
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
echo -e "${CYAN}                    PIPEENLINEA - Inicio Automático                 ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ============================================================================
# PASO 1: Verificaciones de Prerequisitos
# ============================================================================
echo -e "${BLUE}[1/6]${NC} Verificando prerequisitos..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    echo "Instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    exit 1
fi

# Verificar que Docker esté corriendo
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker no está corriendo${NC}"
    echo "Inicia Docker Desktop o el daemon de Docker"
    exit 1
fi

echo -e "${GREEN}✅ Docker y Docker Compose están listos${NC}"

# ============================================================================
# PASO 2: Configuración de Variables de Entorno
# ============================================================================
echo -e "${BLUE}[2/6]${NC} Configurando variables de entorno..."

if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado, creando desde .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Archivo .env creado${NC}"
    else
        echo -e "${YELLOW}⚠️  .env.example tampoco existe, creando .env básico...${NC}"
        cat > .env <<EOF
# Base de Datos PostgreSQL
DB_HOST=postgres
DB_PORT=5432
DB_NAME=pipeenlinea
DB_USER=pipeenlinea_user
DB_PASSWORD=pipeenlinea_secure_2024

# Flask
FLASK_ENV=development
SECRET_KEY=$(openssl rand -hex 32)

# pgAdmin (opcional, solo desarrollo)
PGADMIN_EMAIL=admin@pipeenlinea.com
PGADMIN_PASSWORD=admin123

# Azure PostgreSQL (producción)
# AZURE_DB_HOST=your-server.postgres.database.azure.com
# AZURE_DB_PORT=5432
# AZURE_DB_NAME=pipeenlinea
# AZURE_DB_USER=your-user@your-server
# AZURE_DB_PASSWORD=your-password
# AZURE_DB_SSLMODE=require
EOF
        echo -e "${GREEN}✅ Archivo .env creado con valores por defecto${NC}"
    fi
else
    echo -e "${GREEN}✅ Archivo .env encontrado${NC}"
fi

# Verificar secret.key
if [ ! -f secret.key ]; then
    echo -e "${YELLOW}⚠️  secret.key no encontrado${NC}"
    echo -e "${RED}❌ CRÍTICO: El archivo secret.key es necesario para desencriptar los JSONs${NC}"
    echo ""
    echo "Por favor:"
    echo "1. Copia tu archivo secret.key a la raíz del proyecto"
    echo "2. Ejecuta este script nuevamente"
    exit 1
fi
echo -e "${GREEN}✅ secret.key encontrado${NC}"

# Verificar archivos JSON en working/
if [ ! -d "working" ]; then
    echo -e "${YELLOW}⚠️  Directorio working/ no encontrado${NC}"
    mkdir -p working
    echo -e "${GREEN}✅ Directorio working/ creado${NC}"
fi

json_count=$(find working -name "*.json" 2>/dev/null | wc -l)
if [ "$json_count" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No se encontraron archivos JSON en working/${NC}"
    echo "   (Esto es normal si ya migraste los datos)"
else
    echo -e "${GREEN}✅ Encontrados $json_count archivos JSON en working/${NC}"
fi

# ============================================================================
# PASO 3: Detener Servicios Previos (si existen)
# ============================================================================
echo -e "${BLUE}[3/6]${NC} Verificando servicios existentes..."

if docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Hay servicios corriendo, deteniéndolos...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Servicios previos detenidos${NC}"
else
    echo -e "${GREEN}✅ No hay servicios previos corriendo${NC}"
fi

# ============================================================================
# PASO 4: Iniciar PostgreSQL
# ============================================================================
echo ""
echo -e "${BLUE}[4/6]${NC} Iniciando PostgreSQL..."

docker-compose up -d postgres

# Esperar a que PostgreSQL esté listo (máximo 30 segundos)
echo -n "Esperando a que PostgreSQL esté listo"
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U pipeenlinea_user > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✅ PostgreSQL está listo y aceptando conexiones${NC}"
        break
    fi
    echo -n "."
    sleep 1

    if [ $i -eq 30 ]; then
        echo ""
        echo -e "${RED}❌ PostgreSQL no respondió en 30 segundos${NC}"
        echo "Ver logs: docker-compose logs postgres"
        exit 1
    fi
done

# Verificar si las tablas ya existen
echo "Verificando esquema de base de datos..."
table_count=$(docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs || echo "0")

if [ "$table_count" -eq "0" ]; then
    echo -e "${YELLOW}⚠️  Base de datos vacía, creando esquema...${NC}"

    if [ -f "database/schema.sql" ]; then
        docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea < database/schema.sql
        echo -e "${GREEN}✅ Esquema creado${NC}"

        if [ -f "database/indexes.sql" ]; then
            docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea < database/indexes.sql
            echo -e "${GREEN}✅ Índices creados${NC}"
        fi
    else
        echo -e "${RED}❌ No se encontró database/schema.sql${NC}"
        echo "Continuar sin esquema, la app debe crearlo..."
    fi
else
    echo -e "${GREEN}✅ Base de datos ya tiene $table_count tablas${NC}"
fi

# ============================================================================
# PASO 5: Iniciar Aplicación Flask
# ============================================================================
echo ""
echo -e "${BLUE}[5/6]${NC} Iniciando aplicación Flask..."

# Build de la imagen (por si hubo cambios)
echo "Construyendo imagen de la aplicación..."
docker-compose build app

# Iniciar aplicación
docker-compose up -d app

# Esperar a que la app esté lista
echo -n "Esperando a que la aplicación esté lista"
for i in {1..20}; do
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✅ Aplicación Flask está respondiendo${NC}"
        break
    fi
    echo -n "."
    sleep 1

    if [ $i -eq 20 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  La aplicación no responde aún (puede tardar un poco más)${NC}"
        echo "   Continúa verificando en segundo plano..."
        break
    fi
done

# ============================================================================
# PASO 6: Verificación Final y Reporte
# ============================================================================
echo ""
echo -e "${BLUE}[6/6]${NC} Verificación final del sistema..."

# Estado de servicios
services_status=$(docker-compose ps 2>&1)
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                        ESTADO DE SERVICIOS                         ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
docker-compose ps
echo ""

# Verificar cada servicio
postgres_ok=false
app_ok=false

if docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${GREEN}✅ PostgreSQL${NC} - Corriendo"
    postgres_ok=true
else
    echo -e "${RED}❌ PostgreSQL${NC} - No está corriendo"
fi

if docker-compose ps | grep -q "app.*Up"; then
    echo -e "${GREEN}✅ Flask App${NC} - Corriendo"
    app_ok=true
else
    echo -e "${RED}❌ Flask App${NC} - No está corriendo"
fi

# Estadísticas de base de datos
if [ "$postgres_ok" = true ]; then
    echo ""
    echo -e "${CYAN}📊 Estadísticas de Base de Datos:${NC}"
    docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -c "
        SELECT
            tablename AS \"Tabla\",
            pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS \"Tamaño\"
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size('public.'||tablename) DESC;
    " 2>/dev/null || echo "No se pudo obtener estadísticas"
fi

# ============================================================================
# Reporte Final
# ============================================================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                         ¡SISTEMA LISTO! 🚀                         ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ "$app_ok" = true ]; then
    echo -e "${GREEN}🌐 Aplicación Web:${NC}      http://localhost:8000"
else
    echo -e "${YELLOW}⚠️  Aplicación Web:${NC}      No está respondiendo aún"
    echo "   Ejecuta: docker-compose logs -f app"
fi

echo -e "${GREEN}🗄️  PostgreSQL:${NC}          localhost:5432"
echo -e "${GREEN}📊 pgAdmin (opcional):${NC}   Ejecuta: docker-compose --profile dev up -d pgadmin"
echo "                         Luego accede a: http://localhost:5050"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                      COMANDOS ÚTILES                               ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Ver logs en tiempo real:"
echo -e "  ${BLUE}docker-compose logs -f${NC}"
echo ""
echo "Ver logs solo de la app:"
echo -e "  ${BLUE}docker-compose logs -f app${NC}"
echo ""
echo "Conectar a PostgreSQL:"
echo -e "  ${BLUE}docker-compose exec postgres psql -U pipeenlinea_user -d pipeenlinea${NC}"
echo ""
echo "Detener servicios:"
echo -e "  ${BLUE}docker-compose down${NC}"
echo ""
echo "Reiniciar servicios:"
echo -e "  ${BLUE}docker-compose restart${NC}"
echo ""
echo "Migrar datos desde JSON (DRY-RUN):"
echo -e "  ${BLUE}docker-compose --profile migrate run --rm migration --dry-run${NC}"
echo ""
echo "Migrar datos desde JSON (REAL):"
echo -e "  ${BLUE}docker-compose --profile migrate run --rm migration${NC}"
echo ""

# Advertencia si hay archivos JSON pero no se han migrado
if [ "$json_count" -gt 0 ] && [ "$table_count" -gt 0 ]; then
    row_count=$(docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -t -c "SELECT COUNT(*) FROM solicitudes;" 2>/dev/null | xargs || echo "0")
    if [ "$row_count" -eq "0" ]; then
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}                    ⚠️  MIGRACIÓN PENDIENTE                         ${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "Se detectaron archivos JSON pero la base de datos está vacía."
        echo "Para migrar los datos ejecuta:"
        echo -e "  ${BLUE}docker-compose --profile migrate run --rm migration${NC}"
        echo ""
    fi
fi

echo -e "${GREEN}✅ Sistema iniciado exitosamente${NC}"
echo ""
