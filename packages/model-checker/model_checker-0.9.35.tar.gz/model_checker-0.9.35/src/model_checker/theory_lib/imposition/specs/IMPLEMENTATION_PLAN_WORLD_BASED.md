# Detailed Implementation Plan: World-Based Verifiers for Imposition

## Overview

This plan details how to revise `ImpositionOperator.find_verifiers_and_falsifiers` to correctly handle world-relative evaluation of imposition claims, with special focus on ensuring proper world-shifting when imposition appears inside modal operators.

## Key Problems to Solve

1. **World Context Problem**: The current implementation evaluates imposition at a single evaluation point, but needs to determine verifiers/falsifiers across all worlds.

2. **Modal World-Shifting Problem**: When `□(A ⊡ B)` is evaluated, the necessity operator shifts the evaluation world for its argument. The imposition operator must respect this shifted world context when computing its truth value. Currently, it may be using the original evaluation world instead of the shifted one.

3. **Null State Problem**: Using the null state as a verifier is incorrect - imposition should be verified by the specific worlds where it holds true.

## Critical Insight: World-Shifting in Modal Contexts

When a modal operator like `□` evaluates `A ⊡ B` at different worlds, the evaluation happens in two phases:

**Phase 1 (Constraint Generation):**
- `NecessityOperator.true_at` creates: `ForAll(w, is_world(w) → semantics.true_at(A ⊡ B, {"world": w}))`
- This correctly passes each world w to the imposition evaluation
- The formula `ImpositionOperator.true_at(A, B, {"world": w})` uses the shifted world

**Phase 2 (Proposition Creation & Evaluation):**
- `find_verifiers_and_falsifiers` is called ONCE to determine which worlds verify the imposition
- It computes: verifiers = {w | A ⊡ B is true at w}
- Later, when modal operators check truth at world w, they check: is w in verifiers?
- This automatically handles world-shifting because each world's membership was determined by its local imposition behavior

## Implementation Details

### Understanding the Evaluation Flow

When `□(A ⊡ B)` is evaluated:

1. `NecessityOperator.true_at` creates: `ForAll(w, is_world(w) → semantics.true_at(A ⊡ B, {"world": w}))`
2. During proposition creation, `find_proposition` is called with the main evaluation world
3. However, during model checking, the formula evaluates `A ⊡ B` at each world w

The key issue is that `find_verifiers_and_falsifiers` is called only once during proposition creation, but the imposition needs different truth values at different worlds.

### Step 1: Understand When find_verifiers_and_falsifiers is Called

The method is called during Phase 2 (proposition creation) in `LogosProposition.__init__`:
```python
self.verifiers, self.falsifiers = self.find_proposition()
# which calls:
operator.find_verifiers_and_falsifiers(*arguments, eval_point)
```

At this point, `eval_point` contains the world where the proposition is being created (usually the main world). This is NOT the shifted world from modal evaluation.

### Step 2: Revise find_verifiers_and_falsifiers for World-Based Truth

```python
def find_verifiers_and_falsifiers(self, leftarg, rightarg, eval_point):
    """Find verifiers and falsifiers for an imposition statement.
    
    CRITICAL: This method is called during proposition creation, NOT during
    modal evaluation. It must compute which worlds verify/falsify the imposition
    so that modal operators can later check truth at different worlds.
    
    The verifiers are the worlds where A ⊡ B is true.
    The falsifiers are the worlds where A ⊡ B is false.
    
    For each world w:
    - A ⊡ B is true at w iff for all verifiers x of A and all worlds u 
      such that imposition(x, w, u), B is true at u
    - A ⊡ B is false at w iff there exists a verifier x of A and a world u
      such that imposition(x, w, u) and B is false at u
    """
    # Check if we have the necessary components
    if not hasattr(leftarg, 'proposition') or leftarg.proposition is None or \
       not hasattr(rightarg, 'proposition') or rightarg.proposition is None:
        # During constraint generation phase, use formula-based evaluation
        return self._formula_based_evaluation(leftarg, rightarg, eval_point)
    
    # Get model structure and semantics
    model = leftarg.proposition.model_structure
    semantics = self.semantics
    z3_model = model.z3_model
    
    # Initialize verifier and falsifier sets
    verifiers = set()
    falsifiers = set()
    
    # Get the verifiers of the antecedent (these are states, not worlds)
    leftarg_verifiers = leftarg.proposition.verifiers
    
    # CRITICAL: Check each world to determine if A ⊡ B is true or false there
    # This allows modal operators to later check if a specific world is in the verifier set
    for world in model.z3_world_states:
        # For THIS world, check if all A-impositions lead to B being true
        imposition_found = False
        all_impositions_satisfy_B = True
        
        for x_state in leftarg_verifiers:
            # Check all possible outcome worlds FROM THIS WORLD
            for outcome_world in model.z3_world_states:
                # Check if imposition(x_state, world, outcome_world) holds
                if z3_model.evaluate(semantics.imposition(x_state, world, outcome_world)):
                    imposition_found = True
                    
                    # Check if B is true at the outcome world
                    B_truth = rightarg.proposition.truth_value_at(outcome_world)
                    
                    if B_truth is False:
                        all_impositions_satisfy_B = False
                        break
            
            if not all_impositions_satisfy_B:
                break
        
        # Determine the truth value at THIS world
        if not imposition_found:
            # No impositions from this world - vacuously true
            verifiers.add(world)
        elif all_impositions_satisfy_B:
            # All impositions satisfy B - true at this world
            verifiers.add(world)
        else:
            # Some imposition fails to satisfy B - false at this world
            falsifiers.add(world)
    
    return verifiers, falsifiers
```

