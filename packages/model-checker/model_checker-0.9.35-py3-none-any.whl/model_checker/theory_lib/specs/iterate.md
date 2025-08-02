# Implementation Plan for Theory-Specific Iteration

## Overview

This document outlines a plan for extending the `ModelIterator` functionality from the default theory to the bimodal, exclusion, and imposition theories in the ModelChecker framework. Each theory requires specific modifications to support iteration and difference calculation between successive models.

## Current Implementation

The current iteration system (in `builder/iterate.py`) works well with the default theory and provides:

1. A way to find multiple distinct models for a logical example
2. Constraints that require each new model to differ from previous models
3. Detection of model isomorphism to avoid redundant models
4. Tracking of differences between successive models
5. Visual representation of these differences

The default theory already implements difference tracking between models, which is visible in the dev_cli.py output:

```
=== DIFFERENCES FROM PREVIOUS MODEL ===

World Changes:
  + a.b.c (world)
  - b.c (world)
  - a.b (world)
  - a.c (world)

Possible State Changes:
  + a.b.c
  - b
  - a.b

Proposition Changes:
  A:
    Verifiers: {a, a.b.c, a.c, b.c, c, □}
      + {a, a.b.c, a.c, b.c, c, □}
      - {a.b, b}
    Falsifiers: {a, c}
      + {a, c}
      - {a.c}
...
```

## Implementation Requirements

To extend this functionality to other theories, each theory needs to implement:

1. **Theory-specific difference calculation**: A method `calculate_model_differences()` to identify relevant changes between models
2. **Model structure initialization for iteration**: Proper support for re-initializing model structures during iteration
3. **Differentiable component extraction**: A method `get_differentiable_components()` to identify theory-specific elements that should differ
4. **Structural constraint generation**: A method `get_structural_constraints()` to guide the search for non-isomorphic models

## Theory-Specific Implementation Plans

### 1. Bimodal Theory (`bimodal/semantic.py`)

The bimodal theory requires special handling due to its temporal dimension. 

#### Implementation Tasks:

1. **Add `calculate_model_differences()` method to `BimodalStructure`:**
   ```python
   def calculate_model_differences(self, previous_structure):
       """Calculate differences between this model and a previous model.
       
       Returns a structured dictionary of differences:
       {
           "world_changes": {added: [], removed: []},
           "time_changes": {added: [], removed: []},
           "state_changes": {added: [], removed: []},
           "proposition_changes": {...},
           "relation_changes": {...}
       }
       """
       differences = {
           "world_changes": {"added": [], "removed": []},
           "time_changes": {"added": [], "removed": []}, 
           "state_changes": {"added": [], "removed": []},
           "proposition_changes": {},
           "relation_changes": {}
       }
       
       # Compare world arrays and time intervals
       self._compare_world_arrays(previous_structure, differences)
       
       # Compare time points in each world
       self._compare_time_points(previous_structure, differences)
       
       # Compare states at each time point in each world
       self._compare_world_states(previous_structure, differences)
       
       # Compare proposition values
       self._compare_propositions(previous_structure, differences)
       
       # Compare task relations
       self._compare_task_relations(previous_structure, differences)
       
       return differences
   ```

2. **Add helper methods for difference calculation:**
   ```python
   def _compare_world_arrays(self, previous_structure, differences):
       """Compare world arrays between models and track additions/removals."""
       # Implementation details
       
   def _compare_time_points(self, previous_structure, differences):
       """Compare time points between models and track additions/removals."""
       # Implementation details
       
   def _compare_world_states(self, previous_structure, differences):
       """Compare states at each time point in each world."""
       # Implementation details
       
   def _compare_propositions(self, previous_structure, differences):
       """Compare truth values of propositions across worlds and times."""
       # Implementation details
       
   def _compare_task_relations(self, previous_structure, differences):
       """Compare task relations between successive states."""
       # Implementation details
   ```

