"""
A3 - Automated project creation through AI-powered planning and code generation.

This package provides a complete solution for transforming high-level project objectives
into fully implemented, modular Python projects.
"""

from .core.api import A3
from .core.models import (
    ProjectPlan, ProjectStatus, ProjectPhase, ProjectProgress,
    Module, FunctionSpec, DependencyGraph, ImplementationStatus,
    EnhancedDependencyGraph, FunctionDependency, DependencyType,
    StructureAnalysis, FunctionGap, ImportIssue, ImportIssueType,
    OptimizationSuggestion
)

__version__ = "0.3.6"
__all__ = [
    "A3", 
    "ProjectPlan", 
    "ProjectStatus", 
    "ProjectPhase",
    "ProjectProgress",
    "Module",
    "FunctionSpec", 
    "DependencyGraph",
    "EnhancedDependencyGraph",
    "FunctionDependency",
    "DependencyType",
    "ImplementationStatus",
    "StructureAnalysis",
    "FunctionGap", 
    "ImportIssue",
    "ImportIssueType",
    "OptimizationSuggestion"
]