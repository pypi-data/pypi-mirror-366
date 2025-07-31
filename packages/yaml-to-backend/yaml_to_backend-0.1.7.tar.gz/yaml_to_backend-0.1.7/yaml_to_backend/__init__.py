#!/usr/bin/env python3
"""
YAML-to-Backend - Generador de Backends a partir de YAML

Una librería para generar automáticamente backends RESTful completos
a partir de definiciones de entidades en archivos YAML.
"""

__version__ = "0.1.7"
__author__ = "Tecinter"
__email__ = "info@tecinter.com.ar"

# Importar solo la configuración por defecto
from .config import update_config

# API pública principal
__all__ = [
    "update_config",
    "get_run_backend"
]

# Función para importar run_backend cuando se necesite
def get_run_backend():
    """Importa y retorna la función run_backend"""
    from .app import run_backend
    return run_backend 