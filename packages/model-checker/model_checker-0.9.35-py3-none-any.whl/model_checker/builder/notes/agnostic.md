# Making iterate.py Theory-Agnostic

## Overview

The current implementation of `iterate.py` contains theory-specific code that needs to be refactored to use a more flexible, theory-agnostic approach. This document outlines a strategy for moving theory-specific details from `_create_non_isomorphic_constraint` to the semantic modules of each theory.

## Current Issues

1. `iterate.py` makes direct references to theory-specific concepts:
   - `world_states` which may not exist in all theories
   - The accessibility relation `R` which doesn't exist in any current theory 
   - Hard-coded assumptions about the structure of models

2. This creates several problems:
   - Tightly couples the iteration module to the default theory implementation
   - Makes it difficult to support different model structures across theories
   - Requires modification of iterate.py when adding new theories

## Solution Strategy

### 1. Define Theory Interface for Non-Isomorphic Constraint Generation

In each theory's `semantic.py`, define standardized methods that iterate.py can call:

```python
def get_differentiable_functions(self):
    """Returns functions that should be used to create difference constraints.
    
    Each theory can define which Z3 functions should be evaluated when 
    creating constraints to differentiate models.
    
    Returns:
        list: Tuples of (function_ref, arity, description)
    """
    # Return theory-specific functions
    return [
        (self.verify, 2, "verification"),
        (self.falsify, 2, "falsification"),
        (self.is_part_of, 2, "part-whole relation"),
        (self.possible, 1, "possibility"), 
        (self.is_world, 1, "world state")
    ]

def create_difference_constraints(self, prev_model):
    """Create theory-specific constraints to differentiate models.
    
    This method creates constraints that, when added to a solver,
    will ensure the next model differs from prev_model in ways that
    are semantically meaningful for this theory.
    
    Args:
        prev_model: The previous Z3 model to differ from
        
    Returns:
        list: Z3 constraints that force meaningful differences
    """
    # Generate theory-specific constraints
    constraints = []
    # ...theory-specific implementation...
    return constraints
```

### 2. Modify ModelStructure Class to Support Constraint Generation

Extend `ModelStructure` in each theory with methods to support non-isomorphic constraint generation:

```python
def get_world_properties(self, world, z3_model):
    """Get properties of a specific world for graph representation.
    
    This method extracts relevant properties from a world state that are
    used for isomorphism checking.
    
    Args:
        world: The world state to analyze
        z3_model: The current Z3 model
        
    Returns:
        dict: Dictionary of world properties
    """
    # Return theory-specific world properties
    properties = {}
    # ...implementation...
    return properties

def get_relation_edges(self, z3_model):
    """Get theory-specific relation edges for graph representation.
    
    Args:
        z3_model: The current Z3 model
        
    Returns:
        list: List of tuples (source, target, attributes) 
             for additional edges
    """
    # Return theory-specific edges
    extra_edges = []
    # ...implementation...
    return extra_edges

def get_structural_constraints(self, z3_model):
    """Generate constraints that force structural differences in the model.
    
    Args:
        z3_model: The current Z3 model to differ from
        
    Returns:
        list: List of Z3 constraints that force structural differences
    """
    # Return theory-specific structural constraints
    constraints = []
    # ...implementation...
    return constraints
```

### 3. Update ModelIterator._create_non_isomorphic_constraint

Refactor the method to use theory-specific implementations:

```python
def _create_non_isomorphic_constraint(self, z3_model):
    """Create a constraint that forces structural differences to avoid isomorphism."""
    if not HAS_NETWORKX:
        return None
            
    model_structure = self.build_example.model_structure
    semantics = model_structure.semantics
    
    # First try to use theory-specific difference constraints
    if hasattr(semantics, 'create_difference_constraints'):
        try:
            theory_constraints = semantics.create_difference_constraints(z3_model)
            if theory_constraints:
                return z3.Or(theory_constraints)
        except Exception as e:
            logger.warning(f"Error in theory-specific constraints: {e}")
    
    # Fall back to using model structure's constraints
    if hasattr(model_structure, 'get_structural_constraints'):
        try:
            structural_constraints = model_structure.get_structural_constraints(z3_model)
            if structural_constraints:
                return z3.Or(structural_constraints)
        except Exception as e:
            logger.warning(f"Error getting structural constraints: {e}")
    
    # If we reach here, we couldn't create constraints
    logger.warning("Could not create non-isomorphic constraints")
    return None
```

### 4. Update ModelGraph to Support Different Theories

Modify the ModelGraph class to use the theory-specific methods:

```python
def __init__(self, model_structure, z3_model):
    # ...existing initialization...
    
    # Use theory-specific properties for nodes
    for i, world in enumerate(model_structure.z3_world_states):
        # Get world properties using theory-specific method
        properties = model_structure.get_world_properties(world, z3_model)
        self.graph.add_node(i, **properties)
    
    # Use theory-specific relation edges
    extra_edges = model_structure.get_relation_edges(z3_model)
    for source, target, attrs in extra_edges:
        self.graph.add_edge(source, target, **attrs)
```

## Implementation Plan

### Phase 1: Add New Theory Interface Methods

1. Add `get_differentiable_functions` and `create_difference_constraints` to `default/semantic.py` Semantics class
2. Add model structure methods to `default/semantic.py` ModelStructure class
3. Create documentation for the new interface methods

### Phase 2: Refactor iterate.py

1. Update `_create_non_isomorphic_constraint` to use the new interface
2. Update `_create_stronger_constraint` to use the new interface
3. Remove theory-specific code from iterate.py
4. Update ModelGraph to use theory-specific methods

### Phase 3: Testing

1. Test with default theory to ensure backwards compatibility
2. Test with different theories to ensure they work correctly
3. Fix any issues discovered during testing

### Phase 4: Documentation and Examples

1. Update documentation for the new interface
2. Add examples of implementing the interface for different theories
3. Update developer guidelines for adding new theories

## Specific Implementation Details

### For default/semantic.py

The default theory already has some of the required methods:

1. `get_differentiable_functions` - Already exists, returns the core functions
2. `create_difference_constraints` - Already exists, creates verification/falsification constraints
3. `get_world_properties` - Already exists
4. `get_relation_edges` - Already exists
5. `get_structural_constraints` - Already exists

### For iterate.py

The main changes will be:

1. Remove explicit use of `world_states`
2. Remove references to accessibility relation `R`
3. Use theory-specific methods to get model structure information
4. Add graceful fallbacks for theories that don't implement all methods

## Migration Guidelines for Theory Developers

When creating a new theory, implement these methods:

1. In Semantics class:
   - `get_differentiable_functions()`
   - `create_difference_constraints(prev_model)`

2. In ModelStructure class:
   - `get_world_properties(world, z3_model)`
   - `get_relation_edges(z3_model)`
   - `get_structural_constraints(z3_model)`
   - `get_stronger_constraints(z3_model, escape_attempt)`

## Benefits of This Approach

1. **Modularity**: Each theory defines its own constraint generation logic
2. **Extensibility**: New theories can implement their own constraints without modifying iterate.py
3. **Cleaner Code**: Theory-specific details are kept in the appropriate modules
4. **Better Testing**: Theory-specific functionality can be tested independently
5. **More Flexibility**: Different theories can use different model structures