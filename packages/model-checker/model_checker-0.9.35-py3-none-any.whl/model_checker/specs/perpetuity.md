# Perpetuity Issue in Bimodal Logic Implementation

## Problem Description

The `BM_TH_1` example in the bimodal theory is expected to be a theorem (with `expectation: False` indicating that no countermodel should be found), but the implementation is incorrectly finding a countermodel. This indicates an issue with the semantic treatment of the perpetuity relationship between necessity operators (`\Box`) and future tense operators (`\Future`).

Example `BM_TH_1` represents the principle:
```
\Box A → \Future A
```

Which states that if A is necessarily true (true in all accessible worlds), then A is true at all future times. This should be a theorem in bimodal logic.

## Analysis of the Countermodel

The generated countermodel has the following properties:

```
World Histories:
  W_0: (0:b) =⟹ (+1:a)

Evaluation Point:
  World History W_0: b =⟹ a
  Time: 0
  World State: b
```

The model shows:
- A single world (W_0) with two time points (0 and 1)
- At time 0, world state is 'b', and at time 1, world state is 'a'
- The premise `\Box A` is true at W_0, time 0, indicating A is true in all accessible worlds at time 0
- The conclusion `\Future A` is false at W_0, time 0, which should be impossible if `\Box A` is true

The issue appears to be in the relationship between modal accessibility and temporal progression. The countermodel essentially shows:
- A is true at all worlds accessible from W_0 at time 0
- But A is not true at all future times from W_0

This contradicts the expected behavior where necessity should entail truth at all times (perpetuity).

## Root Cause

Looking at the frame constraints in `semantic.py`, there are three advanced constraints that were commented out:

```python
# constraints.append(world_uniqueness)
# constraints.append(skolem_abundance)
# constraints.append(task_restriction)
```

These constraints are critical for ensuring proper bimodal behavior:

1. **World Uniqueness**: Ensures each world has a unique history, preventing duplicate worlds with identical states.
2. **Skolem Abundance**: Guarantees time-shifted worlds exist, ensuring temporal operators work correctly.
3. **Task Restriction**: Ensures that the task relation (transitions between states) only holds within lawful world histories.

The issue occurs because without these constraints, the model doesn't properly enforce the connection between necessity and future-tense operators. Specifically:

- The necessity operator `\Box` evaluates truth across all accessible worlds at the current time
- The future operator `\Future` evaluates truth across all future times in the current world
- Without proper constraints, these two dimensions can be inconsistent

## Fix Approaches

### 1. Enable Advanced Constraints

The commented-out constraints would enforce the proper relationship, but they cause Z3 to timeout due to their complexity. This suggests we need a more efficient approach.

### 2. Implement a Perpetuity Constraint

A targeted constraint that directly enforces the perpetuity relationship between necessity and time:

```python
def build_perpetuity_constraint():
    """Build a constraint that ensures necessity implies truth at all future times."""
    world_id = z3.Int('perpetuity_world')
    time = z3.Int('perpetuity_time')
    future_time = z3.Int('perpetuity_future_time')
    state = z3.BitVec('perpetuity_state', self.N)
    atom = z3.Const('perpetuity_atom', syntactic.AtomSort)
    
    # If a world is defined at some time and a future time
    time_defined_condition = z3.And(
        self.is_world(world_id),
        self.defined_at_time(world_id, time),
        self.defined_at_time(world_id, future_time),
        future_time >= time
    )
    
    # If something is necessarily true at time, it must be true at future_time
    perpetuity_condition = z3.Implies(
        z3.And(
            time_defined_condition,
            self.necessarily_true_at(atom, world_id, time)
        ),
        self.truth_condition(
            z3.Select(self.world_function(world_id), future_time),
            atom
        )
    )
    
    return z3.ForAll([world_id, time, future_time, atom], perpetuity_condition)
```

Where `necessarily_true_at` would be a new helper function that determines if something is true in all accessible worlds:

