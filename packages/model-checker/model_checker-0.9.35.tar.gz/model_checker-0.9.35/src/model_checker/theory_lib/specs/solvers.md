# Z3 Solver State Management and Isolation in ModelChecker

## Problem Analysis

When running bimodal examples separately vs. sequentially, there are inconsistent results:
- Running `BM_CM_3` and `BM_CM_4` one after the other successfully finds countermodels for both
- Running `BM_CM_4` alone results in "no countermodel" (UNSAT)
- Running `BM_CM_4` followed by `BM_CM_3` results in "no countermodel" for both

This inconsistency demonstrates solver state leakage between examples, violating the "Deterministic Behavior" principle from our design philosophy. The Z3 solver state from one example is influencing subsequent examples, causing unpredictable results depending on execution order.

## Current Implementation Analysis

### Z3 Solver Context Management

1. **Where Solvers Are Created**:
   - `ModelDefaults.solve()` in `model.py` (line 842-896) is the primary method that creates Z3 solver instances
   - Each call to `solve()` creates a new `z3.Solver()` instance
   - However, these solvers share the same global Z3 context (`z3._main_ctx`)

2. **State Cleanup Mechanisms**:
   - `_reset_global_state()` in `SemanticDefaults` (line 170-202) provides a base implementation for cleanup
   - `_reset_global_state()` in `BimodalSemantics` (line 74-114) extends this with theory-specific cleanup
   - `_cleanup_solver_resources()` in `ModelDefaults` (line 801-842) attempts to clean solver resources
   - Garbage collection is called at various points to release Z3 resources

3. **Current Missing Elements**:
   - The critical problem is that while we create new solver instances, they share the same global Z3 context
   - Only `BuildModule.run_examples()` (line 610-611) explicitly resets the global context (`z3._main_ctx = None`)
   - This reset is not applied consistently across all entry points

### Root Cause Identification

In accordance with our "Root Cause Analysis" philosophy, we've identified the primary issue:

Z3 maintains a global context (`z3._main_ctx`) that persists between solver instances. This context:
1. Accumulates solver heuristics and learning from previous examples
2. Influences solving strategies and outcomes of subsequent examples
3. Remains in memory until explicitly reset

This violates our "Deterministic Behavior" principle, as the outcome of an example should not depend on which examples were run before it.

## Implementation Plan

Following the "Structural Solutions" philosophy, we need to implement a comprehensive fix that addresses the root cause rather than adding workarounds:

### 1. Create a Dedicated Z3 Context Manager

Create a new utility class in `model_checker/utils.py` to consistently manage Z3 context resets:

```python
class Z3ContextManager:
    """Provides centralized management of Z3 solver contexts.
    
    This class ensures proper isolation between different solver instances by explicitly
    resetting the Z3 global context when needed. It implements a fail-fast approach
    and enforces deterministic behavior by preventing state leakage between examples.
    """
    
    @staticmethod
    def reset_context():
        """Explicitly reset the Z3 global context.
        
        This method forces Z3 to create a fresh context for the next solver instance,
        ensuring complete isolation between different examples.
        """
        import z3
        if hasattr(z3, '_main_ctx'):
            z3._main_ctx = None
            
        # Force garbage collection to ensure clean state
        import gc
        gc.collect()
```

### 2. Modify ModelDefaults.solve() to Use the Context Manager

Update `ModelDefaults.solve()` in `model.py` to explicitly reset the Z3 context before creating a new solver:

```python
def solve(self, model_constraints, max_time):
    """Uses the Z3 solver to find a model satisfying the given constraints.
    
    Creates a completely fresh Z3 context for each example to ensure
    proper isolation and deterministic behavior regardless of which
    examples were run previously.
    
    Args:
        model_constraints (ModelConstraints): The logical constraints to solve
        max_time (int): Maximum solving time in milliseconds (0 for unlimited)
        
    Returns:
        tuple: Contains result information (timeout flag, model/core, satisfiability)
    """
    from model_checker.utils import Z3ContextManager
    
    # Reset Z3 context to ensure clean state
    Z3ContextManager.reset_context()
    
    # Import z3 after context reset to ensure it uses the fresh context
    import z3
    
    # Create a new solver with the fresh context
    self.solver = z3.Solver()
    
    try:
        # Set up the solver with the constraints
        self.solver = self._setup_solver(model_constraints)

        # Set timeout and solve
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
        print(f"An error occurred during solving: {e}")
        return True, None, False, None
    finally:
        # Ensure proper cleanup to prevent any possible state leakage
        self._cleanup_solver_resources()
```

### 3. Enhance SemanticDefaults._reset_global_state()

Improve the base implementation in `SemanticDefaults` to include explicit instructions for subclasses:

```python
def _reset_global_state(self):
    """Reset any global state that could cause interference between examples.
    
    Following the fail-fast philosophy, this method explicitly resets all cached
    state that could lead to non-deterministic behavior between examples.
    
    Subclasses MUST override this method and call super()._reset_global_state()
    to ensure proper cleanup of both shared and theory-specific resources.
    
    Example for subclasses:
    
    def _reset_global_state(self):
        # Always call parent implementation first
        super()._reset_global_state()
        
        # Reset theory-specific caches
        self._theory_specific_cache = {}
        
        # Clear any references to model structures
        if hasattr(self, 'model_structure'):
            delattr(self, 'model_structure')
            
        # Reset mutable data structures but preserve immutable definitions
        self.data_cache = {}
    """
    # Reset general caches
    self._cached_values = {}
    
    # Force garbage collection to release any lingering Z3 objects
    import gc
    gc.collect()
```

