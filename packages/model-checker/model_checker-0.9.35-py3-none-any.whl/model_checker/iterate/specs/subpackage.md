# Implementation Plan: Refactoring Model Iteration System

This document outlines a comprehensive plan for refactoring the model iteration functionality from the `builder` package into its own dedicated `iterate` subpackage, with a focus on proper separation between theory-agnostic and theory-specific components.

## 1. Goals and Design Philosophy

### Primary Goals
- Create a clean separation between theory-agnostic and theory-specific iteration logic
- Establish a base class in `iterate/core.py` that can be inherited by theory-specific implementations
- Eliminate fallbacks, default values, and dynamic selection in core iteration code
- Design a system where new theories can be added without modifying the core iteration code
- Remove all theory-specific functionality from core code to ensure flexibility and maintainability

### Design Philosophy
- **No Default Values**: All parameters must be explicitly provided; no implicit fallbacks
- **Theory Isolation**: Theory-specific code must be completely isolated from core iteration logic
- **Clear Interfaces**: Well-defined abstract base classes that theories must implement
- **Direct Subclass Usage**: Each theory must explicitly provide its own iterator implementation for use in examples.py
- **Fail Fast**: Let errors occur naturally rather than adding complex conditional logic
- **Theory Agnostic Core**: The base iterator class must work with any theory without modifications

## 2. Architecture Overview

### Class Hierarchy

```
BaseModelIterator (in iterate/core.py)
├── DefaultModelIterator (in theory_lib/default/iterate.py)
├── BimodalModelIterator (in theory_lib/bimodal/iterate.py)
├── ExclusionModelIterator (in theory_lib/exclusion/iterate.py)
└── ImpositionModelIterator (in theory_lib/imposition/iterate.py)
```

### Package Structure

```
src/model_checker/
├── iterate/                     # New dedicated package for iteration
│   ├── __init__.py              # Public API exports
│   ├── core.py                  # Base iterator class and theory-agnostic functions
│   ├── graph_utils.py           # Graph utilities moved from builder/graph_utils.py
│   ├── notes/                   # Documentation and implementation notes
│   │   └── subpackage.md        # This implementation plan
│   └── tests/                   # Tests for iteration functionality
│       ├── __init__.py
│       ├── test_core.py         # Tests for core iteration
│       └── test_graph_utils.py  # Tests for graph utilities
└── theory_lib/
    ├── default/
    │   ├── iterate.py           # DefaultModelIterator implementation
    │   └── ...
    ├── bimodal/
    │   ├── iterate.py           # BimodalModelIterator implementation
    │   └── ...
    ├── exclusion/
    │   ├── iterate.py           # ExclusionModelIterator implementation
    │   └── ...
    └── imposition/
        ├── iterate.py           # ImpositionModelIterator implementation
        └── ...
```

## 3. Key Design Principles

### Theory-Agnostic Base Class

`BaseModelIterator` in `iterate/core.py` will provide the theory-agnostic iteration framework with well-defined extension points for theory-specific behavior. It must not contain:

- Theory-specific conditions or checks
- Hardcoded references to theory-specific attributes
- Display methods with theory-specific conditions
- Any methods that assume specific theory implementation details

All theory-specific functionality should be pushed down to the theory-specific subclasses through well-defined abstract methods.

### Theory-Specific Iterator Requirements

Each theory must implement its own iterator subclass in `theory_lib/<theory_name>/iterate.py` that:

- Inherits from `BaseModelIterator`
- Implements all required abstract methods for that theory
- Specifies which semantic primitives or defined relations make up the main ingredients of a model worth comparing
- Contains only theory-specific details, with general methods inherited from the base class

### Usage in Examples

The `iterate_example` function in `core.py` will no longer take an `iterator_class` parameter. Instead:

1. Each theory's `examples.py` module will be responsible for using the theory's specific iterator class
2. When the `iterate` setting is > 1 in a theory's examples, the theory's iterator implementation should be used
3. This ensures that the theory developer explicitly defines which iterator to use, rather than relying on dynamic detection

## 4. Core Components Design

### `BaseModelIterator` (in `iterate/core.py`)

The base class will provide the theory-agnostic iteration framework with well-defined extension points for theory-specific behavior.