```python
def necessarily_true_at(self, atom, world_id, time):
    """Returns a formula that is true if atom is true in all accessible worlds at time."""
    other_world = z3.Int('necessity_other_world')
    return z3.ForAll(
        [other_world],
        z3.Implies(
            z3.And(
                self.is_world(other_world),
                self.defined_at_time(other_world, time)
            ),
            self.truth_condition(
                z3.Select(self.world_function(other_world), time),
                atom
            )
        )
    )
```

### 3. Simplify World Uniqueness Constraint

A simplified version of the world uniqueness constraint that is less computationally intensive:

```python
def build_simplified_world_uniqueness():
    """A simplified world uniqueness constraint focusing on the main evaluation time."""
    world_one = z3.Int('world_one')
    world_two = z3.Int('world_two')
    
    # Only enforce uniqueness for worlds at the main time point
    simplified_uniqueness = z3.ForAll(
        [world_one, world_two],
        z3.Implies(
            z3.And(
                self.is_world(world_one),
                self.is_world(world_two),
                world_one != world_two,
                self.defined_at_time(world_one, self.main_time),
                self.defined_at_time(world_two, self.main_time)
            ),
            z3.Select(self.world_function(world_one), self.main_time) !=
            z3.Select(self.world_function(world_two), self.main_time)
        )
    )
    
    return simplified_uniqueness
```

### 4. Implement an Explicit Bimodal Accessibility Constraint

Define accessibility so that both modal and temporal dimensions are properly connected:

```python
def build_bimodal_accessibility_constraint():
    """Ensure proper coordination between modal and temporal accessibility."""
    world_id = z3.Int('accessibility_world')
    time = z3.Int('accessibility_time')
    future_time = z3.Int('accessibility_future_time')
    
    # All future times are accessible from current time
    temporal_accessibility = z3.ForAll(
        [world_id, time, future_time],
        z3.Implies(
            z3.And(
                self.is_world(world_id),
                self.defined_at_time(world_id, time),
                self.defined_at_time(world_id, future_time),
                future_time >= time
            ),
            # All worlds accessible at time are also accessible at future_time
            z3.ForAll(
                [z3.Int('other_world')],
                z3.Implies(
                    z3.And(
                        self.is_world(z3.Int('other_world')),
                        self.defined_at_time(z3.Int('other_world'), time)
                    ),
                    self.defined_at_time(z3.Int('other_world'), future_time)
                )
            )
        )
    )
    
    return temporal_accessibility
```

## Recommended Implementation

The most effective approach is a combination of methods 2 and 3:

1. Add a specific perpetuity constraint that directly enforces the relationship between necessity and time
2. Use a simplified world uniqueness constraint focused on the main evaluation time

This approach should be more efficient than the full constraints while still ensuring the correct bimodal behavior. Implementation steps:

1. Add the perpetuity constraint to `build_frame_constraints()`:

```python
def build_frame_constraints(self):
    # ... existing code ...
    
    # Add perpetuity constraint
    perpetuity_constraint = self.build_perpetuity_constraint()
    constraints.append(perpetuity_constraint)
    
    # Add simplified world uniqueness
    simplified_uniqueness = self.build_simplified_world_uniqueness()
    constraints.append(simplified_uniqueness)
    
    return constraints
```

2. Add the helper methods `build_perpetuity_constraint()`, `necessarily_true_at()`, and `build_simplified_world_uniqueness()` to the `BimodalSemantics` class as described above.

## Conclusion

The issue with the `BM_TH_1` example is due to insufficient constraints on the relationship between modal necessity and temporal operators. By adding targeted constraints that specifically enforce the perpetuity property (necessity implies truth at all times), we can correct the semantic behavior without requiring the full, computationally expensive constraints that cause timeouts.

This approach aligns with the project's design philosophy of making intentional, explicit choices about semantic behavior rather than relying on implicit assumptions, while still maintaining practical performance characteristics.