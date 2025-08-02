# Operator-Semantics Pairing: Implementation Plan

## Problem Overview

The current implementation of theory integration has an issue where operators from one theory can be instantiated with semantics objects from another theory, causing runtime errors when operators try to access theory-specific methods. Specifically:

1. The `ImpositionOperator` expects a semantics object with an `imposition` method
2. When imported into a project using the default theory's semantics, it throws an `AttributeError` because the default `Semantics` class lacks this method
3. This breaks cross-theory compatibility despite common `Proposition` and `ModelStructure` classes

## Root Cause Analysis

The issue stems from how operators are instantiated in `ModelConstraints` and how they're linked to semantic theories:

1. In `BuildExample.__init__()`, a semantics instance is created with:
   ```python
   self.model_constraints = ModelConstraints(
       self.settings,
       self.example_syntax,
       self.semantics(self.settings),  # Creates the semantics instance
       self.proposition,
   )
   ```

2. This single semantics instance is then used to initialize ALL operators, regardless of which theory they originate from

3. The operators from different theories expect their native semantics interface, but receive only one implementation

4. Missing method calls result in `AttributeError` exceptions

## Implementation Plan

### Option 1: Semantics Interface Protocol (Recommended)

Define a common protocol/interface that all semantics classes must implement:

1. Create a `SemanticProtocol` class or abstract base class:
   ```python
   from abc import ABC, abstractmethod
   
   class SemanticProtocol(ABC):
       @abstractmethod
       def true_at(self, sentence, eval_world):
           pass
           
       @abstractmethod
       def false_at(self, sentence, eval_world):
           pass
           
       # Additional common methods...
       
       # Theory-specific methods would have default implementations
       def imposition(self, state, world, outcome):
           raise NotImplementedError("This semantics does not support imposition")
   ```

2. Update `ModelConstraints` to pass operators their native semantics:
   ```python
   def copy_dictionary(self, operator_collection):
       semantics_map = self._build_semantics_map()  # Map theories to semantics instances
       operators = {}
       for name, operator_class in operator_collection.items():
           theory_name = getattr(operator_class, "theory", "default")
           theory_semantics = semantics_map.get(theory_name, self.semantics)
           operators[name] = operator_class(theory_semantics)
       return operators
       
   def _build_semantics_map(self):
       # Build a map of theory names to semantics instances
       semantics_map = {"default": self.semantics}
       if hasattr(self.semantics, "imposition"):
           semantics_map["imposition"] = self.semantics
       # Add more theory-specific mappings as needed
       return semantics_map
   ```

3. Annotate operators with their required theory:
   ```python
   class ImpositionOperator(Operator):
       name = "\\imposition"
       arity = 2
       theory = "imposition"  # New attribute identifying required semantics
   ```

### Option 2: Operator Adapters

Create adapter classes for cross-theory compatibility:

1. Implement adapter factories for operators:
   ```python
   def adapt_operator(operator_class, target_semantics_class):
       if operator_class.name == "\\imposition" and not hasattr(target_semantics_class, "imposition"):
           return ImpositionAdapter
       return operator_class
   ```

2. Create adapter implementations:
   ```python
   class ImpositionAdapter(Operator):
       name = "\\imposition"
       arity = 2
       
       def true_at(self, leftarg, rightarg, eval_world):
           # Implement using functionality available in the target semantics
           # Could use a fallback implementation using other primitives
   ```

3. Modify `ModelConstraints` to use adapters when needed:
   ```python
   def copy_dictionary(self, operator_collection):
       operators = {}
       for name, operator_class in operator_collection.items():
           adapted_class = adapt_operator(operator_class, type(self.semantics))
           operators[name] = adapted_class(self.semantics)
       return operators
   ```

### Option 3: Dynamic Method Resolution

Implement dynamic method resolution for operators to find compatible methods:

1. Add method resolution to `Operator` base class:
   ```python
   def _resolve_method(self, method_name, *args, **kwargs):
       if hasattr(self.semantics, method_name):
           method = getattr(self.semantics, method_name)
           return method(*args, **kwargs)
       # Fall back to alternatives
       if method_name == "imposition" and hasattr(self.semantics, "counterfactual"):
           # Use counterfactual as a fallback for imposition
           return self.semantics.counterfactual(*args, **kwargs)
       raise AttributeError(f"Semantics object has no method '{method_name}'")
   ```

2. Update operators to use the resolution method:
   ```python
   def true_at(self, leftarg, rightarg, eval_world):
       sem = self.semantics
       N = sem.N
       x = z3.BitVec("t_imp_x", N)
       u = z3.BitVec("t_imp_u", N)
       return ForAll(
           [x, u],
           z3.Implies(
               z3.And(
                   sem.extended_verify(x, leftarg, eval_world),
                   self._resolve_method("imposition", x, eval_world, u)
               ),
               sem.true_at(rightarg, u),
           ),
       )
   ```

## Implementation Recommendation

**Option 1: Semantics Interface Protocol** is recommended because:

1. It provides a clear contract that semantics classes must follow
2. It allows for theory-specific extensions while maintaining core compatibility
3. It's explicit about which methods are required vs. optional
4. It enables future expansion to new theories with different requirements

Implementation steps:

1. Define the `SemanticProtocol` abstract base class
2. Update semantics classes to inherit from this protocol
3. Modify `ModelConstraints` to handle theory-specific semantics pairing
4. Add theory attributes to operator classes
5. Update operator instantiation to use the appropriate semantics instance

## Testing Strategy

1. Create explicit tests for cross-theory operator-semantics pairing:
   ```python
   def test_imposition_operator_with_default_semantics():
       """Test that ImpositionOperator works with default semantics."""
       # This should produce a specific error or use a fallback
   
   def test_default_operators_with_imposition_semantics():
       """Test that default operators work with ImpositionSemantics."""
       # This should work without errors
   ```

2. Test importing operators from multiple theories:
   ```python
   def test_mixed_operator_collection():
       """Test that operators from multiple theories can coexist."""
       mixed_collection = OperatorCollection()
       mixed_collection.add_operator(ImpositionOperator)
       mixed_collection.add_operator(BoxrightOperator)
       # Test instantiation and basic functions
   ```

3. Test theory extension pattern:
   ```python
   def test_theory_extension():
       """Test that a theory can extend another theory's operators."""
       # Test registration and inheritance patterns
   ```

## Alternatives Considered

### Complete Theory Isolation

Only allow operators from the same theory to be used together:

- Pros: Simpler implementation, no compatibility issues
- Cons: Limits theory composition and reuse

### Explicit Operator Registration

Require explicit registration of which operators work with which semantics:

- Pros: Precise control over compatibility
- Cons: More verbose, requires maintaining a compatibility matrix

### Factory Pattern

Use factory methods to create operators based on the semantics they'll be used with:

- Pros: Flexible instantiation logic
- Cons: Adds complexity to operator creation

## Migration Strategy

1. Implement the new protocol without breaking existing code
2. Update theories one by one to use the new pattern
3. Add deprecation warnings for direct operator instantiation
4. Provide helper functions for theory composition

## Next Steps

1. Create the `SemanticProtocol` class
2. Update the core semantic classes to implement the protocol
3. Modify `ModelConstraints` to handle operator-semantics pairing
4. Update theory initialization in `BuildExample`
5. Add tests for cross-theory compatibility