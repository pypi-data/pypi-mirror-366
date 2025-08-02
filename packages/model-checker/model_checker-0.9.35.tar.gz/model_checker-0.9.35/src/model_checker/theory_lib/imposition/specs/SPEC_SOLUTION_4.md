# Implementation Specification: Proposition-Based Formula Evaluation

## Overview

This document provides a detailed implementation plan for Solution 4 from SPEC_3.md. The solution addresses the delegation chain bug by modifying operators to use existing proposition values instead of creating new formulas through semantic delegation during Phase 2 evaluation.

## Problem Context

During Phase 2 of model evaluation, when `find_verifiers_and_falsifiers` is called:
- The current implementation creates new formulas through delegation chains
- These complex nested formulas evaluate differently than individual proposition checks
- This causes incorrect results for modal operators like necessity (□)

## Solution Approach

Instead of creating new formulas, operators will:
1. Access already-evaluated proposition values
2. Check truth values directly at each world
3. Return verifiers/falsifiers based on these checks

## Implementation Details

### Step 1: Add Proposition Access Methods

First, ensure propositions have methods to check truth values:

```python
# In model.py, class PropositionDefaults
class PropositionDefaults:
    # Existing methods...
    
    def is_true_at(self, world):
        """Check if this proposition is true at the given world."""
        evaluate = self.model_structure.z3_model.evaluate
        return bool(evaluate(IsMember(world, self.verifiers)))
    
    def is_false_at(self, world):
        """Check if this proposition is false at the given world."""
        evaluate = self.model_structure.z3_model.evaluate
        return bool(evaluate(IsMember(world, self.falsifiers)))
    
    def get_truth_value_at(self, world):
        """Get the truth value (True/False/Neither) at the given world."""
        if self.is_true_at(world):
            return True
        elif self.is_false_at(world):
            return False
        else:
            return None  # Neither true nor false
```

### Step 2: Modify NecessityOperator

Update the NecessityOperator to use proposition values:

```python
# In logos/subtheories/modal/operators.py
class NecessityOperator(syntactic.Operator):
    """Implementation of the necessity/universal modality (□)."""
    name = "\\Box"
    arity = 1

    # Keep existing true_at, false_at, extended_verify, extended_falsify methods
    
    def find_verifiers_and_falsifiers(self, argument, eval_point):
        """Finds the verifiers and falsifiers for a necessity statement.
        
        Uses proposition-based evaluation to avoid delegation chain issues.
        """
        # Check if argument has a proposition
        if not hasattr(argument, 'proposition') or argument.proposition is None:
            # Fallback to formula-based evaluation if no proposition exists
            return self._formula_based_evaluation(argument, eval_point)
        
        # Get the model structure
        model = argument.proposition.model_structure
        
        # Check truth at all worlds
        all_worlds = model.z3_world_states
        all_true = True
        exists_false = False
        
        for world in all_worlds:
            truth_value = argument.proposition.get_truth_value_at(world)
            
            if truth_value is False:
                exists_false = True
                all_true = False
                break
            elif truth_value is None:
                # Neither true nor false - this shouldn't happen in our models
                raise ValueError(
                    f"{argument} is neither true nor false at world {world}"
                )
        
        # Return appropriate verifiers/falsifiers
        if all_true:
            return {self.semantics.null_state}, set()
        elif exists_false:
            return set(), {self.semantics.null_state}
        else:
            raise ValueError(
                f"Unexpected state: all_true={all_true}, exists_false={exists_false}"
            )
    
    def _formula_based_evaluation(self, argument, eval_point):
        """Fallback to original formula-based evaluation."""
        evaluate = argument.proposition.model_structure.z3_model.evaluate
        if bool(evaluate(self.true_at(argument, eval_point))):
            return {self.semantics.null_state}, set()
        if bool(evaluate(self.false_at(argument, eval_point))):
            return set(), {self.semantics.null_state}
        raise ValueError(
            f"{self.name} {argument} "
            f"is neither true nor false in the world {eval_point}."
        )
```

### Step 3: Update PossibilityOperator (if needed)

Since PossibilityOperator is defined in terms of NecessityOperator, it should automatically benefit from the fix. However, we should verify this:

```python
class PossibilityOperator(syntactic.DefinedOperator):
    """Implementation of the possibility/existential modality (◇)."""
    
    name = "\\Diamond"
    arity = 1
    
    def derived_definition(self, argument):
        """Defines possibility as negation of necessity of negation."""
        return [NegationOperator, [NecessityOperator, [NegationOperator, argument]]]
    
    # The find_verifiers_and_falsifiers method will be inherited from DefinedOperator
    # and will use the updated NecessityOperator implementation
```

### Step 4: Ensure Proposition Evaluation Order

We need to ensure that propositions are evaluated in the correct order:

