import asyncio
import logging
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import *
from .core.entity_parser import EntityParser
from .core.model_generator import ModelGenerator
from .db.connection import DatabaseManager, set_db_manager
from .security.auth import AuthManager
from .api.crud_generator import CRUDGenerator
from .api.auth_routes import router as auth_router

# Configurar logging
if LOG:
    logging.basicConfig(
        level=logging.INFO if DEBUG else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)

class BackendGenerator:
    """Generador principal del backend"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Backend Generador",
            description="Backend generado automáticamente desde archivos YAML",
            version="1.0.0",
            debug=DEBUG
        )
        
        # Configurar CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Inicializar componentes
        self.entity_parser = EntityParser(ENTITIES_PATH)
        self.model_generator = ModelGenerator()
        self.db_manager = DatabaseManager(DATABASE_URL)
        self.auth_manager = AuthManager(
            secret_key=JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
            access_token_expire_minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        self.crud_generator = CRUDGenerator(self.auth_manager)
        
        # Modelos generados
        self.generated_models = {}
        self.pydantic_models = {}
        
    async def initialize(self):
        """Inicializa el backend completo"""
        try:
            logger.info("Iniciando generación del backend...")
            
            # 1. Cargar entidades desde YAML
            logger.info("Cargando entidades desde archivos YAML...")
            entities = self.entity_parser.load_entities()
            
            if not entities:
                logger.warning("No se encontraron entidades para cargar")
                return
                
            # 2. Generar modelos ORM y Pydantic
            logger.info("Generando modelos ORM y Pydantic...")
            models_result = self.model_generator.generate_all_models(entities)
            self.generated_models = models_result['orm_models']
            self.pydantic_models = models_result['pydantic_models']
            
            # 3. Inicializar base de datos
            logger.info("Inicializando base de datos...")
            all_models = list(self.generated_models.values())
            
            if INSTALL:
                logger.info("Modo instalación activado - reiniciando base de datos...")
                await self.db_manager.init_db(all_models)
                await self.db_manager.reset_db()
                await self._create_initial_users()
            else:
                await self.db_manager.init_db(all_models)
            
            # Establecer DatabaseManager global
            set_db_manager(self.db_manager)
            
            # 4. Generar endpoints CRUD
            logger.info("Generando endpoints CRUD...")
            for entity_name, entity_data in entities.items():
                if entity_name in self.generated_models and entity_name in self.pydantic_models:
                    model_class = self.generated_models[entity_name]
                    pydantic_models = self.pydantic_models[entity_name]
                    
                    router = self.crud_generator.generate_crud_router(
                        entity_name=entity_name,
                        entity_data=entity_data,
                        model_class=model_class,
                        pydantic_models=pydantic_models
                    )
                    
                    # Registrar router
                    self.app.include_router(router)
                    logger.info(f"Router generado para entidad: {entity_name}")
            
            # 5. Registrar rutas de autenticación
            self.app.include_router(auth_router)
            
            # 6. Endpoint de salud
            @self.app.get("/")
            async def health_check():
                return {
                    "status": "ok",
                    "message": "Backend funcionando correctamente"
                }
            
            logger.info("Backend generado exitosamente!")
            
        except Exception as e:
            logger.error(f"Error durante la inicialización: {e}")
            raise
    
    async def _create_initial_users(self):
        """Crea usuarios iniciales para modo instalación"""
        try:
            # Obtener el modelo Usuario desde los modelos generados
            from .config import AUTH, INITIAL_USERS
            from sqlalchemy import select
            
            # Obtener el modelo Usuario desde los modelos generados
            Usuario = self.generated_models.get('Usuario')
            if not Usuario:
                logger.warning("Modelo Usuario no encontrado, saltando creación de usuarios iniciales")
                return
            
            # Obtener la columna de usuario desde la configuración
            user_column = AUTH['columna_usuario']
            password_column = AUTH['columna_password']
            
            async with self.db_manager.get_session() as session:
                for user_data in INITIAL_USERS:
                    # Verificar si el usuario ya existe usando la columna configurada
                    result = await session.execute(
                        select(Usuario).where(getattr(Usuario, user_column) == user_data[user_column])
                    )
                    existing_user = result.scalar_one_or_none()
                    
                    if not existing_user:
                        # Crear hash de la contraseña
                        hashed_password = self.auth_manager.get_password_hash(user_data[password_column])
                        
                        # Crear usuario usando las columnas configuradas
                        user_kwargs = {
                            user_column: user_data[user_column],
                            password_column: hashed_password,
                            'rol': user_data['rol']
                        }
                        
                        # Agregar campos adicionales si existen
                        for key, value in user_data.items():
                            if key not in [user_column, password_column, 'rol']:
                                user_kwargs[key] = value
                        
                        new_user = Usuario(**user_kwargs)
                        session.add(new_user)
                        await session.commit()
                        logger.info(f"Usuario inicial creado: {user_data[user_column]}")
                    else:
                        logger.info(f"Usuario ya existe: {user_data[user_column]}")
                        
        except Exception as e:
            logger.error(f"Error creando usuarios iniciales: {e}")
            raise
    
    def run(self):
        """Ejecuta el servidor"""
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=PORT,
            log_level="info" if DEBUG else "warning"
        )

def create_backend():
    """Función factory para crear y configurar el backend"""
    return BackendGenerator()

def run_backend():
    """Función para ejecutar el backend completo"""
    async def main():
        backend = create_backend()
        await backend.initialize()
        return backend
    
    # Ejecutar la inicialización
    backend = asyncio.run(main())
    
    # Ejecutar el servidor
    backend.run() 