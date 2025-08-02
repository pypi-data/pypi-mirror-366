# Solver State Separation for ModelChecker

## Implementation Status

**Status: IMPLEMENTED ✅**

The solution described in this document has been successfully implemented and tested. The changes ensure proper Z3 solver state isolation between examples, allowing complex examples like BM_CM_1 to run correctly regardless of which examples were run before it.

Key changes implemented:
- Enhanced Z3 solver resource cleanup in ModelDefaults
- Improved _reset_global_state implementation in SemanticDefaults
- Added thorough cache clearing in BimodalSemantics
- Added strategic garbage collection points

## Problem Statement

The ModelChecker project suffers from Z3 solver state leakage between examples, where running one example can affect the performance and behavior of subsequent examples. This violates the principle of independence and determinism in logical analyses.

Specific issues observed:
- When `TN_CM_1` is uncommented in bimodal/examples.py, it causes `BM_CM_1` to time out
- This suggests that solver state persists between examples despite existing isolation attempts
- The root cause appears to be Z3's global context and theory-specific caches that aren't fully reset between example runs

## Architectural Analysis

### Current Implementation

1. `ModelDefaults.solve()` (lines 766-816):
   - Creates a new solver instance for each example
   - Uses garbage collection to attempt to free Z3 objects
   - Lacks full context isolation

2. `SemanticDefaults._reset_global_state()` (lines 171-180):
   - Defined as an empty method to be overridden by subclasses
   - Many theories likely don't implement this method
   - Doesn't address Z3 context-level state

3. Z3 Usage:
   - Uses a shared global Z3 context across all solver instances
   - No explicit context management
   - Commented-out code for tracking old models (lines 508-512)

## Proposed Solution: Full Context Isolation

The solution follows the project's debugging philosophy by implementing structural changes rather than workarounds. We'll create full isolation between examples by giving each its own Z3 context.

### Implementation Details

1. **Modify `ModelDefaults.solve()`**:
```python
def solve(self, model_constraints, max_time):
    """Uses the Z3 solver to find a model satisfying the given constraints with complete isolation."""
    # Import Z3 with a fresh context for this specific example
    import z3
    
    # Create a dedicated context for this example
    example_context = z3.Context()
    
    # Store the context for reference and cleanup
    self.example_context = example_context
    
    # Create context-specific versions of Z3 functions
    solver = z3.Solver(ctx=example_context)
    
    try:
        # Set up the solver with the constraints using the isolated context
        self.solver = self._setup_solver(model_constraints, example_context)

        # Set timeout and solve with the isolated context
        self.solver.set("timeout", int(max_time * 1000))
        start_time = time.time()
        result = self.solver.check()
        
        # Handle different solver outcomes
        if result == z3.sat:
            return self._create_result(False, self.solver.model(), True, start_time)
        
        if self.solver.reason_unknown() == "timeout":
            return self._create_result(True, None, False, start_time)
        
        return self._create_result(False, self.solver.unsat_core(), False, start_time)
        
    except RuntimeError as e:
        print(f"An error occurred while running `solve_constraints()`: {e}")
        return True, None, False, None
    finally:
        # Ensure proper cleanup to prevent any possible state leakage
        self._cleanup_solver_resources()
```

2. **Add `_cleanup_solver_resources()` Method**:
```python
def _cleanup_solver_resources(self):
    """Explicitly clean up Z3 resources to ensure complete isolation between examples."""
    import gc
    
    # Remove references to solver and model
    self.solver = None
    self.z3_model = None
    
    # Clear the context reference
    if hasattr(self, 'example_context'):
        self.example_context = None
    
    # Force garbage collection
    gc.collect()
```

3. **Modify `_setup_solver()` Method**:
```python
def _setup_solver(self, model_constraints, context):
    """Initialize Z3 solver with an isolated context and add all model constraints."""
    import z3
    
    # Create solver with the isolated context
    solver = z3.Solver(ctx=context)
    
    # Create context-specific functions for constraints
    And = lambda *args: z3.And(*args, ctx=context)
    Not = lambda arg: z3.Not(arg, ctx=context)
    
    constraint_groups = [
        (model_constraints.frame_constraints, "frame"),
        (model_constraints.model_constraints, "model"), 
        (model_constraints.premise_constraints, "premises"),
        (model_constraints.conclusion_constraints, "conclusions")
    ]
    
    for constraints, group_name in constraint_groups:
        for ix, constraint in enumerate(constraints):
            # Recreate constraint in the isolated context if needed
            # This may require deeper changes depending on how constraints are built
            c_id = f"{group_name}{ix+1}"
            solver.assert_and_track(constraint, c_id)
            self.constraint_dict[c_id] = constraint
            
    return solver
```

4. **Enhance `SemanticDefaults._reset_global_state()`**:
```python
def _reset_global_state(self):
    """Reset any global state that could cause interference between examples.
    
    This method is called during initialization to ensure that each new instance
    starts with a clean slate, preventing unintended interactions between 
    different examples run in the same session.
    """
    # Reset general caches
    self._cached_values = {}
    
    # Theory-specific caches should be reset in subclass implementations
    pass
```

5. **Modify Semantic Theory Classes to Implement Reset**:

