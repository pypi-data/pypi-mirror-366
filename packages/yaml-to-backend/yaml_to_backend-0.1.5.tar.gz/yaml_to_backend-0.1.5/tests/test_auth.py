import pytest
import pytest_asyncio
from datetime import datetime
from yaml_to_backend.security.auth import AuthManager
from yaml_to_backend.db.models import Usuario
from yaml_to_backend.db.connection import DatabaseManager
from yaml_to_backend.config import DATABASE_URL

@pytest.fixture
def auth_manager():
    """Fixture para el gestor de autenticación"""
    return AuthManager(
        secret_key="test_secret_key",
        algorithm="HS256",
        access_token_expire_minutes=30
    )

@pytest_asyncio.fixture
async def db_manager():
    """Fixture para el gestor de base de datos"""
    db_manager = DatabaseManager(DATABASE_URL)
    await db_manager.init_db()
    yield db_manager
    await db_manager.close_db()

@pytest_asyncio.fixture
async def test_user(db_manager):
    """Fixture para un usuario de prueba"""
    async with db_manager.session_maker() as session:
        # Crear usuario de prueba
        user = Usuario(
            username="testuser",
            password="hashed_password",
            rol="usuario",
            fecha_creacion=datetime.now(),
            deleted_at=None
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        yield user
        
        # Limpiar usuario de prueba
        await session.delete(user)
        await session.commit()

class TestAuthManager:
    """Pruebas para el gestor de autenticación"""
    
    def test_password_hashing(self, auth_manager):
        """Prueba el hash de contraseñas"""
        password = "test_password"
        hashed = auth_manager.get_password_hash(password)
        
        assert hashed != password
        assert auth_manager.verify_password(password, hashed)
        assert not auth_manager.verify_password("wrong_password", hashed)
    
    def test_token_creation_and_verification(self, auth_manager):
        """Prueba la creación y verificación de tokens JWT"""
        data = {"sub": "testuser", "rol": "usuario"}
        
        # Crear token
        token = auth_manager.create_access_token(data)
        assert token is not None
        
        # Verificar token
        payload = auth_manager.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["rol"] == "usuario"
    
    def test_invalid_token(self, auth_manager):
        """Prueba la verificación de tokens inválidos"""
        invalid_token = "invalid_token"
        payload = auth_manager.verify_token(invalid_token)
        assert payload is None
    
    def test_permission_checking(self, auth_manager):
        """Prueba la verificación de permisos"""
        # Crear usuario de prueba
        user = Usuario(username="testuser", rol="admin")
        
        # Permisos de prueba
        permissions = {
            "admin": ["r", "w", "d"],
            "usuario": ["r"]
        }
        
        # Verificar permisos de admin
        assert auth_manager.has_permission(user, permissions, "r")
        assert auth_manager.has_permission(user, permissions, "w")
        assert auth_manager.has_permission(user, permissions, "d")
        
        # Cambiar rol a usuario
        user.rol = "usuario"
        assert auth_manager.has_permission(user, permissions, "r")
        assert not auth_manager.has_permission(user, permissions, "w")
        assert not auth_manager.has_permission(user, permissions, "d")
    
    def test_yo_permission_filter(self, auth_manager):
        """Prueba los filtros de permisos tipo 'yo'"""
        user = Usuario(id=1, username="testuser", rol="usuario")
        
        # Permisos con configuración 'yo'
        permissions = {
            "usuario": {
                "yo": {
                    "campo_usuario": "usuario_id"
                }
            }
        }
        
        # Obtener filtro
        user_filter = auth_manager.get_user_filter(user, permissions)
        assert user_filter == {"usuario_id": 1}
        
        # Permisos 'yo' sin campo_usuario (usuario mismo)
        permissions_self = {
            "usuario": {
                "yo": {}
            }
        }
        
        user_filter_self = auth_manager.get_user_filter(user, permissions_self)
        assert user_filter_self == {"id": 1}
    
    @pytest.mark.asyncio
    async def test_authenticate_user(self, auth_manager, db_manager, test_user):
        """Prueba la autenticación de usuarios"""
        async with db_manager.session_maker() as session:
            # Crear un nuevo usuario para evitar conflictos de sesión
            new_user = Usuario(
                username="testuser_auth",
                password=auth_manager.get_password_hash("test_password"),
                rol="usuario"
            )
            session.add(new_user)
            await session.commit()
            
            # Probar autenticación exitosa
            user = await auth_manager.authenticate_user("testuser_auth", "test_password", session)
            assert user is not None
            assert user.username == "testuser_auth"
            
            # Probar autenticación fallida
            user_failed = await auth_manager.authenticate_user("testuser_auth", "wrong_password", session)
            assert user_failed is None
            
            # Probar usuario inexistente
            user_not_found = await auth_manager.authenticate_user("nonexistent", "test_password", session)
            assert user_not_found is None
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, auth_manager, db_manager, test_user):
        """Prueba la obtención del usuario actual desde token"""
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials
        
        async with db_manager.session_maker() as session:
            # Crear token válido
            token_data = {"sub": test_user.username}
            token = auth_manager.create_access_token(token_data)
            
            # Simular credenciales HTTP
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            
            # Obtener usuario actual
            current_user = await auth_manager.get_current_user(credentials, session)
            assert current_user is not None
            assert current_user.username == test_user.username
            
            # Probar token inválido
            invalid_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
            
            with pytest.raises(HTTPException):
                await auth_manager.get_current_user(invalid_credentials, session) 