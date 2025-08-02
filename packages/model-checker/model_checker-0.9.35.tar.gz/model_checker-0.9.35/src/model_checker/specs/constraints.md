# Bimodal Theory Refactoring Strategy: Time-Indexed World Functions

## Overview

This document outlines a strategy for refactoring the bimodal semantic theory to represent worlds as functions from time points to world states, with a focus on minimizing model size and improving performance.

## Important Clarifications

This implementation is for a **non-standard bimodal logic** with these key characteristics:

1. **No Accessibility Relation**: Unlike standard modal logic, there is no accessibility relation between worlds. Modal operators (□, ◇) quantify over all worlds without restriction.

2. **Task Relations Within Worlds**: Each world represents a function from times to world states, where the task relation must hold between consecutive states within the same world.

3. **Operator Implementation Preservation**: The existing semantics in `operators.py` are correct and should be preserved. Changes focus on representation and constraint generation.

4. **One-Time Constraint Generation**: Premise and conclusion constraints should be generated once and added to the solver upfront, not dynamically during evaluation.

## Current Implementation

The current implementation in `bimodal/semantic.py` represents worlds as:

- `world_function`: Maps world IDs to arrays, where each array maps times to world states
- `is_world`: Boolean function determining if a world ID refers to a valid world
- `defined_at_time`: Boolean function determining if a world is defined at a specific time
- Various explicit constraints that manage world relationships and frame properties

Issues with the current approach:
1. Models often contain more worlds than necessary
2. Models may include more time points than needed
3. Having to explicitly set `max_worlds` and time search ranges creates inefficient models
4. Constraints are complex and potentially redundant

## Refactoring Goals

1. **Minimal World Creation**: Models should only create the worlds and time points needed to satisfy the constraints
2. **Lazy Evaluation**: Avoid explicit maximum limits, allowing Z3 to determine optimal model size
3. **Natural Time Intervals**: World histories should have naturally coherent intervals without artificial constraints
4. **Frame Constraint Simplification**: Streamline frame constraints to improve solver performance
5. **Consistent World Referencing**: Use world IDs consistently throughout the codebase

## Implementation Strategy

### Phase 1: Core Data Structure Adjustments

#### 1.1 Update Primitives Definition
```python
def define_primitives(self):
    """Define the Z3 primitive functions and relations used in the bimodal logic model."""
    # Define the task relation between world states
    self.task = z3.Function(
        "Task",
        self.WorldStateSort,
        self.WorldStateSort,
        z3.BoolSort()
    )

    # Mapping from world IDs to world histories (arrays from time to state)
    self.world_function = z3.Function(
        'world_function', 
        self.WorldIdSort,  # Input: world ID 
        z3.ArraySort(self.TimeSort, self.WorldStateSort)  # Output: world history
    )
    
    # Function to determine if a world_id maps to a valid world history
    self.is_world = z3.Function(
        'is_world',
        self.WorldIdSort,  # Input: world ID
        z3.BoolSort()      # Output: whether it's a valid world history
    )
    
    # Function to determine if a world is defined at a specific time
    self.defined_at_time = z3.Function(
        'defined_at_time',
        self.WorldIdSort,  # Input: world ID
        self.TimeSort,     # Input: time
        z3.BoolSort()      # Output: whether world is defined at time
    )
    
    # Remove explicit maximum world ID limit
    # We'll rely on Z3's natural minimality instead
    
    # Truth condition for atomic propositions at world states
    self.truth_condition = z3.Function(
        "truth_condition",
        self.WorldStateSort,
        syntactic.AtomSort,
        z3.BoolSort()
    )
    
    # Dictionary to store world time intervals after extraction
    self.world_time_intervals = {}
    
    # Main point of evaluation with world ID and time
    self.main_world = z3.IntVal(0)
    self.main_time = z3.IntVal(0)
    self.main_point = {
        "world": self.main_world,
        "time": self.main_time,
    }
```

#### 1.2 Update World ID References
Ensure consistent world ID references throughout the codebase:
- Make all methods that work with worlds take world IDs as inputs
- Never use world arrays directly in method signatures
- Update `BimodalProposition` to work exclusively with world IDs
- Update `BimodalStructure` to use world IDs as primary keys

#### 1.3 World ID Validation Function
```python
def validate_world_id(self, world_id):
    """Validate that a world ID is of the correct type."""
    if not isinstance(world_id, int) and not (
        isinstance(world_id, z3.ArithRef) and world_id.sort() == self.WorldIdSort
    ):
        raise TypeError(f"World ID must be an integer or Z3 Int, got {type(world_id)}: {world_id}")
    return world_id
```

