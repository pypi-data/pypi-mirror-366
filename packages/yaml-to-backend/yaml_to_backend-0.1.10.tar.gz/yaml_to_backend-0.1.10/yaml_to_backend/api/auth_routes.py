from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Any
import logging
from ..security.auth import AuthManager
# Los modelos se generan dinámicamente, no se importan directamente
# from ..db.models import Usuario

# Tipo para el usuario (se generará dinámicamente)
Usuario = Any
from ..db.connection import get_db_session, get_db_manager
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from ..config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, AUTH

logger = logging.getLogger(__name__)

security = HTTPBearer()

router = APIRouter(prefix="/api/auth", tags=["autenticación"])

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str  # Mantener username para compatibilidad con OAuth2
    password: str

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, session: AsyncSession = Depends(get_db_session)):
    """Endpoint de login que devuelve un token JWT"""
    auth_manager = AuthManager(
        secret_key=JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
        access_token_expire_minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    try:
        # El campo username del OAuth2 se mapea a la columna configurada
        user = await auth_manager.authenticate_user(login_data.username, login_data.password, session)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Obtener la columna de usuario desde la configuración
        user_column = AUTH['columna_usuario']
        user_value = getattr(user, user_column)
            
        # Crear token de acceso
        access_token_expires = timedelta(minutes=auth_manager.access_token_expire_minutes)
        access_token = auth_manager.create_access_token(
            data={"sub": user_value}, expires_delta=access_token_expires
        )
        
        logger.info(f"Login exitoso para usuario: {user_value}")
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        # Re-lanzar HTTPException sin modificar
        raise
    except Exception as e:
        logger.error(f"Error en login: {e}")
        import traceback
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        # Hacer rollback en caso de error
        try:
            await session.rollback()
        except Exception:
            # Ignorar errores de rollback para evitar problemas de event loop
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

async def get_current_user_with_session(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db_session)
):
    """Dependencia para obtener usuario actual con sesión de base de datos"""
    auth_manager = AuthManager(JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return await auth_manager.get_current_user(credentials, session)

@router.get("/me")
async def get_current_user_info(current_user: Usuario = Depends(get_current_user_with_session)):
    """Obtiene información del usuario actual"""
    # Obtener la columna de usuario desde la configuración
    user_column = AUTH['columna_usuario']
    user_value = getattr(current_user, user_column)
    
    return {
        "id": current_user.id,
        "username": user_value,  # Mantener 'username' en la respuesta para compatibilidad
        "rol": current_user.rol
    } 