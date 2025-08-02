# Fix Counterfactual Evaluation in Logos Theory

## Problem Analysis

### Observed Issue

When running the counterfactual example IM_CM_24, we observe incorrect evaluation:

```
|(A \boxright B)| = < {□}, ∅ >  (True in a.b)
  |A| = < {b, □}, ∅ >  (True in a.b)
  |A|-alternatives to a.b = {a.b}
    |B| = < {b.c}, {a} >  (False in a.b)
```

This is incorrect because:
- A is true at a.b (verified by b)
- The only A-alternative to a.b is {a.b} itself
- B is false at a.b (falsified by a)
- Therefore, `A \boxright B` should be **false** at a.b, not true

Similarly for world a.c:
```
|(A \boxright B)| = < {□}, ∅ >  (True in a.c)
  |A|-alternatives to a.c = {a.b, a.c, b.c}
    |B| = < {b.c}, {a} >  (False in a.b)
    |B| = < {b.c}, {a} >  (False in a.c)
```

Since B is false at both a.b and a.c (two of the three A-alternatives), the counterfactual should be false at a.c.

### Root Cause

The root cause is identical to the imposition operator issue:

1. **World-Relative Truth Not Captured**: The counterfactual operator's `find_verifiers_and_falsifiers` method evaluates at a single evaluation point and returns null state as verifier/falsifier. This doesn't capture that counterfactual truth is world-relative.

2. **Null State Verification Problem**: Using `{□}` (null state) as verifier when the counterfactual is true globally is incorrect. The counterfactual should be verified by the specific worlds where it holds true.

3. **Modal Interaction Failure**: When `□(A \boxright B)` is evaluated, the necessity operator needs to check if the counterfactual is true at each world. But with null state verification, it can't distinguish world-specific truth values.

### Code Analysis

In `CounterfactualOperator.find_verifiers_and_falsifiers`:

```python
def find_verifiers_and_falsifiers(self, left_sent_obj, right_sent_obj, eval_point):
    """Finds the verifiers and falsifiers for a counterfactual conditional."""
    evaluate = left_sent_obj.proposition.model_structure.z3_model.evaluate
    if bool(evaluate(self.true_at(left_sent_obj, right_sent_obj, eval_point))):
        return {self.semantics.null_state}, set()
    if bool(evaluate(self.false_at(left_sent_obj, right_sent_obj, eval_point))):
        return set(), {self.semantics.null_state}
    raise ValueError(...)
```

This evaluates the counterfactual at `eval_point` only and uses null state for verification. It should instead check each world to build world-based verifier/falsifier sets.

## Solution Implementation

### Phase 1: World-Based Verifiers for Counterfactuals

#### Step 1: Revise CounterfactualOperator.find_verifiers_and_falsifiers

```python
def find_verifiers_and_falsifiers(self, leftarg, rightarg, eval_point):
    """Find verifiers and falsifiers for a counterfactual conditional.
    
    A counterfactual A □→ B is:
    - True at world w iff for all verifiers x of A and all worlds u 
      such that u is an x-alternative to w, B is true at u
    - False at world w iff there exists a verifier x of A and a world u
      such that u is an x-alternative to w and B is false at u
      
    This method checks each world to determine truth value and builds
    verifier/falsifier sets accordingly.
    """
    # Get model structure and semantics
    model = leftarg.proposition.model_structure
    semantics = self.semantics
    z3_model = model.z3_model
    
    # Initialize verifier and falsifier sets
    verifiers = set()
    falsifiers = set()
    
    # Get the verifiers of the antecedent
    leftarg_verifiers = leftarg.proposition.verifiers
    
    # Check each world to determine if A □→ B is true or false there
    for world in model.z3_world_states:
        # For THIS world, check if all A-alternatives satisfy B
        alternative_found = False
        all_alternatives_satisfy_B = True
        
        for x_state in leftarg_verifiers:
            # Check all possible alternative worlds
            for alt_world in model.z3_world_states:
                # Check if alt_world is an x-alternative to this world
                if z3_model.evaluate(semantics.is_alternative(alt_world, x_state, world)):
                    alternative_found = True
                    
                    # Check if B is true at the alternative world
                    B_truth = rightarg.proposition.truth_value_at(alt_world)
                    
                    if B_truth is False:
                        all_alternatives_satisfy_B = False
                        break
            
            if not all_alternatives_satisfy_B:
                break
        
        # Determine truth at this world
        if not alternative_found:
            # No A-alternatives from this world - vacuously true
            verifiers.add(world)
        elif all_alternatives_satisfy_B:
            # All A-alternatives satisfy B - true at this world
            verifiers.add(world)
        else:
            # Some A-alternative falsifies B - false at this world
            falsifiers.add(world)
    
    return verifiers, falsifiers
```

#### Step 2: Update extended_verify and extended_falsify

```python
def extended_verify(self, state, leftarg, rightarg, eval_point):
    """A state verifies A □→ B at a world if the state is that world
    and A □→ B is true at that world."""
    world = eval_point["world"]
    return z3.And(
        state == world,
        self.true_at(leftarg, rightarg, eval_point)
    )

def extended_falsify(self, state, leftarg, rightarg, eval_point):
    """A state falsifies A □→ B at a world if the state is that world
    and A □→ B is false at that world."""
    world = eval_point["world"]
    return z3.And(
        state == world,
        self.false_at(leftarg, rightarg, eval_point)
    )
```

### Phase 2: Apply Same Fix to Modal Operators

The modal operators (Necessity, Possibility) have the same issue. They should also use world-based verification:

#### Update NecessityOperator.find_verifiers_and_falsifiers

