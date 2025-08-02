# Maximize Mode Pickle Problem Analysis and Solution Design

## Problem Statement

When running the model checker with the `--maximize` flag to compare semantic theories, the system encounters a pickle error:

```
ERROR: ImpositionSemantics (Fine) for N = 4.  cannot pickle 'module' object
ERROR: LogosSemantics (Brast-McKie) for N = 4.  cannot pickle 'module' object
```

This error prevents the comparison mode from finding the maximum model sizes for different semantic theories.

## Root Cause Analysis

### 1. Multiprocessing Architecture

The `compare_semantics` method in `BuildModule` uses `ProcessPoolExecutor` to run model checking tasks in parallel:

```python
with concurrent.futures.ProcessPoolExecutor() as executor:
    # ...
    futures[executor.submit(self.try_single_N, *new_case)] = new_case
```

### 2. Object Serialization Issue

When submitting tasks to the process pool, Python must serialize (pickle) all arguments. The `semantic_theory` dictionary contains:

```python
semantic_theory = {
    "semantics": ImpositionSemantics,  # Class reference
    "proposition": Proposition,         # Class reference
    "model": ModelStructure,           # Class reference
    "operators": imposition_operators,  # OperatorCollection instance
    "dictionary": {}                   # Translation dict
}
```

### 3. Module Reference Problem

The error occurs because:

1. **OperatorCollection objects** contain references to operator classes
2. **Operator classes** may have module-level imports or references
3. **Class definitions** themselves may reference modules that cannot be pickled
4. **Dynamic imports** in theory modules create unpicklable module references

### 4. Specific Problematic Elements

After investigation, the likely culprits are:

1. **OperatorCollection instances** - These are complex objects with class references
2. **Dynamically imported modules** - The theory loading system uses dynamic imports
3. **Module-level references** - Classes may reference their defining module

## Solution Design

### Option 1: Serialize Only Essential Data (Recommended)

Instead of passing entire semantic theory dictionaries, pass only the minimal data needed:

```python
# Instead of passing semantic_theory dict, pass:
theory_config = {
    "theory_name": theory_name,
    "semantics_name": semantic_theory["semantics"].__name__,
    "semantics_module": semantic_theory["semantics"].__module__,
    "proposition_name": semantic_theory["proposition"].__name__,
    "model_name": semantic_theory["model"].__name__,
    "operators": serialize_operators(semantic_theory["operators"]),
    "dictionary": semantic_theory.get("dictionary", {})
}
```

Then reconstruct the classes in the worker process:

```python
def try_single_N(self, theory_name, theory_config, example_case):
    # Reconstruct classes from names
    semantics_class = import_class(theory_config["semantics_module"], 
                                   theory_config["semantics_name"])
    # ... etc
```

### Option 2: Use Threading Instead of Multiprocessing

Replace `ProcessPoolExecutor` with `ThreadPoolExecutor`:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as executor:
    # Same logic, but no pickling required
```

**Pros:**
- No serialization issues
- Simpler implementation
- Shared memory access

**Cons:**
- Python GIL may limit parallelism
- Z3 solver calls may release GIL, so this could still work well

### Option 3: Refactor Operator Storage

Change how operators are stored in semantic theories:

```python
# Instead of OperatorCollection, use simple dict
"operators": {
    "\\imposition": "ImpositionOperator",
    "\\could": "MightImpositionOperator",
    # ... operator name to class name mapping
}
```

Then reconstruct in worker:

```python
operators = OperatorCollection()
for op_name, op_class_name in theory_config["operators"].items():
    op_class = getattr(operator_module, op_class_name)
    operators.add_operator(op_class)
```

### Option 4: Custom Pickle Support

Add `__getstate__` and `__setstate__` methods to problematic classes:

```python
class OperatorCollection:
    def __getstate__(self):
        # Return only picklable data
        return {
            'operators': [(name, cls.__name__, cls.__module__) 
                         for name, cls in self.operator_dictionary.items()]
        }
    
    def __setstate__(self, state):
        # Reconstruct from picklable data
        self.operator_dictionary = {}
        for name, cls_name, module_name in state['operators']:
            module = importlib.import_module(module_name)
            cls = getattr(module, cls_name)
            self.operator_dictionary[name] = cls
```

## Recommended Implementation Plan

### Phase 1: Quick Fix (Threading)

1. Change `ProcessPoolExecutor` to `ThreadPoolExecutor` in `compare_semantics`
2. Test with both theories to ensure it works
3. Monitor performance to see if GIL is a bottleneck

### Phase 2: Robust Solution (Serialization)

1. Create serialization functions for semantic theories:
   ```python
   def serialize_semantic_theory(theory):
       """Convert theory to picklable format"""
       
   def deserialize_semantic_theory(data):
       """Reconstruct theory from picklable format"""
   ```

2. Update `compare_semantics` to use serialized data

3. Update `try_single_N` to deserialize before use

### Phase 3: Long-term Refactor

1. Redesign operator storage to be serialization-friendly
2. Add pickle support to all model checker classes
3. Consider using a configuration-based approach instead of class references

## Testing Strategy

1. **Unit tests** for serialization/deserialization functions
2. **Integration tests** for maximize mode with multiple theories
3. **Performance tests** to compare threading vs multiprocessing
4. **Edge cases**: Large models, complex operators, deep inheritance

## Implementation Priority

Given the current needs:

1. **Immediate**: Implement Option 2 (Threading) as a quick fix
2. **Short-term**: Implement Option 1 (Minimal serialization) for better performance
3. **Long-term**: Consider Option 3/4 for architectural improvements

## Code Changes Required

### For Threading Solution (Option 2):

```python
# In builder/module.py, line 402:
# Change:
with concurrent.futures.ProcessPoolExecutor() as executor:
# To:
with concurrent.futures.ThreadPoolExecutor() as executor:
```

### For Serialization Solution (Option 1):

1. Add serialization utilities to `builder/module.py`
2. Modify `compare_semantics` to serialize before submission
3. Modify `try_single_N` to deserialize parameters
4. Handle dynamic imports properly

## Risks and Mitigations

1. **Risk**: Threading may be slower than multiprocessing
   - **Mitigation**: Profile and optimize Z3 usage; Z3 may release GIL

2. **Risk**: Serialization may miss some operator features
   - **Mitigation**: Comprehensive testing of all operator types

3. **Risk**: Dynamic imports may still cause issues
   - **Mitigation**: Use fully qualified names and careful import management