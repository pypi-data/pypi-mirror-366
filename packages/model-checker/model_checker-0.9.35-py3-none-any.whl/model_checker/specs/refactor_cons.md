# Frame Constraints Refactoring Analysis for Bimodal Logic

## Overview
This document analyzes the Z3 constraints used in the bimodal semantic model and proposes improvements to make the frame constraints more effective at generating models that match the expected outcomes in `bimodal/examples.py`.

## Current Constraint System

After analyzing the Z3 output from running the examples, the current frame constraints are structured as follows in `BimodalSemantics.build_frame_constraints()`:

1. `valid_main_world`: The main world must be valid
2. `valid_main_time`: The main time must be valid
3. `classical_truth`: Each sentence letter has a definite truth value
4. `enumeration_constraint`: World enumeration starts at 0 
5. `convex_world_ordering`: Worlds form a convex ordering (no gaps)
6. `lawful`: Worlds follow the task relation for state transitions
7. `skolem_abundance`: Ensures time-shifted worlds exist using Skolem functions
8. `world_uniqueness`: All valid worlds must be unique
9. `world_interval`: Each world has a valid time interval

**Commented out constraints:**
- `task_restriction`: Task relation only holds between states in lawful world histories
- `task_minimization`: Encourages minimal changes between consecutive world states

## Observations from Example Results

The following issues were identified from the examples:

1. **Example BM_CM_3**: Has expectation=True but fails to find a countermodel for "Possibility to Some Future". The model fails to enforce the necessary time-shifted worlds.

2. **Example BM_TH_4**: Successfully proves that `\past A` implies `\Diamond A`, which matches the expectation=False.

3. **Example BM_TH_5**: Successfully proves that `\Box A` implies `\Future \Box A`, which matches the expectation=False.

4. **Modal examples** (MD_CM_*): Generally work as expected.

5. **Tense examples** (TN_CM_*): Generate appropriate models that match expectations.

## Constraint Interaction Analysis

### Critical Issues

1. **Skolem vs. Existential Abundance**: The current implementation uses Skolem functions (`forward_of`, `backward_of`) instead of existential quantifiers. While this can improve Z3 performance, it creates a subtle but important distinction in how time-shifted worlds are created.

2. **World Interval Constraints**: The world interval constraint is working properly but may be too strict, limiting the creation of alternative intervals needed for certain examples.

3. **Commented-out Constraints**: The task_restriction and task_minimization constraints are commented out, which may allow invalid models in some cases.

4. **Counter-intuitive Modal/Temporal Interaction**: The modal operators (`\Box`, `\Diamond`) and temporal operators (`\Future`, `\Past`) don't interact in ways that match philosophical intuitions in some examples.

### Detailed Z3 Constraint Analysis

When checking countermodels like BM_CM_3, the following constraint interactions are observed in the Z3 output:

1. The abundance constraint correctly creates forwards-shifted worlds (via `forward_of`) but doesn't properly connect these to the semantic evaluation of temporal operators.

2. The `\Diamond A` premise correctly creates alternate worlds with true/false states for A, but these don't align with the temporal structure for `\future A`.

3. The unsatisfiable cores for the theorems (BM_TH_*) consistently include the world interval and abundance constraints, showing they're critical to the proofs.

## Detailed Refactoring Work and Results

### 1. Initial Approach and Implementation

We began by implementing several changes as recommended in the original analysis:

1. Reordered the constraints by moving `world_interval` earlier and applying more important constraints first
2. Made `task_restriction` and `task_minimization` optional via settings
3. Attempted to replace the Skolem function approach with a clearer existential approach
4. Added a `connect_shift_to_temporal` method to explicitly link time-shifted worlds to temporal operator semantics
5. Modified the example settings for BM_CM_3 to give Z3 more time (30 seconds) and space (M=3)

### 2. Results and Findings

After implementing these changes, we observed the following results:

1. **BM_CM_3 Challenge**: Despite our changes, the BM_CM_3 example remains problematic. It consistently times out after 30 seconds without finding a model.