### Step 2: Update _formula_based_evaluation

The fallback method should follow the same pattern but use formulas:

```python
def _formula_based_evaluation(self, leftarg, rightarg, eval_point):
    """Fallback evaluation using formulas instead of propositions.
    
    This is used during the constraint generation phase before propositions exist.
    """
    model_structure = eval_point.get('model_structure')
    if model_structure is None:
        # If we don't have model structure, fall back to original approach
        # This maintains compatibility during constraint generation
        evaluate = leftarg.proposition.model_structure.z3_model.evaluate
        null_state = self.semantics.null_state
        if bool(evaluate(self.true_at(leftarg, rightarg, eval_point))):
            return {null_state}, set()
        if bool(evaluate(self.false_at(leftarg, rightarg, eval_point))):
            return set(), {null_state}
        raise ValueError(
            f"{leftarg.name} {self.name} {rightarg.name} "
            f"is neither true nor false in the world {eval_point}."
        )
    
    # If we have model structure, use world-based evaluation with formulas
    # (Implementation similar to main method but using formulas)
```

### Step 3: How Modal Operators Use the Verifier Sets

When `NecessityOperator` evaluates `□(A ⊡ B)`:

1. During constraint generation (Phase 1):
   - `NecessityOperator.true_at` creates a formula that checks `semantics.true_at(A ⊡ B, {"world": w})` for each world w
   - This delegates to `ImpositionOperator.true_at(A, B, {"world": w})`
   - Each world w is properly passed to the imposition evaluation

2. During proposition creation (Phase 2):
   - `(A ⊡ B).proposition` is created with verifiers = {worlds where A ⊡ B is true}
   - When printing, `truth_value_at(w)` checks if w is in the verifier set
   - This correctly shows different truth values at different worlds

### Step 4: Ensure Compatibility with Extended Semantics

The `extended_verify` and `extended_falsify` methods need to be updated to work with world-based verifiers:

```python
def extended_verify(self, state, leftarg, rightarg, eval_point):
    """A state verifies A ⊡ B at a world if the state is that world
    and A ⊡ B is true at that world.
    
    CRITICAL: The eval_point contains the current evaluation world,
    which may be different from the main world if we're inside a modal operator.
    """
    world = eval_point["world"]
    # The state must be the world itself where imposition is true
    return z3.And(
        state == world,
        self.true_at(leftarg, rightarg, eval_point)
    )

def extended_falsify(self, state, leftarg, rightarg, eval_point):
    """A state falsifies A ⊡ B at a world if the state is that world
    and A ⊡ B is false at that world.
    
    CRITICAL: The eval_point contains the current evaluation world,
    which may be different from the main world if we're inside a modal operator.
    """
    world = eval_point["world"]
    # The state must be the world itself where imposition is false
    return z3.And(
        state == world,
        self.false_at(leftarg, rightarg, eval_point)
    )
```

## Testing and Validation

### Test Case 1: Basic Imposition
```python
premises = ['A', '\\neg B']
conclusions = ['\\neg (A \\imposition B)']
```
Expected: Should find a model where A is true at a world and B is false at that world's A-alternatives.

### Test Case 2: Modal Context (PROBE2)
```python
premises = ['\\Diamond A', '\\Box \\neg B']
conclusions = ['\\Box \\neg (A \\imposition B)']
```
Expected: Should correctly evaluate imposition at each world without false premise errors.

### Test Case 3: Nested Modal (IM_CM_24)
```python
premises = ['(A \\imposition B)']
conclusions = ['\\Box (A \\imposition B)']
```
Expected: Should find a countermodel where imposition holds at one world but not another.

## Implementation Checklist

1. [ ] Update `find_verifiers_and_falsifiers` to use world-based evaluation
2. [ ] Remove null state as verifier/falsifier
3. [ ] Update `extended_verify` and `extended_falsify` to match world-based approach
4. [ ] Test with basic imposition examples
5. [ ] Test with modal contexts (PROBE2)
6. [ ] Test with nested modals (IM_CM_24)
7. [ ] Verify no false premise models occur
8. [ ] Check that world context is properly respected in modal operators

## Key Insights

1. **World as Verifier**: In this approach, a world w verifies `A ⊡ B` iff `A ⊡ B` is true at w. This is more natural than using the null state.

2. **Local Evaluation**: Each world's verification status depends only on the impositions from that specific world, not global properties.

3. **Modal Compatibility**: This approach naturally works with modal operators because they can check the verifier/falsifier sets at different worlds.

4. **World-Shifting Works Automatically**: The key insight is that world-shifting happens at two levels:
   - **Phase 1 (Constraints)**: Modal operators create formulas that evaluate at different worlds
   - **Phase 2 (Propositions)**: Imposition's verifier set contains exactly those worlds where it's true
   - When a modal operator checks truth at a shifted world w, it simply checks if w is in the verifier set
   - This automatically gives the correct world-relative truth value

## Potential Issues and Solutions

### Issue 1: Performance
Checking all worlds and all impositions could be slow for large models.

**Solution**: Add early termination when possible and cache imposition results.

### Issue 2: Constraint Generation Phase
During Phase 1, propositions don't exist yet.

**Solution**: The `_formula_based_evaluation` fallback handles this case, though it may use the less accurate null state approach during constraint generation.

### Issue 3: Consistency
Need to ensure the world-based evaluation matches the constraint-based semantics.

**Solution**: Carefully test that the same models are found with both approaches.

## Next Steps

1. Implement the revised `find_verifiers_and_falsifiers` method
2. Run the test cases to verify correct behavior
3. Check for false premise models
4. Fine-tune based on test results