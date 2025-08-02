# Serialization Solution Implementation Plan

## Overview

This document provides a detailed implementation plan for solving the pickle error in `--maximize` mode by serializing only essential data instead of passing complex objects to the process pool.

## Architecture Design

### Core Concept

Instead of passing unpicklable objects (classes, OperatorCollection instances), we will:
1. Extract serializable metadata from semantic theories
2. Pass only primitive data types to worker processes
3. Reconstruct the necessary objects within each worker process

### Data Flow

```
Main Process                    Worker Process
------------                    --------------
semantic_theory    ------>      theory_config
(complex objects)  serialize    (simple data)
                                     |
                                     v
                                deserialize
                                     |
                                     v
                                reconstructed
                                semantic_theory
```

## Implementation Details

### 1. Serialization Functions

Create a new module `src/model_checker/builder/serialize.py`:

```python
"""
Serialization utilities for multiprocessing in maximize mode.

This module provides functions to serialize and deserialize semantic theories
for use with ProcessPoolExecutor, avoiding pickle errors with complex objects.
"""

import importlib
from typing import Dict, Any, Union, Type
from model_checker.syntactic import OperatorCollection


def serialize_operators(operators: Union[OperatorCollection, dict]) -> Dict[str, Dict[str, str]]:
    """
    Serialize an OperatorCollection or dict of operators to a picklable format.
    
    Args:
        operators: Either an OperatorCollection instance or a dict of operators
        
    Returns:
        Dictionary mapping operator names to their class info:
        {
            "\\imposition": {
                "class_name": "ImpositionOperator",
                "module_name": "model_checker.theory_lib.imposition.operators"
            },
            ...
        }
    """
    serialized = {}
    
    if isinstance(operators, OperatorCollection):
        operator_dict = operators.operator_dictionary
    else:
        operator_dict = operators
    
    for op_name, op_class in operator_dict.items():
        serialized[op_name] = {
            "class_name": op_class.__name__,
            "module_name": op_class.__module__
        }
    
    return serialized


def deserialize_operators(operator_data: Dict[str, Dict[str, str]]) -> OperatorCollection:
    """
    Reconstruct an OperatorCollection from serialized data.
    
    Args:
        operator_data: Serialized operator information
        
    Returns:
        OperatorCollection instance with all operators restored
    """
    collection = OperatorCollection()
    
    for op_name, class_info in operator_data.items():
        module = importlib.import_module(class_info["module_name"])
        op_class = getattr(module, class_info["class_name"])
        collection.add_operator(op_class)
    
    return collection


def serialize_semantic_theory(theory_name: str, semantic_theory: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize a semantic theory dictionary to a picklable format.
    
    Args:
        theory_name: Name of the theory (e.g., "Fine", "Brast-McKie")
        semantic_theory: Dictionary containing semantics, operators, etc.
        
    Returns:
        Serialized theory configuration with only picklable data
    """
    return {
        "theory_name": theory_name,
        "semantics": {
            "class_name": semantic_theory["semantics"].__name__,
            "module_name": semantic_theory["semantics"].__module__
        },
        "proposition": {
            "class_name": semantic_theory["proposition"].__name__,
            "module_name": semantic_theory["proposition"].__module__
        },
        "model": {
            "class_name": semantic_theory["model"].__name__,
            "module_name": semantic_theory["model"].__module__
        },
        "operators": serialize_operators(semantic_theory["operators"]),
        "dictionary": semantic_theory.get("dictionary", {})  # Already serializable
    }


def deserialize_semantic_theory(theory_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reconstruct a semantic theory from serialized configuration.
    
    Args:
        theory_config: Serialized theory configuration
        
    Returns:
        Semantic theory dictionary with all classes restored
    """
    # Helper function to load a class from module and class name
    def load_class(class_info: Dict[str, str]) -> Type:
        module = importlib.import_module(class_info["module_name"])
        return getattr(module, class_info["class_name"])
    
    return {
        "semantics": load_class(theory_config["semantics"]),
        "proposition": load_class(theory_config["proposition"]),
        "model": load_class(theory_config["model"]),
        "operators": deserialize_operators(theory_config["operators"]),
        "dictionary": theory_config["dictionary"]
    }


def import_class(module_name: str, class_name: str) -> Type:
    """
    Import a class from a module by name.
    
    Args:
        module_name: Fully qualified module name
        class_name: Name of the class to import
        
    Returns:
        The imported class
        
    Raises:
        ImportError: If module cannot be imported
        AttributeError: If class doesn't exist in module
    """
    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except ImportError as e:
        raise ImportError(f"Cannot import module '{module_name}': {e}")
    except AttributeError as e:
        raise AttributeError(f"Class '{class_name}' not found in module '{module_name}': {e}")
```

