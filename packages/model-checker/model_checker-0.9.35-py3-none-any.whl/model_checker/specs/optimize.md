# Bimodal Frame Constraint Analysis

## Issue Summary

The `TN_CM_1` and `TN_CM_2` examples in the bimodal theory are incorrectly reporting as unsatisfiable despite having expectations of `True` (meaning they should be satisfiable). These counterexamples test:

1. `TN_CM_1`: Tests whether `A` implies `\Future A`. This should be invalid because the truth of a proposition at the present time does not necessitate its truth at all future times.

2. `TN_CM_2`: Tests whether `\future A` and `\future B` imply `\future (A \wedge B)`. This should be invalid because A and B might be true at different future time points.

## Precise Constraint Analysis

After careful examination of the constraints, I've identified the exact mechanism causing the issue:

### 1. Core of the issue: `is_shifted_by` and Bidirectional Constraints

In the current implementation, the `is_shifted_by` method creates a bidirectional constraint:

```python
def is_shifted_by(self, source_world, shift, target_world):
    """Predicate that target_id is a world shifted from source_id by shift amount."""
    time = z3.Int('time_to_shift')
    source_array = self.world_function(source_world)
    target_array = self.world_function(target_world)
    
    # Calculate shifted time once to reuse
    shifted_time = time + shift
    
    return z3.And(
        self.shifted_times(source_world, shift, target_world),
        z3.ForAll(
            [time],
            # States must match when both are defined
            z3.Implies(
                self.defined_at_time(source_world, time),
                z3.Select(source_array, time) == z3.Select(target_array, shifted_time)
            )
        )
    )
```

This creates a requirement that for every time t where source_world is defined, the state at source_world at time t must exactly match the state at target_world at time t+shift.

### 2. The Problem: Constraint Rigidity

When tracing the constraint chain for `TN_CM_1`:

- **Premise**: 'A' is true at time 0 in world 0
- **Skolem abundance**: For any non-zero time shift, there must exist a world that is world 0 shifted by that amount
- **Critical Constraint**: For time_shift = 1, there must exist a world (world_1) such that:
  - For all times t where world 0 is defined, 
  - State at time t in world 0 must equal state at time t+1 in world_1
  
- **Problem for TN_CM_1**: 
  - When we need 'A' true at time 0 but false at time 1 in world 0
  - The skolem abundance and is_shifted_by constraints force that:
    - If 'A' is true at time 0 in world 0
    - Then 'A' must be true at time 1 in some world_1
    - Therefore, there cannot be a world where 'A' changes from true to false over time

The key insight: The current framework is building a world structure that enforces consistency of state patterns across time shifts, but this inadvertently prevents temporal variation within a single world.

### 3. Unsatisfiable Core Confirms This Analysis

The Z3 unsatisfiable core for `TN_CM_1` includes:

1. The skolem abundance constraint
2. The premise that 'A' is true at time 0
3. The need for 'A' to be false at some future time

Z3 cannot find a satisfying assignment because the constraint structure forces 'A' to have the same truth value at all times.

## Solution

The solution is to modify how the time-shift constraints work while preserving the essential behavior of time-shifted worlds:

### 1. Identify the Task Relation

The task relation is currently defined to govern transitions between states at consecutive time points:

```python
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
```

Importantly, this constraint doesn't by itself force any specific truth values to propagate - it only requires that consecutive states are related by a valid task relation.

### 2. Fix the Core Issue: Modified Skolem Abundance

The key is to maintain the existence of time-shifted worlds while relaxing the rigid state pattern enforcement:

```python
# Separate time structure from state matching
time_structure = z3.ForAll(
    [source_world, time_shift],
    z3.Implies(
        z3.And(
            self.is_world(source_world),
            time_shift != z3.IntVal(0),
            self.defined_at_time(source_world, time_shift)
        ),
        # Ensure shifted world exists
        z3.And(
            self.is_world(world_shifted_from(source_world)),
            # Only ensure time intervals match
            self.shifted_times(source_world, shift, world_shifted_from(source_world))
        )
    )
)

# Add optional state pattern constraint
state_patterns = z3.ForAll(
    [source_world, other_world, check_time],
    z3.Implies(
        z3.And(
            self.is_world(source_world),
            self.is_world(other_world),
            # Some conditions where state patterns should match
            # For example, only for certain worlds or time ranges
            source_world != self.main_world,  # Example condition
            other_world != self.main_world,   # Example condition
            self.defined_at_time(source_world, check_time),
            self.defined_at_time(other_world, check_time + 1)
        ),
        # Optional state pattern constraint
        self.task(
            z3.Select(self.world_function(source_world), check_time),
            z3.Select(self.world_function(other_world), check_time + 1)
        )
    )
)
```

### 3. Simplified Solution: Modify just the `is_shifted_by` Method

A more targeted approach is to modify `is_shifted_by` to only enforce time interval matching without strict state pattern preservation:

```python
def is_shifted_by(self, source_world, shift, target_world):
    """Predicate that target_id is a world shifted from source_id by shift amount."""
    # Only ensure time intervals match without requiring identical states
    return self.shifted_times(source_world, shift, target_world)
```

This removes the problematic constraint while preserving the essential time interval matching.

### 4. Implementation Recommendation

Given the analysis, the simplest solution is to:

1. Modify the `is_shifted_by` method to use only `shifted_times` without forcing states to match exactly.
2. Keep the task relation constraints that govern transitions between consecutive time points.
3. Re-enable the commented-out task_restriction constraint to maintain proper task relations.

## Implementation Plan

1. Create a backup of the current implementation.

2. Modify the `is_shifted_by` method:
```python
def is_shifted_by(self, source_world, shift, target_world):
    """Predicate that target_id is a world shifted from source_id by shift amount."""
    # Only ensure time intervals match
    return self.shifted_times(source_world, shift, target_world)
```

3. Ensure the task_restriction constraint is enabled:
```python
# In build_frame_constraints
constraints.append(task_restriction)  # Uncomment this line
```

4. Test with both `TN_CM_1` and `TN_CM_2` to verify they correctly find countermodels.

5. Verify that the bimodal theorems still correctly report no countermodels.

## Expected Outcome

After implementing these changes:

1. The model will maintain the desired behavior of time interval matching between time-shifted worlds.
2. The unintended enforcement of identical state patterns will be removed.
3. `TN_CM_1` will correctly find a countermodel where 'A' is true at time 0 but false at some future time.
4. `TN_CM_2` will correctly find a countermodel where 'A' and 'B' are true at different future times.
5. The bimodal theorems will remain unsatisfiable as expected.

This solution offers a minimal change to the codebase while effectively addressing the root cause of the problem.