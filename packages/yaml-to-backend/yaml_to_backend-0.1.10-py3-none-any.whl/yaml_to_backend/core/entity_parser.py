import yaml
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class EntityParser:
    """Parser para archivos YAML de entidades"""
    
    def __init__(self, entities_path: str):
        self.entities_path = Path(entities_path)
        self.entities = {}
        
    def load_entities(self) -> Dict[str, Any]:
        """Carga todas las entidades desde archivos YAML"""
        if not self.entities_path.exists():
            logger.warning(f"Directorio de entidades no encontrado: {self.entities_path}")
            return {}
            
        for yaml_file in self.entities_path.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as file:
                    entity_data = yaml.safe_load(file)
                    if entity_data and 'entidad' in entity_data:
                        entity_name = entity_data['entidad']
                        self.entities[entity_name] = entity_data
                        logger.info(f"Entidad cargada: {entity_name}")
            except Exception as e:
                logger.error(f"Error cargando entidad desde {yaml_file}: {e}")
                
        return self.entities
    
    def get_entity(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene una entidad específica por nombre"""
        return self.entities.get(entity_name)
    
    def get_all_entities(self) -> Dict[str, Any]:
        """Obtiene todas las entidades cargadas"""
        return self.entities
    
    def validate_entity(self, entity_data: Dict[str, Any]) -> bool:
        """Valida que una entidad tenga la estructura correcta"""
        required_fields = ['entidad', 'tabla', 'campos']
        
        for field in required_fields:
            if field not in entity_data:
                logger.error(f"Campo requerido faltante: {field}")
                return False
                
        if not entity_data['campos']:
            logger.error("La entidad debe tener al menos un campo")
            return False
            
        return True 