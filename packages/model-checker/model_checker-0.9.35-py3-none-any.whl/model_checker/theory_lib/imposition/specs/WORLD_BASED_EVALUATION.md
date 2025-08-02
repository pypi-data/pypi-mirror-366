# Implementation Specification: World-Based Evaluation for Imposition

## Problem Analysis

### Current Issues

1. **World Evaluation Context Lost**: When the necessity operator (□) evaluates `A ⊡ B` at different worlds, the imposition operator doesn't properly use the shifted world context. It evaluates at the main evaluation world regardless of the modal context.

2. **Inappropriate Null State Verification**: The current implementation treats imposition as verified by the null state (□) when true everywhere. This is incorrect for Kit Fine's semantics - imposition should be verified by the actual worlds where it holds true.

3. **False Premise Models**: The current approach leads to models where premises that should be satisfiable become unsatisfiable.

### Root Cause

The imposition operator's `find_verifiers_and_falsifiers` method tries to determine a global set of verifiers/falsifiers, but imposition truth is inherently world-relative. The truth value of `A ⊡ B` at world w depends on:
- The verifiers of A
- The imposition relation from w
- The truth of B at the resulting worlds

This cannot be captured by a single global set of verifiers/falsifiers.

## Proposed Solution

### Core Principle

Treat imposition more like a standard proposition:
- Verified by the worlds where it's true
- Falsified by the worlds where it's false
- Properly evaluate at each world based on local conditions

### Implementation Strategy

#### 1. Revise ImpositionOperator.find_verifiers_and_falsifiers

```python
def find_verifiers_and_falsifiers(self, leftarg, rightarg, eval_point):
    """Find verifiers and falsifiers for an imposition statement.
    
    Unlike the current implementation, this checks the truth value
    at each world individually and builds verifier/falsifier sets
    based on world-local evaluation.
    """
    # Get the model and semantics
    model = leftarg.proposition.model_structure
    semantics = self.semantics
    
    verifiers = set()
    falsifiers = set()
    
    # For each world, determine if A ⊡ B is true or false there
    for world in model.z3_world_states:
        # Check if A ⊡ B is true at this specific world
        world_point = {"world": world}
        
        # Get verifiers of A
        leftarg_verifiers = leftarg.proposition.verifiers
        
        # Check if all A-outcomes from THIS world satisfy B
        all_outcomes_satisfy_B = True
        exists_outcome = False
        
        for verifier in leftarg_verifiers:
            # Find outcome worlds from THIS world
            for outcome in model.z3_world_states:
                if model.z3_model.evaluate(semantics.imposition(verifier, world, outcome)):
                    exists_outcome = True
                    B_truth = rightarg.proposition.get_truth_value_at(outcome)
                    
                    if B_truth is False:
                        all_outcomes_satisfy_B = False
                        break
            
            if not all_outcomes_satisfy_B:
                break
        
        # Determine truth at this world
        if not exists_outcome:
            # No A-alternatives: vacuously true
            verifiers.add(world)
        elif all_outcomes_satisfy_B:
            # All A-alternatives satisfy B: true
            verifiers.add(world)
        else:
            # Some A-alternative falsifies B: false
            falsifiers.add(world)
    
    return verifiers, falsifiers
```

#### 2. Alternative: Lazy Evaluation Approach

Instead of pre-computing verifiers/falsifiers, compute truth values on demand:

