#!/bin/bash
# ============================================================================
# Pre-Migration Validation Script
# Verifica que todo esté listo antes de migrar
# ============================================================================

set -e

echo "=========================================="
echo "  PRE-MIGRATION VALIDATION CHECK"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para verificar archivos
check_file() {
    file=$1
    required=$2

    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        if [ "$size" -gt 0 ]; then
            echo -e "${GREEN}✅ $file ($(numfmt --to=iec-i --suffix=B $size 2>/dev/null || echo $size bytes))${NC}"
        else
            if [ "$required" = "true" ]; then
                echo -e "${RED}❌ $file existe pero está vacío${NC}"
                ERRORS=$((ERRORS+1))
            else
                echo -e "${YELLOW}⚠️  $file existe pero está vacío (opcional)${NC}"
                WARNINGS=$((WARNINGS+1))
            fi
        fi
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}❌ $file NO ENCONTRADO${NC}"
            ERRORS=$((ERRORS+1))
        else
            echo -e "${YELLOW}⚠️  $file no encontrado (opcional)${NC}"
            WARNINGS=$((WARNINGS+1))
        fi
    fi
}

# 1. Verificar secret.key
echo "1. Verificando clave de encriptación..."
check_file "secret.key" "true"
echo ""

# 2. Verificar archivos JSON principales
echo "2. Verificando archivos JSON encriptados..."
check_file "working/users.json" "true"
check_file "working/empresas.json" "true"
check_file "working/solicitudes.json" "true"
check_file "working/logs.json" "true"
check_file "working/cosechas.json" "false"
check_file "working/geolocations.json" "false"
check_file "working/acl.json" "false"
check_file "working/agendas.json" "false"
check_file "working/pagadoras.json" "false"
check_file "working/roips.json" "false"
echo ""

# 3. Verificar .env
echo "3. Verificando configuración..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env existe${NC}"

    # Verificar variables críticas
    if grep -q "DB_PASSWORD=changeme123" .env 2>/dev/null; then
        echo -e "${YELLOW}⚠️  DB_PASSWORD usa valor por defecto - CAMBIAR antes de producción${NC}"
        WARNINGS=$((WARNINGS+1))
    fi

    if grep -q "SECRET_KEY=" .env 2>/dev/null; then
        echo -e "${GREEN}✅ SECRET_KEY configurado${NC}"
    else
        echo -e "${RED}❌ SECRET_KEY no encontrado en .env${NC}"
        ERRORS=$((ERRORS+1))
    fi
else
    echo -e "${YELLOW}⚠️  .env no encontrado - usa .env.example como template${NC}"
    WARNINGS=$((WARNINGS+1))
fi
echo ""

# 4. Verificar Docker
echo "4. Verificando Docker..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker instalado: $(docker --version)${NC}"

    if command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}✅ Docker Compose instalado: $(docker-compose --version)${NC}"
    else
        echo -e "${RED}❌ Docker Compose NO instalado${NC}"
        ERRORS=$((ERRORS+1))
    fi
else
    echo -e "${RED}❌ Docker NO instalado${NC}"
    ERRORS=$((ERRORS+1))
fi
echo ""

# 5. Verificar espacio en disco
echo "5. Verificando espacio en disco..."
available=$(df -h . | awk 'NR==2 {print $4}')
echo -e "${GREEN}✅ Espacio disponible: $available${NC}"
echo ""

# 6. Verificar estructura de directorios
echo "6. Verificando directorios necesarios..."
for dir in database migration_logs logs; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅ $dir/${NC}"
    else
        echo -e "${YELLOW}⚠️  $dir/ no existe (se creará automáticamente)${NC}"
        WARNINGS=$((WARNINGS+1))
    fi
done
echo ""

# 7. Test de desencriptación (opcional)
echo "7. Test de desencriptación (opcional)..."
if [ -f "secret.key" ] && [ -f "working/users.json" ]; then
    python3 -c "
from cryptography.fernet import Fernet
import json

try:
    with open('secret.key', 'rb') as f:
        key = f.read()
    fernet = Fernet(key)

    with open('working/users.json', 'rb') as f:
        encrypted = f.read()

    decrypted = fernet.decrypt(encrypted)
    data = json.loads(decrypted.decode('utf-8'))

    print('✅ Desencriptación exitosa - {} registros en users.json'.format(len(data)))
except Exception as e:
    print('❌ Error de desencriptación:', e)
    exit(1)
" 2>&1

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Test de desencriptación exitoso${NC}"
    else
        echo -e "${RED}❌ Error en desencriptación - verifica secret.key${NC}"
        ERRORS=$((ERRORS+1))
    fi
else
    echo -e "${YELLOW}⚠️  No se puede ejecutar test (faltan archivos)${NC}"
fi
echo ""

# Resumen
echo "=========================================="
echo "  RESUMEN"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ TODO LISTO PARA MIGRACIÓN${NC}"
    echo ""
    echo "Siguiente paso:"
    echo "  ./start.sh"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS advertencia(s) - revisa arriba${NC}"
    echo ""
    echo "Puedes continuar pero revisa las advertencias:"
    echo "  ./start.sh"
    exit 0
else
    echo -e "${RED}❌ $ERRORS error(es) crítico(s)${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $WARNINGS advertencia(s)${NC}"
    fi
    echo ""
    echo "Corrige los errores antes de continuar"
    exit 1
fi
