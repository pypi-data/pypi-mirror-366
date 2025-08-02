# Strategy for Optimizing Model Size in Bimodal Logic

## Problem Statement

The current implementation of bimodal semantics creates models with excessive complexity in two dimensions:

1. **Excess Worlds**: Even simple examples may create up to 100 nearly identical worlds (the `max_world_id` limit), when only 2-3 distinct worlds would be sufficient to satisfy the constraints.

2. **Excess Time Points**: Each world history may contain unnecessary time points that don't contribute to satisfying the constraints.

This inefficiency leads to:

1. Slower model generation due to larger constraint sets
2. Difficult-to-interpret output with redundant worlds and time points
3. Excessive memory usage for storing duplicate world histories
4. Potentially hitting system limits for complex models

## Current Progress

### Phase 1: World Count Limitation (COMPLETED)

We have successfully implemented and tested Phase 1 of our optimization strategy by limiting the number of worlds created in a model:

1. Added a `max_worlds` setting to `DEFAULT_EXAMPLE_SETTINGS` with a default value of 5.
2. Implemented a world count constraint in `world_interval_constraint()` that ensures no worlds with IDs >= `max_worlds` are created.
3. Created tests that verify the limitation works correctly for both:
   - Default maximum (5 worlds)
   - Custom maximum (as specified in settings)
   - Complex modal formulas

Phase 1 has successfully addressed the issue of excess worlds, allowing us to focus on the remaining phases and on optimizing time points.

## Time Point Optimization Strategy

Just as we limited the number of worlds, we should also limit the number of time points in each world. The current implementation has these issues:

1. **Excessive Time Points**: Worlds contain many undefined or redundant time points.
2. **Arbitrary Time Ranges**: The time range is defined by `time_search_range` (default: 1000), leading to unnecessarily large search spaces.
3. **No Temporal Minimization**: Z3 has no guidance to use the minimal set of time points needed.

### Core Approach to Time Optimization

1. **Time Range Restriction**: Limit the range of time points around the main time point.
2. **Time Point Minimization**: Create constraints that encourage Z3 to use the minimal number of time points per world.
3. **Relevant Time Points**: Focus on time points that directly contribute to formula evaluation.

## Implementation Plan for Time Optimization

### Phase 1-T: Explicit Time Range Narrowing

1. Add a new `min_time_range` setting to control the minimum time range around the main time (default: 2):

```python
DEFAULT_EXAMPLE_SETTINGS = {
    # Existing settings...
    'max_worlds': 5,
    'min_time_range': 2,  # New setting - minimum range around main time
}
```

2. Implement a constraint that limits the time range in each world to only what's necessary:

```python
def build_time_limit_constraint(self):
    """Build constraint limiting time points in each world."""
    world_id = z3.Int('time_limit_world')
    time_point = z3.Int('time_limit_point')
    min_range = self.settings.get('min_time_range', 2)
    
    # Calculate min/max time based on main_time
    min_time = self.main_time - min_range
    max_time = self.main_time + min_range
    
    # Only time points within range can be defined
    time_range_constraint = z3.ForAll(
        [world_id, time_point],
        z3.Implies(
            z3.And(
                self.is_world(world_id),
                z3.Or(time_point < min_time, time_point > max_time)
            ),
            # Time points outside the range must be undefined
            z3.Not(self.defined_at_time(world_id, time_point))
        )
    )
    
    return time_range_constraint
```

3. Add this constraint to the frame constraints:

```python
def build_frame_constraints(self):
    # Existing constraints...
    
    # Add time limit constraint
    time_limit = self.build_time_limit_constraint()
    
    return [
        # Existing constraints...
        time_limit
    ]
```

### Phase 2-T: Optimized Time Point Requirements

Add constraints that ensure only necessary time points are defined:

```python
def build_minimal_time_constraint(self):
    """Ensure only time points that contribute to formula evaluation are defined."""
    world_id = z3.Int('min_time_world')
    time_point = z3.Int('min_time_point')
    
    # Get sentence objects from model constraints
    sentences = self.model_constraints.syntax.all_sentences
    
    # Create a constraint requiring time points to be used in some evaluation
    time_usage_constraint = z3.ForAll(
        [world_id, time_point],
        z3.Implies(
            z3.And(
                self.is_world(world_id),
                self.defined_at_time(world_id, time_point),
                time_point != self.main_time  # Always allow main time
            ),
            # This time point must be used for evaluating some sentence
            z3.Or([
                # Either in a premise evaluation
                z3.Or([self._time_used_in_evaluation(s, world_id, time_point) 
                      for s in self.model_constraints.syntax.premises]),
                # Or in a conclusion evaluation
                z3.Or([self._time_used_in_evaluation(s, world_id, time_point) 
                      for s in self.model_constraints.syntax.conclusions])
            ])
        )
    )
    
    return time_usage_constraint

def _time_used_in_evaluation(self, sentence, world_id, time_point):
    """Determine if a time point is used when evaluating a sentence."""
    # Base case - for atomic sentences, only the time itself is used
    if sentence.sentence_letter is not None:
        return time_point == self.main_time
    
    # For modal/temporal operators, delegate to operator implementation
    operator = sentence.operator
    arguments = sentence.arguments or ()
    
    # Only certain operators actually need additional time points
    if hasattr(operator, 'time_points_required'):
        return operator.time_points_required(*arguments, world_id, time_point)
    
    # Default to requiring only main time
    return time_point == self.main_time
```