### 2. Update BuildModule Methods

#### 2.1 Import Serialization Utilities

In `src/model_checker/builder/module.py`, add import at the top:

```python
from model_checker.builder.serialize import (
    serialize_semantic_theory,
    deserialize_semantic_theory
)
```

#### 2.2 Create Wrapper for try_single_N

Add a new method that handles deserialization:

```python
def try_single_N_serialized(self, theory_name, theory_config, example_case):
    """
    Wrapper for try_single_N that deserializes the semantic theory first.
    
    This method is designed to be called by ProcessPoolExecutor with
    serialized data that can be pickled across process boundaries.
    
    Args:
        theory_name: Name of the theory
        theory_config: Serialized theory configuration
        example_case: Example case with premises, conclusions, settings
        
    Returns:
        tuple: (success, runtime)
    """
    # Reconstruct the semantic theory from serialized data
    semantic_theory = deserialize_semantic_theory(theory_config)
    
    # Call the original method with reconstructed objects
    return self.try_single_N(theory_name, semantic_theory, example_case)
```

#### 2.3 Update compare_semantics Method

Replace the existing `compare_semantics` method:

```python
def compare_semantics(self, example_theory_tuples):
    """
    Compare different semantic theories by finding maximum model sizes.
    
    This method attempts to find the maximum model size (N) for each semantic theory
    by incrementally testing larger values of N until a timeout occurs. It runs the
    tests concurrently using a ProcessPoolExecutor for better performance.
    
    The method now uses serialization to avoid pickle errors with complex objects.
    
    Args:
        example_theory_tuples: List of tuples containing (theory_name, semantic_theory, example_case)
            where example_case is [premises, conclusions, settings]
            
    Returns:
        list: List of tuples containing (theory_name, max_N) where max_N is the largest
              number of worlds for which a model was found within the time limit
    """
    results = []
    active_cases = {}  # Track active cases and their current N values
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Initialize first run for each case
        futures = {}
        all_times = []
        
        for case in example_theory_tuples:
            theory_name, semantic_theory, (premises, conclusions, settings) = case
            
            # Serialize the semantic theory for pickling
            theory_config = serialize_semantic_theory(theory_name, semantic_theory)
            
            # Create example case with copied settings
            example_case = [premises, conclusions, settings.copy()]
            active_cases[theory_name] = settings['N']  # Store initial N
            all_times.append(settings['max_time'])
            
            # Submit with serialized data
            new_case = (theory_name, theory_config, example_case)
            futures[executor.submit(self.try_single_N_serialized, *new_case)] = (
                theory_name, theory_config, example_case, semantic_theory
            )
        
        max_time = max(all_times) if all_times else 1
            
        while futures:
            done, _ = concurrent.futures.wait(
                futures,
                return_when=concurrent.futures.FIRST_COMPLETED
            )
            
            for future in done:
                theory_name, theory_config, example_case, semantic_theory = futures.pop(future)
                max_time = example_case[2]['max_time']
                
                try:
                    success, runtime = future.result()
                    
                    if success and runtime < max_time:
                        # Increment N and submit new case
                        example_case[2]['N'] = active_cases[theory_name] + 1
                        active_cases[theory_name] = example_case[2]['N']
                        
                        # Submit with same serialized config but updated N
                        new_case = (theory_name, theory_config, example_case)
                        futures[executor.submit(self.try_single_N_serialized, *new_case)] = (
                            theory_name, theory_config, example_case, semantic_theory
                        )
                    else:
                        # Found max N for this case
                        results.append((theory_name, active_cases[theory_name] - 1))
                        
                except Exception as e:
                    print(
                        f"\nERROR: {semantic_theory['semantics'].__name__} "
                        f"({theory_name}) for N = {example_case[2]['N']}. {str(e)}"
                    )
                    # Log the error but try to continue with other theories
                    results.append((theory_name, active_cases.get(theory_name, 0) - 1))
                    
    return results
```

### 3. Error Handling and Edge Cases

#### 3.1 Handle Missing Modules

Add error handling for dynamic imports:

```python
def safe_import_module(module_name: str):
    """Safely import a module with helpful error messages."""
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        # Check if it's a theory module
        if "theory_lib" in module_name:
            theory_name = module_name.split(".")[-2]
            raise ImportError(
                f"Cannot import theory module '{theory_name}'. "
                f"Make sure the theory is properly installed. "
                f"Original error: {e}"
            )
        raise
```

