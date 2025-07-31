from typing import List, Dict, Any, Optional, Union
import yaml
import os
from pathlib import Path
from gliner import GLiNER


class ArchitectureExtractor:
    """Enhanced GLiNER-based extractor for architecture-specific entity recognition."""
    
    SUPPORTED_MODELS = {
        'base': 'urchade/gliner_base',
        'medium-v2.1': 'urchade/gliner_medium-v2.1', 
        'large-v2.1': 'urchade/gliner_large-v2.1',
        'multi': 'urchade/gliner_multi-v2.1'
    }
    
    def __init__(self, model_size: str = 'medium-v2.1', config_path: Optional[str] = None):
        """
        Initialize the Architecture Extractor.
        
        Args:
            model_size: Size of GLiNER model to use ('base', 'medium-v2.1', 'large-v2.1', 'multi')
            config_path: Path to architecture labels configuration file
        """
        self.model_size = model_size
        self.model = None
        self.architecture_labels = {}
        self.phase_labels = {}
        self.role_focus_areas = {}
        
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "architecture_labels.yaml"
        
        self._load_configuration(config_path)
        self._initialize_model()
    
    def _load_configuration(self, config_path: Union[str, Path]) -> None:
        """Load architecture labels configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                self.architecture_labels = config.get('architecture_labels', {})
                self.phase_labels = config.get('phase_specific_labels', {})
                self.role_focus_areas = config.get('role_focus_areas', {})
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")
    
    def _initialize_model(self) -> None:
        """Initialize the GLiNER model."""
        if self.model_size not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model size: {self.model_size}. "
                           f"Supported: {list(self.SUPPORTED_MODELS.keys())}")
        
        model_name = self.SUPPORTED_MODELS[self.model_size]
        try:
            self.model = GLiNER.from_pretrained(model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load GLiNER model '{model_name}': {e}")
    
    def get_labels_for_phase(self, phase: str) -> List[str]:
        """Get specific labels for a TOGAF ADM phase."""
        phase_key = phase.lower().replace(' ', '_').replace('-', '_')
        return self.phase_labels.get(phase_key, [])
    
    def get_labels_for_role(self, role: str) -> List[str]:
        """Get specific labels focused on a particular architecture role."""
        role_key = role.lower().replace(' ', '_').replace('-', '_')
        return self.role_focus_areas.get(role_key, [])
    
    def get_all_labels(self, categories: Optional[List[str]] = None) -> List[str]:
        """
        Get all architecture labels or specific categories.
        
        Args:
            categories: List of label categories to include. If None, returns all.
        
        Returns:
            List of architecture-specific labels
        """
        if categories is None:
            # Return all labels from all categories
            all_labels = []
            for category_labels in self.architecture_labels.values():
                if isinstance(category_labels, list):
                    all_labels.extend(category_labels)
            return list(set(all_labels))  # Remove duplicates
        
        # Return labels from specific categories
        selected_labels = []
        for category in categories:
            if category in self.architecture_labels:
                category_labels = self.architecture_labels[category]
                if isinstance(category_labels, list):
                    selected_labels.extend(category_labels)
        
        return list(set(selected_labels))  # Remove duplicates
    
    def extract_entities(
        self,
        text: str,
        labels: Optional[List[str]] = None,
        phase: Optional[str] = None,
        role: Optional[str] = None,
        categories: Optional[List[str]] = None,
        threshold: float = 0.5,
        include_context: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extract architecture-specific entities from text.
        
        Args:
            text: Input text to analyze
            labels: Custom labels to use. If None, uses architecture labels
            phase: TOGAF ADM phase to focus on
            role: Architecture role to focus on  
            categories: Specific label categories to use
            threshold: Confidence threshold for entity extraction
            include_context: Whether to include contextual information
        
        Returns:
            List of extracted entities with enhanced metadata
        """
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        # Determine labels to use
        extraction_labels = []
        
        if labels:
            extraction_labels = labels
        else:
            # Build labels based on phase, role, and categories
            if phase:
                extraction_labels.extend(self.get_labels_for_phase(phase))
            
            if role:
                extraction_labels.extend(self.get_labels_for_role(role))
            
            if categories:
                extraction_labels.extend(self.get_all_labels(categories))
            
            # If no specific criteria, use all architecture labels
            if not extraction_labels:
                extraction_labels = self.get_all_labels()
        
        # Remove duplicates while preserving order
        extraction_labels = list(dict.fromkeys(extraction_labels))
        
        if not extraction_labels:
            return []
        
        # Extract entities using GLiNER
        try:
            entities = self.model.predict_entities(text, extraction_labels, threshold=threshold)
        except Exception as e:
            raise RuntimeError(f"Entity extraction failed: {e}")
        
        # Enhance entities with contextual information
        enhanced_entities = []
        for entity in entities:
            enhanced_entity = {
                'text': entity.get('text', ''),
                'label': entity.get('label', ''),
                'start': entity.get('start', 0),
                'end': entity.get('end', 0),
                'score': entity.get('score', 0.0)
            }
            
            if include_context:
                enhanced_entity.update(self._add_contextual_metadata(
                    entity, phase, role, categories
                ))
            
            enhanced_entities.append(enhanced_entity)
        
        return enhanced_entities
    
    def _add_contextual_metadata(
        self,
        entity: Dict[str, Any],
        phase: Optional[str],
        role: Optional[str], 
        categories: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Add contextual metadata to extracted entities."""
        metadata = {}
        
        entity_label = entity.get('label', '').lower()
        
        # Determine which category the entity belongs to
        entity_categories = []
        for cat_name, cat_labels in self.architecture_labels.items():
            if isinstance(cat_labels, list) and entity_label in [l.lower() for l in cat_labels]:
                entity_categories.append(cat_name)
        
        metadata['categories'] = entity_categories
        
        # Add phase relevance
        if phase:
            phase_labels = [l.lower() for l in self.get_labels_for_phase(phase)]
            metadata['phase_relevant'] = entity_label in phase_labels
            metadata['target_phase'] = phase
        
        # Add role relevance  
        if role:
            role_labels = [l.lower() for l in self.get_labels_for_role(role)]
            metadata['role_relevant'] = entity_label in role_labels
            metadata['target_role'] = role
        
        # Calculate contextual score based on relevance
        contextual_score = entity.get('score', 0.0)
        if metadata.get('phase_relevant', False):
            contextual_score *= 1.2  # Boost for phase relevance
        if metadata.get('role_relevant', False):
            contextual_score *= 1.1  # Boost for role relevance
        
        metadata['contextual_score'] = min(contextual_score, 1.0)
        
        return metadata
    
    def analyze_document_type(self, text: str, threshold: float = 0.3) -> Dict[str, Any]:
        """
        Analyze and classify the type of architecture document.
        
        Args:
            text: Document text to analyze
            threshold: Threshold for entity detection
        
        Returns:
            Document analysis with detected phases, roles, and artifact types
        """
        # Extract entities with lower threshold for broader detection
        entities = self.extract_entities(text, threshold=threshold, include_context=False)
        
        # Count entities by category
        category_counts = {}
        phase_indicators = {}
        role_indicators = {}
        
        for entity in entities:
            label = entity['label'].lower()
            
            # Count by architecture categories
            for cat_name, cat_labels in self.architecture_labels.items():
                if isinstance(cat_labels, list) and label in [l.lower() for l in cat_labels]:
                    category_counts[cat_name] = category_counts.get(cat_name, 0) + 1
            
            # Detect phase indicators
            for phase_name, phase_labels in self.phase_labels.items():
                if label in [l.lower() for l in phase_labels]:
                    phase_indicators[phase_name] = phase_indicators.get(phase_name, 0) + 1
            
            # Detect role indicators
            for role_name, role_labels in self.role_focus_areas.items():
                if label in [l.lower() for l in role_labels]:
                    role_indicators[role_name] = role_indicators.get(role_name, 0) + 1
        
        # Determine most likely document characteristics
        analysis = {
            'entity_counts': len(entities),
            'category_distribution': category_counts,
            'likely_phases': sorted(phase_indicators.items(), key=lambda x: x[1], reverse=True)[:3],
            'likely_roles': sorted(role_indicators.items(), key=lambda x: x[1], reverse=True)[:3],
            'document_complexity': self._assess_complexity(category_counts),
            'suggested_model': self._suggest_model_size(len(entities), category_counts)
        }
        
        return analysis
    
    def _assess_complexity(self, category_counts: Dict[str, int]) -> str:
        """Assess document complexity based on entity distribution."""
        total_entities = sum(category_counts.values())
        unique_categories = len(category_counts)
        
        if total_entities < 10 or unique_categories < 3:
            return 'low'
        elif total_entities < 25 or unique_categories < 6:
            return 'medium'
        else:
            return 'high'
    
    def _suggest_model_size(self, entity_count: int, category_counts: Dict[str, int]) -> str:
        """Suggest optimal model size based on document characteristics."""
        complexity = self._assess_complexity(category_counts)
        
        if complexity == 'low' or entity_count < 15:
            return 'base'
        elif complexity == 'medium' or entity_count < 40:
            return 'medium-v2.1'
        else:
            return 'large-v2.1'