3. **Implement `get_differentiable_components()` method:**
   ```python
   def get_differentiable_components(self, z3_model):
       """Return a list of differentiable components in the model.
       
       Each component is a tuple (function, args, value) that can be used
       to create difference constraints.
       """
       components = []
       
       # 1. Add world function components
       for world_id in range(self.max_world_id):
           if z3_model.eval(self.semantics.is_world(world_id), model_completion=True):
               world_array = self.semantics.world_function(world_id)
               for time in range(-self.M+1, self.M):
                   try:
                       state = self.semantics.safe_select(z3_model, world_array, time)
                       components.append((
                           lambda w, t: z3.Select(self.semantics.world_function(w), t),
                           [world_id, time],
                           state
                       ))
                   except z3.Z3Exception:
                       pass
       
       # 2. Add task relation components
       for s1 in self.all_states:
           for s2 in self.all_states:
               try:
                   value = z3_model.eval(self.semantics.task(s1, s2), model_completion=True)
                   components.append((self.semantics.task, [s1, s2], value))
               except z3.Z3Exception:
                   pass
       
       # 3. Add truth condition components
       for state in self.all_states:
           for letter in self.model_constraints.sentence_letters:
               try:
                   value = z3_model.eval(self.semantics.truth_condition(state, letter), model_completion=True)
                   components.append((self.semantics.truth_condition, [state, letter], value))
               except z3.Z3Exception:
                   pass
                   
       return components
   ```

4. **Implement `get_structural_constraints()` method:**
   ```python
   def get_structural_constraints(self, z3_model):
       """Return constraints that force structural differences.
       
       These constraints help guide Z3 towards finding models with different
       structure, helping to escape from isomorphic models.
       """
       constraints = []
       
       # 1. Force different number of worlds
       current_world_count = sum(1 for i in range(self.max_world_id) 
                               if z3_model.eval(self.semantics.is_world(i), model_completion=True))
       
       # Force either more or fewer worlds
       world_count_expr = z3.IntVal(0)
       for i in range(self.max_world_id):
           world_count_expr = z3.If(self.semantics.is_world(i), world_count_expr + 1, world_count_expr)
           
       if current_world_count > 1:
           constraints.append(world_count_expr <= current_world_count - 1)
       constraints.append(world_count_expr >= current_world_count + 1)
       
       # 2. Force different world interval structure
       # Implementation details
       
       # 3. Force different task relations
       # Implementation details
       
       return constraints
   ```

5. **Update `BimodalStructure.__init__` to properly handle re-initialization during iteration**

### 2. Exclusion Theory (`exclusion/semantic.py`)

Exclusion theory has a different semantic basis with exclusion relations instead of the usual mereological relations.

#### Implementation Tasks:

1. **Add `calculate_model_differences()` method to `ExclusionStructure`:**
   ```python
   def calculate_model_differences(self, previous_structure):
       """Calculate differences between this model and a previous model.
       
       Returns a structured dictionary of differences:
       {
           "world_changes": {added: [], removed: []},
           "possible_state_changes": {added: [], removed: []},
           "exclusion_changes": {added: [], removed: []},
           "proposition_changes": {...}
       }
       """
       differences = {
           "world_changes": {"added": [], "removed": []},
           "possible_state_changes": {"added": [], "removed": []},
           "exclusion_changes": {"added": [], "removed": []},
           "proposition_changes": {}
       }
       
       # Compare world states
       self._compare_world_states(previous_structure, differences)
       
       # Compare possible states
       self._compare_possible_states(previous_structure, differences)
       
       # Compare exclusion relations
       self._compare_exclusion_relations(previous_structure, differences)
       
       # Compare proposition values
       self._compare_propositions(previous_structure, differences)
       
       return differences
   ```

2. **Add helper methods for difference calculation:**
   ```python
   def _compare_world_states(self, previous_structure, differences):
       """Compare world states between models and track additions/removals."""
       # Implementation details
       
   def _compare_possible_states(self, previous_structure, differences):
       """Compare possible states between models and track additions/removals."""
       # Implementation details
       
   def _compare_exclusion_relations(self, previous_structure, differences):
       """Compare exclusion relations between models."""
       # Implementation details
       
   def _compare_propositions(self, previous_structure, differences):
       """Compare proposition verifiers and precluders between models."""
       # Implementation details
   ```

