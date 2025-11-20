#!/usr/bin/env bash
# Script de build para Render

set -o errexit  # Salir si hay error

echo "🔧 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔄 Ejecutando migraciones de base de datos..."
alembic upgrade head || echo "⚠️ Error en migraciones, continuando..."

echo "🗄️ Inicializando base de datos..."
python init_db.py

echo "✅ Build completado"