```python
class BaseModelIterator:
    """Base class for all model iterators.
    
    This class provides the core iteration framework but relies on 
    theory-specific subclasses to implement certain methods.
    """
    
    def __init__(self, example, **kwargs):
        """Initialize the iterator with a BuildExample instance.
        
        Args:
            example: A BuildExample instance.
            **kwargs: Additional theory-specific parameters.
        """
        self.example = example
        self._validate_example()
        self._initialize_base_attributes()
        # Additional initialization
        
    def _validate_example(self):
        """Validate the BuildExample instance."""
        # Validation logic
        
    def _initialize_base_attributes(self):
        """Initialize attributes common to all iterators."""
        # Common attribute initialization - MUST NOT contain theory-specific details
        
    def iterate(self):
        """Find a new model distinct from previously found models.
        
        Returns:
            BuildExample: A new example with a distinct model, or None if no more models.
        """
        # Generic iteration algorithm using theory-specific methods
        
    # Abstract methods that must be implemented by subclasses
    def _calculate_differences(self, model1, model2):
        """Calculate differences between two models.
        
        Args:
            model1: First model structure.
            model2: Second model structure.
            
        Returns:
            dict: Dictionary of differences between models.
        """
        raise NotImplementedError("Must be implemented by subclass")
        
    def _create_difference_constraint(self, previous_model):
        """Create a constraint ensuring difference from a previous model.
        
        Args:
            previous_model: A previous model structure.
            
        Returns:
            z3.BoolRef: A Z3 constraint ensuring difference.
        """
        raise NotImplementedError("Must be implemented by subclass")
        
    def _get_structural_constraints(self):
        """Get structural constraints for the model.
        
        Returns:
            list: Z3 constraints enforcing model structure.
        """
        raise NotImplementedError("Must be implemented by subclass")
        
    def _check_isomorphism(self, model1, model2):
        """Check if two models are isomorphic.
        
        Args:
            model1: First model structure.
            model2: Second model structure.
            
        Returns:
            bool: True if models are isomorphic, False otherwise.
        """
        raise NotImplementedError("Must be implemented by subclass")
```

### Simplifying `iterate_example` Function

The simplified `iterate_example` function in `core.py` will be:

```python
def iterate_example(example, max_models=5):
    """Iterate a BuildExample to find multiple models.
    
    Args:
        example: A BuildExample instance.
        max_models: Maximum number of models to find.
        
    Returns:
        list: List of BuildExample instances with distinct models.
    """
    # The iterator_class parameter is removed as each theory must explicitly specify
    # which iterator to use in their own examples.py

    # Get theory name from example
    theory_name = example.theory.name
    
    # Each theory should import this function and provide a wrapper in their own examples.py
    # to specify which iterator class to use
    raise NotImplementedError(
        "iterate_example should be called from a theory-specific implementation "
        "that explicitly specifies which iterator to use"
    )
```

### Theroy-Specific Implementation

Each theory will provide its own wrapper for `iterate_example` in its examples.py module:

```python
# In theory_lib/default/examples.py

def iterate_example(example, max_models=5):
    """Iterate a default theory example to find multiple models.
    
    Args:
        example: A BuildExample instance with a default theory model.
        max_models: Maximum number of models to find.
        
    Returns:
        list: List of BuildExample instances with distinct models.
    """
    from model_checker.theory_lib.default.iterate import DefaultModelIterator
    
    # Create the theory-specific iterator
    iterator = DefaultModelIterator(example)
    iterator.max_models = max_models
    
    # Run iteration
    return iterator.iterate()
```

## 5. Moving Theory-Agnostic Methods to Core

Methods that are currently in theory-specific implementations (like `default/iterate.py`) but are actually theory-agnostic should be moved to the base class. These include:

- `_calculate_basic_differences`: The generic difference detection logic
- Any other methods that use general iteration patterns without theory-specific details

For example, `_calculate_difference` in `default/iterate.py` should be refactored to:
1. Move the general logic to the base class
2. Keep only default theory-specific detection in the subclass

## 6. Implementation Steps

### Phase 1: Create New Package Structure

1. Create necessary directories:
   ```bash
   mkdir -p src/model_checker/iterate/tests
   mkdir -p src/model_checker/iterate/notes
   ```

