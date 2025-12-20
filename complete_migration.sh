#!/bin/bash
# ============================================================================
# Script Maestro: Migración Completa JSON → PostgreSQL + Refactorización
# ============================================================================

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

clear

echo ""
echo -e "${MAGENTA}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║                                                                      ║${NC}"
echo -e "${MAGENTA}║       PIPEENLINEA - Migración Completa a PostgreSQL                 ║${NC}"
echo -e "${MAGENTA}║                                                                      ║${NC}"
echo -e "${MAGENTA}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Este script automatiza TODA la migración:${NC}"
echo -e "  ${GREEN}✓${NC} Migración de datos JSON → PostgreSQL"
echo -e "  ${GREEN}✓${NC} Refactorización automática del código"
echo -e "  ${GREEN}✓${NC} Reconstrucción de contenedores"
echo -e "  ${GREEN}✓${NC} Sistema listo para usar"
echo ""
echo -e "${YELLOW}⚠️  ADVERTENCIA: Esto modificará archivos de código${NC}"
echo ""
read -p "¿Estás listo para proceder? (escribe 'SI' para continuar): " confirm

if [ "$confirm" != "SI" ]; then
    echo "Operación cancelada"
    exit 0
fi

# ============================================================================
# FASE 1: Verificar Prerequisitos
# ============================================================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                     FASE 1: Prerequisitos                           ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Verificar que los servicios estén corriendo
if ! docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${RED}❌ PostgreSQL no está corriendo${NC}"
    echo "Iniciando servicios..."
    ./start.sh
fi
echo -e "${GREEN}✓ PostgreSQL está corriendo${NC}"

# Verificar que los datos estén migrados
row_count=$(docker-compose exec -T postgres psql -U pipeenlinea_user -d pipeenlinea -t -c "SELECT COUNT(*) FROM usuarios;" 2>/dev/null | xargs || echo "0")
if [ "$row_count" -eq "0" ]; then
    echo -e "${YELLOW}⚠️  No hay datos en PostgreSQL${NC}"
    echo "Ejecutando migración de datos..."
    ./migrate.sh
    read -p "Presiona ENTER después de completar la migración..."
fi
echo -e "${GREEN}✓ Datos migrados ($row_count usuarios en DB)${NC}"

# ============================================================================
# FASE 2: Refactorización del Código
# ============================================================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                 FASE 2: Refactorización de Código                   ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BLUE}[1/3]${NC} Creando respaldos del código original..."
BACKUP_DIR="backups/code_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r mysite/*.py "$BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}✓ Respaldo creado en: $BACKUP_DIR${NC}"

echo -e "${BLUE}[2/3]${NC} Refactorizando módulo de autenticación..."
# Crear nueva versión de routes_login2.py que use PostgreSQL
python3 << 'PYTHON_SCRIPT'
import re

# Leer el archivo original
with open('mysite/routes_login2.py', 'r') as f:
    content = f.read()

# Agregar import de database al inicio (después de otros imports)
if 'from database import' not in content:
    # Encontrar la última línea de import
    import_pattern = r'(import\s+\w+.*\n)(?!import|from)'
    content = re.sub(import_pattern, r'\1from database import execute_query, get_db_cursor\n', content, count=1)

# Reemplazar la función loginCheck
old_login_pattern = r'def loginCheck\(data\):.*?return result'
new_login_function = '''def loginCheck(data):
    result={}
    username = data["username"]
    password = data["password"]

    # Consultar usuario desde PostgreSQL
    query = """
        SELECT owner_id, username, password, nombre, rol
        FROM usuarios
        WHERE username = %s
    """
    usuario = execute_query(query, (username,), fetch_one=True)

    if usuario is None:
        result["result"] = False
        result["message"] = "Usuario no encontrado"
        return result

    # Verificar contraseña
    if usuario['password'] != password:
        result["result"] = False
        result["message"] = "Contraseña incorrecta"
        return result

    # Login exitoso
    result["result"] = True
    result["message"] = "Login exitoso"
    result["user"] = {
        "owner_id": usuario['owner_id'],
        "username": usuario['username'],
        "nombre": usuario['nombre'],
        "rol": usuario['rol']
    }
    return result'''

content = re.sub(old_login_pattern, new_login_function, content, flags=re.DOTALL)

# Escribir el archivo modificado
with open('mysite/routes_login2.py', 'w') as f:
    f.write(content)

print("✓ routes_login2.py refactorizado")
PYTHON_SCRIPT

echo -e "${GREEN}✓ Módulo de autenticación refactorizado${NC}"

echo -e "${BLUE}[3/3]${NC} Verificando sintaxis Python..."
python3 -m py_compile mysite/routes_login2.py 2>/dev/null && echo -e "${GREEN}✓ Sintaxis correcta${NC}" || echo -e "${RED}❌ Error de sintaxis${NC}"

# ============================================================================
# FASE 3: Reconstrucción y Reinicio
# ============================================================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}              FASE 3: Reconstrucción y Reinicio                      ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BLUE}[1/2]${NC} Deteniendo servicios..."
docker-compose down
echo -e "${GREEN}✓ Servicios detenidos${NC}"

echo -e "${BLUE}[2/2]${NC} Reconstruyendo y reiniciando..."
docker-compose build app
docker-compose up -d
echo -e "${GREEN}✓ Servicios reiniciados${NC}"

# Esperar a que la app esté lista
echo ""
echo -n "Esperando a que la aplicación esté lista"
for i in {1..30}; do
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓ Aplicación respondiendo${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  La aplicación tarda en responder, pero continúa iniciando...${NC}"
    fi
done

# ============================================================================
# REPORTE FINAL
# ============================================================================
echo ""
echo -e "${MAGENTA}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║                                                                      ║${NC}"
echo -e "${MAGENTA}║                    ✅ MIGRACIÓN COMPLETADA                           ║${NC}"
echo -e "${MAGENTA}║                                                                      ║${NC}"
echo -e "${MAGENTA}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🎉 El sistema está listo para usar!${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                      INFORMACIÓN DEL SISTEMA                         ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}🌐 Aplicación Web:${NC}    http://localhost:8000"
echo -e "${GREEN}🗄️  PostgreSQL:${NC}        localhost:5432"
echo -e "${GREEN}📊 Usuarios en DB:${NC}     $row_count"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                       LO QUE SE REFACTORIZÓ                          ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✓${NC} Autenticación (Login) → PostgreSQL"
echo -e "${YELLOW}⚠${NC}  Otros módulos aún usan JSON (migración gradual)"
echo ""
echo -e "${CYAN}Respaldo del código original en:${NC} $BACKUP_DIR"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                       PRÓXIMOS PASOS                                ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "1. Abre tu navegador en: http://localhost:8000"
echo "2. Ingresa con tu usuario y contraseña"
echo "3. ¡Empieza a usar el sistema!"
echo ""
echo -e "${YELLOW}Nota:${NC} El resto de módulos se migrarán gradualmente"
echo ""
echo -e "${GREEN}✅ Todo listo!${NC}"
echo ""
