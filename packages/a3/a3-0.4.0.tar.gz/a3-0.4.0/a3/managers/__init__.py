"""
Managers module for AI Project Builder.

This module contains manager classes that orchestrate different aspects
of the project generation workflow.
"""

from .base import (
    BaseManager, BaseProjectManager, BaseStateManager,
    BaseFileSystemManager, BaseDependencyAnalyzer, BasePackageManager,
    BaseDataSourceManager
)
from .state import StateManager
from .filesystem import FileSystemManager
from .dependency import DependencyAnalyzer
from .package_manager import PackageManager
from .data_source_manager import DataSourceManager

__all__ = [
    "BaseManager", "BaseProjectManager", "BaseStateManager",
    "BaseFileSystemManager", "BaseDependencyAnalyzer", "BasePackageManager",
    "BaseDataSourceManager",
    "StateManager", "FileSystemManager", "DependencyAnalyzer", "PackageManager",
    "DataSourceManager"
]