3. **Implement `get_differentiable_components()` method:**
   ```python
   def get_differentiable_components(self, z3_model):
       """Return a list of differentiable components in the model.
       
       Each component is a tuple (function, args, value) that can be used
       to create difference constraints.
       """
       components = []
       
       # 1. Add verification components
       for state in self.all_states:
           for letter in self.model_constraints.sentence_letters:
               try:
                   value = z3_model.eval(self.semantics.verify(state, letter), model_completion=True)
                   components.append((self.semantics.verify, [state, letter], value))
               except z3.Z3Exception:
                   pass
       
       # 2. Add exclusion relation components
       for s1 in self.all_states:
           for s2 in self.all_states:
               try:
                   value = z3_model.eval(self.semantics.excludes(s1, s2), model_completion=True)
                   components.append((self.semantics.excludes, [s1, s2], value))
               except z3.Z3Exception:
                   pass
       
       # 3. Add possibility components
       for state in self.all_states:
           try:
               value = z3_model.eval(self.semantics.possible(state), model_completion=True)
               components.append((self.semantics.possible, [state], value))
           except z3.Z3Exception:
               pass
                   
       return components
   ```

4. **Implement `get_structural_constraints()` method:**
   ```python
   def get_structural_constraints(self, z3_model):
       """Return constraints that force structural differences."""
       constraints = []
       
       # 1. Force different patterns of exclusion relations
       # Implementation details
       
       # 2. Force different verification patterns
       # Implementation details
       
       # 3. Force different world states
       # Implementation details
       
       return constraints
   ```

5. **Ensure proper handling of the `iterate` setting in the DEFAULT_EXAMPLE_SETTINGS**

### 3. Imposition Theory (`imposition/semantic.py`)

Imposition theory uses imposition relations for counterfactuals rather than alternatives.

#### Implementation Tasks:

1. **Add `calculate_model_differences()` method to `ImpositionStructure`:**
   ```python
   def calculate_model_differences(self, previous_structure):
       """Calculate differences between this model and a previous model.
       
       Returns a structured dictionary of differences:
       {
           "world_changes": {added: [], removed: []},
           "possible_state_changes": {added: [], removed: []},
           "imposition_changes": {added: [], removed: []},
           "proposition_changes": {...}
       }
       """
       differences = {
           "world_changes": {"added": [], "removed": []},
           "possible_state_changes": {"added": [], "removed": []},
           "imposition_changes": {"added": [], "removed": []},
           "proposition_changes": {}
       }
       
       # Compare world states
       self._compare_world_states(previous_structure, differences)
       
       # Compare possible states
       self._compare_possible_states(previous_structure, differences)
       
       # Compare imposition relations
       self._compare_imposition_relations(previous_structure, differences)
       
       # Compare proposition values
       self._compare_propositions(previous_structure, differences)
       
       return differences
   ```

2. **Add helper methods for difference calculation:**
   ```python
   def _compare_world_states(self, previous_structure, differences):
       """Compare world states between models and track additions/removals."""
       # Implementation details
       
   def _compare_possible_states(self, previous_structure, differences):
       """Compare possible states between models and track additions/removals."""
       # Implementation details
       
   def _compare_imposition_relations(self, previous_structure, differences):
       """Compare imposition relations between models."""
       # Implementation details
       
   def _compare_propositions(self, previous_structure, differences):
       """Compare proposition verifiers and falsifiers between models."""
       # Implementation details
   ```