### Phase 2: Frame Constraint Optimization

```python
def build_frame_constraints(self):
    """Build the frame constraints for the bimodal logic model.
    
    This method constructs the fundamental constraints that define the behavior 
    of the model with a focus on minimal world and time creation.
    
    The implementation should be tested with increasingly complex constraint sets:
    1. Start with core constraints (main_point_constraint, enumerate_worlds, etc.)
    2. Add more complex constraints gradually during testing (temporal coherence, etc.)
    3. Finally add all complex constraints (world uniqueness, skolem abundance, etc.)
    """
    constraints = []
    
    # 1. The main point exists - world 0 at time 0 is defined
    main_point_constraint = z3.And(
        self.is_world(self.main_world),
        self.defined_at_time(self.main_world, self.main_time)
    )
    constraints.append(main_point_constraint)

    # 2. World enumeration starts at 0 and is continuous
    enumerate_world = z3.Int('enumerate_world')
    enumerate_worlds = z3.ForAll(
        [enumerate_world],
        z3.Implies(
            self.is_world(enumerate_world),
            enumerate_world >= 0
        )
    )
    constraints.append(enumerate_worlds)
    
    # 3. Worlds form a convex ordering (no gaps)
    convex_world = z3.Int('convex_world')
    convex_world_ordering = z3.ForAll(
        [convex_world],
        z3.Implies(
            z3.And(self.is_world(convex_world), convex_world > 0),
            self.is_world(convex_world - 1)
        )
    )
    constraints.append(convex_world_ordering)
    
    # 4. All worlds have at least one time point
    world_has_time = z3.Int('world_has_time')
    time_existence = z3.Int('time_existence')
    worlds_have_times = z3.ForAll(
        [world_has_time],
        z3.Implies(
            self.is_world(world_has_time),
            z3.Exists(
                [time_existence],
                self.defined_at_time(world_has_time, time_existence)
            )
        )
    )
    constraints.append(worlds_have_times)

    # 5. Time intervals are coherent (no gaps)
    coherence_world = z3.Int('coherence_world')
    coherence_time = z3.Int('coherence_time') 
    future_time = z3.Int('future_time')
    between_time = z3.Int('between_time')
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
                [between_time],
                z3.Implies(
                    z3.And(coherence_time < between_time, between_time < future_time),
                    self.defined_at_time(coherence_world, between_time)
                )
            )
        )
    )
    constraints.append(coherence_constraint)
    
    # 6. Each sentence letter has a definite truth value at each state
    world_state = z3.BitVec('world_state', self.N)
    sentence_letter = z3.Const('atom_interpretation', syntactic.AtomSort)
    classical_truth = z3.ForAll(
        [world_state, sentence_letter],
        z3.Or(
            self.truth_condition(world_state, sentence_letter),
            z3.Not(self.truth_condition(world_state, sentence_letter))
        )
    )
    constraints.append(classical_truth)
    
    # 7. Worlds are lawful (consecutive states follow task relation)
    lawful_world = z3.Int('lawful_world_id')
    lawful_time = z3.Int('lawful_time')
    worlds_are_lawful = z3.ForAll(
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
    constraints.append(worlds_are_lawful)

    # 8. Every valid world is unique
    world_one = z3.Int('world_one')
    world_two = z3.Int('world_two')
    some_time = z3.Int('some_time')
    world_uniqueness = z3.ForAll(
        [world_one, world_two],
        z3.Implies(
            z3.And(
                self.is_world(world_one),
                self.is_world(world_two),
                world_one != world_two
            ),
            # Worlds must differ at some time point that is valid for both
            z3.Exists(
                [some_time],
                z3.And(
                    self.defined_at_time(world_one, some_time),
                    self.defined_at_time(world_two, some_time),
                    z3.Select(self.world_function(world_one), some_time) !=
                    z3.Select(self.world_function(world_two), some_time)
                )
            )
        )
    )
    constraints.append(world_uniqueness)
    
    # 9. All valid time-shifted worlds exist (skolem abundance)
    # Define Skolem functions that directly compute the necessary worlds
    world_forward_of = z3.Function('forward_of', self.WorldIdSort, self.WorldIdSort)
    world_backward_of = z3.Function('backward_of', self.WorldIdSort, self.WorldIdSort) 
    # Variable for world being constrained
    source_world = z3.Int('abundance_source_id')
    # Use Skolem functions instead of existential quantifiers
    skolem_abundance = z3.ForAll(
        [source_world],
        z3.Implies(
            # If the source_world is a valid world
            self.is_world(source_world),
            # Then both:
            z3.And(
                # Forwards condition - the forwards shifted world exists
                z3.Implies(
                    self.is_shifted_by(source_world, 1, world_forward_of(source_world)),
                    self.is_world(world_forward_of(source_world)),
                ),
                # Backwards condition - the backwards shifted world exists
                z3.Implies(
                    self.is_shifted_by(source_world, -1, world_backward_of(source_world)),
                    self.is_world(world_backward_of(source_world)),
                ),
            )
        )
    )
    constraints.append(skolem_abundance)
    
    # 10. Task relation only holds between states in lawful world histories
    some_state = z3.BitVec('task_restrict_some_state', self.N)
    next_state = z3.BitVec('task_restrict_next_state', self.N)
    task_world = z3.Int('task_world')
    time_shifted = z3.Int('time_shifted')
    task_restriction = z3.ForAll(
        [some_state, next_state],
        z3.Implies(
            # If there is a task from some_state to next_state
            self.task(some_state, next_state),
            # Then for some task_world at time_shifted:
            z3.Exists(
                [task_world, time_shifted],
                z3.And(
                    # The task_world is a valid world
                    self.is_world(task_world),
                    # Where time_shifted is a time in the task_world,
                    self.defined_at_time(task_world, time_shifted),
                    # The successor of time_shifted is a time in the task_world
                    self.defined_at_time(task_world, time_shifted + 1),
                    # The task_world is in some_state at time_shifted
                    some_state == z3.Select(self.world_function(task_world), time_shifted),
                    # And the task_world is in next_state at the successor of time_shifted
                    next_state == z3.Select(self.world_function(task_world), time_shifted + 1)
                )
            )
        )
    )
    constraints.append(task_restriction)
    
    # Note: During testing, we'll start with a subset of these constraints
    # and gradually add more as we verify the implementation works correctly.
    # The implementation order will be:
    # 1. Basic constraints (1-4): These are essential for world identity and existence
    # 2. Middle complexity (5-7): These ensure coherent time intervals and lawful transitions
    # 3. High complexity (8-10): These ensure world uniqueness and proper task relations
    
    return constraints
```

