# Example Separation to Prevent Z3 State Leakage

## Problem Statement

When running examples sequentially in the same process, Z3 state leakage can cause non-deterministic behavior, where the results of one example influence the results of subsequent examples. Specifically:

- Running `BM_CM_3` followed by `BM_CM_4` produces different results than running `BM_CM_4` alone
- This violates the "Deterministic Behavior" principle from our design philosophy
- Even explicit Z3 context resets and garbage collection don't fully clear the Z3 state

## Solution: Complete Process Isolation

The solution is to run each example in a separate Python process to ensure complete isolation of Z3 state. This is implemented by:

1. Modifying `__main__.py` to use `run_examples_isolated()` instead of `run_examples()`
2. Removing ineffective Z3 context reset code from `model.py`
3. Making `run_examples()` redirect to `run_examples_isolated()`
4. Ensuring proper PYTHONPATH handling in subprocess execution

## Implementation Steps

### 1. Modify `__main__.py` to use process isolation

In `/src/model_checker/__main__.py`, change:

```python
# Find line 253 (approximately) in the main() function
module.run_examples()
```

to:

```python
# Always use process isolation for reliable Z3 context management
module.run_examples_isolated()
```

### 2. Remove ineffective Z3 state reset code

In `/src/model_checker/model.py`, modify the `_reset_global_state()` method:

```python
def _reset_global_state(self):
    """Reset any global state that could cause interference between examples.
    
    Note: This method no longer attempts to reset Z3 state, as it's ineffective.
    For guaranteed isolation between examples, all execution now uses 
    ProcessIsolationManager which runs each example in a separate process.
    
    Subclasses MUST override this method and call super()._reset_global_state()
    to ensure proper cleanup of their specific resources.
    """
    # Reset general caches only - no Z3 state reset attempts
    self._cached_values = {}
```

Also modify the `_cleanup_solver_resources()` method:

```python
def _cleanup_solver_resources(self):
    """Clean up solver resources to release memory.
    
    This method simply clears references to solver objects. It no longer attempts
    to reset Z3 state as that approach was unreliable.
    
    All examples now run in separate processes via ProcessIsolationManager,
    which provides guaranteed isolation for Z3 context between examples.
    """
    # Remove references to solver and model
    self.solver = None
    self.z3_model = None
    
    # Clear the context reference (if it exists)
    if hasattr(self, 'example_context'):
        self.example_context = None
```

And update the `solve()` method docstring and implementation:

```python
def solve(self, model_constraints, max_time):
    """Uses the Z3 solver to find a model satisfying the given constraints.
    
    Note: This method is only called within an isolated process context, as
    all examples now run via ProcessIsolationManager in separate processes.
    
    Args:
        model_constraints (ModelConstraints): The logical constraints to solve
        max_time (int): Maximum solving time in milliseconds (0 for unlimited)
        
    Returns:
        tuple: Contains result information (timeout flag, model/core, satisfiability)
        
    Notes:
        - If the constraints are unsatisfiable, returns the unsatisfiable core
        - If solving times out, sets the timeout flag but still returns partial results
    """
    # Import z3
    import z3
    
    # Create a new solver instance
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
        # Clear references to solver objects
        self.solver = None
```

### 3. Update `run_examples()` to redirect to `run_examples_isolated()`

In `/src/model_checker/builder/module.py`, modify the `run_examples()` method:

```python
def run_examples(self):
    """Process and execute each example case with all semantic theories.
    
    This method is now a wrapper that calls run_examples_isolated to ensure
    all examples run in isolated processes. This provides complete Z3 context
    isolation between examples, preventing state leakage.
    """
    import warnings
    warnings.warn(
        "run_examples now redirects to run_examples_isolated to ensure all examples "
        "run with complete Z3 context isolation.",
        DeprecationWarning, 
        stacklevel=2
    )
    
    # Always use isolated execution
    return self.run_examples_isolated()
```

### 4. Update `process_example()` to use process isolation

In `/src/model_checker/builder/module.py`, modify the `process_example()` method:

```python
def process_example(self, example_name, example_case, theory_name, semantic_theory):
    """Process a single model checking example.
    
    This method is now deprecated as all examples run through process_example_isolated
    for guaranteed isolation.
    
    Args:
        example_name (str): Name of the example being processed
        example_case (list): The example case containing [premises, conclusions, settings]
        theory_name (str): Name of the semantic theory being used
        semantic_theory (dict): Dictionary containing the semantic theory implementation
        
    Returns:
        BuildExample: The example after processing
    """
    import warnings
    warnings.warn(
        "process_example is deprecated. All examples now run through process_example_isolated "
        "via ProcessIsolationManager to ensure complete Z3 context isolation.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Simply delegate to process_example_isolated
    return self.process_example_isolated(example_name, example_case, theory_name, semantic_theory)
```

### 5. Fix module path handling in `run_examples_isolated()`

In `/src/model_checker/builder/module.py`, modify the path extraction in `run_examples_isolated()`:

```python
# Get module path - either from module_path or module_flags.file_path
if hasattr(self, 'module_path'):
    module_path = self.module_path
else:
    module_path = self.module_flags.file_path
```

### 6. Update PYTHONPATH handling in `ProcessIsolationManager`

In `/src/model_checker/utils/process_isolation.py`, update the `run_example()` method to handle PYTHONPATH correctly:

```python
# Get the src directory for PYTHONPATH
current_file = os.path.abspath(__file__)
src_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

# Set up environment with correct PYTHONPATH
env = os.environ.copy()
python_path = env.get("PYTHONPATH", "")
if python_path:
    env["PYTHONPATH"] = f"{src_dir}:{python_path}"
else:
    env["PYTHONPATH"] = src_dir

# Execute the process and capture its output
result = subprocess.run(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    check=False,  # Don't raise exception on non-zero exit
    env=env       # Use our environment with the correct PYTHONPATH
)
```

### 7. Update `example_runner.py` to provide more complete mock objects

In `/src/model_checker/utils/example_runner.py`, update the mock module creation:

```python
# Create mock module with minimum required attributes
class MockModule:
    def __init__(self):
        self.general_settings = {"print_z3": False, "print_constraints": False}
        # Add module_flags field for BuildExample
        class ModuleFlags:
            def __init__(self):
                self.file_path = example_module_path
        self.module_flags = ModuleFlags()
```

## Expected Behavior

After implementing these changes:

1. Each example will run in its own separate process with a clean Z3 context
2. BM_CM_4 will produce the same result whether run alone or after BM_CM_3
3. No attempted Z3 state reset code will be executed, as it's ineffective
4. The original output format and colors will be preserved

## Confirmation of Results

To verify the fix, run:

```bash
./dev_cli.py /path/to/bimodal/examples.py
```

With BM_CM_3 and BM_CM_4 both enabled, and then with only BM_CM_4 enabled. The results should be consistent in both cases.

## Why Process Isolation Works

Process isolation completely solves the Z3 state leakage issue because:

1. Each example gets its own memory space and Z3 context
2. Python processes don't share global state, so internal Z3 state can't leak between processes
3. All solver instances are truly independent
4. The approach is robust against any changes in Z3's internal implementation

This approach aligns perfectly with the "Deterministic Behavior" principle from our design philosophy and ensures that examples produce consistent results regardless of execution order.