2. **Constraint Interactions**: We identified unexpected interactions between the abundance constraint (whether using existential or Skolem approaches) and other constraints, particularly when the temporal operators are involved.

3. **Theorem Validation**: The theorem examples (BM_TH_4 and BM_TH_5) continue to work correctly, proving the validity of the temporal-modal interactions. This suggests our basic approach to constraints is fundamentally sound.

4. **Constraint Sensitivity**: The system is highly sensitive to the addition of constraints. In particular, the `task_minimization` and the new `connect_shift_to_temporal` constraints appeared to over-constrain the model, making it impossible to find countermodels for examples that should have them.

### 3. Current Implementation Status

Our current implementation:

```python
def build_frame_constraints(self):
    """Build the frame constraints for the bimodal logic model."""
    # Basic constraints
    valid_main_world = self.is_world(self.main_world)
    valid_main_time = self.is_valid_time(self.main_time)
    classical_truth = self.classical_truth_conditions()
    enumeration_constraint = self.enumerate_constraints()
    convex_world_ordering = self.build_convex_ordering()
    
    # World structure constraints
    world_interval = self.world_interval_constraint()
    lawful = self.build_lawful_constraint()
    
    # Advanced relationships
    abundance_constraint = self.build_abundance_constraint()
    world_uniqueness = self.build_world_uniqueness()
    
    # Assemble all constraints in the optimal order
    constraints = [
        # Core structure
        valid_main_world,
        valid_main_time,
        classical_truth,
        enumeration_constraint,
        convex_world_ordering,
        
        # World and time framework - moved world_interval earlier to establish time intervals before other constraints
        world_interval,
        lawful,
        
        # Relationships and interactions
        abundance_constraint,
        world_uniqueness,
    ]
    
    # Use task_restriction only if specifically requested
    if self.settings.get('use_task_restriction', False):
        task_restriction = self.build_task_restriction()
        constraints.append(task_restriction)
        
    # Use task_minimization only if specifically requested
    if self.settings.get('use_task_minimization', False):
        task_minimization = self.build_task_minimization()
        constraints.append(task_minimization)
    
    return constraints
```

We reverted to using the original Skolem function approach for abundance rather than using existential quantifiers:

```python
def build_abundance_constraint(self):
    """Build constraint ensuring necessary time-shifted worlds exist."""
    # Define Skolem functions
    forward_of = z3.Function('forward_of', self.WorldIdSort, self.WorldIdSort)
    backward_of = z3.Function('backward_of', self.WorldIdSort, self.WorldIdSort)
    source_world = z3.Int('abundance_source_id')
    
    # Use Skolem functions instead of existential quantifiers
    abundance_constraint = z3.ForAll(
        [source_world],
        z3.Implies(
            self.is_world(source_world),
            z3.And(
                z3.Implies(
                    self.can_shift_forward(source_world),
                    z3.And(
                        self.is_world(forward_of(source_world)),
                        self.is_shifted_by(source_world, 1, forward_of(source_world))
                    )
                ),
                z3.Implies(
                    self.can_shift_backward(source_world),
                    z3.And(
                        self.is_world(backward_of(source_world)),
                        self.is_shifted_by(source_world, -1, backward_of(source_world))
                    )
                )
            )
        )
    )
    return abundance_constraint
```

And simplified the `connect_shift_to_temporal` method to just return `True` for now:

```python
def connect_shift_to_temporal(self, source_world, target_world, shift):
    """Connect shifted worlds to temporal operator semantics."""
    # For now, don't add additional constraints as they're making some examples unsatisfiable
    return z3.BoolVal(True)
```

### 4. Recommendations for Future Work

1. **Further Analyze BM_CM_3**: This example appears to be particularly challenging. A targeted approach with simplified constraints is needed to identify why Z3 can't find a model.

2. **Consider Hybrid Approaches**: The Z3 solver may be struggling with the complex interplay between modal and temporal operators. Consider breaking these into simpler sub-constraints.

3. **Alternative Constraint Formulations**: Investigate alternative ways to formulate the abundance constraint that maintain the necessary logical properties but are more solver-friendly.