This requires adding `time_points_required` methods to temporal operators (e.g., Diamond, Box) to specify which time points they need.

### Phase 3-T: Z3 Optimization for Time Points

Implement a constraint that directly minimizes the number of defined time points:

```python
def add_time_optimization_objective(self, optimizer):
    """Add objective to minimize the number of defined time points."""
    world_id = z3.Int('opt_time_world')
    time_point = z3.Int('opt_time_point')
    min_range = self.settings.get('min_time_range', 2)
    
    # Calculate time range around main time
    min_time = self.main_time - min_range
    max_time = self.main_time + min_range
    
    # Count defined time points in all worlds
    defined_times_count = z3.Sum([
        z3.Sum([
            z3.If(self.defined_at_time(i, t), 1, 0)
            for t in range(min_time, max_time + 1)
        ])
        for i in range(self.max_world_id)
    ])
    
    # Add objective to minimize defined time points
    optimizer.minimize(defined_times_count)
```

### Phase 4-T: Comprehensive Time and World Optimization

Integrate time and world optimization into a cohesive framework:

1. Create a new `ModelOptimizer` class:

```python
class ModelOptimizer:
    """Class for optimizing model size in both world and time dimensions."""
    
    def __init__(self, semantics, constraints):
        self.semantics = semantics
        self.constraints = constraints
        self.settings = semantics.settings
    
    def build_minimal_model(self):
        """Build a model that minimizes both worlds and time points."""
        optimizer = z3.Optimize()
        
        # Add all standard constraints
        for constraint in self.constraints:
            optimizer.add(constraint)
        
        # Add world count minimization objective
        self._add_world_minimization(optimizer)
        
        # Add time point minimization objective
        self._add_time_minimization(optimizer)
        
        # Set solver parameters
        optimizer.set("timeout", self.settings.get("max_time", 1) * 1000)
        
        # Check if model exists
        if optimizer.check() == z3.sat:
            return optimizer.model()
        return None
    
    def _add_world_minimization(self, optimizer):
        """Add objective to minimize the number of worlds."""
        world_count = z3.Sum([
            z3.If(self.semantics.is_world(i), 1, 0) 
            for i in range(self.semantics.max_world_id)
        ])
        optimizer.minimize(world_count)
    
    def _add_time_minimization(self, optimizer):
        """Add objective to minimize the number of defined time points."""
        # Implementation from Phase 3-T
```

2. Integrate with existing model construction:

```python
def create_model(self):
    """Create a model with minimal worlds and time points."""
    # Traditional approach as fallback
    if not self.settings.get("optimize", True):
        return super().create_model()
    
    # Create optimizer
    optimizer = ModelOptimizer(self, self.constraints)
    
    # Try to build minimal model
    model = optimizer.build_minimal_model()
    
    # If optimization fails, fall back to standard approach
    if model is None:
        return super().create_model()
        
    return model
```

## Expected Outcomes of Time Optimization

With these changes, we expect to see:

1. Models with minimal time points, focusing only on those required for formula evaluation
2. Much faster model generation due to drastically smaller search spaces
3. More comprehensible output showing only essential time points
4. Support for more complex formulas without performance degradation

## Testing Plan for Time Optimization

1. **Base Test**: Simple formulas should have minimal time points (just enough to satisfy the constraints)
2. **Modal Test**: Formulas with modal operators should include only necessary additional time points
3. **Complex Test**: Complex formulas with nested modal/temporal operators should still find minimal models
4. **Performance Test**: Compare solving times before and after optimization

## Next Steps

1. Implement Phase 1-T: Time Range Narrowing
2. Test the implementation with simple formulas
3. Assess performance improvement
4. Proceed to Phase 2-T if additional optimization is needed

## Implementation Timeline

1. Phase 1-T (Time Range Narrowing): 1-2 days
2. Phase 2-T (Required Time Points): 2-3 days
3. Phase 3-T (Z3 Optimization): 2-3 days
4. Phase 4-T (Integrated Framework): 3-4 days

Total estimated time: 8-12 days for complete implementation