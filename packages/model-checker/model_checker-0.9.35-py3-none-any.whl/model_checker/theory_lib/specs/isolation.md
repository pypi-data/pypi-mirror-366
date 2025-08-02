# Z3 Solver Isolation Strategy

## Problem Statement

The ModelChecker framework currently exhibits state leakage between examples when run in sequence. Specifically:
- When running two bimodal examples (BM_CM_3 and BM_CM_4) together, both find countermodels
- When running BM_CM_4 alone, no countermodel is found
- When running BM_CM_3 after BM_CM_4, no countermodel is found

This suggests that Z3 solver state is persisting between examples, causing different behavior depending on execution order.

## Purpose and Scope

The goal of this implementation is to:
1. **Eliminate Z3 Solver State Leakage**: Ensure complete isolation between model checking instances
2. **Improve Performance**: Leverage parallel processing capabilities for faster execution
3. **Maintain Output Consistency**: Make no changes to the printed output format or content
4. **Preserve API Compatibility**: Users should experience no interface changes

This is strictly an internal architectural improvement focused on reliability and performance, not a user-facing feature change.

## Root Cause Analysis

1. **Z3 Context Sharing**: Z3 maintains a global context (`_main_ctx`) that persists between solver instances unless explicitly reset.

2. **Memory Management Issues**: The Z3 Python API may not completely clean up resources when solver instances go out of scope, leading to memory leaks and state entanglement.

3. **Constraint Accumulation**: Constraints from previous examples may implicitly affect subsequent examples through cached solver state.

4. **Incomplete Model Cleanup**: When a model structure is created and discarded, not all Z3 resources are being properly released.

## Current Implementation Analysis

The current implementation attempts to address this with:

1. **Explicit Solver Creation**: Each ModelStructure creates its own Z3 Solver instance.

2. **Cleanup Methods**: The `_cleanup_solver_resources()` method attempts to release references to Z3 objects.

3. **Limited Global State Reset**: `reset_global_state()` methods in semantic classes try to clear caches.

However, these measures are insufficient because:

1. They don't fully isolate the Z3 context between examples
2. They rely on Python's garbage collection which may not immediately reclaim Z3 resources
3. Resources created during constraint generation and model evaluation can persist

## Proposed Solution: Multi-Process Isolation

The most robust solution is to use separate processes for each example, completely isolating Z3 state.

### Architecture

1. **Process Pool Manager**:
   - A central manager class that handles process creation and communication
   - Maintains a pool of worker processes for evaluating examples

2. **Example Worker Process**:
   - Each example runs in its own dedicated process
   - Complete Z3 context isolation between examples
   - Results serialized and returned to main process

3. **Serialization Layer**:
   - Handles serialization of inputs (constraints, settings) to worker processes
   - Deserializes model results back to main process

### Implementation Plan

#### 1. Process Manager Class

```python
class ModelCheckerProcessManager:
    """Manages multiple isolated processes for model checking examples."""
    
    def __init__(self, num_workers=None):
        """Initialize process pool with configurable number of workers."""
        self.pool = multiprocessing.Pool(num_workers)
        self.results = {}
        
    def check_example(self, example_id, example_case, theory_name, semantic_theory):
        """Submit an example for checking in an isolated process."""
        # Submit task to process pool
        future = self.pool.apply_async(
            _isolated_example_worker,
            (example_id, example_case, theory_name, semantic_theory)
        )
        self.results[example_id] = future
        return future
        
    def get_results(self, example_id, timeout=None):
        """Get results for a specific example."""
        if example_id not in self.results:
            raise KeyError(f"No example with ID {example_id}")
        return self.results[example_id].get(timeout=timeout)
        
    def get_all_results(self, timeout=None):
        """Get all results, optionally waiting for completion."""
        return {
            example_id: future.get(timeout=timeout)
            for example_id, future in self.results.items()
        }
        
    def shutdown(self):
        """Clean up process pool."""
        self.pool.close()
        self.pool.join()
```

#### 2. Isolated Worker Function

```python
def _isolated_example_worker(example_id, example_case, theory_name, semantic_theory):
    """Process worker function that runs in an isolated process.
    
    This function has a completely isolated Z3 context, ensuring no state
    leakage between different examples.
    """
    # Force clean Z3 state at the start
    import z3
    if hasattr(z3, '_main_ctx'):
        z3._main_ctx = None
    
    # Import delayed to ensure fresh imports in the worker process
    from model_checker.builder.example import BuildExample
    
    # Create model and process example
    model = BuildExample(semantic_theory, example_case)
    
    # Serialize results for return to parent process
    serialized_results = {
        'example_id': example_id,
        'has_model': model.model_structure.z3_model_status,
        'runtime': model.model_structure.z3_model_runtime,
        # Additional result data to be serialized
    }
    
    # For countermodels, include model information
    if model.model_structure.z3_model_status:
        serialized_results['model_info'] = _serialize_model_info(model)
    
    return serialized_results
```