4. **Incremental Testing**: Continue making small changes and testing each change individually to pinpoint which specific constraints are causing the most problems.

5. **Example Simplification**: Create simplified versions of problematic examples to understand what specific aspects of the examples trigger solver difficulties.

6. **Deep Z3 Investigation**: Use Z3's profiling capabilities to understand what's happening during the solver runtime. This could reveal bottlenecks in the constraint solving process.

7. **Revisit Temporal-Modal Interaction**: The fundamental challenge appears to be properly linking worlds across both temporal and modal dimensions. This core interaction needs careful design to ensure Z3 can reason efficiently about it.

This ongoing work represents progress towards more reliable constraint modeling, but further refinement is needed to handle all the test cases correctly.

### 3. Improve Abundance Constraint

**Implementation Details:**

```python
def build_abundance_constraint(self):
    """Build constraint ensuring necessary time-shifted worlds exist.
    
    Replace the Skolem function approach with a clearer existential approach
    that directly enforces the relationship between temporal shifts and world existence.
    """
    source_world = z3.Int('abundance_source_id')
    shifted_world = z3.Int('abundance_shifted_world')
    
    # Each world must have appropriate time-shifted counterparts
    abundance_constraint = z3.ForAll(
        [source_world],
        z3.Implies(
            # If the source_world is a valid world
            self.is_world(source_world),
            # Then both:
            z3.And(
                # Forwards condition
                z3.Implies(
                    # If source can shift forward
                    self.can_shift_forward(source_world),
                    # Then some forward-shifted world exists
                    z3.Exists(
                        [shifted_world],
                        z3.And(
                            self.is_world(shifted_world),
                            self.is_shifted_by(source_world, 1, shifted_world),
                            # Explicit connection to temporal operators
                            self.connect_shift_to_temporal(source_world, shifted_world, 1)
                        )
                    )
                ),
                # Backwards condition
                z3.Implies(
                    # If source can shift backwards
                    self.can_shift_backward(source_world),
                    # Then some backwards-shifted world exists
                    z3.Exists(
                        [shifted_world],
                        z3.And(
                            self.is_world(shifted_world),
                            self.is_shifted_by(source_world, -1, shifted_world),
                            # Explicit connection to temporal operators
                            self.connect_shift_to_temporal(source_world, shifted_world, -1)
                        )
                    )
                )
            )
        )
    )
    return abundance_constraint

def connect_shift_to_temporal(self, source_world, target_world, shift):
    """Connect shifted worlds to temporal operator semantics.
    
    This helper method creates constraints that explicitly link
    time-shifted worlds to the semantics of temporal operators.
    
    Args:
        source_world: Source world ID
        target_world: Target world ID
        shift: Direction of shift (1 for forward, -1 for backward)
        
    Returns:
        Z3 formula connecting the worlds to temporal semantics
    """
    atom = z3.Const('temporal_atom', syntactic.AtomSort)
    source_time = z3.Int('temporal_source_time')
    target_time = z3.Int('temporal_target_time')
    
    # Connect the shifted worlds to temporal operator semantics
    return z3.ForAll(
        [atom, source_time],
        z3.Implies(
            z3.And(
                # Source time is valid for source world
                self.is_valid_time_for_world(source_world, source_time),
                # Target time is adjusted by shift
                z3.And(
                    target_time == source_time + shift,
                    self.is_valid_time_for_world(target_world, target_time)
                )
            ),
            # Ensure that truth values at source and target are consistent with shift
            z3.Implies(
                # If atom is true at target_world[target_time]
                self.truth_condition(
                    z3.Select(self.world_function(target_world), target_time),
                    atom
                ),
                # Then for forward shifts, the atom must be future-true at source_world[source_time]
                # and for backward shifts, the atom must be past-true at source_world[source_time]
                z3.Or(
                    shift != 1,  # Not a forward shift
                    # The atom is future-true at source
                    z3.Not(z3.ForAll(
                        [z3.Int('future_time')],
                        z3.Implies(
                            z3.And(
                                z3.Int('future_time') > source_time,
                                self.is_valid_time_for_world(source_world, z3.Int('future_time'))
                            ),
                            z3.Not(self.truth_condition(
                                z3.Select(self.world_function(source_world), z3.Int('future_time')),
                                atom
                            ))
                        )
                    )),
                    shift != -1,  # Not a backward shift
                    # The atom is past-true at source
                    z3.Not(z3.ForAll(
                        [z3.Int('past_time')],
                        z3.Implies(
                            z3.And(
                                z3.Int('past_time') < source_time,
                                self.is_valid_time_for_world(source_world, z3.Int('past_time'))
                            ),
                            z3.Not(self.truth_condition(
                                z3.Select(self.world_function(source_world), z3.Int('past_time')),
                                atom
                            ))
                        )
                    ))
                )
            )
        )
    )
```