```python
def find_verifiers_and_falsifiers(self, argument, eval_point):
    """Find verifiers and falsifiers for a necessity statement.
    
    □A is:
    - True at world w iff A is true at all worlds
    - False at world w iff A is false at some world
    
    Since necessity is not world-relative in the same way as counterfactuals,
    we can still use a simplified approach, but should consider world-based
    verification for consistency.
    """
    # Option 1: Keep current implementation (simpler)
    # Option 2: Use world-based verification for consistency
    
    # For now, keeping current implementation as necessity truth
    # doesn't vary by evaluation world in standard modal logic
    evaluate = argument.proposition.model_structure.z3_model.evaluate
    if bool(evaluate(self.true_at(argument, eval_point))):
        return {self.semantics.null_state}, set()
    if bool(evaluate(self.false_at(argument, eval_point))):
        return set(), {self.semantics.null_state}
    raise ValueError(...)
```

### Phase 3: Testing Strategy

#### Test Cases

1. **Basic Counterfactual**: 
   ```python
   premises = ['A', '\\neg B']
   conclusions = ['\\neg (A \\boxright B)']
   ```

2. **Modal Context (IM_CM_24)**:
   ```python
   premises = ['(A \\boxright B)']
   conclusions = ['\\Box (A \\boxright B)']
   ```

3. **Complex Alternatives**:
   ```python
   premises = ['\\Diamond A', '\\Box \\neg B']
   conclusions = ['\\Box \\neg (A \\boxright B)']
   ```

## Implementation Plan

### Step 1: Implement CounterfactualOperator Fix ✓
1. ✓ Update `find_verifiers_and_falsifiers` to use world-based evaluation
2. ✓ Update `extended_verify` and `extended_falsify` to match
3. ✓ Test with IM_CM_24 example

### Step 2: Verify Correctness ✓
1. ✓ Run all counterfactual examples (33 tests pass)
2. ✓ Check that world-specific evaluation is correct
3. ✓ Ensure no false premise models

### Step 3: Consider Modal Operator Updates
1. Evaluate if modal operators need similar updates
2. Test interaction between modal and counterfactual operators
3. Ensure consistency across the theory

## Implementation Status

### Completed Changes

#### CounterfactualOperator.find_verifiers_and_falsifiers
- ✓ Implemented world-based evaluation
- ✓ Checks each world to determine if A □→ B is true or false there
- ✓ Returns worlds as verifiers/falsifiers instead of null state

#### CounterfactualOperator.extended_verify/falsify
- ✓ Updated to use world-based verification
- ✓ A state verifies A □→ B if it's the world where A □→ B is true
- ✓ A state falsifies A □→ B if it's the world where A □→ B is false

### Test Results

The IM_CM_24 example now produces correct results:
```
|(A \boxright B)| = < {b.c}, {a.b, a.c} >  (False in a.b)
  |A| = < {b, □}, ∅ >  (True in a.b)
  |A|-alternatives to a.b = {a.b}
    |B| = < {b.c}, {a} >  (False in a.b)

|(A \boxright B)| = < {b.c}, {a.b, a.c} >  (False in a.c)
  |A| = < {b, □}, ∅ >  (True in a.c)
  |A|-alternatives to a.c = {a.b, a.c, b.c}
    |B| = < {b.c}, {a} >  (True in b.c)
    |B| = < {b.c}, {a} >  (False in a.b)
    |B| = < {b.c}, {a} >  (False in a.c)
```

The counterfactual is now correctly:
- Verified by world b.c (where all A-alternatives satisfy B)
- Falsified by worlds a.b and a.c (where some A-alternative falsifies B)

This allows `□(A \boxright B)` to be correctly evaluated as false.

### Additional Test Results

All 33 counterfactual tests pass successfully:
- 21 countermodel tests (CF_CM_1 through CF_CM_21)
- 12 theorem tests (CF_TH_1 through CF_TH_12)

No false premise models were encountered, and the world-based evaluation correctly handles all test cases including:
- Basic counterfactuals
- Nested modal operators with counterfactuals
- Complex alternative world scenarios
- Might counterfactuals

## Next Steps

The counterfactual operator now correctly implements world-based verification. The modal operators (necessity, possibility) currently still use null state verification, which works for their simpler semantics but could be updated for consistency with the overall approach.

## Expected Results

After implementation, we should see:

```
|(A \boxright B)| = < {b.c}, {a.b, a.c} >  (False in a.b)
  |A| = < {b, □}, ∅ >  (True in a.b)
  |A|-alternatives to a.b = {a.b}
    |B| = < {b.c}, {a} >  (False in a.b)

|(A \boxright B)| = < {b.c}, {a.b, a.c} >  (False in a.c)
  |A| = < {b, □}, ∅ >  (True in a.c)
  |A|-alternatives to a.c = {a.b, a.c, b.c}
    |B| = < {b.c}, {a} >  (True in b.c)
    |B| = < {b.c}, {a} >  (False in a.b)
    |B| = < {b.c}, {a} >  (False in a.c)
```

The counterfactual would be:
- Verified by world b.c (where it's true)
- Falsified by worlds a.b and a.c (where it's false)

This would correctly allow `□(A \boxright B)` to be false, providing the expected countermodel.

## Key Insights

1. **World-Relative Semantics**: Counterfactuals have world-relative truth conditions that cannot be captured by global null state verification.

2. **Verifier Identity**: In world-relative operators, the verifying state should be the world itself where the formula is true, not an abstract null state.

3. **Modal Interaction**: Proper world-based verification ensures that modal operators can correctly evaluate formulas at different worlds.

4. **Consistency**: This approach aligns with the hyperintensional framework where verification is state-based rather than globally abstract.