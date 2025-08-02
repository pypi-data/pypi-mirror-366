# Root Cause Analysis for TN_CM_1 and TN_CM_2 Countermodel Issues

## Overview
This document analyzes why `TN_CM_1` and `TN_CM_2` examples in the bimodal theory are failing to find countermodels despite the expectation setting indicating they should succeed.

## Problem Statement
According to the analysis of `examples.py` and execution of `dev_cli.py`, two specific examples fail to find countermodels:

1. **TN_CM_1**: Testing if `A` implies `\Future A` (should find a countermodel)
2. **TN_CM_2**: Testing if `\future A, \future B` implies `\future (A ∧ B)` (should find a countermodel)

Both examples have `expectation: True` set, indicating countermodels should exist, but Z3 reports these as "no countermodel".

## Technical Analysis

### Example 1: TN_CM_1

```python
# TN_CM_1:
TN_CM_1_premises = ['A']
TN_CM_1_conclusions = ['\\Future A']
```

From the unsatisfiable core, we can see the conflicting constraints:

```
PREMISES CONSTRAINTS:
1. And(defined_at_time(0, 0), truth_condition(world_function(0)[0], A))

CONCLUSIONS CONSTRAINTS:
1. Not(ForAll([future_true_time],
           Implies(And(defined_at_time(0, future_true_time),
                       0 < future_true_time),
                   And(defined_at_time(0, future_true_time),
                       truth_condition(world_function(0)[future_true_time], A)))))
```

The key issue is in the frame constraint:

```
FRAME CONSTRAINTS:
1. ForAll([abundance_source_id, time_shift],
       Implies(And(is_world(abundance_source_id),
                   0 != time_shift,
                   defined_at_time(abundance_source_id, time_shift)),
               ... 
```

### Example 2: TN_CM_2

```python
# TN_CM_2:
TN_CM_2_premises = ['\\future A', '\\future B']
TN_CM_2_conclusions = ['\\future (A \\wedge B)']
```

The problem stems from the same frame constraint and similar issues with how future times are handled.

## Root Cause

The core issue resides in the handling of time-shifted worlds in the `skolem_abundance` constraint in `semantic.py` around line 370:

```python
# Variable for world being constrained
source_world = z3.Int('abundance_source_id')
# Variable for time shift
time_shift = z3.Int('time_shift')
# Use Skolem functions with strengthened formulation to ensure worlds exist
world_shifted_from = z3.Function('world_shifted_from', self.WorldIdSort, self.WorldIdSort)
skolem_abundance = z3.ForAll(
    [source_world, time_shift],
    z3.Implies(
        # If the source_world is a valid world
        z3.And(
            self.is_world(source_world),
            time_shift != z3.IntVal(0),
            self.defined_at_time(source_world, time_shift)
        ),
        # Then both:
        z3.And(
            # Forward shifted world must exist
            self.is_world(world_shifted_from(source_world)),
            # It must be a proper time shift of source_world
            self.is_shifted_by(source_world, time_shift, world_shifted_from(source_world)),
        )
    )
)
```

The issue is that this constraint enforces that for every time-shifted world, there must exist another world that is a shifted version of it. This is too strict for temporal operators like `\Future` and `\future`.

When we examine the specific implementation in operators.py, we see that:

1. In `FutureOperator.true_at()` (lines 532-548), it checks if the argument is true at *all* future times:
   ```python
   return z3.ForAll(
       future_time,
       z3.Implies(
           z3.And(
               semantics.defined_at_time(eval_world, future_time),
               eval_time < future_time,
           ),
           semantics.true_at(argument, eval_world, future_time),
       )
   )
   ```

2. In `DefFutureOperator` (defined operator `\future`), which is derived as:
   ```python
   def derived_definition(self, argument):
       return [NegationOperator, [FutureOperator, [NegationOperator, argument]]]
   ```
   
The way the `skolem_abundance` constraint is defined, it doesn't allow for a model where:
- At the current time `t`, statement `A` is true
- At some future time `t+n`, statement `A` is false

The constraint forces a consistency of state transitions that prevents the creation of countermodels where a proposition is true at the current time but not in the future, or where two propositions are individually true in some future but not simultaneously true in any future time.

## Solution

The solution requires modifying the `skolem_abundance` constraint in `semantic.py` to be less restrictive for time transitions. Two potential approaches:

1. **Weaken the constraint**: Make the world-shifting constraint apply only to certain types of world transitions, excluding those needed for temporal operators.

2. **Modify temporal operators**: Change the implementation of `FutureOperator` and `DefFutureOperator` to work with the existing constraints by using a different approach to accessing future times.

The most direct solution would be to modify the `skolem_abundance` constraint to make it conditional:

```python
skolem_abundance = z3.ForAll(
    [source_world, time_shift],
    z3.Implies(
        z3.And(
            self.is_world(source_world),
            time_shift != z3.IntVal(0),
            self.defined_at_time(source_world, time_shift),
            # Add condition to exclude temporal transitions within the same world
            Not(self.is_temporal_shift_in_same_world(source_world, time_shift))
        ),
        ...
    )
)
```

This would require implementing `is_temporal_shift_in_same_world()` to identify transitions that should be excluded from the constraint.

## Conclusion

The issues with `TN_CM_1` and `TN_CM_2` stem from overly restrictive frame constraints in the bimodal logic implementation. The `skolem_abundance` constraint enforces a world-shifting behavior that prevents finding valid countermodels for temporal operators. By modifying this constraint or the temporal operator implementations, we can enable the expected countermodel behavior.

In both examples, a valid countermodel would include a world where a proposition is true at the current time but false at some future time, which the current constraints prevent from being constructed.