**Rationale:**
- The new implementation uses existential quantifiers for better clarity
- It explicitly links time-shifted worlds to the semantics of temporal operators
- The `connect_shift_to_temporal` method establishes clear relationships between time shifts and temporal operator truth conditions

### 4. Reinstate Task Minimization

**Implementation Details:**

```python
def build_task_minimization(self):
    """Build a soft constraint encouraging minimal changes between consecutive world states.
    
    This constraint is restored but with lower priority to allow more flexibility.
    """
    world_id = z3.Int('minimal_world')
    time_point = z3.Int('minimal_time')
    
    # Create a soft constraint for task minimization
    # Instead of a direct implication, create a weighted soft constraint
    task_minimization = z3.ForAll(
        [world_id, time_point],
        z3.Implies(
            z3.And(
                self.is_world(world_id),
                self.is_valid_time_for_world(world_id, time_point),
                self.is_valid_time_for_world(world_id, time_point + 1)
            ),
            # Add a weighted equality constraint rather than a strict equality
            # This allows Z3 to break this constraint when necessary
            z3.PWeight(
                z3.Select(self.world_function(world_id), time_point) == 
                z3.Select(self.world_function(world_id), time_point + 1),
                1.0  # Lower weight gives this constraint less priority
            )
        )
    )
    
    return task_minimization
```

**Rationale:**
- The task minimization constraint is reinstated but with lower priority
- It uses `PWeight` to create a soft constraint that Z3 can override when necessary
- This helps generate more intuitive models while still allowing flexibility for counterexamples

### Complete Implementation Plan

To implement all these changes, a modular constraint system should be created:

```python
def build_frame_constraints(self):
    """Build all frame constraints with a modular approach for better maintainability."""
    # Basic constraints
    valid_main_world = self.is_world(self.main_world)
    valid_main_time = self.is_valid_time(self.main_time)
    classical_truth = self.classical_truth_conditions()
    enumeration_constraint = self.enumerate_constraints()
    convex_world_ordering = self.build_convex_ordering()
    
    # World structure constraints
    world_interval = self.world_interval_constraint()
    lawful = self.build_lawful_constraint()
    task_restriction = self.build_task_restriction()
    
    # Advanced relationships
    skolem_abundance = self.build_abundance_constraint()
    world_uniqueness = self.build_world_uniqueness()
    
    # Optional constraints
    task_minimization = self.build_task_minimization()
    
    # Assemble all constraints in the optimal order
    constraints = [
        # Core structure
        valid_main_world,
        valid_main_time,
        classical_truth,
        enumeration_constraint,
        convex_world_ordering,
        
        # World and time framework
        world_interval,
        lawful,
        task_restriction,
        
        # Relationships and interactions
        skolem_abundance,
        world_uniqueness,
        
        # Optimization constraints
        task_minimization,
    ]
    
    # Allow selective enablement based on settings
    if not self.settings.get('use_task_minimization', True):
        constraints.remove(task_minimization)
    
    return constraints
```

This implementation provides a comprehensive solution to the issues identified in the analysis, with detailed code for each recommended change. The modular approach makes it easy to selectively enable or disable constraints based on specific needs or examples.
