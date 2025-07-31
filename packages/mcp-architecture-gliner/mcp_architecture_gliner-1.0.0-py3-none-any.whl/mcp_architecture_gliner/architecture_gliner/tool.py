from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .models import ArchitectureExtractor


class EntityExtractionRequest(BaseModel):
    """Request model for entity extraction."""
    text: str = Field(..., description="Text to analyze for architecture entities")
    labels: Optional[List[str]] = Field(None, description="Custom labels to extract")
    phase: Optional[str] = Field(None, description="TOGAF ADM phase context")
    role: Optional[str] = Field(None, description="Architecture role context")
    categories: Optional[List[str]] = Field(None, description="Label categories to focus on")
    threshold: float = Field(0.5, description="Confidence threshold for extraction")
    model_size: str = Field("medium-v2.1", description="GLiNER model size to use")
    include_context: bool = Field(True, description="Include contextual metadata")


class DocumentAnalysisRequest(BaseModel):
    """Request model for document analysis."""
    text: str = Field(..., description="Document text to analyze")
    threshold: float = Field(0.3, description="Threshold for entity detection")


class ArchitectureGLiNERTool:
    """
    Enhanced GLiNER tool for architecture-specific entity extraction and document analysis.
    """
    
    def __init__(self):
        """Initialize the architecture GLiNER tool."""
        self._extractors = {}  # Cache extractors by model size
    
    def _get_extractor(self, model_size: str) -> ArchitectureExtractor:
        """Get or create an extractor for the specified model size."""
        if model_size not in self._extractors:
            self._extractors[model_size] = ArchitectureExtractor(model_size=model_size)
        return self._extractors[model_size]
    
    def extract_entities(self, request: EntityExtractionRequest) -> List[Dict[str, Any]]:
        """
        Extract architecture-specific entities from text.
        
        Args:
            request: Entity extraction request parameters
        
        Returns:
            List of extracted entities with contextual metadata
        """
        extractor = self._get_extractor(request.model_size)
        
        return extractor.extract_entities(
            text=request.text,
            labels=request.labels,
            phase=request.phase,
            role=request.role,
            categories=request.categories,
            threshold=request.threshold,
            include_context=request.include_context
        )
    
    def analyze_document(self, request: DocumentAnalysisRequest) -> Dict[str, Any]:
        """
        Analyze and classify an architecture document.
        
        Args:
            request: Document analysis request parameters
        
        Returns:
            Document analysis with detected phases, roles, and characteristics
        """
        # Use medium model for document analysis by default
        extractor = self._get_extractor("medium-v2.1")
        
        return extractor.analyze_document_type(
            text=request.text,
            threshold=request.threshold
        )
    
    def get_available_labels(self, categories: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """
        Get available architecture labels by category.
        
        Args:
            categories: Specific categories to return. If None, returns all.
        
        Returns:
            Dictionary of label categories and their labels
        """
        # Use any extractor to get labels (model size doesn't matter for this)
        extractor = self._get_extractor("medium-v2.1")
        
        if categories:
            result = {}
            for category in categories:
                if category in extractor.architecture_labels:
                    result[category] = extractor.architecture_labels[category]
            return result
        
        return extractor.architecture_labels
    
    def get_phase_labels(self, phase: str) -> List[str]:
        """
        Get specific labels for a TOGAF ADM phase.
        
        Args:
            phase: TOGAF ADM phase name
        
        Returns:
            List of labels relevant to the specified phase
        """
        extractor = self._get_extractor("medium-v2.1")
        return extractor.get_labels_for_phase(phase)
    
    def get_role_labels(self, role: str) -> List[str]:
        """
        Get specific labels for an architecture role.
        
        Args:
            role: Architecture role name
        
        Returns:
            List of labels relevant to the specified role
        """
        extractor = self._get_extractor("medium-v2.1")
        return extractor.get_labels_for_role(role)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about available GLiNER models.
        
        Returns:
            Dictionary with model information and capabilities
        """
        extractor = self._get_extractor("medium-v2.1")
        
        return {
            "supported_models": list(ArchitectureExtractor.SUPPORTED_MODELS.keys()),
            "model_details": ArchitectureExtractor.SUPPORTED_MODELS,
            "available_categories": list(extractor.architecture_labels.keys()),
            "supported_phases": list(extractor.phase_labels.keys()),
            "supported_roles": list(extractor.role_focus_areas.keys())
        }