"""
Core module containing the main API, data models, and base interfaces.
"""

from .api import A3
from .models import (
    ProjectPlan, ProjectStatus, ProjectPhase, ProjectProgress,
    Module, FunctionSpec, DependencyGraph, ImplementationStatus,
    ProjectResult, SpecificationSet, ImplementationResult, IntegrationResult,
    EnhancedDependencyGraph, FunctionGap, OptimizationSuggestion, StructureAnalysis
)
from .gap_analyzer import IntelligentGapAnalyzer
from .interfaces import (
    BaseEngine, PlanningEngineInterface, SpecificationGeneratorInterface,
    CodeGeneratorInterface, IntegrationEngineInterface, StateManagerInterface,
    ProjectManagerInterface, AIClientInterface, FileSystemManagerInterface,
    DependencyAnalyzerInterface
)

__all__ = [
    "A3",
    "ProjectPlan", "ProjectStatus", "ProjectPhase", "ProjectProgress",
    "Module", "FunctionSpec", "DependencyGraph", "ImplementationStatus",
    "ProjectResult", "SpecificationSet", "ImplementationResult", "IntegrationResult",
    "EnhancedDependencyGraph", "FunctionGap", "OptimizationSuggestion", "StructureAnalysis",
    "IntelligentGapAnalyzer",
    "BaseEngine", "PlanningEngineInterface", "SpecificationGeneratorInterface",
    "CodeGeneratorInterface", "IntegrationEngineInterface", "StateManagerInterface",
    "ProjectManagerInterface", "AIClientInterface", "FileSystemManagerInterface",
    "DependencyAnalyzerInterface"
]