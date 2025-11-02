#!/bin/bash

# Script para verificar qualidade do código
echo "🔍 Verificando qualidade do código..."

echo "📏 Executando Black (formatação)..."
black --check --diff src/ pipeline.py

echo "🔎 Executando Flake8 (linting)..."
flake8 src/ pipeline.py

echo "🏷️  Executando MyPy (type checking)..."
mypy src/ pipeline.py

echo "✅ Verificação de qualidade concluída!"