### 4. Apply Consistent Context Reset in BuildModule

Ensure the context reset is applied at all entry points for example processing:

```python
def process_example(self, example_name, example_case, theory_name, semantic_theory):
    """Process a single model checking example with a fresh Z3 context.
    
    Args:
        example_name (str): Name of the example being processed
        example_case (list): The example case containing [premises, conclusions, settings]
        theory_name (str): Name of the semantic theory being used
        semantic_theory (dict): Dictionary containing the semantic theory implementation
        
    Returns:
        BuildExample: The example after processing
    """
    from model_checker.utils import Z3ContextManager
    
    # Always reset Z3 context at the start of processing a new example
    Z3ContextManager.reset_context()
    
    # Disable debug logs for cleaner output
    import logging
    logging.getLogger().setLevel(logging.ERROR)
    
    try:
        # Create and solve the example with a fresh Z3 context
        example = BuildExample(self, semantic_theory, example_case)
        
        # [... remaining example processing ...]
        
        return example
    finally:
        # Force cleanup after processing
        import gc
        gc.collect()
```

### 5. Add Strategic Context Resets

Add the context reset at other key points where examples might be processed:

- `BuildExample.__init__` (during initialization)
- `ModelDefaults.__init__` (before constraint solving)
- Entry points in `cli.py` where examples are loaded

### 6. Create a Test Suite for Z3 Context Isolation

Implement test cases that verify proper solver isolation:

```python
def test_solver_isolation():
    """Test that examples produce consistent results regardless of execution order."""
    from model_checker.builder import BuildModule
    import importlib
    
    # Helper function to run a single example and return its result
    def run_single_example(module, example_name, theory_name):
        example_case = module.example_range[example_name]
        semantic_theory = module.semantic_theories[theory_name]
        example = module.process_example(example_name, example_case, theory_name, semantic_theory)
        return example.model_structure.z3_model_status
    
    # Create a minimal module for testing
    test_settings = {
        "file_path": "path/to/bimodal/examples.py",
    }
    
    # Test running BM_CM_4 alone
    module1 = BuildModule(test_settings)
    module1.example_range = {"BM_CM_4": module1.test_example_range["BM_CM_4"]}
    result1 = run_single_example(module1, "BM_CM_4", "Brast-McKie")
    
    # Test running BM_CM_3 then BM_CM_4
    module2 = BuildModule(test_settings)
    module2.example_range = {
        "BM_CM_3": module2.test_example_range["BM_CM_3"],
        "BM_CM_4": module2.test_example_range["BM_CM_4"]
    }
    run_single_example(module2, "BM_CM_3", "Brast-McKie")
    result2 = run_single_example(module2, "BM_CM_4", "Brast-McKie")
    
    # Verify consistent results
    assert result1 == result2, "Example results should be consistent regardless of execution order"
```

## Testing and Verification

We've conducted the following tests to verify the issue and validate the solution:

1. **Order-Dependent Test Results**:
   - Running `BM_CM_4` alone results in "no countermodel" (UNSATISFIABLE)
   - Running `BM_CM_3` followed by `BM_CM_4` results in finding countermodels for both
   - Running `BM_CM_4` followed by `BM_CM_3` results in "no countermodel" for both
   - This confirms that solver state leakage is occurring and affecting results

2. **Expected Results After Fix**:
   - Running `BM_CM_4` alone should find a countermodel (SAT)
   - Running examples in any order should produce consistent results
   - No timeouts should occur for examples that previously completed successfully

3. **Performance Impact Test**:
   - From our observations, solver times range from 0.038 to 0.076 seconds for individual examples
   - Context reset might add minimal overhead but should not significantly impact overall runtime
   - Test with various example counts to ensure scaling performance is maintained

## Implementation Guidelines

Following our design philosophy, the implementation should adhere to these principles:

1. **Fail Fast**:
   - Don't add complex conditional logic to handle context management edge cases
   - Let errors propagate naturally with informative tracebacks
   - Add assertions to validate proper context usage

2. **No Silent Failures**:
   - Don't catch exceptions just to avoid errors in the context reset process
   - If errors occur during context management, they should be clearly visible

3. **Clear Data Flow**:
   - Make the Z3 context management explicit and traceable
   - Document the context lifecycle and ownership responsibility

4. **Refactor Over Workaround**:
   - Implement the proper structural solution (context reset) rather than workarounds
   - Don't add complexity to preserve backward compatibility with existing code

5. **Root Cause Analysis**:
   - The implementation directly addresses the source of the problem (shared Z3 context)
   - It creates proper isolation between examples rather than masking symptoms

## Conclusion

The solution directly addresses the root cause of solver state leakage by ensuring each example runs with a completely fresh Z3 context. This approach:

1. Aligns with our "Deterministic Behavior" philosophy by ensuring consistent results regardless of execution order
2. Follows "Fail Fast" by allowing a clean context for each example rather than adding complex state management
3. Supports "Clear Data Flow" by making the Z3 context lifecycle explicit
4. Implements a proper structural solution rather than workarounds

By implementing these changes, the ModelChecker will produce consistent results for bimodal examples (and all other theories) regardless of the order in which they are run, making the system more predictable and reliable.