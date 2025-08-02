# Bimodal Operator World Validation Strategy

## Problem Description

When implementing the world count limitation functionality, we encountered an error where operators would attempt to access `semantics.world_time_intervals[current_world]` for world IDs that didn't actually exist in the model. This happens because:

1. Our world count limitation successfully prevented creating worlds beyond the `max_worlds` limit
2. However, during formula evaluation, operators would still try to process worlds from their argument's extension
3. Some of these worlds might not actually be present in the current model

This mismatch causes a `KeyError` when operators try to access time intervals for non-existent worlds.

## Fail-Fast Philosophy Implementation

Following the project's debugging philosophy principles:

1. **Root Cause Analysis**: The root issue is a mismatch between the worlds referenced in formula extensions and the worlds that actually exist in the model.
2. **Clear Data Flow**: We need to ensure that operators only process worlds that actually exist in the model.
3. **No Silent Failures**: We won't add defensive code that silently ignores errors.
4. **No Defensive Programming**: Rather than catch exceptions, we'll explicitly filter out invalid worlds.

## Strategy 1: BaseOperatorMixin Approach

This approach uses a mixin class to add consistent world validation across all operators:

```python
class BaseOperatorMixin:
    """Mixin class for common bimodal operator functionality."""
    
    def get_valid_worlds(self, argument):
        """Get the set of world IDs that are valid in the current model."""
        model_structure = argument.proposition.model_structure
        semantics = model_structure.semantics
        return set(semantics.world_time_intervals.keys())
```

Benefits:
- Centralizes the world validation logic in one place
- Makes the validation intent explicit
- Ensures consistent handling across all operators

Drawbacks:
- Requires multiple inheritance (e.g., `class NegationOperator(syntactic.Operator, BaseOperatorMixin):`)
- Adds complexity to the class hierarchy

## Strategy 2: Semantics Validation Function (Recommended Alternative)

A cleaner approach is to add a validation method to the `BimodalSemantics` class:

```python
def get_valid_worlds(self):
    """Return the set of world IDs that are valid in the current model.
    
    Returns:
        set: Set of world IDs that have defined time intervals
    """
    return set(self.world_time_intervals.keys())
```

Then, operators can access this function through the semantics object:

```python
def find_truth_condition(self, argument, eval_world, eval_time):
    """Gets truth-condition for an operator."""
    model_structure = argument.proposition.model_structure
    semantics = model_structure.semantics
    valid_worlds = semantics.get_valid_worlds()
    
    # Only process worlds that exist in the model
    for world_id, temporal_profile in argument.proposition.extension.items():
        if world_id not in valid_worlds:
            continue
        # Process world...
```

Benefits:
- Avoids multiple inheritance
- Keeps validation logic with the semantics class where it belongs
- Clearer separation of concerns
- More consistent with the existing codebase structure

## Strategy 3: Extension Filtering Utility Function

Another alternative is to create a utility function that filters an extension:

```python
def filter_extension_to_valid_worlds(extension, semantics):
    """Filter an extension to only include worlds that exist in the current model.
    
    Args:
        extension: Dictionary mapping world_ids to temporal profiles
        semantics: BimodalSemantics instance
        
    Returns:
        dict: Filtered extension with only valid worlds
    """
    valid_worlds = set(semantics.world_time_intervals.keys())
    return {world_id: profile for world_id, profile in extension.items() 
            if world_id in valid_worlds}
```

This utility function could be placed in a common module and imported by operators.

## Implementation Recommendation

The **Semantics Validation Function** (Strategy 2) is recommended as it:

1. Aligns with the project's architecture (keeping semantic operations in the semantics class)
2. Avoids multiple inheritance
3. Makes the intent clear (we're explicitly validating against worlds that exist in the model)
4. Follows the fail-fast philosophy by explicitly filtering invalid worlds rather than handling exceptions

This approach maintains the clear separation between semantics and operators while ensuring that operators only process worlds that actually exist in the model.

## Additional Considerations

1. **Model Extraction Improvements**: We've also improved the model extraction process to ensure `world_time_intervals` is properly reset and populated only for worlds that actually exist in the model.

2. **Documentation**: Since this is a subtle interaction between world limits and operator processing, it's worth documenting this behavior in the comments for both the `get_valid_worlds` method and the operator methods that use it.

3. **Tests**: Beyond fixing the immediate error, we should create tests that specifically verify operators correctly handle world limits, ensuring our solution is robust against future changes.