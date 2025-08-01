"""
Tests for the StateManager class.

This module contains unit tests for state management functionality,
including saving/loading project plans, progress tracking, and checkpoints.
"""

import json
import pytest
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from a3.managers.state import StateManager, StateManagerError, StateCorruptionError, CheckpointError
from a3.core.models import (
    ProjectPlan, ProjectProgress, ProjectPhase, ProjectStatus,
    Module, FunctionSpec, DependencyGraph, Argument, ImplementationStatus
)


class TestStateManager:
    """Test cases for StateManager class."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def state_manager(self, temp_project_dir):
        """Create a StateManager instance for testing."""
        manager = StateManager(temp_project_dir)
        manager.initialize()
        return manager
    
    @pytest.fixture
    def sample_project_plan(self):
        """Create a sample project plan for testing."""
        # Create sample arguments
        arg1 = Argument(name="x", type_hint="int", description="First number")
        arg2 = Argument(name="y", type_hint="int", description="Second number")
        
        # Create sample function
        func = FunctionSpec(
            name="add_numbers",
            module="math_utils",
            docstring="Add two numbers together.",
            arguments=[arg1, arg2],
            return_type="int",
            implementation_status=ImplementationStatus.NOT_STARTED
        )
        
        # Create sample module
        module = Module(
            name="math_utils",
            description="Mathematical utility functions",
            file_path="math_utils.py",
            dependencies=[],
            functions=[func]
        )
        
        # Create dependency graph
        dep_graph = DependencyGraph(
            nodes=["math_utils"],
            edges=[]
        )
        
        # Create project plan
        return ProjectPlan(
            objective="Create a simple math utility library",
            modules=[module],
            dependency_graph=dep_graph,
            estimated_functions=1,
            created_at=datetime.now()
        )
    
    def test_initialization(self, temp_project_dir):
        """Test StateManager initialization."""
        manager = StateManager(temp_project_dir)
        assert not manager._initialized
        
        manager.initialize()
        assert manager._initialized
        assert manager.a3_dir.exists()
        assert manager.checkpoints_dir.exists()
        assert manager.status_file.exists()
    
    def test_save_and_load_project_plan(self, state_manager, sample_project_plan):
        """Test saving and loading project plans."""
        # Save the project plan
        state_manager.save_project_plan(sample_project_plan)
        
        # Verify file was created
        assert state_manager.plan_file.exists()
        
        # Load the project plan
        loaded_plan = state_manager.load_project_plan()
        
        # Verify the loaded plan matches the original
        assert loaded_plan is not None
        assert loaded_plan.objective == sample_project_plan.objective
        assert len(loaded_plan.modules) == len(sample_project_plan.modules)
        assert loaded_plan.modules[0].name == sample_project_plan.modules[0].name
        assert loaded_plan.estimated_functions == sample_project_plan.estimated_functions
    
    def test_load_nonexistent_project_plan(self, state_manager):
        """Test loading a project plan when none exists."""
        loaded_plan = state_manager.load_project_plan()
        assert loaded_plan is None
    
    def test_save_and_load_progress(self, state_manager):
        """Test saving and loading project progress."""
        # Save initial progress
        phase = ProjectPhase.PLANNING
        data = {
            "total_functions": 5,
            "implemented_functions": 2,
            "failed_functions": ["func1"]
        }
        
        state_manager.save_progress(phase, data)
        
        # Load progress
        progress = state_manager.get_current_progress()
        
        assert progress is not None
        assert progress.current_phase == phase
        assert progress.total_functions == 5
        assert progress.implemented_functions == 2
        assert progress.failed_functions == ["func1"]
    
    def test_progress_phase_progression(self, state_manager):
        """Test that progress correctly tracks phase progression."""
        # Start with planning
        state_manager.save_progress(ProjectPhase.PLANNING, {})
        progress = state_manager.get_current_progress()
        assert progress.current_phase == ProjectPhase.PLANNING
        assert len(progress.completed_phases) == 0
        
        # Move to specification
        state_manager.save_progress(ProjectPhase.SPECIFICATION, {})
        progress = state_manager.get_current_progress()
        assert progress.current_phase == ProjectPhase.SPECIFICATION
        assert ProjectPhase.PLANNING in progress.completed_phases
    
    def test_create_and_restore_checkpoint(self, state_manager, sample_project_plan):
        """Test checkpoint creation and restoration."""
        # Set up initial state
        state_manager.save_project_plan(sample_project_plan)
        state_manager.save_progress(ProjectPhase.PLANNING, {"total_functions": 1})
        
        # Create checkpoint
        checkpoint_id = state_manager.create_checkpoint()
        assert checkpoint_id is not None
        assert isinstance(checkpoint_id, str)
        
        # Verify checkpoint directory exists
        checkpoint_dir = state_manager.checkpoints_dir / checkpoint_id
        assert checkpoint_dir.exists()
        assert (checkpoint_dir / "metadata.json").exists()
        
        # Store original objective for comparison
        original_objective = sample_project_plan.objective
        
        # Modify state
        modified_plan = sample_project_plan
        modified_plan.objective = "Modified objective"
        state_manager.save_project_plan(modified_plan)
        
        # Restore checkpoint
        success = state_manager.restore_checkpoint(checkpoint_id)
        assert success
        
        # Verify state was restored
        restored_plan = state_manager.load_project_plan()
        assert restored_plan.objective == original_objective
    
    def test_restore_nonexistent_checkpoint(self, state_manager):
        """Test restoring a checkpoint that doesn't exist."""
        with pytest.raises(CheckpointError):
            state_manager.restore_checkpoint("nonexistent_checkpoint")
    
    def test_list_checkpoints(self, state_manager, sample_project_plan):
        """Test listing available checkpoints."""
        # Initially no checkpoints
        checkpoints = state_manager.list_checkpoints()
        assert len(checkpoints) == 0
        
        # Create a checkpoint
        state_manager.save_project_plan(sample_project_plan)
        checkpoint_id = state_manager.create_checkpoint()
        
        # List checkpoints
        checkpoints = state_manager.list_checkpoints()
        assert len(checkpoints) == 1
        assert checkpoints[0]["checkpoint_id"] == checkpoint_id
    
    def test_cleanup_state(self, state_manager, sample_project_plan):
        """Test state cleanup functionality."""
        # Create multiple checkpoints
        state_manager.save_project_plan(sample_project_plan)
        
        checkpoint_ids = []
        for i in range(12):  # Create more than the limit (10)
            checkpoint_id = state_manager.create_checkpoint()
            checkpoint_ids.append(checkpoint_id)
        
        # Verify all checkpoints exist
        assert len(state_manager.list_checkpoints()) == 12
        
        # Run cleanup
        state_manager.cleanup_state()
        
        # Verify old checkpoints were removed (should keep last 10)
        remaining_checkpoints = state_manager.list_checkpoints()
        assert len(remaining_checkpoints) == 10
    
    def test_get_project_status(self, state_manager):
        """Test getting project status."""
        # Initial status
        status = state_manager.get_project_status()
        assert isinstance(status, ProjectStatus)
        assert not status.is_active
        assert not status.can_resume
        
        # After saving a plan
        sample_plan = ProjectPlan(objective="Test objective")
        state_manager.save_project_plan(sample_plan)
        
        status = state_manager.get_project_status()
        assert status.is_active
        assert status.can_resume
    
    def test_corrupted_plan_file(self, state_manager):
        """Test handling of corrupted project plan file."""
        # Create corrupted JSON file
        with open(state_manager.plan_file, 'w') as f:
            f.write("invalid json content")
        
        with pytest.raises(StateCorruptionError):
            state_manager.load_project_plan()
    
    def test_corrupted_progress_file(self, state_manager):
        """Test handling of corrupted progress file."""
        # Create corrupted JSON file
        with open(state_manager.progress_file, 'w') as f:
            f.write("invalid json content")
        
        with pytest.raises(StateCorruptionError):
            state_manager.get_current_progress()
    
    def test_atomic_operations(self, state_manager, sample_project_plan):
        """Test that operations are atomic (temp files are cleaned up)."""
        # Mock an exception during file writing
        with patch('shutil.move', side_effect=Exception("Simulated error")):
            with pytest.raises(StateManagerError):
                state_manager.save_project_plan(sample_project_plan)
        
        # Verify temp file was cleaned up
        assert not state_manager.plan_temp.exists()
        
        # Verify original file wasn't created/corrupted
        assert not state_manager.plan_file.exists()
    
    def test_validation_before_save(self, state_manager):
        """Test that validation occurs before saving."""
        # Create invalid project plan
        invalid_plan = ProjectPlan(objective="")  # Empty objective should fail validation
        
        with pytest.raises(StateManagerError):
            state_manager.save_project_plan(invalid_plan)
        
        # Verify file wasn't created
        assert not state_manager.plan_file.exists()


if __name__ == "__main__":
    pytest.main([__file__])