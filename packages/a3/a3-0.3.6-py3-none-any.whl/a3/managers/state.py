"""
State management implementation for AI Project Builder.

This module provides the StateManager class that handles all project state
persistence, including project plans, progress tracking, and checkpoints.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import uuid

from ..core.interfaces import StateManagerInterface
from ..core.models import (
    ProjectPlan, ProjectProgress, ProjectPhase, ProjectStatus,
    Module, FunctionSpec, DependencyGraph, Argument,
    ImplementationStatus, ValidationResult, ModelConfiguration
)
from .base import BaseStateManager


class StateManagerError(Exception):
    """Base exception for state manager errors."""
    pass


class StateCorruptionError(StateManagerError):
    """Exception raised when state data is corrupted."""
    pass


class CheckpointError(StateManagerError):
    """Exception raised during checkpoint operations."""
    pass


class StateManager(BaseStateManager):
    """
    Manages project state persistence in the .A3 directory.
    
    Handles saving/loading project plans, progress tracking, and checkpoint
    functionality with atomic operations and error recovery.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the state manager.
        
        Args:
            project_path: Path to the project directory
        """
        super().__init__(project_path)
        
        # Define state file paths
        self.plan_file = self.a3_dir / "project_plan.json"
        self.progress_file = self.a3_dir / "progress.json"
        self.status_file = self.a3_dir / "status.json"
        self.model_config_file = self.a3_dir / "model_config.json"
        self.checkpoints_dir = self.a3_dir / "checkpoints"
        
        # Temporary files for atomic operations
        self.plan_temp = self.a3_dir / "project_plan.json.tmp"
        self.progress_temp = self.a3_dir / "progress.json.tmp"
        self.status_temp = self.a3_dir / "status.json.tmp"
        self.model_config_temp = self.a3_dir / "model_config.json.tmp"
    
    def initialize(self) -> None:
        """Initialize the state manager and create necessary directories."""
        super().initialize()
        
        # Create checkpoints directory
        self.checkpoints_dir.mkdir(exist_ok=True)
        
        # Initialize status file if it doesn't exist
        if not self.status_file.exists():
            initial_status = ProjectStatus(
                is_active=False,
                progress=None,
                errors=[],
                can_resume=False,
                next_action=None
            )
            self._save_status(initial_status)
    
    def save_project_plan(self, plan: ProjectPlan) -> None:
        """
        Save project plan to persistent storage with atomic operations.
        
        Args:
            plan: The project plan to save
            
        Raises:
            StateManagerError: If saving fails
        """
        self._ensure_initialized()
        
        try:
            # Validate the plan before saving
            plan.validate()
            
            # Convert to dictionary for JSON serialization
            plan_dict = self._project_plan_to_dict(plan)
            
            # Write to temporary file first (atomic operation)
            with open(self.plan_temp, 'w', encoding='utf-8') as f:
                json.dump(plan_dict, f, indent=2, default=str)
            
            # Move temporary file to final location
            shutil.move(str(self.plan_temp), str(self.plan_file))
            
            # Update status
            self._update_status(is_active=True, can_resume=True)
            
        except Exception as e:
            # Clean up temporary file if it exists
            if self.plan_temp.exists():
                self.plan_temp.unlink()
            raise StateManagerError(f"Failed to save project plan: {e}") from e
    
    def load_project_plan(self) -> Optional[ProjectPlan]:
        """
        Load project plan from persistent storage.
        
        Returns:
            The loaded project plan, or None if no plan exists
            
        Raises:
            StateCorruptionError: If the plan data is corrupted
        """
        self._ensure_initialized()
        
        if not self.plan_file.exists():
            return None
        
        try:
            with open(self.plan_file, 'r', encoding='utf-8') as f:
                plan_dict = json.load(f)
            
            # Convert from dictionary to ProjectPlan object
            plan = self._dict_to_project_plan(plan_dict)
            
            # Validate the loaded plan
            plan.validate()
            
            return plan
            
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Project plan file is corrupted: {e}") from e
        except Exception as e:
            raise StateCorruptionError(f"Failed to load project plan: {e}") from e
    
    def save_progress(self, phase: ProjectPhase, data: Dict[str, Any]) -> None:
        """
        Save progress information for a specific phase.
        
        Args:
            phase: The current project phase
            data: Additional data to save with the progress
            
        Raises:
            StateManagerError: If saving fails
        """
        self._ensure_initialized()
        
        try:
            # Ensure directories exist
            self.a3_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing progress or create new
            current_progress = self.get_current_progress()
            if current_progress is None:
                current_progress = ProjectProgress(
                    current_phase=phase,
                    completed_phases=[],
                    total_functions=0,
                    implemented_functions=0,
                    failed_functions=[],
                    last_updated=datetime.now()
                )
            
            # Update progress
            current_progress.current_phase = phase
            current_progress.last_updated = datetime.now()
            
            # Add to completed phases if not already there
            if phase not in current_progress.completed_phases:
                # Only add if we're moving forward
                phase_order = [ProjectPhase.PLANNING, ProjectPhase.SPECIFICATION, 
                              ProjectPhase.IMPLEMENTATION, ProjectPhase.INTEGRATION, 
                              ProjectPhase.COMPLETED]
                
                current_index = phase_order.index(phase)
                for i, completed_phase in enumerate(current_progress.completed_phases):
                    completed_index = phase_order.index(completed_phase)
                    if completed_index >= current_index:
                        break
                else:
                    # Add previous phases as completed if they're not already
                    for prev_phase in phase_order[:current_index]:
                        if prev_phase not in current_progress.completed_phases:
                            current_progress.completed_phases.append(prev_phase)
            
            # Update with additional data
            if 'total_functions' in data:
                current_progress.total_functions = data['total_functions']
            if 'implemented_functions' in data:
                current_progress.implemented_functions = data['implemented_functions']
            if 'failed_functions' in data:
                current_progress.failed_functions = data['failed_functions']
            
            # Validate before saving
            current_progress.validate()
            
            # Convert to dictionary and save atomically
            progress_dict = self._progress_to_dict(current_progress)
            
            with open(self.progress_temp, 'w', encoding='utf-8') as f:
                json.dump(progress_dict, f, indent=2, default=str)
            
            shutil.move(str(self.progress_temp), str(self.progress_file))
            
            # Update status with better error handling
            try:
                next_action = self._determine_next_action(current_progress)
                self._update_status(
                    is_active=True,
                    can_resume=True,
                    next_action=next_action
                )
            except Exception as status_error:
                # Log but don't fail the progress save
                print(f"Warning: Failed to update status: {status_error}")
                pass
            
        except Exception as e:
            if self.progress_temp.exists():
                self.progress_temp.unlink()
            raise StateManagerError(f"Failed to save progress: {e}") from e
    
    def get_current_progress(self) -> Optional[ProjectProgress]:
        """
        Get current project progress information.
        
        Returns:
            Current progress, or None if no progress exists
            
        Raises:
            StateCorruptionError: If progress data is corrupted
        """
        self._ensure_initialized()
        
        if not self.progress_file.exists():
            return None
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                progress_dict = json.load(f)
            
            progress = self._dict_to_progress(progress_dict)
            progress.validate()
            
            return progress
            
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Progress file is corrupted: {e}") from e
        except Exception as e:
            raise StateCorruptionError(f"Failed to load progress: {e}") from e
    
    def create_checkpoint(self) -> str:
        """
        Create a checkpoint of current project state.
        
        Returns:
            Checkpoint ID for later restoration
            
        Raises:
            CheckpointError: If checkpoint creation fails
        """
        self._ensure_initialized()
        
        try:
            # Generate unique checkpoint ID
            checkpoint_id = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            checkpoint_dir = self.checkpoints_dir / checkpoint_id
            
            # Create checkpoint directory
            checkpoint_dir.mkdir(exist_ok=True)
            
            # Copy all state files to checkpoint
            state_files = [
                (self.plan_file, "project_plan.json"),
                (self.progress_file, "progress.json"),
                (self.status_file, "status.json"),
                (self.model_config_file, "model_config.json")
            ]
            
            for source_file, target_name in state_files:
                if source_file.exists():
                    target_file = checkpoint_dir / target_name
                    shutil.copy2(str(source_file), str(target_file))
            
            # Save checkpoint metadata
            metadata = {
                "checkpoint_id": checkpoint_id,
                "created_at": datetime.now().isoformat(),
                "project_path": str(self.project_path),
                "files_saved": [name for _, name in state_files if (self.a3_dir / name).exists()]
            }
            
            metadata_file = checkpoint_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            return checkpoint_id
            
        except Exception as e:
            # Clean up partial checkpoint
            if 'checkpoint_dir' in locals() and checkpoint_dir.exists():
                shutil.rmtree(str(checkpoint_dir), ignore_errors=True)
            raise CheckpointError(f"Failed to create checkpoint: {e}") from e
    
    def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Restore project state from a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to restore
            
        Returns:
            True if restoration was successful, False otherwise
            
        Raises:
            CheckpointError: If restoration fails
        """
        self._ensure_initialized()
        
        checkpoint_dir = self.checkpoints_dir / checkpoint_id
        
        if not checkpoint_dir.exists():
            raise CheckpointError(f"Checkpoint {checkpoint_id} does not exist")
        
        try:
            # Load checkpoint metadata
            metadata_file = checkpoint_dir / "metadata.json"
            if not metadata_file.exists():
                raise CheckpointError(f"Checkpoint {checkpoint_id} is missing metadata")
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Verify checkpoint integrity
            expected_files = metadata.get("files_saved", [])
            for filename in expected_files:
                checkpoint_file = checkpoint_dir / filename
                if not checkpoint_file.exists():
                    raise CheckpointError(f"Checkpoint {checkpoint_id} is missing file: {filename}")
            
            # Create backup of current state
            backup_id = self.create_checkpoint()
            
            try:
                # Restore files from checkpoint
                state_files = [
                    ("project_plan.json", self.plan_file),
                    ("progress.json", self.progress_file),
                    ("status.json", self.status_file),
                    ("model_config.json", self.model_config_file)
                ]
                
                for source_name, target_file in state_files:
                    source_file = checkpoint_dir / source_name
                    if source_file.exists():
                        # Use atomic operation
                        temp_file = target_file.with_suffix('.tmp')
                        shutil.copy2(str(source_file), str(temp_file))
                        shutil.move(str(temp_file), str(target_file))
                
                return True
                
            except Exception as restore_error:
                # Attempt to restore from backup
                try:
                    self.restore_checkpoint(backup_id)
                except Exception:
                    pass  # Best effort recovery
                raise restore_error
            
        except Exception as e:
            raise CheckpointError(f"Failed to restore checkpoint {checkpoint_id}: {e}") from e
    
    def cleanup_state(self) -> None:
        """Clean up temporary state files and old checkpoints."""
        self._ensure_initialized()
        
        # Clean up temporary files
        temp_files = [self.plan_temp, self.progress_temp, self.status_temp, self.model_config_temp]
        for temp_file in temp_files:
            if temp_file.exists():
                temp_file.unlink()
        
        # Clean up old checkpoints (keep last 10)
        if self.checkpoints_dir.exists():
            checkpoints = sorted(
                [d for d in self.checkpoints_dir.iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Remove old checkpoints beyond the limit
            for old_checkpoint in checkpoints[10:]:
                shutil.rmtree(str(old_checkpoint), ignore_errors=True)
    
    def get_project_status(self) -> ProjectStatus:
        """
        Get current project status.
        
        Returns:
            Current project status
        """
        self._ensure_initialized()
        
        if not self.status_file.exists():
            return ProjectStatus()
        
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                status_dict = json.load(f)
            
            return self._dict_to_status(status_dict)
            
        except Exception:
            # Return default status if file is corrupted
            return ProjectStatus()
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all available checkpoints.
        
        Returns:
            List of checkpoint information dictionaries
        """
        self._ensure_initialized()
        
        checkpoints = []
        
        if not self.checkpoints_dir.exists():
            return checkpoints
        
        for checkpoint_dir in self.checkpoints_dir.iterdir():
            if not checkpoint_dir.is_dir():
                continue
            
            metadata_file = checkpoint_dir / "metadata.json"
            if not metadata_file.exists():
                continue
            
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                checkpoints.append(metadata)
            except Exception:
                continue  # Skip corrupted checkpoints
        
        # Sort by creation time (newest first)
        checkpoints.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return checkpoints
    
    def save_model_configuration(self, config: ModelConfiguration) -> None:
        """
        Save model configuration to persistent storage with atomic operations.
        
        Args:
            config: The model configuration to save
            
        Raises:
            StateManagerError: If saving fails
        """
        self._ensure_initialized()
        
        try:
            # Validate the configuration before saving
            config.validate()
            
            # Convert to dictionary for JSON serialization
            config_dict = self._model_config_to_dict(config)
            
            # Write to temporary file first (atomic operation)
            with open(self.model_config_temp, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            # Move temporary file to final location
            shutil.move(str(self.model_config_temp), str(self.model_config_file))
            
        except Exception as e:
            # Clean up temporary file if it exists
            if self.model_config_temp.exists():
                self.model_config_temp.unlink()
            raise StateManagerError(f"Failed to save model configuration: {e}") from e
    
    def load_model_configuration(self) -> Optional[ModelConfiguration]:
        """
        Load model configuration from persistent storage.
        
        Returns:
            The loaded model configuration, or None if no configuration exists
            
        Raises:
            StateCorruptionError: If the configuration data is corrupted
        """
        self._ensure_initialized()
        
        if not self.model_config_file.exists():
            return None
        
        try:
            with open(self.model_config_file, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # Convert from dictionary to ModelConfiguration object
            config = self._dict_to_model_config(config_dict)
            
            # Validate the loaded configuration
            config.validate()
            
            return config
            
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Model configuration file is corrupted: {e}") from e
        except Exception as e:
            raise StateCorruptionError(f"Failed to load model configuration: {e}") from e
    
    def get_or_create_model_configuration(self, default_model: str = "qwen/qwen-2.5-72b-instruct:free") -> ModelConfiguration:
        """
        Get existing model configuration or create a default one.
        
        Args:
            default_model: Default model to use if no configuration exists
            
        Returns:
            Model configuration (existing or newly created)
        """
        config = self.load_model_configuration()
        
        if config is None:
            # Create default configuration for projects without model config (migration logic)
            config = ModelConfiguration(
                current_model=default_model,
                available_models=[default_model],
                fallback_models=[default_model],
                preferences={
                    "auto_fallback": True,
                    "model_validation": True
                }
            )
            
            # Save the default configuration
            try:
                self.save_model_configuration(config)
            except Exception as e:
                # Log warning but don't fail - return the config anyway
                print(f"Warning: Failed to save default model configuration: {e}")
        
        return config
    
    def update_model_configuration(self, **kwargs) -> None:
        """
        Update model configuration with given parameters.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Raises:
            StateManagerError: If update fails
        """
        config = self.get_or_create_model_configuration()
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        # Update timestamp
        config.last_updated = datetime.now()
        
        # Save updated configuration
        self.save_model_configuration(config)

    # Private helper methods for serialization/deserialization
    
    def _project_plan_to_dict(self, plan: ProjectPlan) -> Dict[str, Any]:
        """Convert ProjectPlan to dictionary for JSON serialization."""
        return {
            "objective": plan.objective,
            "modules": [self._module_to_dict(module) for module in plan.modules],
            "dependency_graph": self._dependency_graph_to_dict(plan.dependency_graph),
            "estimated_functions": plan.estimated_functions,
            "created_at": plan.created_at.isoformat()
        }
    
    def _dict_to_project_plan(self, data: Dict[str, Any]) -> ProjectPlan:
        """Convert dictionary to ProjectPlan object."""
        modules = [self._dict_to_module(module_data) for module_data in data.get("modules", [])]
        dependency_graph = self._dict_to_dependency_graph(data.get("dependency_graph", {}))
        
        return ProjectPlan(
            objective=data["objective"],
            modules=modules,
            dependency_graph=dependency_graph,
            estimated_functions=data.get("estimated_functions", 0),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        )
    
    def _module_to_dict(self, module: Module) -> Dict[str, Any]:
        """Convert Module to dictionary for JSON serialization."""
        return {
            "name": module.name,
            "description": module.description,
            "file_path": module.file_path,
            "dependencies": module.dependencies,
            "functions": [self._function_spec_to_dict(func) for func in module.functions]
        }
    
    def _dict_to_module(self, data: Dict[str, Any]) -> Module:
        """Convert dictionary to Module object."""
        functions = [self._dict_to_function_spec(func_data) for func_data in data.get("functions", [])]
        
        return Module(
            name=data["name"],
            description=data["description"],
            file_path=data["file_path"],
            dependencies=data.get("dependencies", []),
            functions=functions
        )
    
    def _function_spec_to_dict(self, func: FunctionSpec) -> Dict[str, Any]:
        """Convert FunctionSpec to dictionary for JSON serialization."""
        return {
            "name": func.name,
            "module": func.module,
            "docstring": func.docstring,
            "arguments": [self._argument_to_dict(arg) for arg in func.arguments],
            "return_type": func.return_type,
            "implementation_status": func.implementation_status.value
        }
    
    def _dict_to_function_spec(self, data: Dict[str, Any]) -> FunctionSpec:
        """Convert dictionary to FunctionSpec object."""
        arguments = [self._dict_to_argument(arg_data) for arg_data in data.get("arguments", [])]
        
        return FunctionSpec(
            name=data["name"],
            module=data["module"],
            docstring=data["docstring"],
            arguments=arguments,
            return_type=data.get("return_type", "None"),
            implementation_status=ImplementationStatus(data.get("implementation_status", "not_started"))
        )
    
    def _argument_to_dict(self, arg: Argument) -> Dict[str, Any]:
        """Convert Argument to dictionary for JSON serialization."""
        return {
            "name": arg.name,
            "type_hint": arg.type_hint,
            "default_value": arg.default_value,
            "description": arg.description
        }
    
    def _dict_to_argument(self, data: Dict[str, Any]) -> Argument:
        """Convert dictionary to Argument object."""
        return Argument(
            name=data["name"],
            type_hint=data["type_hint"],
            default_value=data.get("default_value"),
            description=data.get("description", "")
        )
    
    def _dependency_graph_to_dict(self, graph: DependencyGraph) -> Dict[str, Any]:
        """Convert DependencyGraph to dictionary for JSON serialization."""
        return {
            "nodes": graph.nodes,
            "edges": graph.edges
        }
    
    def _dict_to_dependency_graph(self, data: Dict[str, Any]) -> DependencyGraph:
        """Convert dictionary to DependencyGraph object."""
        return DependencyGraph(
            nodes=data.get("nodes", []),
            edges=[tuple(edge) for edge in data.get("edges", [])]
        )
    
    def _progress_to_dict(self, progress: ProjectProgress) -> Dict[str, Any]:
        """Convert ProjectProgress to dictionary for JSON serialization."""
        return {
            "current_phase": progress.current_phase.value,
            "completed_phases": [phase.value for phase in progress.completed_phases],
            "total_functions": progress.total_functions,
            "implemented_functions": progress.implemented_functions,
            "failed_functions": progress.failed_functions,
            "last_updated": progress.last_updated.isoformat()
        }
    
    def _dict_to_progress(self, data: Dict[str, Any]) -> ProjectProgress:
        """Convert dictionary to ProjectProgress object."""
        return ProjectProgress(
            current_phase=ProjectPhase(data.get("current_phase", "planning")),
            completed_phases=[ProjectPhase(phase) for phase in data.get("completed_phases", [])],
            total_functions=data.get("total_functions", 0),
            implemented_functions=data.get("implemented_functions", 0),
            failed_functions=data.get("failed_functions", []),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        )
    
    def _status_to_dict(self, status: ProjectStatus) -> Dict[str, Any]:
        """Convert ProjectStatus to dictionary for JSON serialization."""
        return {
            "is_active": status.is_active,
            "progress": self._progress_to_dict(status.progress) if status.progress else None,
            "errors": status.errors,
            "can_resume": status.can_resume,
            "next_action": status.next_action
        }
    
    def _dict_to_status(self, data: Dict[str, Any]) -> ProjectStatus:
        """Convert dictionary to ProjectStatus object."""
        progress_data = data.get("progress")
        progress = self._dict_to_progress(progress_data) if progress_data else None
        
        return ProjectStatus(
            is_active=data.get("is_active", False),
            progress=progress,
            errors=data.get("errors", []),
            can_resume=data.get("can_resume", False),
            next_action=data.get("next_action")
        )
    
    def _save_status(self, status: ProjectStatus) -> None:
        """Save project status atomically."""
        try:
            status_dict = self._status_to_dict(status)
            
            with open(self.status_temp, 'w', encoding='utf-8') as f:
                json.dump(status_dict, f, indent=2, default=str)
            
            shutil.move(str(self.status_temp), str(self.status_file))
            
        except Exception as e:
            if self.status_temp.exists():
                self.status_temp.unlink()
            raise StateManagerError(f"Failed to save status: {e}") from e
    
    def _update_status(self, **kwargs) -> None:
        """Update project status with given parameters."""
        current_status = self.get_project_status()
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(current_status, key):
                setattr(current_status, key, value)
        
        self._save_status(current_status)
    
    def _determine_next_action(self, progress: ProjectProgress) -> Optional[str]:
        """Determine the next action based on current progress."""
        phase_actions = {
            ProjectPhase.PLANNING: "Generate specifications",
            ProjectPhase.SPECIFICATION: "Implement functions",
            ProjectPhase.IMPLEMENTATION: "Integrate modules",
            ProjectPhase.INTEGRATION: "Project complete",
            ProjectPhase.COMPLETED: None
        }
        
        return phase_actions.get(progress.current_phase)
    
    def _model_config_to_dict(self, config: ModelConfiguration) -> Dict[str, Any]:
        """Convert ModelConfiguration to dictionary for JSON serialization."""
        return {
            "current_model": config.current_model,
            "available_models": config.available_models,
            "fallback_models": config.fallback_models,
            "preferences": config.preferences,
            "last_updated": config.last_updated.isoformat()
        }
    
    def _dict_to_model_config(self, data: Dict[str, Any]) -> ModelConfiguration:
        """Convert dictionary to ModelConfiguration object."""
        return ModelConfiguration(
            current_model=data["current_model"],
            available_models=data.get("available_models", []),
            fallback_models=data.get("fallback_models", []),
            preferences=data.get("preferences", {}),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        )