### Phase 3: Model Extraction Optimization

```python
def extract_model_elements(self, z3_model):
    """Extract all model elements efficiently focusing only on defined worlds and times."""
    # Reset state
    self.world_time_intervals = {}
    
    # 1. Extract valid world IDs efficiently
    all_worlds = []
    # Start with world 0 and increment until finding invalid world
    world_id = 0
    while True:
        try:
            is_valid = z3_model.eval(self.is_world(world_id))
            if z3.is_true(is_valid):
                all_worlds.append(world_id)
                world_id += 1
            else:
                break
        except z3.Z3Exception:
            break
    
    # 2. Extract world arrays for each valid world ID
    world_arrays = {}
    for world_id in all_worlds:
        try:
            world_array_expr = self.world_function(world_id)
            world_array = z3_model.eval(world_array_expr)
            world_arrays[world_id] = world_array
        except z3.Z3Exception:
            continue
    
    # 3. Extract time-state mappings focusing only on defined times
    world_histories = {}
    for world_id in all_worlds:
        if world_id not in world_arrays:
            continue
            
        world_array = world_arrays[world_id]
        time_states = {}
        
        # Find minimum and maximum times by testing ranges
        # Start with a reasonable range and expand as needed
        min_time, max_time = self._find_defined_time_range(z3_model, world_id)
        
        # Extract states for each defined time point
        for time in range(min_time, max_time + 1):
            try:
                # Check if this time is defined
                is_defined = z3_model.eval(self.defined_at_time(world_id, time))
                if z3.is_true(is_defined):
                    # Extract the world state
                    time_val = z3.IntVal(time)
                    state = self.safe_select(z3_model, world_array, time_val)
                    state_val = bitvec_to_worldstate(state)
                    time_states[time] = state_val
            except z3.Z3Exception:
                continue
        
        # Only include worlds with at least one defined state
        if time_states:
            world_histories[world_id] = time_states
            # Update time intervals for this world
            min_time = min(time_states.keys())
            max_time = max(time_states.keys())
            self.world_time_intervals[world_id] = (min_time, max_time)
    
    # 4. Extract time shift relations between worlds
    time_shift_relations = {}
    for source_id in world_histories:
        time_shift_relations[source_id] = {}
        # Add self-shift (shift by 0)
        time_shift_relations[source_id][0] = source_id
        
        # Check essential shifts (+1, -1)
        for target_id in world_histories:
            if source_id != target_id:
                for shift in [1, -1]:
                    if self._check_world_shift(world_histories, source_id, shift, target_id):
                        time_shift_relations[source_id][shift] = target_id
    
    # 5. Identify main world history
    main_world_history = world_histories.get(self.main_world, {})
    
    return world_histories, main_world_history, world_arrays, time_shift_relations

def _find_defined_time_range(self, z3_model, world_id):
    """Find the range of defined time points for a world."""
    # Start with a reasonable range
    min_time = 0
    max_time = 0
    
    # Search backward until finding undefined time
    for t in range(-1, -101, -1):
        if not z3.is_true(z3_model.eval(self.defined_at_time(world_id, t))):
            min_time = t + 1
            break
    
    # Search forward until finding undefined time
    for t in range(1, 101):
        if not z3.is_true(z3_model.eval(self.defined_at_time(world_id, t))):
            max_time = t - 1
            break
    
    return min_time, max_time

def _check_world_shift(self, world_histories, source_id, shift, target_id):
    """Check if target_id is a shifted version of source_id by shift amount."""
    source_times = set(world_histories[source_id].keys())
    target_times = set(world_histories[target_id].keys())
    
    # Check if time pattern matches when shifted
    for time in source_times:
        shifted_time = time + shift
        if shifted_time not in target_times:
            return False
        
        # Check if states match
        source_state = world_histories[source_id][time]
        target_state = world_histories[target_id][shifted_time]
        if source_state != target_state:
            return False
    
    # Check in reverse direction too
    for time in target_times:
        unshifted_time = time - shift
        if unshifted_time not in source_times:
            return False
    
    return True
```

