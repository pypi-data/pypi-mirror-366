from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from ..db.models import Usuario

logger = logging.getLogger(__name__)

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
security = HTTPBearer()

class AuthManager:
    """Gestor de autenticación y autorización"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", access_token_expire_minutes: int = 30):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return pwd_context.verify(plain_password, hashed_password)
        
    def get_password_hash(self, password: str) -> str:
        """Genera el hash de una contraseña"""
        return pwd_context.hash(password)
        
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Crea un token JWT de acceso"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
        
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica y decodifica un token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
            
    async def authenticate_user(self, username: str, password: str, session) -> Optional[Usuario]:
        """Autentica un usuario con username y password"""
        try:
            from sqlalchemy import select
            from ..config import AUTH
            
            # Obtener la columna de usuario desde la configuración
            user_column = AUTH['columna_usuario']
            
            result = await session.execute(
                select(Usuario).where(getattr(Usuario, user_column) == username)
            )
            user = result.scalar_one_or_none()
            
            if user and self.verify_password(password, user.password):
                return user
        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            # Hacer rollback en caso de error
            try:
                await session.rollback()
            except Exception:
                # Ignorar errores de rollback para evitar problemas de event loop
                pass
            
        return None
        
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security), session = None) -> Usuario:
        """Obtiene el usuario actual desde el token JWT"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = self.verify_token(credentials.credentials)
            if payload is None:
                raise credentials_exception
                
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
                
        except JWTError:
            raise credentials_exception
            
        if session:
            from sqlalchemy import select
            from ..config import AUTH
            
            # Obtener la columna de usuario desde la configuración
            user_column = AUTH['columna_usuario']
            
            result = await session.execute(
                select(Usuario).where(getattr(Usuario, user_column) == username)
            )
            user = result.scalar_one_or_none()
        else:
            # Fallback para casos donde no hay sesión disponible
            user = None
            
        if user is None:
            raise credentials_exception
            
        return user
        
    def has_permission(self, user: Usuario, entity_permissions: Dict[str, Any], action: str) -> bool:
        """Verifica si un usuario tiene permisos para una acción específica"""
        user_role = user.rol
        
        # Verificar permisos por rol
        if user_role in entity_permissions:
            permissions = entity_permissions[user_role]
            
            # Si es una lista simple de permisos
            if isinstance(permissions, list):
                return action in permissions
                
            # Si es un diccionario con permisos especiales
            elif isinstance(permissions, dict):
                # Verificar permisos directos
                if action in permissions:
                    return True
                    
                # Verificar permisos 'yo'
                if 'yo' in permissions:
                    return True
                    
        return False
        
    def get_user_filter(self, user: Usuario, entity_permissions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Obtiene el filtro para permisos tipo 'yo'"""
        user_role = user.rol
        
        if user_role in entity_permissions:
            permissions = entity_permissions[user_role]
            
            if isinstance(permissions, dict) and 'yo' in permissions:
                yo_config = permissions['yo']
                
                # Si es el usuario mismo
                if 'campo_usuario' not in yo_config:
                    return {'id': user.id}
                    
                # Si es una entidad relacionada
                else:
                    campo_usuario = yo_config['campo_usuario']
                    return {campo_usuario: user.id}
                    
        return None 