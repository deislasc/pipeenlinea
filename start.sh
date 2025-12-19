#!/bin/bash
# ============================================================================
# Script de Inicio Rápido - Pipeenlinea
# ============================================================================

set -e

echo "=========================================="
echo "  PIPEENLINEA - Inicio Rápido"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que existe .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
    echo "Creando desde .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  IMPORTANTE: Edita .env con tus credenciales antes de continuar${NC}"
    echo ""
    read -p "Presiona ENTER para continuar..."
fi

# Función para verificar si un servicio está corriendo
check_service() {
    service_name=$1
    if docker-compose ps | grep -q "$service_name.*Up"; then
        echo -e "${GREEN}✅ $service_name está corriendo${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name NO está corriendo${NC}"
        return 1
    fi
}

# Menú principal
echo "Selecciona una opción:"
echo ""
echo "1) 🚀 Inicio Completo (PostgreSQL + App)"
echo "2) 🗄️  Solo PostgreSQL"
echo "3) 📦 Migración de Datos (Dry-Run)"
echo "4) 📦 Migración de Datos (REAL)"
echo "5) 🔍 Ver Logs"
echo "6) 🛑 Detener Todo"
echo "7) 🧹 Limpiar Todo (¡CUIDADO!)"
echo "8) 📊 Estado de Servicios"
echo "9) 🔧 pgAdmin (solo desarrollo)"
echo "0) ❌ Salir"
echo ""
read -p "Opción: " option

case $option in
    1)
        echo ""
        echo "🚀 Iniciando servicios completos..."
        echo ""

        # Levantar PostgreSQL primero
        echo "1/3: Levantando PostgreSQL..."
        docker-compose up -d postgres

        # Esperar a que PostgreSQL esté listo
        echo "Esperando a que PostgreSQL esté listo..."
        sleep 10

        # Verificar conexión
        if docker-compose exec -T postgres pg_isready -U pipeenlinea_user > /dev/null 2>&1; then
            echo -e "${GREEN}✅ PostgreSQL está listo${NC}"
        else
            echo -e "${RED}❌ PostgreSQL no responde${NC}"
            exit 1
        fi

        # Levantar aplicación
        echo ""
        echo "2/3: Levantando aplicación Flask..."
        docker-compose up -d app

        echo ""
        echo "3/3: Verificando servicios..."
        sleep 5
        check_service "postgres"
        check_service "app"

        echo ""
        echo -e "${GREEN}✅ Todo listo!${NC}"
        echo ""
        echo "Accede a la aplicación en: http://localhost:8000"
        echo "Ver logs: docker-compose logs -f"
        ;;

    2)
        echo ""
        echo "🗄️  Iniciando solo PostgreSQL..."
        docker-compose up -d postgres

        sleep 5
        check_service "postgres"

        echo ""
        echo "Conectar con: docker-compose exec postgres psql -U pipeenlinea_user -d pipeenlinea"
        ;;

    3)
        echo ""
        echo "📦 Ejecutando migración (DRY-RUN)..."
        echo ""
        docker-compose --profile migrate run --rm migration --dry-run
        ;;

    4)
        echo ""
        echo -e "${YELLOW}⚠️  ADVERTENCIA: Esto migrará TODOS los datos a PostgreSQL${NC}"
        read -p "¿Estás seguro? (escribe 'SI' para continuar): " confirm

        if [ "$confirm" = "SI" ]; then
            echo ""
            echo "📦 Ejecutando migración REAL..."
            echo ""
            docker-compose --profile migrate run --rm migration

            echo ""
            echo -e "${GREEN}✅ Migración completada${NC}"
            echo ""
            echo "Verifica los datos con:"
            echo "  docker-compose exec postgres psql -U pipeenlinea_user -d pipeenlinea"
        else
            echo "Migración cancelada"
        fi
        ;;

    5)
        echo ""
        echo "📋 Logs (Ctrl+C para salir)..."
        docker-compose logs -f
        ;;

    6)
        echo ""
        echo "🛑 Deteniendo servicios..."
        docker-compose down
        echo -e "${GREEN}✅ Servicios detenidos${NC}"
        ;;

    7)
        echo ""
        echo -e "${RED}⚠️  ADVERTENCIA: Esto eliminará TODOS los contenedores, volúmenes y datos${NC}"
        read -p "¿Estás COMPLETAMENTE seguro? (escribe 'BORRAR TODO' para continuar): " confirm

        if [ "$confirm" = "BORRAR TODO" ]; then
            echo ""
            echo "🧹 Limpiando todo..."
            docker-compose down -v --remove-orphans
            docker system prune -f
            echo -e "${GREEN}✅ Limpieza completada${NC}"
        else
            echo "Limpieza cancelada"
        fi
        ;;

    8)
        echo ""
        echo "📊 Estado de servicios:"
        echo ""
        docker-compose ps
        echo ""

        # Verificar cada servicio
        check_service "postgres" || true
        check_service "app" || true

        # Estadísticas de base de datos
        echo ""
        if check_service "postgres" > /dev/null 2>&1; then
            echo "📊 Estadísticas de base de datos:"
            docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -c "
                SELECT
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 5;
            " 2>/dev/null || echo "No se pudo obtener estadísticas"
        fi
        ;;

    9)
        echo ""
        echo "🔧 Iniciando pgAdmin (desarrollo)..."
        docker-compose --profile dev up -d pgadmin

        sleep 5
        check_service "pgadmin"

        echo ""
        echo "Accede a pgAdmin en: http://localhost:5050"
        echo "Email: admin@pipeenlinea.com"
        echo "Password: (el configurado en .env)"
        ;;

    0)
        echo "Saliendo..."
        exit 0
        ;;

    *)
        echo -e "${RED}Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