```python
# In model.py, ModelDefaults.interpret method
def interpret(self, sentences):
    """Recursively updates sentences with their semantic interpretations in the model.
    
    Ensures propositions are created in dependency order.
    """
    if not self.z3_model:
        return

    # First pass: Create all propositions
    for sent_obj in sentences:
        if sent_obj.proposition is not None:
            continue
        if sent_obj.arguments:
            self.interpret(sent_obj.arguments)
        sent_obj.update_proposition(self)
    
    # Second pass: Evaluate propositions
    # This ensures all propositions exist before evaluation
    for sent_obj in sentences:
        if hasattr(sent_obj.proposition, 'evaluate'):
            sent_obj.proposition.evaluate()
```

### Step 5: Add Safety Checks

Add validation to ensure the approach is working correctly:

```python
# In the operator implementation
def find_verifiers_and_falsifiers(self, argument, eval_point):
    """Enhanced with validation checks."""
    # ... main implementation ...
    
    # Validation: Compare with formula-based result in debug mode
    if hasattr(self.semantics, 'debug_mode') and self.semantics.debug_mode:
        prop_result = (verifiers, falsifiers)  # From proposition-based evaluation
        formula_result = self._formula_based_evaluation(argument, eval_point)
        
        if prop_result != formula_result:
            print(f"WARNING: Evaluation mismatch for {self.name} {argument}")
            print(f"  Proposition-based: {prop_result}")
            print(f"  Formula-based: {formula_result}")
    
    return verifiers, falsifiers
```

## Testing Strategy

### Unit Tests

Create specific tests for the new evaluation method:

```python
# test_proposition_evaluation.py
def test_necessity_uses_proposition_values():
    """Test that NecessityOperator uses proposition values correctly."""
    # Setup
    premises = ['\\Diamond A', '\\Box \\neg B']
    conclusions = ['\\Box \\neg (A \\imposition B)']
    
    # Build model
    model = create_model(premises, conclusions)
    
    # Verify proposition values are used
    box_neg_ab = model.conclusions[0]
    verifiers, falsifiers = box_neg_ab.operator.find_verifiers_and_falsifiers(
        box_neg_ab.arguments[0], 
        model.main_point
    )
    
    # Check results
    assert len(verifiers) == 1
    assert len(falsifiers) == 0
```

### Integration Tests

Test with the original failing example:

```python
def test_imposition_bug_fixed():
    """Test that the original imposition bug is fixed."""
    premises = []
    conclusions = ['\\Box \\neg (A \\imposition B)']
    
    model = create_model(premises, conclusions)
    
    # The conclusion should be false (countermodel exists)
    assert model.z3_model is not None
    assert model.check_result() == True  # Found countermodel as expected
```

### Regression Tests

Ensure other theories still work:

```python
def test_logos_examples_unchanged():
    """Ensure logos theory examples still work."""
    # Run all logos examples
    # Verify same results as before
```

## Rollout Plan

### Phase 1: Implementation (1-2 days)
1. Add proposition access methods
2. Modify NecessityOperator
3. Add debug validation

### Phase 2: Testing (2-3 days)
1. Create unit tests
2. Run integration tests
3. Verify imposition bug is fixed
4. Run regression tests on all theories

### Phase 3: Extension (1 week)
1. Identify other operators that could benefit
2. Apply same pattern to other modal operators
3. Document the pattern for future operators

### Phase 4: Monitoring (ongoing)
1. Add logging to track evaluation paths
2. Monitor for any evaluation mismatches
3. Gather performance metrics

## Risks and Mitigations

### Risk 1: Circular Dependencies
**Risk**: Operators might depend on each other in ways that create circles.
**Mitigation**: 
- Implement dependency tracking
- Add cycle detection
- Fallback to formula evaluation if cycles detected

### Risk 2: Incomplete Propositions
**Risk**: Some propositions might not be fully evaluated when needed.
**Mitigation**:
- Add existence checks before using proposition values
- Implement lazy evaluation if needed
- Maintain formula-based fallback

### Risk 3: Performance Impact
**Risk**: Additional checks might slow down evaluation.
**Mitigation**:
- Cache proposition values
- Use efficient data structures
- Profile and optimize hot paths

## Success Criteria

1. The imposition theory bug is fixed
2. All existing tests pass
3. No performance regression > 10%
4. Code is well-documented and maintainable
5. Pattern is reusable for other operators

## Future Enhancements

1. **Automatic Detection**: Automatically detect when proposition-based evaluation should be used
2. **Caching Layer**: Add intelligent caching of evaluation results
3. **Diagnostic Tools**: Build tools to visualize evaluation paths
4. **Performance Optimization**: Optimize for common patterns

## Conclusion

This implementation plan provides a systematic approach to fixing the delegation chain bug while maintaining system integrity. By using existing proposition values instead of creating new formulas, we avoid the complexity that leads to incorrect evaluations while working within the existing two-phase architecture.