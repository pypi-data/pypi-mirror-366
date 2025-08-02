# Bimodal Logic Frame Constraints Review

This document provides a detailed analysis of the frame constraints implemented in the bimodal logic semantics. These constraints define the fundamental structure of bimodal logical models, particularly focusing on temporal-modal interactions.

## Overview of Bimodal Logic

Bimodal logic extends standard modal logic by adding a temporal dimension. The key elements of the model structure are:

- **World States**: Instantaneous configurations represented as bitvectors
- **Time Points**: Discrete points along a temporal axis
- **World Histories**: Temporally extended sequences of states that follow lawful transitions
- **Task Relation**: Defines valid transitions between consecutive world states

## Core Z3 Sorts and Primitives

### Sorts
1. **WorldStateSort**: BitVecSort representing instantaneous world states
2. **TimeSort**: IntSort representing time points 
3. **WorldIdSort**: IntSort mapping world IDs to world arrays

### Primitive Functions
1. **task**: Binary relation indicating valid transitions between world states
2. **world_function**: Maps world IDs to arrays representing world histories (time→state mappings)
3. **truth_condition**: Function assigning truth values to atomic propositions at states
4. **is_world**: Boolean function indicating whether a world_id maps to a valid world history
5. **world_interval_start/end**: Functions defining the time interval for each world

## Frame Constraints Analysis

The `build_frame_constraints` method establishes the following constraints:

### 1. Main World Validity
```python
valid_main_world = self.is_world(self.main_world)
```
Ensures the main world (ID 0) is a valid world history that can be used for evaluation.

### 2. Main Time Validity
```python
valid_main_time = self.is_valid_time(self.main_time)
```
Ensures the evaluation time is within the valid time range (-M+1, M-1).

### 3. Classical Truth Value Constraint
```python
classical_truth = z3.ForAll(
    [world_state, sentence_letter],
    z3.Or(
        self.truth_condition(world_state, sentence_letter),
        z3.Not(self.truth_condition(world_state, sentence_letter))
    )
)
```
Enforces that each sentence letter must have a definite truth value (true or false) at every world state, implementing classical bivalence.

### 4. World Enumeration Constraint
```python
enumeration_constraint = z3.ForAll(
    [enumerate_world],
    z3.Implies(
        self.is_world(enumerate_world),
        enumerate_world >= 0,
    )
)
```
Ensures world IDs start at 0 and are non-negative integers.

### 5. Convex World Ordering
```python
convex_world_ordering = z3.ForAll(
    [convex_world],
    z3.Implies(
        z3.And(
            self.is_world(convex_world),
            convex_world > 0,
        ),
        self.is_world(convex_world - 1)
    )
)
```
Implements "lazy" world creation by ensuring worlds are created in sequence without gaps in IDs. This ensures efficient allocation of world IDs.

### 6. Lawful Transitions
```python
lawful = z3.ForAll(
    [lawful_world, lawful_time],
    z3.Implies(
        z3.And(
            self.is_world(lawful_world),
            self.is_valid_time(lawful_time, -1),  
            self.is_valid_time_for_world(lawful_world, lawful_time),
            self.is_valid_time_for_world(lawful_world, lawful_time + 1),
        ),
        self.task(
            z3.Select(self.world_function(lawful_world), lawful_time),
            z3.Select(self.world_function(lawful_world), lawful_time + 1)
        )
    )
)
```
Requires that successive states in any world history must be connected by the task relation. This is the core constraint ensuring lawful temporal evolution of world states.

### 7. Abundance Constraint (Skolemized)
```python
skolem_abundance = self.skolem_abundance_constraint()
```
Uses Skolem functions to ensure the existence of time-shifted worlds. This optimization improves Z3 performance by eliminating nested quantifiers.

The constraint ensures that for any world that can be shifted forward or backward in time (within valid time bounds), there exists a corresponding world representing that time shift. This is crucial for evaluating modal operators like "necessarily" or "possibly" at different time points.

### 8. World Interval Constraint
```python
world_interval = self.world_interval_constraint()
```
Ensures each world has a valid time interval defined by start and end points, and that arrays are properly defined within these intervals.

### 9. World Uniqueness
```python
world_uniqueness = z3.ForAll(
    [world_one, world_two],
    z3.Implies(
        z3.And(
            self.is_world(world_one),
            self.is_world(world_two),
            world_one != world_two
        ),
        z3.Exists(
            [some_time],
            z3.And(
                self.is_valid_time(some_time),
                self.is_valid_time_for_world(world_one, some_time),
                self.is_valid_time_for_world(world_two, some_time),
                z3.Select(self.world_function(world_one), some_time) !=
                z3.Select(self.world_function(world_two), some_time)
            )
        )
    )
)
```
Requires distinct world IDs to have distinct histories - they must differ at at least one shared time point. This prevents redundant worlds with identical histories.

