#!/usr/bin/env python3
"""
Bot de Trading - MODO REAL
==========================
Ejecuta el bot en modo real (con dinero real)
"""

import os
import sys

# Configurar modo real
os.environ['TRADING_MODE'] = 'real'

# Cambiar al directorio raíz del proyecto
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ejecutar bot principal
exec(open('start_bot.py').read())
