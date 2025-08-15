#!/usr/bin/env python3
"""
Bot de Trading - MODO DEMO
==========================
Ejecuta el bot en modo demo (sin riesgo real)
"""

import os
import sys

# Configurar modo demo
os.environ['TRADING_MODE'] = 'demo'

# Cambiar al directorio raíz del proyecto
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ejecutar bot principal
exec(open('start_bot.py').read())