### 10. Task Relation Restriction (Currently Commented Out)
```python
# task_restriction = ...
```
When enabled, this would restrict the task relation to hold only between states that appear in consecutive positions in some world history. This ensures the task relation truly reflects possible temporal transitions.

### 11. Task State Minimization (Currently Commented Out)
```python
# task_minimization = self.build_task_minimization_constraint()
```
When enabled, this would encourage minimal state changes between consecutive time points, implementing a principle of temporal inertia where states tend to remain the same unless forced to change.

## Optimization Techniques

Several optimization techniques are employed to improve Z3 solver performance:

1. **Skolemization**: The abundance constraint uses Skolem functions instead of nested quantifiers
2. **Convex Ordering**: World IDs are allocated in sequence without gaps
3. **Lazy World Creation**: Worlds are created only as needed
4. **Bounded Time Intervals**: Each world has a specific time interval rather than covering all times
5. **Direct Interval Constraints**: The interval constraints use direct mappings rather than nested quantification

## Design Philosophy Alignment

These frame constraints align with the project's design philosophy:

1. **Fail Fast**: Constraints are strict and will naturally cause errors if violated
2. **Deterministic Behavior**: No default values or fallbacks are used in constraint definitions
3. **Required Parameters**: Parameters are explicitly required with no implicit conversions
4. **Clear Data Flow**: Constraints maintain a clear approach to data passing
5. **No Silent Failures**: No exception handling hides errors in constraint evaluation
6. **Explicit World References**: World IDs are explicitly provided where needed
7. **Prioritizing Code Quality**: The constraints focus on correctness and expressiveness

## Critical Implementation Details

1. **Time Representation**: Times range from -M+1 to M-1, centered around 0
2. **World Time Intervals**: Each world has a specific time interval within the global range
3. **Time Shifting**: The abundance constraint ensures worlds can be shifted in time
4. **Truth Evaluation**: The `true_at` method evaluates sentences at specific world-time pairs
5. **Model Verification**: The `verify_model` method confirms premises are true and conclusions are false

This implementation creates a robust framework for modeling temporal and modal logic, with carefully designed constraints that ensure well-formed models while supporting efficient solving.

## Refactoring Strategy: Unbounded World Histories

To refactor the bimodal semantics to support worlds as arbitrary functions from integers to world states (removing the fixed M time points limitation), consider the following strategies:

### 1. Rethinking Core Primitives

1. **Replace Interval Functions**: 
   - Remove `world_interval_start` and `world_interval_end` functions
   - Create a `defined_at_time` function that maps (world_id, time) to a boolean indicating whether a world is defined at that time point
   - Example: `defined_at_time = z3.Function('defined_at_time', self.WorldIdSort, self.TimeSort, z3.BoolSort())`

2. **Modify World Function**:
   - Keep `world_function` but handle undefined time points differently
   - Add constraints that make `world_function` return a special "undefined" state for times where a world isn't defined
   - Alternatively, require all worlds to be total functions but allow "default states" at irrelevant times

### 2. Core Constraint Modifications

1. **Lawful Transitions**: Update to check `defined_at_time` for both time points:
   ```python
   lawful = z3.ForAll(
       [lawful_world, lawful_time],
       z3.Implies(
           z3.And(
               self.is_world(lawful_world),
               self.defined_at_time(lawful_world, lawful_time),
               self.defined_at_time(lawful_world, lawful_time + 1),
           ),
           self.task(
               z3.Select(self.world_function(lawful_world), lawful_time),
               z3.Select(self.world_function(lawful_world), lawful_time + 1)
           )
       )
   )
   ```

2. **Temporal Coherence**: Add constraints that ensure worlds are temporally coherent:
   ```python
   temporal_coherence = z3.ForAll(
       [world_id, time],
       z3.Implies(
           z3.And(
               self.is_world(world_id),
               self.defined_at_time(world_id, time),
               # Gap in time:
               z3.Not(self.defined_at_time(world_id, time + 1)),
               # But defined again later:
               self.defined_at_time(world_id, time + k)  # for some k > 1
           ),
           False  # Disallow temporal gaps within a world
       )
   )
   ```

3. **Finite Support**: Ensure each world is defined at a finite (but unbounded) number of time points:
   ```python
   # This needs special handling in Z3 - might require indirect constraints
   # such as requiring each world to have a minimum and maximum defined time
   ```