3. **Implement `get_differentiable_components()` method:**
   ```python
   def get_differentiable_components(self, z3_model):
       """Return a list of differentiable components in the model."""
       components = []
       
       # 1. Add verification components
       for state in self.all_states:
           for letter in self.model_constraints.sentence_letters:
               try:
                   value = z3_model.eval(self.semantics.verify(state, letter), model_completion=True)
                   components.append((self.semantics.verify, [state, letter], value))
               except z3.Z3Exception:
                   pass
                   
       # 2. Add falsification components
       for state in self.all_states:
           for letter in self.model_constraints.sentence_letters:
               try:
                   value = z3_model.eval(self.semantics.falsify(state, letter), model_completion=True)
                   components.append((self.semantics.falsify, [state, letter], value))
               except z3.Z3Exception:
                   pass
       
       # 3. Add imposition relation components
       for s1 in self.all_states:
           for w in self.all_states:
               for s2 in self.all_states:
                   try:
                       value = z3_model.eval(self.semantics.imposition(s1, w, s2), model_completion=True)
                       components.append((self.semantics.imposition, [s1, w, s2], value))
                   except z3.Z3Exception:
                       pass
                   
       return components
   ```

4. **Implement `get_structural_constraints()` method:**
   ```python
   def get_structural_constraints(self, z3_model):
       """Return constraints that force structural differences."""
       constraints = []
       
       # 1. Force different imposition patterns
       # Implementation details
       
       # 2. Force different verification patterns
       # Implementation details
       
       # 3. Force different world states
       # Implementation details
       
       return constraints
   ```

5. **Add ImpositionStructure class and update the DEFAULT_EXAMPLE_SETTINGS to include the iterate setting**

## Common Tasks for All Theories

1. **Update DEFAULT_EXAMPLE_SETTINGS** to include iteration-related settings:
   ```python
   DEFAULT_EXAMPLE_SETTINGS = {
       # ... existing settings ...
       'iterate': 1,                   # Maximum number of models to find
       'iteration_attempts': 5,        # Max consecutive isomorphic models before applying stronger constraints
       'escape_attempts': 3,       # Max attempts to escape from isomorphic models
       'iteration_timeout': 1.0,       # Max time for isomorphism checking
   }
   ```

2. **Implement print_differences() methods** to display the differences between successive models:
   ```python
   def print_differences(self, output=sys.__stdout__):
       """Print differences from the previous model."""
       if not hasattr(self, 'model_differences') or not self.model_differences:
           return
           
       print("\n=== DIFFERENCES FROM PREVIOUS MODEL ===\n", file=output)
       
       # Theory-specific implementation for printing differences
       # ...
   ```

## Integration with ModelIterator

Ensure that the `ModelIterator` class can properly work with each theory by:

1. Adding theory detection to choose the appropriate difference calculation method
2. Testing the iteration process with each theory
3. Ensuring proper visualization of differences for each theory

## Implementation Phases

1. **Phase 1:** Implement the `iterate` setting and basic difference tracking for each theory
2. **Phase 2:** Implement advanced isomorphism detection for more efficient iteration
3. **Phase 3:** Add visualization improvements for theory-specific differences

## Testing Strategy

For each theory, create test examples that use the iterate setting:

```python
# Test examples for bimodal theory
example_iterate_bimodal = {
    "name": "iterate_bimodal",
    "premises": ["p → □q"],
    "conclusions": ["□(p → q)"],
    "settings": {
        "N": 2,
        "M": 2,
        "iterate": 3,
        "max_time": 5
    }
}

# Test examples for exclusion theory
example_iterate_exclusion = {
    "name": "iterate_exclusion",
    "premises": ["p", "p ∨ q"],
    "conclusions": ["q"],
    "settings": {
        "N": 3,
        "iterate": 3,
        "max_time": 5
    }
}

# Test examples for imposition theory
example_iterate_imposition = {
    "name": "iterate_imposition",
    "premises": ["p", "p > q"],
    "conclusions": ["q"],
    "settings": {
        "N": 3,
        "iterate": 3,
        "max_time": 5
    }
}
```

Run these examples and verify that:
1. Multiple distinct models are found
2. Differences are correctly identified and displayed
3. Performance remains acceptable

## Conclusion

This implementation plan provides a structured approach to extending the iterate functionality across all theories in the ModelChecker framework. By implementing theory-specific difference calculation and visualization, we'll enable users to explore multiple models for any theory, enhancing the framework's analytical capabilities.
