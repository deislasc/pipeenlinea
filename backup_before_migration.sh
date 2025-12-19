#!/bin/bash
# ============================================================================
# Backup Script - Ejecutar ANTES de la migración
# Crea un backup completo de todos los archivos JSON y la clave
# ============================================================================

set -e

BACKUP_DIR="backup_pre_migration_$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "  BACKUP PRE-MIGRACIÓN"
echo "=========================================="
echo ""

# Crear directorio de backup
mkdir -p "$BACKUP_DIR"

echo "📦 Creando backup en: $BACKUP_DIR"
echo ""

# Backup de working directory
if [ -d "mysite/working" ]; then
    echo "1. Copiando archivos JSON..."
    cp -r mysite/working "$BACKUP_DIR/"
    echo "   ✅ mysite/working/ → $BACKUP_DIR/working/"
fi

# Backup de secret.key
if [ -f "secret.key" ]; then
    echo "2. Copiando secret.key..."
    cp secret.key "$BACKUP_DIR/"
    echo "   ✅ secret.key → $BACKUP_DIR/secret.key"
fi

# Backup de .env
if [ -f ".env" ]; then
    echo "3. Copiando .env..."
    cp .env "$BACKUP_DIR/"
    echo "   ✅ .env → $BACKUP_DIR/.env"
fi

# Crear archivo de metadata
cat > "$BACKUP_DIR/BACKUP_INFO.txt" << EOF
========================================
BACKUP METADATA
========================================

Fecha: $(date)
Host: $(hostname)
Usuario: $(whoami)
Directorio: $(pwd)

ARCHIVOS INCLUIDOS:
$(ls -lh $BACKUP_DIR)

CONTEO DE REGISTROS (aproximado):
$(du -sh $BACKUP_DIR/working/*.json 2>/dev/null || echo "N/A")

Este backup se creó ANTES de la migración a PostgreSQL.
Para restaurar, copia los archivos de vuelta a sus ubicaciones originales.

IMPORTANTE:
- NO elimines este backup hasta confirmar que la migración fue exitosa
- Verifica que PostgreSQL tenga todos los datos correctamente
- Mantén este backup en un lugar seguro fuera del servidor
========================================
EOF

# Comprimir backup
echo ""
echo "4. Comprimiendo backup..."
tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"

if [ -f "${BACKUP_DIR}.tar.gz" ]; then
    backup_size=$(ls -lh "${BACKUP_DIR}.tar.gz" | awk '{print $5}')
    echo "   ✅ Backup comprimido: ${BACKUP_DIR}.tar.gz ($backup_size)"

    # Eliminar directorio sin comprimir
    rm -rf "$BACKUP_DIR"
fi

echo ""
echo "=========================================="
echo "✅ BACKUP COMPLETADO"
echo "=========================================="
echo ""
echo "Archivo: ${BACKUP_DIR}.tar.gz"
echo "Tamaño: $backup_size"
echo ""
echo "Para restaurar:"
echo "  tar -xzf ${BACKUP_DIR}.tar.gz"
echo "  cp -r ${BACKUP_DIR}/working/* mysite/working/"
echo "  cp ${BACKUP_DIR}/secret.key ."
echo ""
echo "⚠️  IMPORTANTE: Guarda este archivo en un lugar seguro!"
echo ""