### 3. Abundance Constraint Redesign

1. **Generalized Time Shifting**: Replace fixed shifts (+1/-1) with arbitrary shifts:
   ```python
   shifted_world = z3.Function('shifted_world', self.WorldIdSort, self.TimeSort, self.WorldIdSort)
   
   shift_constraint = z3.ForAll(
       [source_world, shift_amount],
       z3.Implies(
           self.is_world(source_world),
           z3.And(
               self.is_world(shifted_world(source_world, shift_amount)),
               # For all times where source is defined:
               z3.ForAll(
                   [time],
                   z3.Implies(
                       self.defined_at_time(source_world, time),
                       z3.And(
                           # Target world is defined at shifted time:
                           self.defined_at_time(
                               shifted_world(source_world, shift_amount), 
                               time + shift_amount
                           ),
                           # States match when accounting for shift:
                           z3.Select(self.world_function(source_world), time) ==
                           z3.Select(
                               self.world_function(shifted_world(source_world, shift_amount)), 
                               time + shift_amount
                           )
                       )
                   )
               )
           )
       )
   )
   ```

### 4. Model Extraction Changes

1. **Dynamic Time Range Discovery**:
   ```python
   def _extract_time_range(self, world_id):
       """Extract the minimum and maximum defined times for a world."""
       defined_times = []
       # Check a reasonable range first to establish bounds
       for time in range(-1000, 1000):  # Arbitrary large range
           if z3.is_true(self.z3_model.eval(self.defined_at_time(world_id, time))):
               defined_times.append(time)
               
       if not defined_times:
           return None, None  # World has no defined times
           
       return min(defined_times), max(defined_times)
   ```

2. **World History Extraction**:
   ```python
   def _extract_world_history(self, world_id):
       min_time, max_time = self._extract_time_range(world_id)
       if min_time is None:
           return {}  # Empty history
           
       history = {}
       for time in range(min_time, max_time + 1):
           if z3.is_true(self.z3_model.eval(self.defined_at_time(world_id, time))):
               state = self.safe_select(
                   self.z3_model,
                   self.world_function(world_id),
                   time
               )
               history[time] = bitvec_to_worldstate(state)
               
       return history
   ```

### 5. Settings and Initialization Updates

1. **Remove M Parameter**:
   - Remove `'M'` from settings
   - Remove all references to fixed time ranges
   - Add parameters for reasonable time search boundaries

2. **Initial World Configuration**:
   - Add constraints ensuring the main world is defined at time 0
   - Add constraints ensuring a minimum number of time points exist

### 6. Testing Considerations

1. **Gradual Migration**:
   - Implement side-by-side with the existing implementation
   - Create compatibility layers to ensure existing tests pass
   - Add new tests specifically targeting unbounded world functionality

2. **Boundary Testing**:
   - Test models with extremely distant time points
   - Test worlds with very sparse defined times
   - Test models with many distinct worlds

This refactoring would allow for much more flexible temporal modeling while maintaining the core principles of the bimodal framework. It would also better align with the project's design philosophy by removing arbitrary limits on time ranges.

## Detailed Implementation Strategy: Undefined State Approach

This section outlines a concrete implementation strategy using a special "undefined" state to represent times where a world history is not defined.

### 1. Core Primitive Modifications

```python
def define_primitives(self):
    # ... existing code ...
    
    # Define a special undefined state constant
    self.UNDEFINED_STATE = z3.BitVecVal(2**self.N - 1, self.N)  # All bits set
    
    # Define world function as a total function from times to states
    self.world_function = z3.Function(
        'world_function', 
        self.WorldIdSort,  # Input: world ID 
        z3.ArraySort(self.TimeSort, self.WorldStateSort)  # Output: world history
    )
    
    # Function to determine if a world_id maps to a valid world history
    self.is_world = z3.Function(
        'is_world',
        self.WorldIdSort,  # Input: world ID
        z3.BoolSort()      # Output: whether it's a valid world
    )
    
    # Function to determine if a world is defined at a specific time
    self.defined_at_time = z3.Function(
        'defined_at_time',
        self.WorldIdSort,  # Input: world ID
        self.TimeSort,     # Input: time
        z3.BoolSort()      # Output: whether world is defined at time
    )
```

### 2. Frame Constraint Implementation

