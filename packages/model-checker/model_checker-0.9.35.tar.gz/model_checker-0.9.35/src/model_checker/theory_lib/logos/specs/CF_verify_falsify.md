# Refined Counterfactual Verification and Falsification

## Overview

This document outlines the implementation plan for refining the verifiers and falsifiers of counterfactual sentences to properly respect fusion closure and the hyperintensional semantics of the logos framework.

## Current Issue

The current implementation assigns worlds as verifiers/falsifiers for counterfactuals:
- `(A \boxright B)` is verified by worlds where it's true
- `(A \boxright B)` is falsified by worlds where it's false

This doesn't respect:
1. **Fusion Closure**: Verifiers should be closed under fusion
2. **Hyperintensional Semantics**: States (not just worlds) should verify/falsify counterfactuals
3. **Proper Counterfactual Semantics**: The verification conditions should reflect the fine-grained structure of counterfactual dependence

## Proposed Semantics

### Verification Condition

A state `s` verifies `(A \boxright B)` iff:
- For all verifiers `v` of A
- For all maximal parts `t` of `s` that are compatible with `v`
- The fusion `t.v` is incompatible with any falsifier of B

Formally:
```
s ⊨ (A □→ B) iff ∀v ∈ Ver(A), ∀t ≤ s : (t is maximal compatible with v) → 
                   ∀f ∈ Fal(B) : ¬Compatible(t.v, f)
```

### Falsification Condition

A state `s` falsifies `(A \boxright B)` iff:
- There exists a verifier `v` of A
- There exists a maximal part `t` of `s` that is compatible with `v`
- The fusion `t.v` is compatible with some falsifier of B

Formally:
```
s ⊭ (A □→ B) iff ∃v ∈ Ver(A), ∃t ≤ s : (t is maximal compatible with v) ∧ 
                   ∃f ∈ Fal(B) : Compatible(t.v, f)
```

## Implementation Plan

### Phase 1: Update find_verifiers_and_falsifiers

```python
def find_verifiers_and_falsifiers(self, leftarg, rightarg, eval_point):
    """Find verifiers and falsifiers for a counterfactual conditional.
    
    A state s verifies (A □→ B) iff:
    - For all verifiers v of A and all maximal parts t of s compatible with v,
      the fusion t.v is incompatible with any falsifier of B
      
    A state s falsifies (A □→ B) iff:
    - There exists a verifier v of A and a maximal part t of s compatible with v
      where the fusion t.v is compatible with some falsifier of B
    """
    # Get model structure and semantics
    model = leftarg.proposition.model_structure
    semantics = self.semantics
    z3_model = model.z3_model
    
    # Get verifiers and falsifiers of the arguments
    leftarg_verifiers = leftarg.proposition.verifiers
    leftarg_falsifiers = leftarg.proposition.falsifiers
    rightarg_verifiers = rightarg.proposition.verifiers
    rightarg_falsifiers = rightarg.proposition.falsifiers
    
    # Initialize verifier and falsifier sets
    verifiers = set()
    falsifiers = set()
    
    # Check each possible state (not just worlds)
    for state in model.all_states:
        # Skip impossible states unless print_impossible is set
        if not z3_model.evaluate(semantics.possible(state)) and not model.settings.get('print_impossible', False):
            continue
            
        # Check if state verifies the counterfactual
        verifies = True
        for v in leftarg_verifiers:
            # Find all maximal parts of state compatible with v
            for t in model.all_states:
                if not z3_model.evaluate(semantics.is_part_of(t, state)):
                    continue
                    
                # Check if t is maximal compatible part
                if z3_model.evaluate(semantics.max_compatible_part(t, state, v)):
                    # Check if t.v is compatible with any falsifier of B
                    tv_fusion = z3_model.evaluate(semantics.fusion(t, v))
                    
                    for f in rightarg_falsifiers:
                        if z3_model.evaluate(semantics.compatible(tv_fusion, f)):
                            verifies = False
                            break
                    
                    if not verifies:
                        break
            
            if not verifies:
                break
        
        if verifies:
            verifiers.add(state)
        
        # Check if state falsifies the counterfactual
        falsifies = False
        for v in leftarg_verifiers:
            # Find all maximal parts of state compatible with v
            for t in model.all_states:
                if not z3_model.evaluate(semantics.is_part_of(t, state)):
                    continue
                    
                # Check if t is maximal compatible part
                if z3_model.evaluate(semantics.max_compatible_part(t, state, v)):
                    # Check if t.v is compatible with any falsifier of B
                    tv_fusion = z3_model.evaluate(semantics.fusion(t, v))
                    
                    for f in rightarg_falsifiers:
                        if z3_model.evaluate(semantics.compatible(tv_fusion, f)):
                            falsifies = True
                            break
                    
                    if falsifies:
                        break
            
            if falsifies:
                break
        
        if falsifies:
            falsifiers.add(state)
    
    return verifiers, falsifiers
```

