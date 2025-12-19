#!/bin/bash
# ============================================================================
# Script de Migración Interactivo - Pipeenlinea
# Migra datos desde JSONs encriptados a PostgreSQL
# ============================================================================

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Banner
echo ""
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}              PIPEENLINEA - Migración de Datos JSON → PostgreSQL    ${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ============================================================================
# Verificaciones previas (solo una vez al inicio)
# ============================================================================
echo -e "${BLUE}📋 Verificando prerequisitos...${NC}"
echo ""

# Verificar que PostgreSQL esté corriendo
if ! docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${RED}❌ PostgreSQL no está corriendo${NC}"
    echo "Inicia los servicios primero con:"
    echo -e "  ${BLUE}./start.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✅ PostgreSQL está corriendo${NC}"

# Verificar archivos JSON
json_count=$(find working -name "*.json" 2>/dev/null | wc -l)
if [ "$json_count" -eq 0 ]; then
    echo -e "${RED}❌ No se encontraron archivos JSON en working/${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Encontrados $json_count archivos JSON en working/${NC}"

# Verificar secret.key
if [ ! -f secret.key ]; then
    echo -e "${RED}❌ Archivo secret.key no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ secret.key encontrado${NC}"

# ============================================================================
# LOOP PRINCIPAL - Permite ejecutar múltiples operaciones
# ============================================================================
while true; do
    # Verificar estado actual de la base de datos
    echo ""
    echo -e "${BLUE}📊 Estado actual de la base de datos:${NC}"
    row_count=$(docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -t -c "SELECT COUNT(*) FROM solicitudes;" 2>/dev/null | xargs || echo "0")
    echo -e "  Registros en tabla solicitudes: ${YELLOW}$row_count${NC}"

    if [ "$row_count" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠️  La tabla ya tiene datos${NC}"
    fi

    # ============================================================================
    # Menú de opciones
    # ============================================================================
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}                    OPCIONES DE MIGRACIÓN                            ${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "1) 🧪 Dry-Run (Prueba sin guardar)"
    echo "   → Simula la migración sin modificar la base de datos"
    echo "   → Verifica que los datos se puedan leer y transformar correctamente"
    echo "   → RECOMENDADO: Ejecutar esto primero"
    echo ""
    echo "2) 🚀 Migración Real (Todo)"
    echo "   → Migra TODOS los archivos JSON a PostgreSQL"
    echo "   → Batch size: 1000 registros por vez"
    echo "   → GUARDA los datos permanentemente"
    echo ""
    echo "3) ⚙️  Migración con Batch Size Personalizado"
    echo "   → Migra todos los archivos con batch size que elijas"
    echo "   → Útil para conjuntos de datos muy grandes"
    echo ""
    echo "4) 🎯 Omitir Tablas Específicas"
    echo "   → Migra todos los archivos EXCEPTO las tablas que elijas"
    echo "   → Útil si solo quieres migrar algunas tablas"
    echo ""
    echo "5) 📊 Ver Estado de la Base de Datos"
    echo "   → Muestra estadísticas de registros por tabla"
    echo ""
    echo "6) 🔄 Limpiar Base de Datos y Empezar de Cero"
    echo "   → ELIMINA todos los datos y reinicia la migración"
    echo "   → ⚠️  PELIGROSO: Borra todo permanentemente"
    echo ""
    echo "0) ❌ Salir"
    echo ""
    read -p "Selecciona una opción: " option

    case $option in
        1)
            echo ""
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${CYAN}                    🧪 DRY-RUN (PRUEBA)                             ${NC}"
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo "Simulando migración sin guardar datos..."
            echo ""

            docker-compose --profile migrate run --rm migration --dry-run

            echo ""
            echo -e "${GREEN}✅ Dry-Run completado${NC}"
            ;;

        2)
            echo ""
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${CYAN}                    🚀 MIGRACIÓN REAL                               ${NC}"
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo -e "${YELLOW}⚠️  ADVERTENCIA: Esto migrará TODOS los datos a PostgreSQL${NC}"
            echo -e "${YELLOW}⚠️  Los datos se guardarán PERMANENTEMENTE${NC}"
            echo ""
            read -p "¿Estás completamente seguro? (escribe 'MIGRAR' para continuar): " confirm

            if [ "$confirm" = "MIGRAR" ]; then
                echo ""
                echo "🚀 Iniciando migración real..."
                echo ""

                # Timestamp de inicio
                start_time=$(date +%s)

                docker-compose --profile migrate run --rm migration

                # Timestamp de fin
                end_time=$(date +%s)
                duration=$((end_time - start_time))

                echo ""
                echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo -e "${GREEN}                    ✅ MIGRACIÓN COMPLETADA                         ${NC}"
                echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo ""
                echo -e "Tiempo total: ${CYAN}${duration}s${NC}"
                echo ""

                # Mostrar estadísticas
                echo "📊 Estadísticas de migración:"
                docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -c "
                    SELECT
                        tablename AS \"Tabla\",
                        n_tup_ins AS \"Registros Insertados\",
                        pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS \"Tamaño\"
                    FROM pg_stat_user_tables
                    WHERE schemaname = 'public'
                    ORDER BY n_tup_ins DESC;
                " 2>/dev/null || echo "No se pudieron obtener estadísticas"

                echo ""
                echo "✅ Los archivos JSON originales permanecen intactos en working/"
            else
                echo "Migración cancelada"
            fi
            ;;

        3)
            echo ""
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${CYAN}              ⚙️  MIGRACIÓN CON BATCH SIZE PERSONALIZADO            ${NC}"
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo "El batch size determina cuántos registros se insertan a la vez."
            echo ""
            echo "Recomendaciones:"
            echo "  - 100-500: Para sistemas con poca RAM"
            echo "  - 1000: Valor por defecto (recomendado)"
            echo "  - 2000-5000: Para sistemas potentes con mucha RAM"
            echo ""
            read -p "Ingresa el batch size (presiona Enter para usar 1000): " batch_size

            if [ -z "$batch_size" ]; then
                batch_size=1000
            fi

            echo ""
            echo "Ejecutando migración con batch size: $batch_size"
            echo ""

            docker-compose --profile migrate run --rm migration --batch-size "$batch_size"

            echo ""
            echo -e "${GREEN}✅ Migración completada con batch size $batch_size${NC}"
            ;;

        4)
            echo ""
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${CYAN}                🎯 OMITIR TABLAS ESPECÍFICAS                        ${NC}"
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo "Tablas disponibles para migrar:"
            echo "  - usuarios"
            echo "  - empresas"
            echo "  - solicitudes"
            echo "  - logs"
            echo "  - cosechas"
            echo "  - geolocalizaciones"
            echo "  - acl"
            echo "  - agendas"
            echo "  - pagadoras"
            echo "  - operaciones_internas_preocupantes"
            echo ""
            echo "Ingresa las tablas a OMITIR separadas por comas"
            echo "Ejemplo: logs,acl,agendas"
            echo ""
            read -p "Tablas a omitir (o Enter para migrar todas): " skip_tables

            if [ -z "$skip_tables" ]; then
                echo ""
                echo "No se omitirá ninguna tabla, migrando todas..."
                docker-compose --profile migrate run --rm migration
            else
                echo ""
                echo "Migrando todas las tablas EXCEPTO: $skip_tables"
                echo ""

                # Convertir comas a múltiples --skip-table
                skip_args=""
                IFS=',' read -ra TABLES <<< "$skip_tables"
                for table in "${TABLES[@]}"; do
                    table=$(echo "$table" | xargs) # trim whitespace
                    skip_args="$skip_args --skip-table $table"
                done

                docker-compose --profile migrate run --rm migration $skip_args
            fi

            echo ""
            echo -e "${GREEN}✅ Migración completada${NC}"
            ;;

        5)
            echo ""
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${CYAN}              📊 ESTADO DE LA BASE DE DATOS                         ${NC}"
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""

            echo "📊 Registros por tabla:"
            docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -c "
                SELECT
                    schemaname AS \"Schema\",
                    tablename AS \"Tabla\",
                    n_tup_ins AS \"Insertados\",
                    n_tup_upd AS \"Actualizados\",
                    n_tup_del AS \"Eliminados\",
                    n_live_tup AS \"Registros Vivos\",
                    pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS \"Tamaño\"
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                ORDER BY tablename;
            " 2>/dev/null || echo "No se pudieron obtener estadísticas"

            echo ""
            echo "💾 Tamaño total de la base de datos:"
            docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -c "
                SELECT pg_size_pretty(pg_database_size('pipeenlinea')) AS \"Tamaño Total\";
            " 2>/dev/null || echo "No se pudo obtener el tamaño"
            ;;

        6)
            echo ""
            echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${RED}              🔄 LIMPIAR BASE DE DATOS (PELIGROSO)                  ${NC}"
            echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo -e "${RED}⚠️  ADVERTENCIA CRÍTICA ⚠️${NC}"
            echo ""
            echo "Esto eliminará TODOS los datos de TODAS las tablas:"
            echo "  - solicitudes"
            echo "  - logs"
            echo "  - usuarios"
            echo "  - empresas"
            echo "  - cosechas"
            echo "  - geolocalizaciones"
            echo "  - acl"
            echo "  - agendas"
            echo "  - pagadoras"
            echo "  - operaciones_internas_preocupantes"
            echo ""
            echo -e "${RED}Esta acción NO se puede deshacer.${NC}"
            echo "Los archivos JSON originales permanecerán intactos en working/"
            echo ""
            read -p "¿Estás COMPLETAMENTE seguro? (escribe 'BORRAR TODO' para continuar): " confirm

            if [ "$confirm" = "BORRAR TODO" ]; then
                echo ""
                echo "🗑️  Eliminando todos los datos..."

                # Truncar todas las tablas
                docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea <<EOF
TRUNCATE TABLE
    operaciones_internas_preocupantes,
    pagadoras,
    agendas,
    acl,
    geolocalizaciones,
    cosechas,
    logs,
    solicitudes,
    empresas,
    usuarios
CASCADE;
EOF

                echo ""
                echo -e "${GREEN}✅ Base de datos limpiada${NC}"
                echo ""
                echo "Ahora puedes ejecutar una migración limpia"
            else
                echo "Limpieza cancelada"
            fi
            ;;

        0)
            echo ""
            echo "👋 Saliendo del sistema de migración..."
            echo ""
            exit 0
            ;;

        *)
            echo ""
            echo -e "${RED}❌ Opción inválida${NC}"
            echo ""
            ;;
    esac

    # ============================================================================
    # MENSAJE PARA VOLVER AL MENÚ
    # ============================================================================
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    read -p "Presiona ENTER para volver al menú principal (o Ctrl+C para salir)..."
    echo ""
done