### Phase 4: Truth and Falsity Evaluation Optimization

```python
def true_at(self, sentence, eval_world, eval_time):
    """Returns a Z3 formula that is satisfied when the sentence is true at the given world and time.
    
    This implementation handles undefined world-time pairs consistently and uses
    direct world ID references for improved clarity and performance.
    
    Args:
        sentence: The sentence to evaluate
        eval_world: The world ID at which to evaluate the sentence
        eval_time: The time point at which to evaluate the sentence
        
    Returns:
        Z3 formula that is satisfied when sentence is true at eval_world at eval_time
    """
    # First check if the world is defined at this time
    defined_expr = self.defined_at_time(eval_world, eval_time)
    
    # Get the world array from the world ID
    world_array = self.world_function(eval_world)
    
    # Base case: atomic sentence - require the world to be defined at this time
    if sentence.sentence_letter is not None:
        eval_world_state = z3.Select(world_array, eval_time)
        return z3.And(
            defined_expr,
            self.truth_condition(eval_world_state, sentence.sentence_letter)
        )

    # Recursive case: complex sentence - delegate to operator
    operator = sentence.operator
    arguments = sentence.arguments or ()
    # Let operators handle undefined states appropriately
    return operator.true_at(*arguments, eval_world, eval_time)

def false_at(self, sentence, eval_world, eval_time):
    """Returns a Z3 formula that is satisfied when the sentence is false at the given world and time.
    
    Implements the same pattern as true_at for consistency, with special handling for atomic sentences.
    
    Args:
        sentence: The sentence to evaluate
        eval_world: The world ID at which to evaluate the sentence
        eval_time: The time point at which to evaluate the sentence
        
    Returns:
        Z3 formula that is satisfied when sentence is false at eval_world at eval_time
    """
    # For atomic sentences, require the world to be defined
    if sentence.sentence_letter is not None:
        defined_expr = self.defined_at_time(eval_world, eval_time)
        world_array = self.world_function(eval_world)
        eval_world_state = z3.Select(world_array, eval_time)
        return z3.And(
            defined_expr,
            z3.Not(self.truth_condition(eval_world_state, sentence.sentence_letter))
        )
    
    # For complex sentences, just negate true_at
    return z3.Not(self.true_at(sentence, eval_world, eval_time))
```

### Phase 5: Progressive Testing Approach