### Phase 2: Ensure Fusion Closure

After computing initial verifiers and falsifiers, ensure they are closed under fusion:

```python
def ensure_fusion_closure(self, states, model, semantics, z3_model):
    """Ensure a set of states is closed under fusion."""
    closed_set = set(states)
    changed = True
    
    while changed:
        changed = False
        new_states = set()
        
        # Check all pairs of states in the current set
        for s1 in closed_set:
            for s2 in closed_set:
                # Compute fusion
                fusion = z3_model.evaluate(semantics.fusion(s1, s2))
                
                # Add to new states if not already in set
                if fusion not in closed_set:
                    new_states.add(fusion)
                    changed = True
        
        closed_set.update(new_states)
    
    return closed_set
```

### Phase 3: Update extended_verify and extended_falsify

These should now check the refined conditions:

```python
def extended_verify(self, state, leftarg, rightarg, eval_point):
    """Check if a state verifies A □→ B using the refined semantics."""
    semantics = self.semantics
    N = semantics.N
    
    # Variables for quantifiers
    v = z3.BitVec("cf_ver_v", N)
    t = z3.BitVec("cf_ver_t", N)
    f = z3.BitVec("cf_ver_f", N)
    
    # For all verifiers v of A
    return ForAll([v],
        z3.Implies(
            semantics.extended_verify(v, leftarg, eval_point),
            # For all maximal parts t of state compatible with v
            ForAll([t],
                z3.Implies(
                    semantics.max_compatible_part(t, state, v),
                    # t.v is incompatible with all falsifiers of B
                    ForAll([f],
                        z3.Implies(
                            semantics.extended_falsify(f, rightarg, eval_point),
                            z3.Not(semantics.compatible(semantics.fusion(t, v), f))
                        )
                    )
                )
            )
        )
    )

def extended_falsify(self, state, leftarg, rightarg, eval_point):
    """Check if a state falsifies A □→ B using the refined semantics."""
    semantics = self.semantics
    N = semantics.N
    
    # Variables for quantifiers
    v = z3.BitVec("cf_fal_v", N)
    t = z3.BitVec("cf_fal_t", N)
    f = z3.BitVec("cf_fal_f", N)
    
    # There exists a verifier v of A
    return Exists([v],
        z3.And(
            semantics.extended_verify(v, leftarg, eval_point),
            # There exists a maximal part t of state compatible with v
            Exists([t],
                z3.And(
                    semantics.max_compatible_part(t, state, v),
                    # t.v is compatible with some falsifier of B
                    Exists([f],
                        z3.And(
                            semantics.extended_falsify(f, rightarg, eval_point),
                            semantics.compatible(semantics.fusion(t, v), f)
                        )
                    )
                )
            )
        )
    )
```

## Testing Strategy

### Test Case 1: Basic Fusion Closure
Verify that if states s1 and s2 both verify a counterfactual, then their fusion s1.s2 also verifies it.

### Test Case 2: Non-World Verifiers
Check cases where non-world states (e.g., atomic states) can verify counterfactuals.

### Test Case 3: Compatibility Constraints
Test that the maximal compatible part calculation works correctly in determining verification.

### Test Case 4: Existing Examples
Ensure all existing counterfactual tests still pass with the refined semantics.

## Implementation Steps

1. **Backup Current Implementation**: Save the current working implementation
2. **Implement Refined find_verifiers_and_falsifiers**: Update the method with the new semantics
3. **Add Fusion Closure**: Ensure verifier/falsifier sets are closed under fusion
4. **Update Extended Methods**: Modify extended_verify and extended_falsify
5. **Test Incrementally**: Run tests after each major change
6. **Debug and Refine**: Address any issues that arise

## Potential Challenges

### Performance
The refined semantics requires checking many more states and computing maximal compatible parts, which could be computationally expensive.

**Mitigation**: 
- Cache maximal compatible part calculations
- Use early termination when possible
- Consider limiting to possible states initially

### Consistency with true_at/false_at
The refined verification conditions should align with the existing true_at and false_at methods.

**Verification**: Ensure that:
- If all verifiers of (A □→ B) are part of world w, then true_at returns true for w
- If some falsifier of (A □→ B) is part of world w, then false_at returns true for w

### Edge Cases
- Empty verifier/falsifier sets for antecedent or consequent
- Impossible states as verifiers/falsifiers
- Null state handling

## Expected Outcomes

After implementation:
1. Counterfactual verifiers/falsifiers will be properly closed under fusion
2. Non-world states can verify/falsify counterfactuals
3. The semantics will more accurately reflect hyperintensional counterfactual dependence
4. All existing tests should continue to pass
5. The framework will support more fine-grained counterfactual reasoning