```python
def build_frame_constraints(self):
    # ... existing world validity constraints ...
    
    # 1. Undefined State Constraint
    # States must either be properly defined or exactly equal to UNDEFINED_STATE
    world_id = z3.Int('undefined_constraint_world')
    time_point = z3.Int('undefined_constraint_time')
    undefined_state_constraint = z3.ForAll(
        [world_id, time_point],
        z3.Implies(
            z3.And(
                self.is_world(world_id),
                z3.Not(self.defined_at_time(world_id, time_point))
            ),
            z3.Select(self.world_function(world_id), time_point) == self.UNDEFINED_STATE
        )
    )
    
    # 2. Definition Coherence Constraint
    # Worlds must be defined for contiguous time intervals
    coherence_world = z3.Int('coherence_world')
    coherence_time = z3.Int('coherence_time')
    future_time = z3.Int('future_time')
    coherence_constraint = z3.ForAll(
        [coherence_world, coherence_time, future_time],
        z3.Implies(
            z3.And(
                self.is_world(coherence_world),
                self.defined_at_time(coherence_world, coherence_time),
                self.defined_at_time(coherence_world, future_time),
                coherence_time < future_time
            ),
            # All times between must also be defined
            z3.ForAll(
                [z3.Int('between_time')],
                z3.Implies(
                    z3.And(
                        coherence_time < z3.Int('between_time'),
                        z3.Int('between_time') < future_time
                    ),
                    self.defined_at_time(coherence_world, z3.Int('between_time'))
                )
            )
        )
    )
    
    # 3. Lawful Transitions Only Apply to Defined States
    lawful_world = z3.Int('lawful_world_id')
    lawful_time = z3.Int('lawful_time')
    lawful = z3.ForAll(
        [lawful_world, lawful_time],
        z3.Implies(
            z3.And(
                self.is_world(lawful_world),
                self.defined_at_time(lawful_world, lawful_time),
                self.defined_at_time(lawful_world, lawful_time + 1)
            ),
            self.task(
                z3.Select(self.world_function(lawful_world), lawful_time),
                z3.Select(self.world_function(lawful_world), lawful_time + 1)
            )
        )
    )
    
    # 4. Minimum Definition Constraint
    # Each world must be defined for at least one time point
    min_def_world = z3.Int('min_def_world')
    min_def_constraint = z3.ForAll(
        [min_def_world],
        z3.Implies(
            self.is_world(min_def_world),
            z3.Exists(
                [z3.Int('some_def_time')],
                self.defined_at_time(min_def_world, z3.Int('some_def_time'))
            )
        )
    )
    
    # 5. Main World Constraint
    # Main world must be defined at main time
    main_def_constraint = self.defined_at_time(self.main_world, self.main_time)
    
    # ... other constraints ...
    
    return [
        # ... existing constraints ...
        undefined_state_constraint,
        coherence_constraint,
        min_def_constraint,
        main_def_constraint,
        # ... other constraints ...
    ]
```

### 3. Semantic Evaluation with Undefined Checks

```python
def true_at(self, sentence, eval_world, eval_time):
    """Evaluate sentence truth, accounting for undefined states."""
    # First check if world is defined at time
    defined_expr = self.defined_at_time(eval_world, eval_time)
    
    # Handle undefined cases - can implement various semantics here:
    # Option 1: Undefined world-times make all sentences false
    # Option 2: Undefined world-times make atomic sentences false, but complex
    #           sentences are evaluated recursively
    # Option 3: Throw a specific error for undefined evaluation
    
    # Using Option 2 here:
    world_array = self.world_function(eval_world)
    
    sentence_letter = sentence.sentence_letter
    
    # Base case - for atomic sentences, require defined state
    if sentence_letter is not None:
        eval_world_state = z3.Select(world_array, eval_time)
        return z3.And(
            defined_expr,
            self.truth_condition(eval_world_state, sentence_letter)
        )

    # Recursive case - delegate to operator semantics
    operator = sentence.operator
    arguments = sentence.arguments or ()
    
    # Let operators handle undefined states appropriately
    return operator.true_at(*arguments, eval_world, eval_time)
```

### 4. Time-Shift Relations with Undefined Handling

```python
def is_shifted_by(self, source_world, shift, target_world):
    """Predicate that target_world is shifted from source_world by shift amount."""
    time = z3.Int('shift_check_time')
    source_array = self.world_function(source_world)
    target_array = self.world_function(target_world)
    
    return z3.ForAll(
        [time],
        z3.And(
            # Definition pattern must match when shifted
            self.defined_at_time(source_world, time) == 
            self.defined_at_time(target_world, time + shift),
            
            # States must match when both are defined
            z3.Implies(
                z3.And(
                    self.defined_at_time(source_world, time),
                    self.defined_at_time(target_world, time + shift)
                ),
                z3.Select(source_array, time) == z3.Select(target_array, time + shift)
            )
        )
    )
```

