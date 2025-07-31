#!/usr/bin/env python3
"""
Pruebas de integración para endpoints del backend generador
Estas pruebas requieren que el backend esté en funcionamiento
"""

import pytest
import asyncio
import httpx
import time
import json
from typing import Dict, Any, Optional

class TestBackendIntegration:
    """Pruebas de integración para el backend completo"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.auth_token: Optional[str] = None
        self.test_entities: Dict[str, Any] = {}
    
    def setup_method(self):
        """Configuración antes de cada prueba"""
        self.auth_token = None
        self.test_entities = {}
    
    def get_headers(self) -> Dict[str, str]:
        """Obtiene headers con autenticación si está disponible"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def test_backend_is_running(self):
        """Prueba que el backend esté en funcionamiento"""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/docs")
                assert response.status_code == 200, "Backend no está respondiendo"
                print("✅ Backend está en funcionamiento")
        except Exception as e:
            pytest.fail(f"Backend no está accesible: {e}")
    
    def test_health_check(self):
        """Prueba endpoint de health check"""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/")
                assert response.status_code in [200, 404], "Health check falló"
                print("✅ Health check funcionando")
        except Exception as e:
            pytest.fail(f"Health check falló: {e}")
    
    def test_auth_login_success(self):
        """Prueba login exitoso con credenciales por defecto"""
        try:
            with httpx.Client(timeout=10.0) as client:
                login_data = {
                    "username": "admin",
                    "password": "admin123"
                }
                
                response = client.post(
                    f"{self.base_url}/api/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                )
                
                assert response.status_code == 200, f"Login falló: {response.status_code}"
                
                data = response.json()
                assert "access_token" in data, "Token no encontrado en respuesta"
                assert data["token_type"] == "bearer", "Tipo de token incorrecto"
                
                self.auth_token = data["access_token"]
                print("✅ Login exitoso")
                
        except Exception as e:
            pytest.fail(f"Login falló: {e}")
    
    def test_auth_login_invalid_credentials(self):
        """Prueba login con credenciales inválidas"""
        try:
            with httpx.Client(timeout=10.0) as client:
                login_data = {
                    "username": "invalid",
                    "password": "invalid"
                }
                
                response = client.post(
                    f"{self.base_url}/api/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                )
                
                assert response.status_code == 401, "Login con credenciales inválidas debería fallar"
                print("✅ Login con credenciales inválidas rechazado correctamente")
                
        except Exception as e:
            pytest.fail(f"Prueba de login inválido falló: {e}")
    
    def test_auth_me_endpoint(self):
        """Prueba endpoint /api/auth/me"""
        # Primero hacer login
        self.test_auth_login_success()
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{self.base_url}/api/auth/me",
                    headers=self.get_headers()
                )
                
                assert response.status_code == 200, f"Endpoint /me falló: {response.status_code}"
                
                data = response.json()
                assert "id" in data, "ID de usuario no encontrado"
                assert "username" in data, "Username no encontrado"
                assert "rol" in data, "Rol no encontrado"
                assert data["username"] == "admin", "Username incorrecto"
                assert data["rol"] == "admin", "Rol incorrecto"
                
                print("✅ Endpoint /me funcionando correctamente")
                
        except Exception as e:
            pytest.fail(f"Endpoint /me falló: {e}")
    
    def test_auth_me_unauthorized(self):
        """Prueba endpoint /api/auth/me sin autenticación"""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.base_url}/api/auth/me")
                
                assert response.status_code in [401, 403], "Endpoint /me debería requerir autenticación"
                print("✅ Endpoint /me rechaza acceso no autenticado correctamente")
                
        except Exception as e:
            pytest.fail(f"Prueba de autorización falló: {e}")
    
    def test_usuario_endpoints(self):
        """Prueba endpoints CRUD para entidad Usuario"""
        # Primero hacer login
        self.test_auth_login_success()
        
        try:
            with httpx.Client(timeout=10.0) as client:
                headers = self.get_headers()
                
                # 1. Listar usuarios
                response = client.get(f"{self.base_url}/api/usuario/", headers=headers)
                assert response.status_code == 200, f"Listar usuarios falló: {response.status_code}"
                usuarios = response.json()
                assert isinstance(usuarios, list), "Respuesta debería ser una lista"
                print("✅ Listar usuarios funcionando")
                
                # 2. Crear nuevo usuario
                nuevo_usuario = {
                    "username": f"test_user_{int(time.time())}",
                    "password": "test123",
                    "rol": "usuario"
                }
                
                response = client.post(
                    f"{self.base_url}/api/usuario/",
                    json=nuevo_usuario,
                    headers=headers
                )
                
                assert response.status_code == 200, f"Crear usuario falló: {response.status_code}"
                usuario_creado = response.json()
                assert "id" in usuario_creado, "ID no encontrado en respuesta"
                assert usuario_creado["username"] == nuevo_usuario["username"], "Username incorrecto"
                
                usuario_id = usuario_creado["id"]
                self.test_entities["usuario_id"] = usuario_id
                print("✅ Crear usuario funcionando")
                
                # 3. Obtener usuario por ID
                response = client.get(f"{self.base_url}/api/usuario/{usuario_id}", headers=headers)
                assert response.status_code == 200, f"Obtener usuario por ID falló: {response.status_code}"
                usuario_obtenido = response.json()
                assert usuario_obtenido["id"] == usuario_id, "ID incorrecto"
                print("✅ Obtener usuario por ID funcionando")
                
                # 4. Actualizar usuario
                datos_actualizacion = {
                    "rol": "editor"
                }
                
                response = client.put(
                    f"{self.base_url}/api/usuario/{usuario_id}",
                    json=datos_actualizacion,
                    headers=headers
                )
                
                assert response.status_code == 200, f"Actualizar usuario falló: {response.status_code}"
                usuario_actualizado = response.json()
                assert usuario_actualizado["rol"] == "editor", "Rol no se actualizó"
                print("✅ Actualizar usuario funcionando")
                
                # 5. Eliminar usuario
                response = client.delete(f"{self.base_url}/api/usuario/{usuario_id}", headers=headers)
                assert response.status_code == 200, f"Eliminar usuario falló: {response.status_code}"
                print("✅ Eliminar usuario funcionando")
                
        except Exception as e:
            pytest.fail(f"Pruebas de endpoints Usuario fallaron: {e}")
    
    def test_tarea_endpoints(self):
        """Prueba endpoints CRUD para entidad Tarea"""
        # Primero hacer login
        self.test_auth_login_success()
        
        try:
            with httpx.Client(timeout=10.0) as client:
                headers = self.get_headers()
                
                # 1. Listar tareas
                response = client.get(f"{self.base_url}/api/tarea/", headers=headers)
                assert response.status_code == 200, f"Listar tareas falló: {response.status_code}"
                tareas = response.json()
                assert isinstance(tareas, list), "Respuesta debería ser una lista"
                print("✅ Listar tareas funcionando")
                
                # 2. Crear nueva tarea
                nueva_tarea = {
                    "titulo": f"Tarea de prueba {int(time.time())}",
                    "descripcion": "Descripción de prueba",
                    "usuario_id": 1,  # Asumiendo que existe un usuario con ID 1
                    "completada": False
                }
                
                response = client.post(
                    f"{self.base_url}/api/tarea/",
                    json=nueva_tarea,
                    headers=headers
                )
                
                assert response.status_code == 200, f"Crear tarea falló: {response.status_code}"
                tarea_creada = response.json()
                assert "id" in tarea_creada, "ID no encontrado en respuesta"
                assert tarea_creada["titulo"] == nueva_tarea["titulo"], "Título incorrecto"
                
                tarea_id = tarea_creada["id"]
                self.test_entities["tarea_id"] = tarea_id
                print("✅ Crear tarea funcionando")
                
                # 3. Obtener tarea por ID
                response = client.get(f"{self.base_url}/api/tarea/{tarea_id}", headers=headers)
                assert response.status_code == 200, f"Obtener tarea por ID falló: {response.status_code}"
                tarea_obtenida = response.json()
                assert tarea_obtenida["id"] == tarea_id, "ID incorrecto"
                print("✅ Obtener tarea por ID funcionando")
                
                # 4. Actualizar tarea
                datos_actualizacion = {
                    "completada": True
                }
                
                response = client.put(
                    f"{self.base_url}/api/tarea/{tarea_id}",
                    json=datos_actualizacion,
                    headers=headers
                )
                
                assert response.status_code == 200, f"Actualizar tarea falló: {response.status_code}"
                tarea_actualizada = response.json()
                assert tarea_actualizada["completada"] == True, "Estado no se actualizó"
                print("✅ Actualizar tarea funcionando")
                
                # 5. Eliminar tarea
                response = client.delete(f"{self.base_url}/api/tarea/{tarea_id}", headers=headers)
                assert response.status_code == 200, f"Eliminar tarea falló: {response.status_code}"
                print("✅ Eliminar tarea funcionando")
                
        except Exception as e:
            pytest.fail(f"Pruebas de endpoints Tarea fallaron: {e}")
    
    def test_yo_endpoints(self):
        """Prueba endpoints tipo 'yo' para datos del usuario autenticado"""
        # Primero hacer login
        self.test_auth_login_success()
        
        try:
            with httpx.Client(timeout=10.0) as client:
                headers = self.get_headers()
                
                # Probar endpoint /yo para tareas
                response = client.get(f"{self.base_url}/api/tarea/yo", headers=headers)
                assert response.status_code == 200, f"Endpoint /yo para tareas falló: {response.status_code}"
                tareas_yo = response.json()
                assert isinstance(tareas_yo, list), "Respuesta debería ser una lista"
                print("✅ Endpoint /yo para tareas funcionando")
                
                # Probar endpoint /yo para usuarios (si existe)
                response = client.get(f"{self.base_url}/api/usuario/yo", headers=headers)
                if response.status_code == 200:
                    usuario_yo = response.json()
                    assert isinstance(usuario_yo, dict), "Respuesta debería ser un objeto"
                    print("✅ Endpoint /yo para usuarios funcionando")
                else:
                    print("ℹ️  Endpoint /yo para usuarios no implementado (esperado)")
                
        except Exception as e:
            pytest.fail(f"Pruebas de endpoints /yo fallaron: {e}")
    
    def test_unauthorized_access(self):
        """Prueba acceso no autorizado a endpoints protegidos"""
        try:
            with httpx.Client(timeout=10.0) as client:
                # Intentar acceder a endpoints sin autenticación
                endpoints = [
                    "/api/usuario/",
                    "/api/tarea/",
                    "/api/usuario/1",
                    "/api/tarea/1"
                ]
                
                for endpoint in endpoints:
                    response = client.get(f"{self.base_url}{endpoint}")
                    assert response.status_code in [401, 403], f"Endpoint {endpoint} debería requerir autenticación"
                
                print("✅ Acceso no autorizado rechazado correctamente")
                
        except Exception as e:
            pytest.fail(f"Pruebas de acceso no autorizado fallaron: {e}")
    
    def test_invalid_endpoints(self):
        """Prueba endpoints inexistentes"""
        try:
            with httpx.Client(timeout=10.0) as client:
                # Probar endpoints que no existen
                response = client.get(f"{self.base_url}/api/entidad_inexistente/")
                assert response.status_code == 404, "Endpoint inexistente debería devolver 404"
                
                response = client.get(f"{self.base_url}/api/usuario/999999")
                assert response.status_code in [404, 400], "ID inexistente debería devolver error"
                
                print("✅ Endpoints inexistentes manejados correctamente")
                
        except Exception as e:
            pytest.fail(f"Pruebas de endpoints inexistentes fallaron: {e}")

def run_integration_tests():
    """Función para ejecutar todas las pruebas de integración"""
    print("🚀 Iniciando pruebas de integración del backend...")
    print("=" * 60)
    
    # Verificar que el backend esté en funcionamiento
    test_instance = TestBackendIntegration()
    
    try:
        # Ejecutar pruebas en orden
        test_instance.test_backend_is_running()
        test_instance.test_health_check()
        test_instance.test_auth_login_success()
        test_instance.test_auth_login_invalid_credentials()
        test_instance.test_auth_me_endpoint()
        test_instance.test_auth_me_unauthorized()
        test_instance.test_usuario_endpoints()
        test_instance.test_tarea_endpoints()
        test_instance.test_yo_endpoints()
        test_instance.test_unauthorized_access()
        test_instance.test_invalid_endpoints()
        
        print("\n" + "=" * 60)
        print("🎉 ¡TODAS LAS PRUEBAS DE INTEGRACIÓN PASARON!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        raise

if __name__ == "__main__":
    run_integration_tests() 