from typing import Dict, Any, List, Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
import logging
import os
from datetime import datetime
import inflection

logger = logging.getLogger(__name__)

class ModelGenerator:
    """Generador de modelos SQLModel desde entidades YAML"""
    
    def __init__(self):
        """Inicializa el generador de modelos"""
        self.generated_models = {}
        self.pydantic_models = {}
        self.models_file = "yaml_to_backend/db/generated_models.py"
        self.base_models_file = "yaml_to_backend/db/models.py"
        
        # Plantillas de descripción para endpoints
        self.endpoint_descriptions = {
            "list": "Lista todos los {entity_plural} del sistema con paginación",
            "create": "Crea un nuevo {entity_singular}",
            "read": "Obtiene un {entity_singular} específico por ID",
            "update": "Actualiza un {entity_singular} existente",
            "delete": "Elimina un {entity_singular} (soft delete)",
            "yo": "Obtiene {entity_plural} del usuario autenticado"
        }
        
    def generate_model_code(self, entity_name: str, entity_data: Dict[str, Any]) -> str:
        """Genera código Python para un modelo SQLModel"""
        
        code_lines = [
            f"class {entity_name}(SQLModel, table=True):",
            f'    """Modelo generado para la entidad {entity_name}"""',
            f"    __tablename__ = '{entity_data['tabla']}'",
            "",
        ]
        
        # Procesar campos del YAML
        for field_name, field_config in entity_data['campos'].items():
            field_code = self._get_field_code(field_name, field_config)
            if field_code:
                code_lines.append(f"    {field_code}")
        
        from ..config import AUTH
        # Obtener configuración de borrado lógico
        delete_column = AUTH['columna_borrado']
        delete_type = AUTH['borrado_logico']
        # Solo agregar campo de borrado lógico si NO existe en el YAML
        if delete_column not in entity_data['campos']:
            if delete_type == 'boolean':
                delete_field = f"    {delete_column}: bool = Field(default=True)"
            else:
                delete_field = f"    {delete_column}: Optional[datetime] = Field(default=None)"
        else:
            delete_field = None
        # Agregar campos automáticos estándar solo si no existen
        if 'fecha_creacion' not in entity_data['campos']:
            code_lines.append("    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)")
        if 'fecha_actualizacion' not in entity_data['campos']:
            code_lines.append("    fecha_actualizacion: Optional[datetime] = Field(default=None)")
        if delete_field:
            code_lines.append(delete_field)
        return "\n".join(code_lines)
    
    def generate_swagger_documentation(self, entity_name: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera documentación Swagger para una entidad"""
        
        entity_singular = entity_name.lower()
        entity_plural = inflection.pluralize(entity_singular)
        
        # Obtener descripción de la entidad
        entity_description = entity_data.get('descripcion', f"Gestión de {entity_plural}")
        
        # Generar descripciones de endpoints
        endpoint_docs = {}
        for operation, template in self.endpoint_descriptions.items():
            description = template.format(
                entity_singular=entity_singular,
                entity_plural=entity_plural
            )
            endpoint_docs[operation] = description
        
        # Generar ejemplos basados en campos
        examples = self._generate_field_examples(entity_data.get('campos', {}))
        
        return {
            "entity_name": entity_name,
            "entity_description": entity_description,
            "endpoint_descriptions": endpoint_docs,
            "examples": examples,
            "tags": [entity_name]
        }
    
    def _generate_field_examples(self, campos: Dict[str, Any]) -> Dict[str, Any]:
        """Genera ejemplos de campos basados en la configuración YAML"""
        examples = {}
        
        for field_name, field_config in campos.items():
            if field_config.get('pk'):
                continue
                
            # Obtener ejemplo del YAML o generar uno por defecto
            if 'ejemplo' in field_config:
                examples[field_name] = field_config['ejemplo']
            else:
                examples[field_name] = self._get_default_example(field_config)
        
        return examples
    
    def _get_default_example(self, field_config: Dict[str, Any]) -> Any:
        """Genera un ejemplo por defecto basado en el tipo de campo"""
        field_type = field_config.get('tipo', 'string').lower()
        
        examples = {
            'integer': 1,
            'int': 1,
            'string': "ejemplo",
            'text': "Texto de ejemplo",
            'boolean': False,
            'bool': False,
            'datetime': "2025-01-01T00:00:00",
            'date': "2025-01-01",
            'float': 1.0,
            'decimal': 1.0,
            'json': {"key": "value"}
        }
        
        return examples.get(field_type, "ejemplo")
    
    def _get_field_code(self, field_name: str, field_config: Dict[str, Any]) -> str:
        """Genera código Python para un campo"""
        field_type = field_config.get('tipo', 'string').lower()
        
        if field_config.get('pk'):
            return f"{field_name}: Optional[int] = Field(default=None, primary_key=True)"
            
        if field_config.get('fk'):
            fk_config = field_config['fk']
            table_name, column_name = fk_config.split('.')
            return f"{field_name}: Optional[int] = Field(default=None, foreign_key='{table_name}.{column_name}')"
        
        # Mapeo de tipos
        type_mapping = {
            'integer': 'int',
            'int': 'int',
            'string': 'str',
            'text': 'str',
            'boolean': 'bool',
            'bool': 'bool',
            'datetime': 'datetime',
            'date': 'datetime',
            'float': 'float',
            'decimal': 'float',
            'json': 'dict'
        }
        
        python_type = type_mapping.get(field_type, 'str')
        
        # Configuración del campo
        field_args = []
        
        if 'max' in field_config:
            field_args.append(f"max_length={field_config['max']}")
            
        if field_config.get('unique'):
            field_args.append("unique=True")
            
        if field_config.get('index'):
            field_args.append("index=True")
            
        if not field_config.get('required', True):
            python_type = f"Optional[{python_type}]"
            field_args.append("default=None")
        
        # Construir la línea del campo
        field_line = f"{field_name}: {python_type}"
        if field_args:
            field_line += f" = Field({', '.join(field_args)})"
        
        return field_line
    
    def generate_pydantic_models_code(self, entity_name: str, entity_data: Dict[str, Any]) -> str:
        """Genera código Python para modelos Pydantic de una entidad"""
        from ..config import AUTH
        
        # Obtener configuración de borrado lógico
        delete_column = AUTH['columna_borrado']
        delete_type = AUTH['borrado_logico']
        
        # Generar documentación Swagger
        swagger_docs = self.generate_swagger_documentation(entity_name, entity_data)
        
        code_lines = [
            f"class {entity_name}Create(BaseModel):",
            f'    """Modelo para crear {entity_name} - {swagger_docs["entity_description"]}"""',
        ]
        
        # Campos para crear (excluir ID y campos automáticos)
        for field_name, field_config in entity_data['campos'].items():
            if not field_config.get('pk'):
                # Excluir campos que se generan automáticamente
                if field_name not in [delete_column, 'fecha_creacion', 'fecha_actualizacion']:
                    field_code = self._get_pydantic_field_code(field_name, field_config, required=True)
                    code_lines.append(f"    {field_code}")
        
        code_lines.extend([
            "",
            f"class {entity_name}Update(BaseModel):",
            f'    """Modelo para actualizar {entity_name}"""',
        ])
        
        # Campos para actualizar (todos opcionales, excluir ID, FK y campos automáticos)
        for field_name, field_config in entity_data['campos'].items():
            if (not field_config.get('pk') and 
                not field_config.get('fk') and 
                field_name not in [delete_column, 'fecha_creacion', 'fecha_actualizacion']):
                # Para password, hacer opcional en Update
                if field_name == 'password':
                    code_lines.append(f"    {field_name}: Optional[str]")
                else:
                    field_code = self._get_pydantic_field_code(field_name, field_config, required=False)
                    code_lines.append(f"    {field_code}")
        
        code_lines.extend([
            "",
            f"class {entity_name}Response(BaseModel):",
            f'    """Modelo para respuesta de {entity_name}"""',
        ])
        
        # Campos para respuesta (todos, incluir campos automáticos)
        for field_name, field_config in entity_data['campos'].items():
            field_code = self._get_pydantic_field_code(field_name, field_config, required=True)
            code_lines.append(f"    {field_code}")
        
        return "\n".join(code_lines)
    
    def _get_pydantic_field_code(self, field_name: str, field_config: Dict[str, Any], required: bool = True) -> str:
        """Genera código Python para un campo Pydantic"""
        from ..config import AUTH
        
        # Obtener configuración de borrado lógico
        delete_column = AUTH['columna_borrado']
        
        field_type = field_config.get('tipo', 'string').lower()
        
        # Mapeo de tipos
        type_mapping = {
            'integer': 'int',
            'int': 'int',
            'string': 'str',
            'text': 'str',
            'boolean': 'bool',
            'bool': 'bool',
            'datetime': 'datetime',
            'date': 'datetime',
            'float': 'float',
            'decimal': 'float',
            'json': 'dict'
        }
        
        python_type = type_mapping.get(field_type, 'str')
        
        # Campos automáticos siempre son opcionales
        if field_name in [delete_column, 'fecha_creacion', 'fecha_actualizacion']:
            python_type = f"Optional[{python_type}]"
        elif not required:
            python_type = f"Optional[{python_type}]"
        
        return f"{field_name}: {python_type}"
    
    def write_models_file(self, entities: Dict[str, Any]):
        """Escribe todos los modelos a un archivo Python"""
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.models_file), exist_ok=True)
        
        # Generar código del archivo
        file_content = [
            '"""Modelos generados automáticamente desde entidades YAML"""',
            "",
            "from typing import Optional, Dict, Type, Any",
            "from sqlmodel import SQLModel, Field",
            "from pydantic import BaseModel",
            "from datetime import datetime",
            "",
            "# Importar modelos existentes",
        ]
        
        # Los modelos SQLModel están en models.py
        # Los modelos Pydantic están definidos aquí
        file_content.append("# Los modelos SQLModel están en models.py")
        file_content.append("# Los modelos Pydantic están definidos aquí")
        
        file_content.extend([
            "",
            "",
        ])
        
        # Solo generar modelos Pydantic (los SQLModel ya existen)
        for entity_name, entity_data in entities.items():
            pydantic_code = self.generate_pydantic_models_code(entity_name, entity_data)
            file_content.append(pydantic_code)
            file_content.append("")
        
        # Generar diccionario centralizado automáticamente
        file_content.extend([
            "",
            "",
            "# =============================================================================",
            "# DICCIONARIO CENTRALIZADO DE MODELOS PYDANTIC",
            "# =============================================================================",
            "# Este diccionario facilita el acceso programático a todos los modelos generados",
            "# Estructura: {entidad: {accion: clase_modelo}}",
            "",
            "PYDANTIC_MODELS: Dict[str, Dict[str, Type[BaseModel]]] = {",
        ])
        
        # Agregar entradas al diccionario
        for entity_name in entities.keys():
            file_content.append(f'    "{entity_name}": {{')
            file_content.append(f'        "create": {entity_name}Create,')
            file_content.append(f'        "update": {entity_name}Update,')
            file_content.append(f'        "response": {entity_name}Response')
            file_content.append("    },")
        
        file_content.extend([
            "}",
            "",
            "# =============================================================================",
            "# FUNCIONES UTILITARIAS PARA ACCESO A MODELOS",
            "# =============================================================================",
            "",
            "def get_pydantic_model(entity_name: str, action: str) -> Type[BaseModel]:",
            '    """',
            "    Obtiene un modelo Pydantic específico por entidad y acción.",
            "    ",
            "    Args:",
            "        entity_name: Nombre de la entidad (ej: \"Usuario\", \"Tarea\")",
            "        action: Acción del modelo (\"create\", \"update\", \"response\")",
            "    ",
            "    Returns:",
            "        Clase del modelo Pydantic solicitado",
            "        ",
            "    Raises:",
            "        KeyError: Si la entidad o acción no existe",
            '    """',
            "    try:",
            "        return PYDANTIC_MODELS[entity_name][action]",
            "    except KeyError:",
            "        available_entities = list(PYDANTIC_MODELS.keys())",
            "        available_actions = list(PYDANTIC_MODELS.get(entity_name, {}).keys())",
            "        raise KeyError(",
            "            f\"Modelo no encontrado para entidad '{entity_name}' y acción '{action}'. \"",
            "            f\"Entidades disponibles: {available_entities}. \"",
            "            f\"Acciones disponibles para '{entity_name}': {available_actions}\"",
            "        )",
            "",
            "def get_all_entities() -> list[str]:",
            '    """Obtiene la lista de todas las entidades disponibles."""',
            "    return list(PYDANTIC_MODELS.keys())",
            "",
            "def get_entity_actions(entity_name: str) -> list[str]:",
            '    """Obtiene las acciones disponibles para una entidad específica."""',
            "    if entity_name not in PYDANTIC_MODELS:",
            "        raise KeyError(f\"Entidad '{entity_name}' no encontrada\")",
            "    return list(PYDANTIC_MODELS[entity_name].keys())",
            "",
            "def validate_entity_action(entity_name: str, action: str) -> bool:",
            '    """Valida si existe un modelo para la entidad y acción especificadas."""',
            "    return entity_name in PYDANTIC_MODELS and action in PYDANTIC_MODELS[entity_name]",
            "",
            "# =============================================================================",
            "# ALIASES PARA ACCESO RÁPIDO (OPCIONAL)",
            "# =============================================================================",
            "",
            "# Acceso directo a modelos específicos",
        ])
        
        # Generar alias automáticamente
        for entity_name in entities.keys():
            file_content.extend([
                f"{entity_name}CreateModel = PYDANTIC_MODELS[\"{entity_name}\"][\"create\"]",
                f"{entity_name}UpdateModel = PYDANTIC_MODELS[\"{entity_name}\"][\"update\"]",
                f"{entity_name}ResponseModel = PYDANTIC_MODELS[\"{entity_name}\"][\"response\"]",
                ""
            ])
        
        # Escribir archivo
        with open(self.models_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(file_content))
        
        logger.info(f"Archivo de modelos generado: {self.models_file}")
    
    def write_base_models_file(self, entities: Dict[str, Any]):
        """Escribe los modelos SQLModel base a yaml_to_backend/db/models.py"""
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.base_models_file), exist_ok=True)
        
        # Generar código del archivo base
        file_content = [
            '"""Modelos SQLModel base generados automáticamente desde entidades YAML"""',
            "",
            "from sqlmodel import SQLModel, Field",
            "from typing import Optional",
            "from datetime import datetime",
            "from yaml_to_backend.db.connection import Base",
            "",
            "",
        ]
        
        # Generar modelos SQLModel para cada entidad
        for entity_name, entity_data in entities.items():
            model_code = self.generate_model_code(entity_name, entity_data)
            file_content.append(model_code)
            file_content.append("")
        
        # Escribir archivo
        with open(self.base_models_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(file_content))
        
        logger.info(f"Archivo de modelos base generado: {self.base_models_file}")
    
    def import_generated_models(self):
        """Importa los modelos generados"""
        try:
            # Limpiar metadata de SQLAlchemy para evitar conflictos
            from sqlmodel import SQLModel
            SQLModel.metadata.clear()
            
            # Importar módulo de modelos base generado
            import importlib.util
            spec = importlib.util.spec_from_file_location("models", self.base_models_file)
            models_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(models_module)
            
            # Extraer modelos SQLModel
            for attr_name in dir(models_module):
                attr = getattr(models_module, attr_name)
                
                # Modelos SQLModel (clases que heredan de SQLModel)
                if (isinstance(attr, type) and 
                    issubclass(attr, SQLModel) and 
                    attr != SQLModel and 
                    hasattr(attr, '__tablename__')):
                    logger.info(f"Encontrado modelo SQLModel: {attr_name}")
                    self.generated_models[attr_name] = attr
            
            # Importar módulo generado para modelos Pydantic
            import importlib.util
            spec = importlib.util.spec_from_file_location("generated_models", self.models_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extraer modelos Pydantic
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # Modelos Pydantic (clases que heredan de BaseModel pero no de SQLModel)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseModel) and 
                    attr != BaseModel and 
                    not issubclass(attr, SQLModel)):
                    logger.info(f"Encontrado modelo Pydantic: {attr_name}")
                    # Agrupar por entidad
                    if attr_name.endswith('Create'):
                        entity_name = attr_name[:-6]  # Remover 'Create' (6 caracteres)
                        logger.info(f"Procesando Create: {attr_name} -> {entity_name}")
                        if entity_name not in self.pydantic_models:
                            self.pydantic_models[entity_name] = {}
                        self.pydantic_models[entity_name]['create'] = attr
                        logger.info(f"Agregado modelo create para {entity_name}")
                    elif attr_name.endswith('Update'):
                        entity_name = attr_name[:-6]  # Remover 'Update' (6 caracteres)
                        logger.info(f"Procesando Update: {attr_name} -> {entity_name}")
                        if entity_name not in self.pydantic_models:
                            self.pydantic_models[entity_name] = {}
                        self.pydantic_models[entity_name]['update'] = attr
                        logger.info(f"Agregado modelo update para {entity_name}")
                    elif attr_name.endswith('Response'):
                        entity_name = attr_name[:-8]  # Remover 'Response' (8 caracteres)
                        logger.info(f"Procesando Response: {attr_name} -> {entity_name}")
                        if entity_name not in self.pydantic_models:
                            self.pydantic_models[entity_name] = {}
                        self.pydantic_models[entity_name]['response'] = attr
                        logger.info(f"Agregado modelo response para {entity_name}")
            
            logger.info(f"Modelos Pydantic encontrados: {self.pydantic_models}")
            logger.info("Modelos generados importados correctamente")
            
        except Exception as e:
            logger.error(f"Error importando modelos generados: {e}")
            raise
    
    def generate_all_models(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Genera todos los modelos desde las entidades"""
        try:
            # Escribir archivo de modelos base (SQLModel)
            self.write_base_models_file(entities)
            
            # Escribir archivo de modelos Pydantic
            self.write_models_file(entities)
            
            # Importar modelos generados
            self.import_generated_models()
            
            logger.info(f"Modelos generados exitosamente: {list(self.generated_models.keys())}")
            
        except Exception as e:
            logger.error(f"Error generando modelos: {e}")
            raise
        
        return {
            'orm_models': self.generated_models,
            'pydantic_models': self.pydantic_models
        } 