### 5. Model Extraction with Undefined Detection

```python
def _extract_world_histories(self, z3_model, worlds, world_arrays):
    """Extracts time-state mappings considering undefined states."""
    world_histories = {}
    
    for world_id in worlds:
        if world_id not in world_arrays:
            continue
            
        world_array = world_arrays[world_id]
        time_states = {}
        
        # Use a broader search range since we don't have fixed intervals
        for time in range(-1000, 1000):  # Adjustable range
            try:
                # Check if defined first
                is_defined = z3_model.eval(self.defined_at_time(world_id, time))
                
                if z3.is_true(is_defined):
                    # Only extract defined states
                    state = self.safe_select(z3_model, world_array, time)
                    
                    # Verify it's not the UNDEFINED_STATE
                    if state.eq(self.UNDEFINED_STATE).simplify().is_false():
                        # Convert to state representation
                        state_val = bitvec_to_worldstate(state)
                        time_states[time] = state_val
            except z3.Z3Exception:
                continue  # Skip problematic times
        
        # Only include worlds with at least one defined state
        if time_states:
            world_histories[world_id] = time_states
    
    return world_histories
```

### 6. Extension Methods for Propositions

```python
def find_extension(self):
    """Computes proposition extension accounting for undefined world-times."""
    extension = {}
    
    # Process atomic sentences
    if self.sentence_letter is not None:
        for world_id in self.model_structure.world_arrays.keys():
            true_times = []
            false_times = []
            
            # Start with a broader search range
            for time in range(-1000, 1000):  # Adjustable range
                try:
                    # Check if defined at this time
                    defined_expr = self.model_structure.semantics.defined_at_time(world_id, time)
                    is_defined = self.z3_model.evaluate(defined_expr)
                    
                    if z3.is_true(is_defined):
                        # Evaluate truth only at defined times
                        truth_expr = self.model_structure.semantics.true_at(
                            self.sentence, world_id, time
                        )
                        evaluated_expr = self.z3_model.evaluate(truth_expr)
                        
                        if z3.is_true(evaluated_expr):
                            true_times.append(time)
                        else:
                            false_times.append(time)
                except z3.Z3Exception:
                    continue  # Skip problematic evaluations
            
            if true_times or false_times:  # Only include non-empty results
                extension[world_id] = (true_times, false_times)
                
        return extension
    
    # Process complex sentences via operator semantics
    # ... existing operator handling ...
```

### 7. Performance Optimizations

1. **Bounded Time Search Strategy**:
   ```python
   def find_time_bounds(self, world_id):
       """Find reasonable bounds for time search to avoid checking -∞ to +∞."""
       # Start with small range
       for range_size in [10, 100, 1000, 10000]:
           min_time, max_time = -range_size, range_size
           
           # Check if world is defined at extremes
           if z3.is_true(self.z3_model.eval(self.defined_at_time(world_id, min_time))) or \
              z3.is_true(self.z3_model.eval(self.defined_at_time(world_id, max_time))):
               # If defined at boundary, double range and check again
               continue
               
           # No definitions at boundaries, use this range
           return min_time, max_time
       
       # Fallback to large default range
       return -10000, 10000
   ```

2. **Binary Search for First/Last Defined Times**:
   ```python
   def binary_search_defined(self, world_id, search_for_max=False):
       """Use binary search to find first or last defined time point efficiently."""
       min_bound, max_bound = self.find_time_bounds(world_id)
       
       if search_for_max:
           # Search for maximum defined time
           left, right = 0, max_bound
           result = None
           
           while left <= right:
               mid = (left + right) // 2
               if z3.is_true(self.z3_model.eval(self.defined_at_time(world_id, mid))):
                   result = mid  # Found a defined time
                   left = mid + 1  # Look for larger defined time
               else:
                   right = mid - 1  # Look in lower half
           
           return result
       else:
           # Search for minimum defined time
           left, right = min_bound, 0
           result = None
           
           while left <= right:
               mid = (left + right) // 2
               if z3.is_true(self.z3_model.eval(self.defined_at_time(world_id, mid))):
                   result = mid  # Found a defined time
                   right = mid - 1  # Look for smaller defined time
               else:
                   left = mid + 1  # Look in upper half
           
           return result
   ```

This implementation strategy leverages a special "undefined" state value to represent times where a world is not defined, providing a clean solution that maintains compatibility with existing code while removing the arbitrary time limits. The approach also includes optimizations for efficiently finding the bounds of defined time points for each world.