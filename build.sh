#!/usr/bin/env bash
# Script de build para Render

set -o errexit  # Salir si hay error

echo "🔧 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔄 Ejecutando migraciones de base de datos..."
# Solo ejecutar migraciones si DATABASE_URL está configurada
if [ -n "$DATABASE_URL" ]; then
    alembic upgrade head || echo "⚠️ Error en migraciones, continuando..."
else
    echo "⚠️ DATABASE_URL no configurada, saltando migraciones..."
fi

echo "✅ Build completado"