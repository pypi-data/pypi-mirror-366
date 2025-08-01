from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Dict, Any, List, Optional, Type
import logging
from datetime import datetime
from ..security.auth import AuthManager
# Los modelos se generan dinámicamente, no se importan directamente
# from ..db.models import Usuario

# Tipo para el usuario (se generará dinámicamente)
Usuario = Any
from ..db.connection import get_db_session
from .auth_routes import get_current_user_with_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel
import inflection

logger = logging.getLogger(__name__)

class CRUDGenerator:
    """Generador de endpoints CRUD para entidades"""
    
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.routers = {}
        
        # Plantillas de descripción para endpoints
        self.endpoint_descriptions = {
            "list": "Lista todos los {entity_plural} del sistema con paginación",
            "create": "Crea un nuevo {entity_singular}",
            "read": "Obtiene un {entity_singular} específico por ID",
            "update": "Actualiza un {entity_singular} existente",
            "delete": "Elimina un {entity_singular} (soft delete)",
            "yo": "Obtiene {entity_plural} del usuario autenticado"
        }
    
    def get_endpoint_description(self, entity_name: str, operation: str, entity_data: Dict[str, Any]) -> str:
        """Genera descripción de endpoint basada en YAML y plantillas"""
        
        entity_singular = entity_name.lower()
        entity_plural = inflection.pluralize(entity_singular)
        
        # Obtener descripción de la entidad
        entity_description = entity_data.get('descripcion', f"Gestión de {entity_plural}")
        
        # Aplicar plantilla según operación
        template = self.endpoint_descriptions.get(operation, f"Operación {operation} para {entity_singular}")
        description = template.format(
            entity_singular=entity_singular,
            entity_plural=entity_plural
        )
        
        return description
        
    def generate_crud_router(self, entity_name: str, model_class: Type[SQLModel], 
                           pydantic_models: Dict[str, Any], entity_data: Dict[str, Any]) -> APIRouter:
        """Genera un router CRUD completo para una entidad"""
        
        router = APIRouter(prefix=f"/api/{entity_name.lower()}", tags=[entity_name])
        
        # Obtener modelos Pydantic
        create_model = pydantic_models['create']
        update_model = pydantic_models['update']
        response_model = pydantic_models['response']
        
        # Obtener permisos de la entidad
        permissions = entity_data.get('permisos', {})
        
        # Endpoint GET / - Listar todos
        list_description = self.get_endpoint_description(entity_name, 'list', entity_data)
        @router.get("/", response_model=List[response_model], description=list_description)
        async def list_entities(
            current_user: Usuario = Depends(get_current_user_with_session),
            session: AsyncSession = Depends(get_db_session),
            skip: int = Query(0, ge=0),
            limit: int = Query(100, ge=1, le=1000)
        ):
            """Lista todas las entidades con paginación"""
            try:
                from ..config import AUTH
                
                # Verificar permisos de lectura
                if not self.auth_manager.has_permission(current_user, permissions, 'r'):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tienes permisos para leer esta entidad"
                    )
                
                # Construir query base
                query = select(model_class)
                
                # Aplicar filtro de borrado lógico
                delete_column = AUTH['columna_borrado']
                delete_type = AUTH['borrado_logico']
                
                if hasattr(model_class, delete_column):
                    if delete_type == 'boolean':
                        # Para boolean, mostrar solo los que son True (no eliminados)
                        query = query.where(getattr(model_class, delete_column) == True)
                    else:
                        # Para timestamp/datetime, mostrar solo los que son None (no eliminados)
                        query = query.where(getattr(model_class, delete_column) == None)
                
                # Aplicar filtros según permisos
                user_filter = self.auth_manager.get_user_filter(current_user, permissions)
                if user_filter:
                    for key, value in user_filter.items():
                        query = query.where(getattr(model_class, key) == value)
                
                # Aplicar paginación
                query = query.offset(skip).limit(limit)
                
                # Ejecutar query
                result = await session.execute(query)
                entities = result.scalars().all()
                
                return entities
                
            except Exception as e:
                logger.error(f"Error listando {entity_name}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error interno del servidor"
                )
        
        # Endpoint POST / - Crear
        create_description = self.get_endpoint_description(entity_name, 'create', entity_data)
        @router.post("/", response_model=response_model, description=create_description)
        async def create_entity(
            entity_data: create_model,
            current_user: Usuario = Depends(get_current_user_with_session),
            session: AsyncSession = Depends(get_db_session)
        ):
            """Crea una nueva entidad"""
            try:
                # Verificar permisos de escritura
                if not self.auth_manager.has_permission(current_user, permissions, 'w'):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tienes permisos para crear esta entidad"
                    )
                
                # Crear la entidad
                entity = model_class(**entity_data.dict())
                session.add(entity)
                await session.commit()
                await session.refresh(entity)
                
                return entity
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error creando {entity_name}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error interno del servidor"
                )
        
        # Endpoint GET /yo - Obtener entidades del usuario actual (DEBE IR ANTES DE /{entity_id})
        if any('yo' in perm for perm in permissions.values()):
            yo_description = self.get_endpoint_description(entity_name, 'yo', entity_data)
            @router.get("/yo", response_model=List[response_model], description=yo_description)
            async def get_my_entities(
                current_user: Usuario = Depends(get_current_user_with_session),
                session: AsyncSession = Depends(get_db_session),
                skip: int = Query(0, ge=0),
                limit: int = Query(100, ge=1, le=1000)
            ):
                """Obtiene las entidades del usuario actual"""
                try:
                    from ..config import AUTH
                    
                    # Verificar permisos 'yo'
                    if not self.auth_manager.has_permission(current_user, permissions, 'yo'):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos para acceder a tus entidades"
                        )
                    
                    # Aplicar filtro de usuario
                    user_filter = self.auth_manager.get_user_filter(current_user, permissions)
                    if not user_filter:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Configuración de permisos 'yo' inválida"
                        )
                    
                    # Construir query con filtros
                    query = select(model_class)
                    
                    # Aplicar filtro de borrado lógico
                    delete_column = AUTH['columna_borrado']
                    delete_type = AUTH['borrado_logico']
                    
                    if hasattr(model_class, delete_column):
                        if delete_type == 'boolean':
                            # Para boolean, mostrar solo los que son True (no eliminados)
                            query = query.where(getattr(model_class, delete_column) == True)
                        else:
                            # Para timestamp/datetime, mostrar solo los que son None (no eliminados)
                            query = query.where(getattr(model_class, delete_column) == None)
                    
                    # Aplicar filtros de usuario
                    for key, value in user_filter.items():
                        query = query.where(getattr(model_class, key) == value)
                    
                    # Aplicar paginación
                    query = query.offset(skip).limit(limit)
                    
                    # Ejecutar query
                    result = await session.execute(query)
                    entities = result.scalars().all()
                    
                    return entities
                    
                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"Error obteniendo entidades 'yo' de {entity_name}: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error interno del servidor"
                    )
        
        # Endpoint GET /{id} - Obtener por ID
        read_description = self.get_endpoint_description(entity_name, 'read', entity_data)
        @router.get("/{entity_id}", response_model=response_model, description=read_description)
        async def get_entity(
            entity_id: int,
            current_user: Usuario = Depends(get_current_user_with_session),
            session: AsyncSession = Depends(get_db_session)
        ):
            """Obtiene una entidad por ID"""
            try:
                from ..config import AUTH
                
                # Verificar permisos de lectura
                if not self.auth_manager.has_permission(current_user, permissions, 'r'):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tienes permisos para leer esta entidad"
                    )
                
                # Buscar la entidad
                query = select(model_class).where(model_class.id == entity_id)
                
                # Aplicar filtro de borrado lógico
                delete_column = AUTH['columna_borrado']
                delete_type = AUTH['borrado_logico']
                
                if hasattr(model_class, delete_column):
                    if delete_type == 'boolean':
                        # Para boolean, mostrar solo los que son True (no eliminados)
                        query = query.where(getattr(model_class, delete_column) == True)
                    else:
                        # Para timestamp/datetime, mostrar solo los que son None (no eliminados)
                        query = query.where(getattr(model_class, delete_column) == None)
                
                result = await session.execute(query)
                entity = result.scalar_one_or_none()
                
                if not entity:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"{entity_name} no encontrada"
                    )
                
                # Verificar permisos 'yo' si aplica
                user_filter = self.auth_manager.get_user_filter(current_user, permissions)
                if user_filter:
                    # Verificar que la entidad pertenece al usuario
                    filter_values = {k: getattr(entity, k) for k in user_filter.keys()}
                    if filter_values != user_filter:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos para acceder a esta entidad"
                        )
                
                return entity
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error obteniendo {entity_name}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error interno del servidor"
                )
        
        # Endpoint PUT /{id} - Actualizar
        update_description = self.get_endpoint_description(entity_name, 'update', entity_data)
        @router.put("/{entity_id}", response_model=response_model, description=update_description)
        async def update_entity(
            entity_id: int,
            entity_data: update_model,
            current_user: Usuario = Depends(get_current_user_with_session),
            session: AsyncSession = Depends(get_db_session)
        ):
            """Actualiza una entidad existente"""
            try:
                # Verificar permisos de escritura
                if not self.auth_manager.has_permission(current_user, permissions, 'w'):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tienes permisos para actualizar esta entidad"
                    )
                
                # Buscar la entidad
                query = select(model_class).where(model_class.id == entity_id)
                result = await session.execute(query)
                entity = result.scalar_one_or_none()
                
                if not entity:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"{entity_name} no encontrada"
                    )
                
                # Verificar permisos 'yo' si aplica
                user_filter = self.auth_manager.get_user_filter(current_user, permissions)
                if user_filter:
                    filter_values = {k: getattr(entity, k) for k in user_filter.keys()}
                    if filter_values != user_filter:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos para actualizar esta entidad"
                        )
                
                # Actualizar la entidad
                update_data = entity_data.dict(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(entity, key, value)
                
                session.add(entity)
                await session.commit()
                await session.refresh(entity)
                
                return entity
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error actualizando {entity_name}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error interno del servidor"
                )
        
        # Endpoint DELETE /{id} - Eliminar
        delete_description = self.get_endpoint_description(entity_name, 'delete', entity_data)
        @router.delete("/{entity_id}", description=delete_description)
        async def delete_entity(
            entity_id: int,
            current_user: Usuario = Depends(get_current_user_with_session),
            session: AsyncSession = Depends(get_db_session)
        ):
            """Elimina una entidad por ID (soft delete)"""
            try:
                from ..config import AUTH
                
                # Verificar permisos de eliminación
                if not self.auth_manager.has_permission(current_user, permissions, 'd'):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tienes permisos para eliminar esta entidad"
                    )
                
                # Buscar la entidad
                query = select(model_class).where(model_class.id == entity_id)
                result = await session.execute(query)
                entity = result.scalar_one_or_none()
                
                if not entity:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"{entity_name} no encontrada"
                    )
                
                # Verificar permisos 'yo' si aplica
                user_filter = self.auth_manager.get_user_filter(current_user, permissions)
                if user_filter:
                    filter_values = {k: getattr(entity, k) for k in user_filter.keys()}
                    if filter_values != user_filter:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos para eliminar esta entidad"
                        )
                
                # Eliminar la entidad (borrado lógico)
                delete_column = AUTH['columna_borrado']
                delete_type = AUTH['borrado_logico']
                
                if hasattr(entity, delete_column):
                    if delete_type == 'timestamp' or delete_type == 'datetime':
                        from datetime import datetime
                        setattr(entity, delete_column, datetime.utcnow())
                    elif delete_type == 'boolean':
                        setattr(entity, delete_column, False)
                    else:
                        # Por defecto, usar timestamp
                        from datetime import datetime
                        setattr(entity, delete_column, datetime.utcnow())
                    
                    session.add(entity)
                else:
                    await session.delete(entity)
                
                await session.commit()
                
                return {"message": f"{entity_name} eliminada correctamente"}
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error eliminando {entity_name}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error interno del servidor"
                )
        

        
        self.routers[entity_name] = router
        return router
    
    def get_all_routers(self) -> Dict[str, APIRouter]:
        """Obtiene todos los routers generados"""
        return self.routers 