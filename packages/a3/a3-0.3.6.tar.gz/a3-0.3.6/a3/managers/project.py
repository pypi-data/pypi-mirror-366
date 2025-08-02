"""
Project manager implementation for AI Project Builder.

This module provides the ProjectManager class that orchestrates the complete
workflow from planning to integration with error recovery and resumption capabilities.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .base import BaseProjectManager
from ..core.models import (
    ProjectPlan, ProjectProgress, ProjectPhase, ProjectResult,
    SpecificationSet, ImplementationResult, IntegrationResult,
    ValidationResult, ProjectStatus, FunctionSpec
)
from ..core.interfaces import (
    ProjectManagerInterface, StateManagerInterface,
    PlanningEngineInterface, SpecificationGeneratorInterface,
    CodeGeneratorInterface, IntegrationEngineInterface,
    CodeExecutorInterface, DebugAnalyzerInterface
)


class ProjectManagerError(Exception):
    """Base exception for project manager errors."""
    pass


class ProjectManager(BaseProjectManager):
    """
    Project manager implementation that orchestrates the complete workflow.
    
    This class manages the entire project generation pipeline from planning
    to integration with error recovery and resumption capabilities.
    """
    
    def __init__(
        self,
        project_path: str,
        state_manager: StateManagerInterface,
        planning_engine: PlanningEngineInterface,
        spec_generator: SpecificationGeneratorInterface,
        code_generator: CodeGeneratorInterface,
        integration_engine: IntegrationEngineInterface,
        code_executor: Optional[CodeExecutorInterface] = None,
        debug_analyzer: Optional[DebugAnalyzerInterface] = None
    ):
        """
        Initialize the project manager.
        
        Args:
            project_path: Path to the project directory
            state_manager: State management component
            planning_engine: Planning engine component
            spec_generator: Specification generator component
            code_generator: Code generator component
            integration_engine: Integration engine component
            code_executor: Code execution and testing component (optional)
            debug_analyzer: Debug analysis and code revision component (optional)
        """
        super().__init__(project_path, state_manager)
        self.planning_engine = planning_engine
        self.spec_generator = spec_generator
        self.code_generator = code_generator
        self.integration_engine = integration_engine
        self.code_executor = code_executor
        self.debug_analyzer = debug_analyzer
        self._logger = logging.getLogger(__name__)
    
    def execute_pipeline(self, objective: str) -> ProjectResult:
        """
        Execute the complete project generation pipeline.
        
        Args:
            objective: High-level project objective
            
        Returns:
            ProjectResult: Result of the pipeline execution
        """
        try:
            self._logger.info(f"Starting pipeline execution for objective: {objective}")
            
            # Phase 1: Planning
            result = self._execute_planning_phase(objective)
            if not result.success:
                return result
            
            # Phase 2: Specification
            result = self._execute_specification_phase()
            if not result.success:
                return result
            
            # Phase 3: Implementation
            result = self._execute_implementation_phase()
            if not result.success:
                return result
            
            # Phase 4: Testing (if code executor is available)
            if self.code_executor:
                result = self._execute_testing_phase()
                if not result.success:
                    return result
            
            # Phase 5: Integration
            result = self._execute_integration_phase()
            if not result.success:
                return result
            
            # Mark as completed
            self.state_manager.save_progress(ProjectPhase.COMPLETED, {
                'completion_time': datetime.now().isoformat()
            })
            
            return ProjectResult(
                success=True,
                message="Pipeline execution completed successfully",
                data={'phase': 'completed'}
            )
            
        except Exception as e:
            self._logger.error(f"Pipeline execution failed: {e}")
            return self._handle_pipeline_error(e)
    
    def resume_pipeline(self) -> ProjectResult:
        """
        Resume an interrupted project generation pipeline.
        
        Returns:
            ProjectResult: Result of the resumption
        """
        try:
            progress = self.state_manager.get_current_progress()
            if not progress:
                return ProjectResult(
                    success=False,
                    message="No progress found to resume",
                    errors=["No resumable state found"]
                )
            
            self._logger.info(f"Resuming pipeline from phase: {progress.current_phase}")
            
            # Validate project state before resuming
            validation = self.validate_project_state()
            if not validation.is_valid:
                return ProjectResult(
                    success=False,
                    message="Cannot resume: project state is invalid",
                    errors=validation.issues
                )
            
            # Resume from the appropriate phase
            if progress.current_phase == ProjectPhase.PLANNING:
                # Need to restart from planning - this shouldn't happen in normal flow
                return ProjectResult(
                    success=False,
                    message="Cannot resume from planning phase - need objective",
                    errors=["Planning phase requires objective parameter"]
                )
            
            elif progress.current_phase == ProjectPhase.SPECIFICATION:
                result = self._execute_specification_phase()
                if result.success:
                    return self._continue_pipeline_from_specification()
                return result
            
            elif progress.current_phase == ProjectPhase.IMPLEMENTATION:
                result = self._execute_implementation_phase()
                if result.success:
                    return self._continue_pipeline_from_implementation()
                return result
            
            elif progress.current_phase == ProjectPhase.TESTING:
                if self.code_executor:
                    result = self._execute_testing_phase()
                    if result.success:
                        return self._continue_pipeline_from_testing()
                    return result
                else:
                    # Skip testing if no executor available
                    return self._continue_pipeline_from_testing()
            
            elif progress.current_phase == ProjectPhase.INTEGRATION:
                result = self._execute_integration_phase()
                if result.success:
                    self.state_manager.save_progress(ProjectPhase.COMPLETED, {
                        'completion_time': datetime.now().isoformat()
                    })
                    return ProjectResult(
                        success=True,
                        message="Pipeline resumed and completed successfully",
                        data={'phase': 'completed'}
                    )
                return result
            
            elif progress.current_phase == ProjectPhase.COMPLETED:
                return ProjectResult(
                    success=True,
                    message="Project is already completed",
                    data={'phase': 'completed'}
                )
            
            else:
                return ProjectResult(
                    success=False,
                    message=f"Unknown phase: {progress.current_phase}",
                    errors=[f"Cannot resume from unknown phase: {progress.current_phase}"]
                )
            
        except Exception as e:
            self._logger.error(f"Pipeline resumption failed: {e}")
            return self._handle_pipeline_error(e)
    
    def _continue_pipeline_from_specification(self) -> ProjectResult:
        """Continue pipeline execution from specification phase."""
        # Execute implementation phase
        result = self._execute_implementation_phase()
        if not result.success:
            return result
        
        # Execute testing phase if available
        if self.code_executor:
            result = self._execute_testing_phase()
            if not result.success:
                return result
        
        # Execute integration phase
        result = self._execute_integration_phase()
        if not result.success:
            return result
        
        # Mark as completed
        self.state_manager.save_progress(ProjectPhase.COMPLETED, {
            'completion_time': datetime.now().isoformat()
        })
        
        return ProjectResult(
            success=True,
            message="Pipeline resumed and completed successfully",
            data={'phase': 'completed'}
        )
    
    def _continue_pipeline_from_implementation(self) -> ProjectResult:
        """Continue pipeline execution from implementation phase."""
        # Execute testing phase if available
        if self.code_executor:
            result = self._execute_testing_phase()
            if not result.success:
                return result
        
        # Execute integration phase
        result = self._execute_integration_phase()
        if not result.success:
            return result
        
        # Mark as completed
        self.state_manager.save_progress(ProjectPhase.COMPLETED, {
            'completion_time': datetime.now().isoformat()
        })
        
        return ProjectResult(
            success=True,
            message="Pipeline resumed and completed successfully",
            data={'phase': 'completed'}
        )
    
    def _continue_pipeline_from_testing(self) -> ProjectResult:
        """Continue pipeline execution from testing phase."""
        # Execute integration phase
        result = self._execute_integration_phase()
        if not result.success:
            return result
        
        # Mark as completed
        self.state_manager.save_progress(ProjectPhase.COMPLETED, {
            'completion_time': datetime.now().isoformat()
        })
        
        return ProjectResult(
            success=True,
            message="Pipeline resumed and completed successfully",
            data={'phase': 'completed'}
        )
    
    def execute_and_test_function(self, function_spec: FunctionSpec) -> ProjectResult:
        """
        Execute and test a specific function with debug analysis if it fails.
        
        Args:
            function_spec: Specification of the function to execute and test
            
        Returns:
            ProjectResult: Result of the execution and testing
        """
        if not self.code_executor:
            return ProjectResult(
                success=False,
                message="Code executor not available",
                errors=["Code executor is required for function execution"]
            )
        
        try:
            # Determine module path
            module_path = self._get_module_path_for_function(function_spec)
            
            # Execute the function
            execution_result = self.code_executor.execute_function(function_spec, module_path)
            
            if execution_result.success:
                return ProjectResult(
                    success=True,
                    message=f"Function '{function_spec.name}' executed successfully",
                    data={'execution_result': execution_result}
                )
            else:
                # If execution failed and we have debug analyzer, try to fix it
                if self.debug_analyzer and execution_result.error:
                    self._logger.info(f"Attempting to debug and fix function '{function_spec.name}'")
                    
                    fix_result = self.debug_analyzer.analyze_and_fix_function(
                        function_spec, module_path, execution_result.error
                    )
                    
                    return ProjectResult(
                        success=fix_result.get('success', False),
                        message=f"Function '{function_spec.name}' execution failed, debug analysis: {fix_result.get('final_status', 'unknown')}",
                        data={
                            'execution_result': execution_result,
                            'debug_result': fix_result
                        }
                    )
                else:
                    return ProjectResult(
                        success=False,
                        message=f"Function '{function_spec.name}' execution failed",
                        errors=[str(execution_result.error)] if execution_result.error else ["Unknown execution error"],
                        data={'execution_result': execution_result}
                    )
        
        except Exception as e:
            self._logger.error(f"Function execution and testing failed: {e}")
            return ProjectResult(
                success=False,
                message=f"Function execution and testing failed: {e}",
                errors=[str(e)]
            )
    
    def modify_project_plan(self, new_plan: ProjectPlan) -> ProjectResult:
        """
        Modify the project plan without losing completed work.
        
        Args:
            new_plan: The new project plan to apply
            
        Returns:
            ProjectResult: Result of the plan modification
        """
        try:
            # Load current progress
            current_progress = self.state_manager.get_current_progress()
            if not current_progress:
                # No existing progress, just save the new plan
                self.state_manager.save_project_plan(new_plan)
                return ProjectResult(
                    success=True,
                    message="Project plan updated successfully (no existing progress)",
                    data={'plan': new_plan}
                )
            
            # Load current plan for comparison
            current_plan = self.state_manager.load_project_plan()
            if not current_plan:
                return ProjectResult(
                    success=False,
                    message="Cannot modify plan: no existing plan found",
                    errors=["No existing plan to modify"]
                )
            
            # Analyze what has changed
            modification_analysis = self._analyze_plan_modifications(current_plan, new_plan, current_progress)
            
            # Update dependency graph if needed
            if modification_analysis['dependency_changes']:
                self._logger.info("Updating dependency graph due to plan changes")
                # Validate new dependency graph
                if new_plan.dependency_graph.has_cycles():
                    return ProjectResult(
                        success=False,
                        message="Cannot apply plan modifications: new dependency graph has cycles",
                        errors=["Circular dependencies detected in new plan"]
                    )
            
            # Save the new plan
            self.state_manager.save_project_plan(new_plan)
            
            # Update progress to reflect changes
            updated_progress = self._update_progress_for_plan_changes(current_progress, modification_analysis)
            self.state_manager.save_progress(updated_progress.current_phase, {
                'plan_modified': True,
                'modification_time': datetime.now().isoformat(),
                'preserved_functions': modification_analysis['preserved_functions'],
                'new_functions': modification_analysis['new_functions'],
                'removed_functions': modification_analysis['removed_functions']
            })
            
            return ProjectResult(
                success=True,
                message=f"Project plan updated successfully. Preserved {len(modification_analysis['preserved_functions'])} completed functions.",
                data={
                    'plan': new_plan,
                    'modification_analysis': modification_analysis,
                    'updated_progress': updated_progress
                }
            )
            
        except Exception as e:
            self._logger.error(f"Plan modification failed: {e}")
            return ProjectResult(
                success=False,
                message=f"Plan modification failed: {e}",
                errors=[str(e)]
            )
    
    def resume_from_last_completed_stage(self) -> ProjectResult:
        """
        Resume project from the last completed stage, skipping completed functions.
        
        Returns:
            ProjectResult: Result of the resumption
        """
        try:
            progress = self.state_manager.get_current_progress()
            if not progress:
                return ProjectResult(
                    success=False,
                    message="No progress found to resume from",
                    errors=["No resumable state found"]
                )
            
            # Determine the last completed stage
            last_completed_phase = self._get_last_completed_phase(progress)
            
            self._logger.info(f"Resuming from last completed stage: {last_completed_phase}")
            
            # Resume from the next phase after the last completed one
            next_phase = self._get_next_phase(last_completed_phase)
            if not next_phase:
                return ProjectResult(
                    success=True,
                    message="Project is already completed",
                    data={'phase': 'completed'}
                )
            
            # Update current phase to the next phase
            progress.current_phase = next_phase
            
            # Resume execution with function skipping
            return self._resume_with_function_skipping(progress)
            
        except Exception as e:
            self._logger.error(f"Resumption from last completed stage failed: {e}")
            return self._handle_pipeline_error(e)
    
    def skip_completed_functions(self, function_specs: List[FunctionSpec]) -> List[FunctionSpec]:
        """
        Filter out functions that have already been completed.
        
        Args:
            function_specs: List of function specifications to filter
            
        Returns:
            List of function specifications that still need to be implemented
        """
        try:
            progress = self.state_manager.get_current_progress()
            if not progress or not hasattr(progress, 'completed_functions'):
                # No progress or no completed functions info, return all functions
                return function_specs
            
            completed_function_names = getattr(progress, 'completed_functions', [])
            
            # Filter out completed functions
            remaining_functions = [
                func for func in function_specs 
                if func.name not in completed_function_names
            ]
            
            skipped_count = len(function_specs) - len(remaining_functions)
            if skipped_count > 0:
                self._logger.info(f"Skipping {skipped_count} already completed functions")
            
            return remaining_functions
            
        except Exception as e:
            self._logger.warning(f"Error filtering completed functions: {e}")
            # Return all functions if filtering fails
            return function_specs
    
    def _analyze_plan_modifications(self, old_plan: ProjectPlan, new_plan: ProjectPlan, 
                                  current_progress: ProjectProgress) -> Dict[str, Any]:
        """Analyze what has changed between old and new plans."""
        analysis = {
            'dependency_changes': False,
            'preserved_functions': [],
            'new_functions': [],
            'removed_functions': [],
            'modified_modules': [],
            'new_modules': [],
            'removed_modules': []
        }
        
        # Get function lists
        old_functions = {}
        for module in old_plan.modules:
            for func in module.functions:
                old_functions[func.name] = func
        
        new_functions = {}
        for module in new_plan.modules:
            for func in module.functions:
                new_functions[func.name] = func
        
        # Analyze function changes
        old_func_names = set(old_functions.keys())
        new_func_names = set(new_functions.keys())
        
        analysis['preserved_functions'] = list(old_func_names & new_func_names)
        analysis['new_functions'] = list(new_func_names - old_func_names)
        analysis['removed_functions'] = list(old_func_names - new_func_names)
        
        # Analyze module changes
        old_module_names = {module.name for module in old_plan.modules}
        new_module_names = {module.name for module in new_plan.modules}
        
        analysis['new_modules'] = list(new_module_names - old_module_names)
        analysis['removed_modules'] = list(old_module_names - new_module_names)
        analysis['modified_modules'] = list(old_module_names & new_module_names)
        
        # Check for dependency changes
        old_edges = set(old_plan.dependency_graph.edges)
        new_edges = set(new_plan.dependency_graph.edges)
        analysis['dependency_changes'] = old_edges != new_edges
        
        return analysis
    
    def _update_progress_for_plan_changes(self, current_progress: ProjectProgress, 
                                        modification_analysis: Dict[str, Any]) -> ProjectProgress:
        """Update progress information to reflect plan changes."""
        # Create a copy of current progress
        updated_progress = ProjectProgress(
            current_phase=current_progress.current_phase,
            completed_phases=current_progress.completed_phases.copy(),
            total_functions=current_progress.total_functions,
            implemented_functions=current_progress.implemented_functions,
            failed_functions=current_progress.failed_functions.copy() if current_progress.failed_functions else []
        )
        
        # Update function counts
        preserved_count = len(modification_analysis['preserved_functions'])
        new_count = len(modification_analysis['new_functions'])
        removed_count = len(modification_analysis['removed_functions'])
        
        # Adjust total functions
        updated_progress.total_functions = updated_progress.total_functions - removed_count + new_count
        
        # If we removed functions that were already implemented, adjust implemented count
        if hasattr(updated_progress, 'completed_functions'):
            completed_functions = getattr(updated_progress, 'completed_functions', [])
            # Remove any completed functions that are no longer in the plan
            updated_completed = [
                func for func in completed_functions 
                if func in modification_analysis['preserved_functions']
            ]
            setattr(updated_progress, 'completed_functions', updated_completed)
            updated_progress.implemented_functions = len(updated_completed)
        
        # Remove failed functions that are no longer in the plan
        if updated_progress.failed_functions:
            updated_progress.failed_functions = [
                func for func in updated_progress.failed_functions
                if func in modification_analysis['preserved_functions']
            ]
        
        return updated_progress
    
    def _get_last_completed_phase(self, progress: ProjectProgress) -> ProjectPhase:
        """Get the last completed phase from progress."""
        if not progress.completed_phases:
            return ProjectPhase.PLANNING
        
        # Return the last completed phase
        phase_order = [
            ProjectPhase.PLANNING,
            ProjectPhase.SPECIFICATION,
            ProjectPhase.IMPLEMENTATION,
            ProjectPhase.TESTING,
            ProjectPhase.INTEGRATION,
            ProjectPhase.COMPLETED
        ]
        
        last_completed = ProjectPhase.PLANNING
        for phase in phase_order:
            if phase in progress.completed_phases:
                last_completed = phase
            else:
                break
        
        return last_completed
    
    def _get_next_phase(self, current_phase: ProjectPhase) -> Optional[ProjectPhase]:
        """Get the next phase after the current one."""
        phase_order = [
            ProjectPhase.PLANNING,
            ProjectPhase.SPECIFICATION,
            ProjectPhase.IMPLEMENTATION,
            ProjectPhase.TESTING,
            ProjectPhase.INTEGRATION,
            ProjectPhase.COMPLETED
        ]
        
        try:
            current_index = phase_order.index(current_phase)
            if current_index < len(phase_order) - 1:
                return phase_order[current_index + 1]
            return None
        except ValueError:
            return None
    
    def _resume_with_function_skipping(self, progress: ProjectProgress) -> ProjectResult:
        """Resume execution with function skipping enabled."""
        # This is similar to resume_pipeline but with function skipping
        if progress.current_phase == ProjectPhase.SPECIFICATION:
            result = self._execute_specification_phase_with_skipping()
            if result.success:
                return self._continue_pipeline_from_specification()
            return result
        
        elif progress.current_phase == ProjectPhase.IMPLEMENTATION:
            result = self._execute_implementation_phase_with_skipping()
            if result.success:
                return self._continue_pipeline_from_implementation()
            return result
        
        elif progress.current_phase == ProjectPhase.TESTING:
            if self.code_executor:
                result = self._execute_testing_phase_with_skipping()
                if result.success:
                    return self._continue_pipeline_from_testing()
                return result
            else:
                return self._continue_pipeline_from_testing()
        
        elif progress.current_phase == ProjectPhase.INTEGRATION:
            result = self._execute_integration_phase()
            if result.success:
                self.state_manager.save_progress(ProjectPhase.COMPLETED, {
                    'completion_time': datetime.now().isoformat()
                })
                return ProjectResult(
                    success=True,
                    message="Pipeline resumed and completed successfully",
                    data={'phase': 'completed'}
                )
            return result
        
        elif progress.current_phase == ProjectPhase.COMPLETED:
            return ProjectResult(
                success=True,
                message="Project is already completed",
                data={'phase': 'completed'}
            )
        
        else:
            return ProjectResult(
                success=False,
                message=f"Cannot resume from phase: {progress.current_phase}",
                errors=[f"Unsupported resumption phase: {progress.current_phase}"]
            )
    
    def _execute_specification_phase_with_skipping(self) -> ProjectResult:
        """Execute specification phase with function skipping."""
        # This is the same as regular specification phase since specs are always regenerated
        return self._execute_specification_phase()
    
    def _execute_implementation_phase_with_skipping(self) -> ProjectResult:
        """Execute implementation phase with function skipping."""
        try:
            self._logger.info("Phase 3: Implementation (with function skipping)")
            
            # Load the project plan
            plan = self.state_manager.load_project_plan()
            if not plan:
                raise RuntimeError("No project plan found for implementation")
            
            # Extract all functions from modules
            all_functions = []
            for module in plan.modules:
                all_functions.extend(module.functions)
            
            # Skip completed functions
            remaining_functions = self.skip_completed_functions(all_functions)
            
            if not remaining_functions:
                self._logger.info("All functions already implemented, skipping implementation phase")
                return ProjectResult(
                    success=True,
                    message="Implementation phase skipped (all functions already completed)",
                    data={'phase': 'implementation', 'skipped': True}
                )
            
            # Create specification set for remaining functions
            from ..core.models import SpecificationSet
            spec_set = SpecificationSet(functions=remaining_functions)
            
            # Implement remaining functions
            impl_result = self.code_generator.implement_all(spec_set)
            
            # Save progress
            self.state_manager.save_progress(ProjectPhase.IMPLEMENTATION, {
                'total_implementations': len(impl_result.implemented_functions),
                'failed_implementations': len(impl_result.failed_functions),
                'skipped_functions': len(all_functions) - len(remaining_functions),
                'implemented_at': datetime.now().isoformat()
            })
            
            return ProjectResult(
                success=impl_result.success,
                message=f"Implementation phase completed (skipped {len(all_functions) - len(remaining_functions)} functions)" + 
                       (" with some failures" if impl_result.failed_functions else " successfully"),
                data={'phase': 'implementation', 'impl_result': impl_result}
            )
            
        except Exception as e:
            self._logger.error(f"Implementation phase with skipping failed: {e}")
            return ProjectResult(
                success=False,
                message=f"Implementation phase failed: {e}",
                errors=[str(e)]
            )
    
    def _execute_testing_phase_with_skipping(self) -> ProjectResult:
        """Execute testing phase with function skipping."""
        try:
            self._logger.info("Phase 4: Testing and Verification (with function skipping)")
            
            if not self.code_executor:
                return ProjectResult(
                    success=True,
                    message="Testing phase skipped (no code executor available)",
                    data={'phase': 'testing', 'skipped': True}
                )
            
            # Load the project plan
            plan = self.state_manager.load_project_plan()
            if not plan:
                raise RuntimeError("No project plan found for testing")
            
            # Extract all functions from modules
            all_functions = []
            for module in plan.modules:
                all_functions.extend(module.functions)
            
            # Skip completed functions for testing
            remaining_functions = self.skip_completed_functions(all_functions)
            
            if not remaining_functions:
                self._logger.info("All functions already tested, skipping testing phase")
                return ProjectResult(
                    success=True,
                    message="Testing phase skipped (all functions already tested)",
                    data={'phase': 'testing', 'skipped': True}
                )
            
            # Generate verification report for remaining functions
            verification_report = self.code_executor.generate_verification_report(remaining_functions)
            
            # Handle failed verifications with debug analysis if available
            failed_functions = [f for f in verification_report['function_results'] if not f['verified']]
            
            if failed_functions and self.debug_analyzer:
                self._logger.info(f"Attempting to debug and fix {len(failed_functions)} failed functions")
                debug_results = self._debug_and_fix_failed_functions(failed_functions, remaining_functions)
                verification_report['debug_results'] = debug_results
            
            # Save progress
            self.state_manager.save_progress(ProjectPhase.TESTING, {
                'total_functions_tested': verification_report['total_functions'],
                'verified_functions': verification_report['verified_functions'],
                'failed_functions': verification_report['failed_functions'],
                'skipped_functions': len(all_functions) - len(remaining_functions),
                'success_rate': verification_report['summary']['success_rate'],
                'tested_at': datetime.now().isoformat()
            })
            
            # Consider testing successful if most functions pass or if we have debug fixes
            success_threshold = 0.8  # 80% success rate
            is_successful = (
                verification_report['summary']['success_rate'] >= success_threshold * 100 or
                (failed_functions and self.debug_analyzer and 
                 verification_report.get('debug_results', {}).get('fixed_functions', 0) > 0)
            )
            
            return ProjectResult(
                success=is_successful,
                message=f"Testing phase completed with {verification_report['summary']['success_rate']:.1f}% success rate (skipped {len(all_functions) - len(remaining_functions)} functions)",
                data={'phase': 'testing', 'verification_report': verification_report}
            )
            
        except Exception as e:
            self._logger.error(f"Testing phase with skipping failed: {e}")
            return ProjectResult(
                success=False,
                message=f"Testing phase failed: {e}",
                errors=[str(e)]
            )

    def debug_and_revise_function(self, function_spec: FunctionSpec, error: Exception) -> ProjectResult:
        """
        Debug and revise a function that has failed.
        
        Args:
            function_spec: Specification of the function to debug
            error: The error that occurred
            
        Returns:
            ProjectResult: Result of the debug and revision process
        """
        if not self.debug_analyzer:
            return ProjectResult(
                success=False,
                message="Debug analyzer not available",
                errors=["Debug analyzer is required for function debugging"]
            )
        
        try:
            # Determine module path
            module_path = self._get_module_path_for_function(function_spec)
            
            # Perform debug and revision loop
            revisions = self.debug_analyzer.debug_and_revise_loop(
                error, function_spec, module_path, max_iterations=3
            )
            
            # Check if any revision was successful
            successful_revisions = [rev for rev in revisions if rev.applied]
            
            if successful_revisions:
                return ProjectResult(
                    success=True,
                    message=f"Function '{function_spec.name}' successfully debugged and revised",
                    data={
                        'revisions': revisions,
                        'successful_revisions': len(successful_revisions),
                        'total_attempts': len(revisions)
                    }
                )
            else:
                return ProjectResult(
                    success=False,
                    message=f"Failed to fix function '{function_spec.name}' after {len(revisions)} attempts",
                    errors=["All revision attempts failed"],
                    data={
                        'revisions': revisions,
                        'total_attempts': len(revisions)
                    }
                )
        
        except Exception as e:
            self._logger.error(f"Debug and revision failed: {e}")
            return ProjectResult(
                success=False,
                message=f"Debug and revision failed: {e}",
                errors=[str(e)]
            )
    
    def get_current_phase(self) -> ProjectPhase:
        """
        Get the current phase of project generation.
        
        Returns:
            ProjectPhase: Current phase
        """
        progress = self.state_manager.get_current_progress()
        return progress.current_phase if progress else ProjectPhase.PLANNING
    
    def validate_project_state(self) -> ValidationResult:
        """
        Validate the current project state for consistency.
        
        Returns:
            ValidationResult: Validation result
        """
        try:
            issues = []
            warnings = []
            
            # Check if project plan exists
            plan = self.state_manager.load_project_plan()
            if not plan:
                issues.append("No project plan found")
            else:
                try:
                    plan.validate()
                except Exception as e:
                    issues.append(f"Project plan validation failed: {e}")
            
            # Check progress consistency
            progress = self.state_manager.get_current_progress()
            if progress:
                try:
                    progress.validate()
                except Exception as e:
                    issues.append(f"Progress validation failed: {e}")
            
            return ValidationResult(
                is_valid=len(issues) == 0,
                issues=issues,
                warnings=warnings
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                issues=[f"Validation error: {e}"],
                warnings=[]
            )
    
    def _execute_planning_phase(self, objective: str) -> ProjectResult:
        """Execute the planning phase."""
        try:
            self._logger.info("Phase 1: Planning")
            plan = self.planning_engine.generate_plan(objective)
            self.state_manager.save_project_plan(plan)
            self.state_manager.save_progress(ProjectPhase.PLANNING, {
                'total_functions': sum(len(module.functions) for module in plan.modules),
                'total_modules': len(plan.modules)
            })
            
            return ProjectResult(
                success=True,
                message="Planning phase completed successfully",
                data={'phase': 'planning', 'plan': plan}
            )
            
        except Exception as e:
            self._logger.error(f"Planning phase failed: {e}")
            return ProjectResult(
                success=False,
                message=f"Planning phase failed: {e}",
                errors=[str(e)]
            )
    
    def _execute_specification_phase(self) -> ProjectResult:
        """Execute the specification generation phase."""
        try:
            self._logger.info("Phase 2: Specification Generation")
            
            # Load the project plan
            plan = self.state_manager.load_project_plan()
            if not plan:
                raise RuntimeError("No project plan found for specification generation")
            
            # Extract all functions from modules
            all_functions = []
            for module in plan.modules:
                all_functions.extend(module.functions)
            
            # Generate specifications
            spec_set = self.spec_generator.generate_specifications(all_functions)
            
            # Save progress
            self.state_manager.save_progress(ProjectPhase.SPECIFICATION, {
                'total_specifications': len(spec_set.functions),
                'generated_at': datetime.now().isoformat()
            })
            
            return ProjectResult(
                success=True,
                message="Specification phase completed successfully",
                data={'phase': 'specification', 'spec_set': spec_set}
            )
            
        except Exception as e:
            self._logger.error(f"Specification phase failed: {e}")
            return ProjectResult(
                success=False,
                message=f"Specification phase failed: {e}",
                errors=[str(e)]
            )
    
    def _execute_implementation_phase(self) -> ProjectResult:
        """Execute the implementation phase."""
        try:
            self._logger.info("Phase 3: Implementation")
            
            # Load the project plan
            plan = self.state_manager.load_project_plan()
            if not plan:
                raise RuntimeError("No project plan found for implementation")
            
            # Extract all functions from modules
            all_functions = []
            for module in plan.modules:
                all_functions.extend(module.functions)
            
            # Create specification set for implementation
            from ..core.models import SpecificationSet
            spec_set = SpecificationSet(functions=all_functions)
            
            # Implement all functions
            impl_result = self.code_generator.implement_all(spec_set)
            
            # Save progress
            self.state_manager.save_progress(ProjectPhase.IMPLEMENTATION, {
                'total_implementations': len(impl_result.implemented_functions),
                'failed_implementations': len(impl_result.failed_functions),
                'implemented_at': datetime.now().isoformat()
            })
            
            return ProjectResult(
                success=impl_result.success,
                message="Implementation phase completed" + (" with some failures" if impl_result.failed_functions else " successfully"),
                data={'phase': 'implementation', 'impl_result': impl_result}
            )
            
        except Exception as e:
            self._logger.error(f"Implementation phase failed: {e}")
            return ProjectResult(
                success=False,
                message=f"Implementation phase failed: {e}",
                errors=[str(e)]
            )
    
    def _execute_testing_phase(self) -> ProjectResult:
        """Execute the testing and verification phase."""
        try:
            self._logger.info("Phase 4: Testing and Verification")
            
            if not self.code_executor:
                return ProjectResult(
                    success=True,
                    message="Testing phase skipped (no code executor available)",
                    data={'phase': 'testing', 'skipped': True}
                )
            
            # Load the project plan
            plan = self.state_manager.load_project_plan()
            if not plan:
                raise RuntimeError("No project plan found for testing")
            
            # Extract all functions from modules
            all_functions = []
            for module in plan.modules:
                all_functions.extend(module.functions)
            
            # Generate verification report
            verification_report = self.code_executor.generate_verification_report(all_functions)
            
            # Handle failed verifications with debug analysis if available
            failed_functions = [f for f in verification_report['function_results'] if not f['verified']]
            
            if failed_functions and self.debug_analyzer:
                self._logger.info(f"Attempting to debug and fix {len(failed_functions)} failed functions")
                debug_results = self._debug_and_fix_failed_functions(failed_functions, all_functions)
                verification_report['debug_results'] = debug_results
            
            # Save progress
            self.state_manager.save_progress(ProjectPhase.TESTING, {
                'total_functions_tested': verification_report['total_functions'],
                'verified_functions': verification_report['verified_functions'],
                'failed_functions': verification_report['failed_functions'],
                'success_rate': verification_report['summary']['success_rate'],
                'tested_at': datetime.now().isoformat()
            })
            
            # Consider testing successful if most functions pass or if we have debug fixes
            success_threshold = 0.8  # 80% success rate
            is_successful = (
                verification_report['summary']['success_rate'] >= success_threshold * 100 or
                (failed_functions and self.debug_analyzer and 
                 verification_report.get('debug_results', {}).get('fixed_functions', 0) > 0)
            )
            
            return ProjectResult(
                success=is_successful,
                message=f"Testing phase completed with {verification_report['summary']['success_rate']:.1f}% success rate",
                data={'phase': 'testing', 'verification_report': verification_report}
            )
            
        except Exception as e:
            self._logger.error(f"Testing phase failed: {e}")
            return ProjectResult(
                success=False,
                message=f"Testing phase failed: {e}",
                errors=[str(e)]
            )
    
    def _execute_integration_phase(self) -> ProjectResult:
        """Execute the integration phase."""
        try:
            self._logger.info("Phase 5: Integration")
            
            # Load the project plan
            plan = self.state_manager.load_project_plan()
            if not plan:
                raise RuntimeError("No project plan found for integration")
            
            # Integrate modules
            integration_result = self.integration_engine.integrate_modules(plan.modules)
            
            # Save progress
            self.state_manager.save_progress(ProjectPhase.INTEGRATION, {
                'integrated_modules': len(plan.modules),
                'integration_success': integration_result.success,
                'integrated_at': datetime.now().isoformat()
            })
            
            return ProjectResult(
                success=integration_result.success,
                message="Integration phase completed" + (" successfully" if integration_result.success else " with errors"),
                data={'phase': 'integration', 'integration_result': integration_result}
            )
            
        except Exception as e:
            self._logger.error(f"Integration phase failed: {e}")
            return ProjectResult(
                success=False,
                message=f"Integration phase failed: {e}",
                errors=[str(e)]
            )
    
    def _debug_and_fix_failed_functions(self, failed_functions: List[Dict], all_functions: List[FunctionSpec]) -> Dict[str, Any]:
        """Debug and attempt to fix failed functions."""
        if not self.debug_analyzer:
            return {'error': 'No debug analyzer available'}
        
        debug_results = {
            'attempted_fixes': 0,
            'successful_fixes': 0,
            'fixed_functions': 0,
            'fix_details': []
        }
        
        # Create a mapping of function names to specs
        function_spec_map = {func.name: func for func in all_functions}
        
        for failed_func in failed_functions:
            func_name = failed_func['name']
            if func_name not in function_spec_map:
                continue
            
            function_spec = function_spec_map[func_name]
            
            try:
                # Determine module path
                module_path = self._get_module_path_for_function(function_spec)
                
                # Create a mock error for debugging (in real scenario, we'd have the actual error)
                mock_error = RuntimeError(f"Function verification failed: {failed_func.get('errors', ['Unknown error'])}")
                
                # Attempt to analyze and fix
                fix_result = self.debug_analyzer.analyze_and_fix_function(
                    function_spec, module_path, mock_error
                )
                
                debug_results['attempted_fixes'] += 1
                
                if fix_result.get('success', False):
                    debug_results['successful_fixes'] += 1
                    if fix_result.get('final_status') == 'fixed':
                        debug_results['fixed_functions'] += 1
                
                debug_results['fix_details'].append({
                    'function_name': func_name,
                    'status': fix_result.get('final_status', 'unknown'),
                    'revisions': len(fix_result.get('revisions', [])),
                    'success': fix_result.get('success', False)
                })
                
            except Exception as e:
                self._logger.warning(f"Failed to debug function {func_name}: {e}")
                debug_results['fix_details'].append({
                    'function_name': func_name,
                    'status': 'debug_failed',
                    'error': str(e),
                    'success': False
                })
        
        return debug_results
    
    def _get_module_path_for_function(self, function_spec: FunctionSpec) -> str:
        """Get the file path for a function's module."""
        # Convert module name to file path
        module_parts = function_spec.module.split('.')
        module_path = Path(self.project_path) / '/'.join(module_parts[:-1]) / f"{module_parts[-1]}.py"
        return str(module_path)
    
    def _handle_pipeline_error(self, error: Exception) -> ProjectResult:
        """Handle pipeline errors with enhanced error recovery."""
        error_message = str(error)
        
        # If we have debug analyzer, try to get more context
        if self.debug_analyzer:
            try:
                # Analyze the error for better context
                traceback_analysis = self.debug_analyzer.analyze_traceback(error)
                error_message = f"{error_message}\nRoot cause: {traceback_analysis.root_cause}"
                
                # Add suggested fixes to the error result
                suggested_fixes = traceback_analysis.suggested_fixes
                return ProjectResult(
                    success=False,
                    message=f"Pipeline execution failed: {error_message}",
                    errors=[str(error)],
                    data={
                        'debug_info': {
                            'root_cause': traceback_analysis.root_cause,
                            'suggested_fixes': suggested_fixes,
                            'error_type': traceback_analysis.error_type
                        }
                    }
                )
            except Exception:
                pass  # Fall back to basic error handling
        
        return ProjectResult(
            success=False,
            message=f"Pipeline execution failed: {error_message}",
            errors=[str(error)]
        )