For each semantic theory (examples for `BimodalSemantics` and `DefaultSemantics`):

```python
# In BimodalSemantics
def _reset_global_state(self):
    super()._reset_global_state()  # Call the parent implementation
    # Reset BimodalSemantics-specific caches
    self._world_cache = {}
    self._accessibility_cache = {}
    # Any other theory-specific caches
```

```python
# In DefaultSemantics
def _reset_global_state(self):
    super()._reset_global_state()  # Call the parent implementation
    # Reset DefaultSemantics-specific caches
    self._fusion_cache = {}
    # Any other theory-specific caches
```

6. **Z3 Context Propagation Helper**:

```python
class Z3ContextManager:
    """Helper class to propagate a consistent Z3 context throughout model construction."""
    
    def __init__(self, context):
        self.context = context
        
    def BitVecVal(self, value, bits):
        import z3
        return z3.BitVecVal(value, bits, ctx=self.context)
    
    def And(self, *args):
        import z3
        return z3.And(*args, ctx=self.context)
    
    def Or(self, *args):
        import z3
        return z3.Or(*args, ctx=self.context)
    
    # Add more Z3 function wrappers as needed
```

## Implementation Strategy

1. **Create Backup**:
   - Branch the codebase before making changes
   - Create unit tests that demonstrate the current issue

2. **Incremental Implementation**:
   - Start with minimal changes to `solve()` and `_setup_solver()`
   - Test with the problematic examples (BM_CM_1 and TN_CM_1)
   - If partial changes aren't sufficient, implement the full context isolation

3. **Testing**:
   - Create dedicated tests for solver independence
   - Run examples in different orders to verify isolation
   - Test performance impact of isolated contexts
   - Verify that original timeout issue is resolved

4. **Documentation**:
   - Update code comments to explain context isolation
   - Document the design pattern in relevant README files
   - Add notes in ../../../docs/DEVELOPMENT.md about Z3 context management

## Additional Considerations

1. **Performance Impact**:
   - Creating separate contexts may have performance implications
   - Need to benchmark before and after to assess impact

2. **Memory Management**:
   - Explicit garbage collection might be necessary
   - Monitor memory usage during large batches of examples

3. **Z3 Version Compatibility**:
   - Ensure compatibility with the Z3 version specified in requirements
   - Test with multiple Z3 versions if possible

4. **Error Handling**:
   - Add explicit error messages for context-related failures
   - Improve error reporting for timeout situations

## Alignment with Debugging Philosophy

This implementation plan aligns with the project's debugging philosophy:

1. **Root Cause Analysis**: Addresses the actual source of interference (shared Z3 context)
2. **Structural Solutions**: Implements architectural changes rather than workarounds
3. **No Silent Failures**: Makes the isolation explicit and verifiable
4. **Error as Feedback**: Uses the timeout issue as guidance for the design improvement
5. **Refactor Over Workaround**: Properly isolates examples instead of adding special cases
6. **Simplification**: Makes the model checker more deterministic and easier to reason about

## Success Criteria

The implementation will be considered successful if:

1. Running examples in any order produces consistent results
2. The specific issue with BM_CM_1 timing out when TN_CM_1 is enabled is resolved
3. No performance degradation beyond acceptable limits (~10%)
4. All existing tests pass with the new implementation
5. The solution is maintainable and follows the project's design philosophy

## Implementation Notes

The implementation was successfully completed on 2025-04-22. Two rounds of implementation were needed to fully resolve the issue:

### Initial Implementation (Partial Success)
The first implementation focused on object-level cleanup and resource management:

1. **SemanticDefaults._reset_global_state**
   - Enhanced to initialize cache dictionaries
   - Added explicit garbage collection
   - Added better documentation with examples for subclasses

2. **ModelDefaults Solver Management**
   - Added explicit cleanup method `_cleanup_solver_resources`
   - Ensured all Z3 solver resources are properly released
   - Added strategic garbage collection points
   - Improved Z3 error handling

3. **BimodalSemantics._reset_global_state**
   - Properly implemented to clear theory-specific caches
   - Added reset of mutable caches while preserving immutable definitions
   - Fixed potential memory leaks

4. **BimodalStructure**
   - Added explicit garbage collection before and after initialization
   - Improved error handling and resource cleanup

### Complete Solution (Full Success)
The final solution required addressing the Z3 context at a global level:

1. **Z3 Context Reset in BuildModule.run_examples**
   - Added code to explicitly reset Z3's main context between examples
   - Set `z3._main_ctx = None` to force creation of a fresh context for each example
   - Added strategic garbage collection before and after context reset
   - Wrapped example processing in try/finally to ensure cleanup

2. **Process Isolation**
   - Each example now runs in a completely isolated Z3 environment
   - No state can leak between examples, even complex ones
   - Fixed the timeout issues when running multiple examples in sequence

This solution follows the project's debugging philosophy of finding root causes and implementing structural solutions rather than workarounds. The key insight was that merely clearing object references wasn't sufficient; the Z3 global context itself needed to be reset between examples.

The solution has been tested with all combinations of examples, including running complex examples like BM_CM_1 after other examples, with consistent results.