```python
class ImpositionProposition(LogosProposition):
    """Special proposition class for imposition that evaluates lazily."""
    
    def __init__(self, sentence, model_structure):
        # Store components but don't compute verifiers/falsifiers yet
        self.sentence = sentence
        self.model_structure = model_structure
        self.leftarg = sentence.arguments[0]
        self.rightarg = sentence.arguments[1]
        self._verifiers = None
        self._falsifiers = None
    
    @property
    def verifiers(self):
        if self._verifiers is None:
            self._compute_verifiers_falsifiers()
        return self._verifiers
    
    @property
    def falsifiers(self):
        if self._falsifiers is None:
            self._compute_verifiers_falsifiers()
        return self._falsifiers
    
    def truth_value_at(self, eval_world):
        """Compute truth value of A ⊡ B at a specific world."""
        semantics = self.model_structure.semantics
        model = self.model_structure.z3_model
        
        # Get verifiers of the antecedent
        leftarg_verifiers = self.leftarg.proposition.verifiers
        
        # Check outcomes from THIS world
        all_outcomes_satisfy_B = True
        exists_outcome = False
        
        for verifier in leftarg_verifiers:
            for outcome in self.model_structure.z3_world_states:
                if model.evaluate(semantics.imposition(verifier, eval_world, outcome)):
                    exists_outcome = True
                    if not self.rightarg.proposition.get_truth_value_at(outcome):
                        all_outcomes_satisfy_B = False
                        break
            
            if not all_outcomes_satisfy_B:
                break
        
        # Return truth value
        return not exists_outcome or all_outcomes_satisfy_B
```

#### 3. Ensure Proper World Context Propagation

The key is ensuring that when modal operators evaluate subformulas at different worlds, that world context is properly used:

```python
# In NecessityOperator.find_verifiers_and_falsifiers
def find_verifiers_and_falsifiers(self, argument, eval_point):
    """Properly propagate world context when checking necessity."""
    
    # For complex arguments like imposition, we need to ensure
    # they evaluate at each world, not just use pre-computed values
    
    # Option 1: Force re-evaluation at each world
    for world in all_worlds:
        # Create a new evaluation context
        world_point = {"world": world}
        
        # For imposition arguments, this should trigger world-specific evaluation
        truth_at_world = self._evaluate_at_world(argument, world_point)
    
    # Option 2: Use truth_value_at method that respects world context
    for world in all_worlds:
        truth_at_world = argument.proposition.truth_value_at(world)
```

## Implementation Plan

### Phase 1: Modify ImpositionOperator (Minimal Change)

1. Update `find_verifiers_and_falsifiers` to compute world-based verifiers/falsifiers
2. Remove the null state verification approach
3. Test with existing examples

### Phase 2: Add World-Aware Truth Evaluation (Medium Change)

1. Override `truth_value_at` in ImpositionOperator or create custom proposition class
2. Ensure it properly evaluates based on the given world, not a pre-computed set
3. Update NecessityOperator to use `truth_value_at` for world-specific evaluation

### Phase 3: Full Architectural Revision (Large Change)

1. Create `ImpositionProposition` class with lazy evaluation
2. Modify the imposition theory to use this custom proposition class
3. Ensure all operators respect world-relative evaluation

## Testing Strategy

### Test Cases

1. **Basic Imposition**: `A`, `¬B` ⊢ `¬(A ⊡ B)`
   - Should find a model where A is true and B is false

2. **Modal Context**: `◇A`, `□¬B` ⊢ `□¬(A ⊡ B)`  
   - Should correctly evaluate imposition at each world
   - Should not get false premise models

3. **Nested Modal**: `□(A ⊡ B)` ⊢ `□□(A ⊡ B)`
   - Should properly handle nested modal contexts

### Validation Criteria

1. No false premise models for satisfiable premises
2. Imposition evaluates correctly at each world
3. Modal operators properly shift evaluation context
4. Results match Kit Fine's semantic theory

## Recommended Approach

Start with **Phase 1** as it requires minimal architectural changes while addressing the core issues:

1. Imposition will be verified by worlds where it's true (not null state)
2. World-specific evaluation will be computed correctly
3. Modal operators will work with the world-based verifiers/falsifiers

If Phase 1 proves insufficient, proceed to Phase 2 or 3 for more comprehensive fixes.

## Key Insight

The fundamental issue is that imposition truth is **world-relative** and cannot be captured by a single global verifier set in the same way as simpler operators. The solution must respect this world-relativity while working within the model checker's architecture.