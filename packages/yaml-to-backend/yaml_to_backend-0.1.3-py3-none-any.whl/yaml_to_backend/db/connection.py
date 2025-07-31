from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlmodel import SQLModel
import logging
from typing import List, Type

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    """Clase base para todos los modelos SQLModel"""
    pass

class DatabaseManager:
    """Gestor de conexión a la base de datos usando SQLModel"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.session_maker = None
        self.is_initialized = False
        # Configuración más robusta para el pool de conexiones
        self.pool_pre_ping = True
        self.pool_recycle = 3600  # Reciclar conexiones cada hora
        self.pool_size = 10
        self.max_overflow = 20
        
    async def init_db(self, models: List[Type] = None):
        """Inicializa la conexión a la base de datos"""
        try:
            # Crear engine asíncrono con configuración robusta
            self.engine = create_async_engine(
                self.database_url,
                echo=False,  # Cambiar a True para debug
                future=True,
                pool_pre_ping=self.pool_pre_ping,
                pool_recycle=self.pool_recycle,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow
            )
            
            # Crear session maker
            self.session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Crear todas las tablas
            async with self.engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
            
            self.is_initialized = True
            logger.info("Base de datos inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise
    
    async def close_db(self):
        """Cierra la conexión a la base de datos"""
        if self.engine:
            await self.engine.dispose()
            self.is_initialized = False
            logger.info("Conexión a base de datos cerrada")
    
    async def reset_db(self):
        """Reinicia la base de datos (borra todas las tablas)"""
        try:
            async with self.engine.begin() as conn:
                # Eliminar todas las tablas
                await conn.run_sync(SQLModel.metadata.drop_all)
                # Crear todas las tablas nuevamente
                await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("Base de datos reiniciada correctamente")
        except Exception as e:
            logger.error(f"Error reiniciando base de datos: {e}")
            raise
    
    def get_session(self) -> AsyncSession:
        """Obtiene una sesión de base de datos"""
        if not self.session_maker:
            raise RuntimeError("Base de datos no inicializada")
        return self.session_maker()

    async def get_db_session(self):
        """Dependencia de FastAPI para obtener sesión de base de datos"""
        if not self.session_maker:
            raise RuntimeError("Base de datos no inicializada")
        
        session = self.session_maker()
        try:
            yield session
        finally:
            await session.close()

# Variable global para el DatabaseManager
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Obtiene la instancia global del DatabaseManager"""
    global _db_manager
    if _db_manager is None:
        raise RuntimeError("DatabaseManager no inicializado")
    return _db_manager

def set_db_manager(db_manager: DatabaseManager):
    """Establece la instancia global del DatabaseManager"""
    global _db_manager
    _db_manager = db_manager

async def get_db_session():
    """Dependencia de FastAPI para obtener sesión de base de datos"""
    db_manager = get_db_manager()
    session = db_manager.session_maker()
    try:
        yield session
    except Exception:
        try:
            await session.rollback()
        except Exception:
            # Ignorar errores de rollback para evitar problemas de event loop
            pass
        raise
    finally:
        try:
            await session.close()
        except Exception:
            # Ignorar errores al cerrar sesión para evitar problemas de event loop
            pass

def register_database(app, database_url: str, models: List[Type] = None):
    """Registra la base de datos con FastAPI usando SQLModel"""
    # SQLModel se integra automáticamente con FastAPI
    # No necesitamos configuración adicional aquí
    pass 