```python
def run_test_suite():
    """Run comprehensive tests for the refactored bimodal implementation.
    
    Testing should proceed through three phases corresponding to 
    increasing constraint complexity:
    
    1. Core constraints only (constraints 1-4)
    2. Adding medium complexity constraints (5-7)
    3. Adding all complex constraints (8-10)
    """
    # Phase 1: Test with core constraints only (1-4)
    print("==== PHASE 1: Testing with core constraints only ====")
    # Simple examples to verify basic functionality
    test_validity("p \\rightarrow p", expected_valid=True)
    test_validity("p \\rightarrow q", expected_valid=False)
    test_validity("\\Box p \\rightarrow p", expected_valid=False)
    
    # Phase 2: Add medium complexity constraints (5-7)
    print("\n==== PHASE 2: Testing with medium complexity constraints ====")
    # Test with time-related formulas
    test_validity("p \\rightarrow X p", expected_valid=False)  # Test temporal operators
    test_validity("\\Box X p \\rightarrow X \\Box p", expected_valid=True)  # Time-modal interaction
    test_validity("\\Diamond p \\rightarrow p", expected_valid=False)
    
    # Phase 3: Add all complex constraints (8-10)
    print("\n==== PHASE 3: Testing with all constraints ====")
    # Complex nested modal operators
    test_validity("\\Box(p \\rightarrow q) \\rightarrow (\\Box p \\rightarrow \\Box q)", expected_valid=True)
    test_validity("\\Box \\Diamond p \\rightarrow \\Diamond \\Box p", expected_valid=False)
    test_validity("\\Diamond \\Box p \\rightarrow \\Box \\Diamond p", expected_valid=True)
    
    # Comparison tests against original implementation
    print("\n==== Comparative Performance Testing ====")
    # Run same complex tests with different constraint subsets
    # Compare model sizes, solving times, and memory usage

def test_validity(formula, expected_valid, constraint_set="all"):
    """Test if a formula is valid as expected using specified constraint subset.
    
    Args:
        formula: The formula string to test
        expected_valid: Whether the formula is expected to be valid
        constraint_set: Which constraint subset to use:
            - "core": Only constraints 1-4
            - "medium": Constraints 1-7
            - "all": All constraints 1-10 (default)
    """
    # Configure model constraints based on constraint_set
    settings = {
        "constraint_set": constraint_set
    }
    
    # Build and check the model
    model = BuildExample(
        f"test_{formula}", 
        "bimodal", 
        premises=[], 
        conclusions=[formula],
        settings=settings
    )
    
    # For valid formulas, no satisfying model should be found
    # For invalid formulas, a countermodel should be found
    assert model.satisfiable != expected_valid
    
    if not expected_valid and model.satisfiable:
        # Verify minimal world count
        world_count = len(model.world_histories)
        print(f"Formula {formula}: {world_count} worlds created")
        
        # Verify minimal time spans
        max_span = 0
        for world_id, (min_time, max_time) in model.world_time_intervals.items():
            span = max_time - min_time + 1
            max_span = max(max_span, span)
        print(f"Formula {formula}: Maximum time span {max_span}")
        
        # Print solving time
        print(f"Formula {formula}: Solved in {model.solving_time:.3f} seconds")
```

## Expected Benefits

1. **Smaller models**: Only necessary worlds and times will be created
2. **Better performance**: Fewer constraints to solve, more focused models
3. **More natural semantics**: World histories reflect only what's needed
4. **Consistent referencing**: World IDs used consistently throughout
5. **Improved debugging**: Clearer relationship between formulas and required worlds

## Potential Challenges

1. **Z3 Solver Behavior**: Z3 may still create more worlds than expected if not properly guided
2. **Performance Trade-offs**: Removing explicit limits might increase solver time in some cases
3. **Testing complexity**: Hard to verify optimal model minimality

## Implementation Order

1. Modify `define_primitives()` and `define_sorts()` for consistent world ID usage
2. Update `build_frame_constraints()` with core constraints (1-4)
3. Improve model extraction to focus on defined elements only
4. Update `true_at` and `false_at` methods to maintain consistent world ID usage
5. Test with simple formulas and core constraints
6. Add mid-complexity constraints (5-7) and test with more complex formulas
7. Add high-complexity constraints (8-10) and verify with advanced test cases
8. Measure performance across constraint sets to find optimal balance

## Metrics for Success

The refactoring will be considered successful if:

1. All tests pass on the standard operators in bimodal/operators.py
2. Countermodels use fewer worlds (at least 20% reduction on average)
3. Time intervals are more focused (minimal required time points)
4. No regressions in solving speed (within 10% of original performance)
5. Code is more maintainable with consistent world ID references

## Conclusion

This refactoring strategy will lead to more efficient bimodal models by eliminating unnecessary worlds and times. By focusing on consistent world ID references throughout the codebase and streamlining frame constraints, the refactored implementation will generate minimal models while preserving the correct semantics of bimodal logic. Z3's natural minimality properties will be leveraged to create only the worlds and time points necessary to satisfy the logical constraints.