#### 3. Module Runner Integration

```python
def run_examples(self):
    """Process and execute each example case with all semantic theories.
    
    Uses isolated processes for complete Z3 state isolation between examples.
    """
    # Create process manager
    manager = ModelCheckerProcessManager()
    
    try:
        # Submit all examples to process pool
        for example_name, example_case in self.example_range.items():
            for theory_name, semantic_theory in self.semantic_theories.items():
                # Make setting copy for each semantic_theory
                example_copy = list(example_case)
                example_copy[2] = example_case[2].copy()
                
                # Submit example to be processed in isolated process
                manager.check_example(
                    f"{example_name}_{theory_name}",
                    example_copy,
                    theory_name,
                    semantic_theory
                )
        
        # Collect and process results
        results = manager.get_all_results()
        
        # Process results to display output
        for example_id, result in results.items():
            if result['has_model']:
                # Display countermodel information
                self._display_countermodel(result)
            else:
                # Display no countermodel message
                print(f"\nEXAMPLE {result['example_id']}: there is no countermodel.")
                print(f"\nZ3 Run Time: {result['runtime']} seconds")
    
    finally:
        # Clean up process pool
        manager.shutdown()
```

### Design Considerations

1. **Serialization Challenges**:
   - Z3 models cannot be directly serialized
   - Need to extract and serialize model information (e.g., world states, truth assignments)
   - Visualization will happen in main process using serialized model data

2. **Performance Overhead**:
   - Process creation has overhead
   - Parallel execution may improve overall performance for multiple examples
   - Memory usage will increase with process count

3. **Error Handling**:
   - Worker process errors must be properly propagated to main process
   - Timeouts need to be handled at both process and solver level

4. **Implementation Phases**:
   1. Basic process isolation with minimal serialization
   2. Enhanced serialization for complete model information
   3. Parallel processing optimization
   4. Full theory support across all theories

## Alternative Approaches

### 1. Thread-Based Isolation with Context Reset

If process-based isolation is too heavyweight, a thread-based approach with explicit context reset could be used:

```python
def run_examples_thread_isolation(self):
    for example_name, example_case in self.example_range.items():
        # Force Z3 context reset
        import z3
        if hasattr(z3, '_main_ctx'):
            z3._main_ctx = None
            
        # Force garbage collection
        import gc
        gc.collect()
        
        # Run example in isolation
        # ...
```

Limitations:
- Less robust than process isolation
- Still potential for state leakage through global Python objects
- Harder to reason about correctness

### 2. Custom Z3 Wrapper with Sandboxing

Create a custom Z3 wrapper that explicitly sets up sandbox environments for each example:

```python
class SandboxedZ3:
    def __init__(self):
        self._reset_context()
        
    def _reset_context(self):
        # Load Z3 with a clean context
        import importlib
        import sys
        if 'z3' in sys.modules:
            del sys.modules['z3']
        self.z3 = importlib.import_module('z3')
        
    def create_solver(self):
        return self.z3.Solver()
```

Limitations:
- Complex implementation
- May interfere with Python's import system
- Performance overhead from module reloading

## Recommendation

The multi-process isolation approach is recommended for several reasons:

1. **Complete Isolation**: Process boundaries guarantee true isolation of state
2. **Scalability**: Naturally supports parallel execution of examples
3. **Robustness**: Crashes in one example won't affect others
4. **Simplicity**: Conceptually clear separation of concerns
5. **Performance**: Parallel processing of examples reduces total runtime

Implementation should proceed in phases, starting with a minimal viable implementation focused on fixing the immediate issue, then expanding to support all theories and optimization for performance.

This approach aligns with the project's design philosophy, particularly:
- **Fail Fast**: Complete isolation prevents masking of errors
- **Deterministic Behavior**: Execution order won't affect results
- **No Silent Failures**: Isolation ensures errors happen consistently
- **Prioritize Code Quality Over Backward Compatibility**: A clean solution even if it requires significant changes

## Implementation Principles

When implementing this solution, adhere to these principles:

1. **Preserve Output Format**: Make no changes to the format or content of printed output. The goal is to maintain consistency with existing user expectations.

2. **Internal Architecture Only**: All changes should be transparent to users of the API. The process isolation and parallelization should be purely an implementation detail.

3. **Progressive Enhancement**: Implement the solution incrementally, testing thoroughly at each stage to ensure no regressions.

4. **Complete Test Coverage**: Ensure that all existing tests pass with the new implementation, focusing especially on previously inconsistent test cases.

5. **Performance Measurement**: Include benchmarking to quantify the performance improvements of parallel processing.

This implementation will significantly improve the reliability of the ModelChecker framework by eliminating Z3 solver context leakage, while also providing performance benefits through parallel processing - all without changing the user experience or output format.
