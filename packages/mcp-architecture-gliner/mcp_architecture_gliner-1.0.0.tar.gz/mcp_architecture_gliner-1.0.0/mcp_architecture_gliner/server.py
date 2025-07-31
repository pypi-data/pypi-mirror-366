#!/usr/bin/env python3
"""
Architecture GLiNER FastMCP Server

This is the main entry point for the MCP server that provides
architecture-specific entity extraction capabilities.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Disable HF transfer for stability
os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '0'

# Import our architecture extractor implementation
from .architecture_gliner.models import ArchitectureExtractor

# Create FastMCP server instance
mcp = FastMCP(
    name="architecture-gliner",
    version="1.0.0"
)

# Global extractor instances cache
_extractors = {}


def _get_extractor(model_size: str = "medium-v2.1") -> ArchitectureExtractor:
    """Get or create an extractor for the specified model size."""
    if model_size not in _extractors:
        _extractors[model_size] = ArchitectureExtractor(model_size=model_size)
    return _extractors[model_size]


@mcp.tool()
def extract_architecture_entities(
    text: str,
    labels: Optional[List[str]] = None,
    phase: Optional[str] = None,
    role: Optional[str] = None,
    categories: Optional[List[str]] = None,
    threshold: float = 0.5,
    model_size: str = "medium-v2.1",
    include_context: bool = True
) -> Dict[str, Any]:
    """
    Extract architecture-specific entities from text using GLiNER.
    
    This tool analyzes input text and extracts entities relevant to software architecture,
    with support for TOGAF ADM phases, architecture roles, and contextual filtering.
    
    Args:
        text: Text to analyze for architecture entities
        labels: Custom labels to extract (if None, uses architecture labels)
        phase: TOGAF ADM phase context (e.g., 'architecture_vision', 'business_architecture')
        role: Architecture role context (e.g., 'enterprise_architect', 'solution_architect')
        categories: Label categories to focus on (e.g., ['patterns', 'quality_attributes'])
        threshold: Confidence threshold for extraction (0.0-1.0)
        model_size: GLiNER model size ('base', 'medium-v2.1', 'large-v2.1')
        include_context: Include contextual metadata in results
    
    Returns:
        Dictionary containing entities, total_count, and processing_info
    """
    try:
        extractor = _get_extractor(model_size)
        
        entities = extractor.extract_entities(
            text=text,
            labels=labels,
            phase=phase,
            role=role,
            categories=categories,
            threshold=threshold,
            include_context=include_context
        )
        
        return {
            "entities": entities,
            "total_count": len(entities),
            "processing_info": {
                "model_size": model_size,
                "threshold": threshold,
                "phase_context": phase,
                "role_context": role,
                "categories_used": categories,
                "include_context": include_context,
                "text_length": len(text)
            }
        }
    except Exception as e:
        logger.error(f"Entity extraction failed: {e}")
        return {
            "error": str(e),
            "entities": [],
            "total_count": 0
        }


@mcp.tool()
def analyze_architecture_document(
    text: str,
    threshold: float = 0.3
) -> Dict[str, Any]:
    """
    Analyze and classify an architecture document.
    
    This tool analyzes a document to determine its likely architecture phases,
    roles, complexity, and suggests optimal processing parameters.
    
    Args:
        text: Document text to analyze
        threshold: Threshold for entity detection (0.0-1.0)
    
    Returns:
        Dictionary containing analysis results
    """
    try:
        extractor = _get_extractor("medium-v2.1")
        
        analysis = extractor.analyze_document_type(
            text=text,
            threshold=threshold
        )
        
        return {
            "analysis": analysis,
            "processing_info": {
                "threshold": threshold,
                "text_length": len(text),
                "analysis_model": "medium-v2.1"
            }
        }
    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        return {
            "error": str(e),
            "analysis": {}
        }


@mcp.tool()
def get_architecture_labels(
    categories: Optional[List[str]] = None
) -> Dict[str, List[str]]:
    """
    Get available architecture labels by category.
    
    Returns all architecture-specific labels organized by category,
    or specific categories if requested.
    
    Args:
        categories: List of categories to return (if None, returns all)
    
    Returns:
        Dictionary of label categories and their labels
    """
    try:
        extractor = _get_extractor("medium-v2.1")
        
        if categories:
            result = {}
            for category in categories:
                if category in extractor.architecture_labels:
                    result[category] = extractor.architecture_labels[category]
            return result
        
        return extractor.architecture_labels
    except Exception as e:
        logger.error(f"Failed to get labels: {e}")
        return {"error": str(e)}


@mcp.tool()
def get_phase_specific_labels(phase: str) -> Dict[str, Any]:
    """
    Get labels specific to a TOGAF ADM phase.
    
    Args:
        phase: TOGAF ADM phase name (e.g., 'architecture_vision', 'business_architecture')
    
    Returns:
        Dictionary containing phase and its specific labels
    """
    try:
        extractor = _get_extractor("medium-v2.1")
        labels = extractor.get_labels_for_phase(phase)
        
        return {
            "phase": phase,
            "labels": labels,
            "count": len(labels)
        }
    except Exception as e:
        logger.error(f"Failed to get phase labels: {e}")
        return {"error": str(e), "phase": phase, "labels": []}


@mcp.tool()
def get_role_specific_labels(role: str) -> Dict[str, Any]:
    """
    Get labels specific to an architecture role.
    
    Args:
        role: Architecture role name (e.g., 'enterprise_architect', 'solution_architect')
    
    Returns:
        Dictionary containing role and its focus area labels
    """
    try:
        extractor = _get_extractor("medium-v2.1")
        labels = extractor.get_labels_for_role(role)
        
        return {
            "role": role,
            "labels": labels,
            "count": len(labels)
        }
    except Exception as e:
        logger.error(f"Failed to get role labels: {e}")
        return {"error": str(e), "role": role, "labels": []}


@mcp.tool()
def get_gliner_model_info() -> Dict[str, Any]:
    """
    Get information about available GLiNER models and capabilities.
    
    Returns:
        Dictionary with model information, supported phases, roles, and categories
    """
    try:
        extractor = _get_extractor("medium-v2.1")
        
        return {
            "supported_models": list(ArchitectureExtractor.SUPPORTED_MODELS.keys()),
            "model_details": ArchitectureExtractor.SUPPORTED_MODELS,
            "available_categories": list(extractor.architecture_labels.keys()),
            "supported_phases": list(extractor.phase_labels.keys()),
            "supported_roles": list(extractor.role_focus_areas.keys()),
            "total_labels": len(extractor.get_all_labels())
        }
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        return {"error": str(e)}


def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Architecture GLiNER MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()