#### 3.2 Handle Circular Imports

Ensure imports are done at the right time:

```python
def deserialize_operators(operator_data: Dict[str, Dict[str, str]]) -> OperatorCollection:
    """Reconstruct an OperatorCollection from serialized data."""
    # Import here to avoid circular imports
    from model_checker.syntactic import OperatorCollection
    
    collection = OperatorCollection()
    # ... rest of implementation
```

### 4. Testing Strategy

#### 4.1 Unit Tests

Create `tests/test_serialize.py`:

```python
import unittest
from model_checker.builder.serialize import (
    serialize_operators,
    deserialize_operators,
    serialize_semantic_theory,
    deserialize_semantic_theory
)

class TestSerialization(unittest.TestCase):
    def test_serialize_operators(self):
        """Test operator serialization and deserialization."""
        # Create test operators
        from model_checker.theory_lib.imposition.operators import ImpositionOperator
        from model_checker.syntactic import OperatorCollection
        
        collection = OperatorCollection()
        collection.add_operator(ImpositionOperator)
        
        # Serialize
        serialized = serialize_operators(collection)
        
        # Check format
        self.assertIn("\\imposition", serialized)
        self.assertEqual(serialized["\\imposition"]["class_name"], "ImpositionOperator")
        
        # Deserialize
        restored = deserialize_operators(serialized)
        
        # Verify
        self.assertIn("\\imposition", restored.operator_dictionary)
        self.assertEqual(
            restored["\\imposition"].__name__, 
            ImpositionOperator.__name__
        )
    
    def test_serialize_semantic_theory(self):
        """Test full semantic theory serialization."""
        # ... test implementation
```

#### 4.2 Integration Tests

Test with actual maximize mode:

```python
def test_maximize_mode_with_serialization():
    """Test that maximize mode works with multiple theories."""
    # Run with both Fine and Brast-McKie theories
    # Verify no pickle errors
    # Check that results are produced
```

### 5. Migration Plan

#### Phase 1: Add Serialization Module
1. Create `serialize.py` with all functions
2. Add unit tests
3. Verify imports work correctly

#### Phase 2: Update BuildModule
1. Add import for serialization functions
2. Create `try_single_N_serialized` wrapper
3. Update `compare_semantics` to use serialization
4. Test with single theory first

#### Phase 3: Full Integration
1. Test with multiple theories
2. Verify translation dictionaries work
3. Performance testing vs threading approach

### 6. Rollback Plan

If serialization causes issues:

1. Keep original methods intact (don't delete)
2. Add feature flag to toggle serialization:
   ```python
   USE_SERIALIZATION = True  # Can be set to False to use old behavior
   ```
3. Log detailed errors for debugging

### 7. Performance Considerations

#### Overhead Analysis

Serialization adds overhead:
- Serializing operators: ~1ms per theory
- Deserializing in worker: ~2ms per theory
- Total overhead: ~3ms per worker task

This is negligible compared to Z3 solver time (typically 100ms+).

#### Optimization Opportunities

1. **Cache deserialized theories** within worker processes
2. **Batch multiple N values** per worker task
3. **Pre-serialize** common theories at startup

### 8. Future Enhancements

#### 8.1 Configuration Files

Instead of code-based theory definitions:

```yaml
# imposition_theory.yaml
semantics:
  class: ImpositionSemantics
  module: model_checker.theory_lib.imposition.semantic
operators:
  - name: \imposition
    class: ImpositionOperator
    module: model_checker.theory_lib.imposition.operators
```

#### 8.2 Theory Registry

Central registry for all theories:

```python
class TheoryRegistry:
    """Central registry for semantic theories."""
    
    _theories = {}
    
    @classmethod
    def register(cls, name, config):
        """Register a theory configuration."""
        cls._theories[name] = config
    
    @classmethod
    def get_serialized(cls, name):
        """Get pre-serialized theory configuration."""
        return cls._theories[name]
```

## Summary

This implementation plan provides a robust solution to the pickle problem by:

1. **Separating data from code** - Only primitive data crosses process boundaries
2. **Maintaining compatibility** - Existing code continues to work
3. **Enabling scalability** - ProcessPoolExecutor can now be used effectively
4. **Improving maintainability** - Clear separation of concerns

The solution is designed to be implemented incrementally with minimal risk to existing functionality.