2. Create initial files:
   ```bash
   touch src/model_checker/iterate/__init__.py
   touch src/model_checker/iterate/core.py
   touch src/model_checker/iterate/graph_utils.py
   touch src/model_checker/iterate/tests/__init__.py
   touch src/model_checker/iterate/tests/test_core.py
   touch src/model_checker/iterate/tests/test_graph_utils.py
   ```

3. Create theory-specific iterate files:
   ```bash
   touch src/model_checker/theory_lib/default/iterate.py
   touch src/model_checker/theory_lib/bimodal/iterate.py
   # Add for other theories as needed
   ```

### Phase 2: Implement Core Iterator and Base Class

1. Implement `BaseModelIterator` in `iterate/core.py`:
   - Extract theory-agnostic code from `builder/iterate.py`
   - Define abstract methods that theories must implement
   - Implement generic iteration algorithm
   - **Remove** any theory-specific conditions and display methods
   - **Move** all theory-agnostic methods from theory-specific implementations

2. Move graph utilities:
   - Move `builder/graph_utils.py` to `iterate/graph_utils.py`
   - Update imports and references

### Phase 3: Implement Theory-Specific Iterators

1. Implement `DefaultModelIterator` in `theory_lib/default/iterate.py`:
   - Extract theory-specific code from `builder/iterate.py` and `theory_lib/default/semantic.py`
   - Implement all required abstract methods
   - Add theory-specific utilities
   - **Keep only** theory-specific logic, inheriting common functionality from the base class

2. Implement other theory iterators:
   - Follow the same pattern for all other theories
   - Ensure proper imports and dependencies

### Phase 4: Update Examples to Use Theory-Specific Iterators

1. Modify theory examples.py files:
   - Add theory-specific iterate_example wrapper functions
   - Update code that uses iteration to use the theory-specific wrappers

### Phase 5: Testing and Validation

1. Update test framework:
   - Update `test_package.py` to recognize new package
   - Ensure all tests pass with new structure

2. Test theory-specific iterations:
   - Verify each theory's iterator works correctly
   - Ensure results match previous implementation

## 7. Benefits of the New Design

1. **Clear Separation of Concerns**:
   - Core code has no knowledge of specific theories
   - Each theory fully controls its own iteration behavior

2. **Explicit Usage**:
   - Theory developers must explicitly specify which iterator to use
   - No hidden magic or auto-detection of theories

3. **Extensibility**:
   - Adding a new theory doesn't require modifying core code
   - Each theory can implement its own comparison logic

4. **Maintainability**:
   - Theory-specific code is isolated in the appropriate modules
   - Base functionality is centralized and reused

5. **Flexibility**:
   - Theory developers can define which semantic primitives or relations matter for comparison
   - Different theories can have completely different notions of model similarity

## 8. Practical Considerations

### Handling Theory-Specific Details

Each theory's iterator will be responsible for determining:
- Which semantic primitives are worth comparing when generating different models
- What constitutes a meaningful difference between models in that theory
- How to display differences between models for that theory

### Guidelines for Adding New Theories

1. Create a new file `theory_lib/<theory_name>/iterate.py`
2. Define a class `<TheoryName>ModelIterator` that inherits from `BaseModelIterator`
3. Implement all required abstract methods
4. Add a theory-specific wrapper for iterate_example in the theory's examples.py

### Theory-Specific Expectations

Each theory implementation should:
1. Specify which semantic primitives or defined relations make up the main ingredients of a model worth comparing
2. Define how to generate and print the differences between models effectively
3. Handle any theory-specific isomorphism detection
4. Implement all required abstract methods from the base class

## 9. Conclusion

The refactored iteration system will establish a clean and maintainable architecture that:

1. Maintains complete separation between theory-agnostic and theory-specific code
2. Requires explicit use of theory-specific iterators rather than dynamic detection
3. Allows each theory to define its own notion of model difference and comparison
4. Eliminates theory-specific conditions from the core code
5. Follows the project's design philosophy of making dependencies explicit and avoiding defaults

This approach ensures that the core iteration code will work with any theory without modification, while allowing each theory to fully customize its iteration behavior according to its specific semantic needs.