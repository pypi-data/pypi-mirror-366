#!/usr/bin/env python3
"""
CLI para YAML-to-Backend - Interfaz de línea de comandos
"""

import argparse
import sys
import os
from pathlib import Path

from .app import run_backend
from .config import update_config


def main():
    """Función principal del CLI"""
    parser = argparse.ArgumentParser(
        description="YAML-to-Backend - Generador de Backends a partir de YAML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  yaml-to-backend                                    # Ejecutar con configuración por defecto
  yaml-to-backend --port 8001                       # Cambiar puerto
  yaml-to-backend --db-host localhost --db-name test # Configurar base de datos
  yaml-to-backend --entities ./mis_entidades/       # Especificar ruta de entidades
        """
    )
    
    # Argumentos de configuración del servidor
    parser.add_argument(
        "--port", 
        type=int, 
        help="Puerto del servidor (por defecto: 8000)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="Host del servidor (por defecto: 0.0.0.0)"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Modo debug"
    )
    
    # Argumentos de base de datos
    parser.add_argument(
        "--db-host", 
        help="Host de la base de datos"
    )
    parser.add_argument(
        "--db-port", 
        type=int,
        help="Puerto de la base de datos"
    )
    parser.add_argument(
        "--db-user", 
        help="Usuario de la base de datos"
    )
    parser.add_argument(
        "--db-password", 
        help="Contraseña de la base de datos"
    )
    parser.add_argument(
        "--db-name", 
        help="Nombre de la base de datos"
    )
    
    # Argumentos de entidades
    parser.add_argument(
        "--entities", 
        help="Ruta al directorio de entidades YAML"
    )
    
    # Argumentos de instalación
    parser.add_argument(
        "--install", 
        action="store_true",
        help="Instalar/reinicializar la base de datos"
    )
    parser.add_argument(
        "--no-install", 
        action="store_true",
        help="No instalar/reinicializar la base de datos"
    )
    
    # Argumentos de logging
    parser.add_argument(
        "--log", 
        action="store_true",
        help="Habilitar logging"
    )
    parser.add_argument(
        "--no-log", 
        action="store_true",
        help="Deshabilitar logging"
    )
    
    args = parser.parse_args()
    
    # Preparar configuración
    config_updates = {}
    
    if args.port is not None:
        config_updates['PORT'] = args.port
    
    if args.debug:
        config_updates['DEBUG'] = True
    
    if args.db_host:
        config_updates['DB_HOST'] = args.db_host
    
    if args.db_port:
        config_updates['DB_PORT'] = args.db_port
    
    if args.db_user:
        config_updates['DB_USER'] = args.db_user
    
    if args.db_password:
        config_updates['DB_PASSWORD'] = args.db_password
    
    if args.db_name:
        config_updates['DB_NAME'] = args.db_name
    
    if args.entities:
        entities_path = Path(args.entities)
        if not entities_path.exists():
            print(f"❌ Error: El directorio de entidades '{args.entities}' no existe")
            sys.exit(1)
        config_updates['ENTITIES_PATH'] = str(entities_path.absolute())
    
    if args.install:
        config_updates['INSTALL'] = True
    
    if args.no_install:
        config_updates['INSTALL'] = False
    
    if args.log:
        config_updates['LOG'] = True
    
    if args.no_log:
        config_updates['LOG'] = False
    
    # Aplicar configuración si hay cambios
    if config_updates:
        update_config(**config_updates)
    
    try:
        print("🚀 Iniciando YAML-to-Backend...")
        run_backend()
    except KeyboardInterrupt:
        print("\n👋 YAML-to-Backend detenido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error al ejecutar YAML-to-Backend: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 