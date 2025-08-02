# Evaluation Point Refactoring Plan

## 1. Overview

This document outlines a plan to standardize how evaluation points are handled across all theories in the ModelChecker project. Currently, there's inconsistency in how evaluation contexts are passed between functions:

- **Default Theory**: Uses a dictionary-based `eval_point` containing `"world"` key
- **Bimodal Theory**: Uses separate parameters `eval_world` and `eval_time`
- **Exclusion Theory**: Inconsistently mixes `eval_world` and `eval_point`
- **Imposition Theory**: Similar to Default, uses dictionary-based `eval_point`

The goal is to standardize on a dictionary-based approach (`eval_point`) across all theories, where `eval_point` contains all necessary evaluation context (world, time, etc.).

## 2. Current Implementation Analysis

### 2.1 Default Theory (Hyperintensional Logic)

✅ **Already uses dictionary approach**:
- Uses `eval_point` dictionary with `"world"` key
- Main point defined as `self.main_point = {"world": self.main_world}`
- Consistently passes `eval_point` through:
  ```python
  def true_at(self, sentence, eval_point):
      # Extract world from eval_point
      eval_world = eval_point["world"]
      # Implementation using eval_world
  ```

### 2.2 Bimodal Theory (Temporal-Modal Logic)

❌ **Uses separate parameters**:
- Takes separate `eval_world` and `eval_time` parameters
- Main point defined as `self.main_point = {"world": self.main_world, "time": self.main_time}`
- Uses separate parameters in methods:
  ```python
  def true_at(self, sentence, eval_world, eval_time):
      # Implementation using both parameters directly
  ```

### 2.3 Exclusion Theory (Unilateral Logic)

⚠️ **Inconsistent usage**:
- Uses `eval_world` in `true_at` but `eval_point` in `false_at`
- Main point defined as `self.main_point = {"world": self.main_world}`
- Inconsistent parameter names:
  ```python
  def true_at(self, sentence, eval_world):
      # Implementation using eval_world
  
  def false_at(self, sentence, eval_point):
      # Implementation using eval_point
  ```

### 2.4 Imposition Theory

✅ **Already uses dictionary approach**:
- Similar to Default, uses `eval_point` dictionary
- Main point defined as `self.main_point = {"world": self.main_world}`
- Consistently uses dictionary in methods like `is_alternative`

## 3. Refactoring Approach

### 3.1 Core Changes

1. **Update Base Classes**:
   - Ensure `SemanticDefaults` methods consistently use `eval_point` parameter
   - Update `ModelDefaults.recursive_print` to consistently use `eval_point` (already does)
   - Update `PropositionDefaults.print_proposition` to consistently use `eval_point` (already does)

2. **Standardize Dictionary Structure**:
   - All theories will use a dictionary with standard keys:
     - `"world"`: World identifier (required in all theories)
     - `"time"`: Time point (required in bimodal theory)
     - Additional theory-specific keys as needed

3. **Implementation Order**:
   1. Fix Exclusion Theory inconsistencies (highest priority)
   2. Refactor Bimodal Theory to use dictionary approach (most complex change)
   3. Verify Default and Imposition theories remain compatible

### 3.2 Specific Theory Changes

#### 3.2.1 Exclusion Theory

```python
# Change false_at to use consistent parameter naming
def false_at(self, sentence, eval_world):
    return z3.Not(self.true_at(sentence, eval_world))
```

#### 3.2.2 Bimodal Theory

For all operators, change from:
```python
def true_at(self, *arguments, eval_world, eval_time):
    # Implementation
```

To:
```python
def true_at(self, *arguments, eval_point):
    eval_world = eval_point["world"]
    eval_time = eval_point["time"]
    # Implementation
```

Apply this pattern to:
- `true_at`
- `false_at`
- `find_truth_condition`
- All operator methods

## 4. Testing Strategy

1. **Unit Tests**:
   - Create tests verifying that theories handle `eval_point` correctly
   - Ensure backward compatibility during transition (if needed)
   - Test with mixed theories to ensure proper parameter handling

2. **Integration Tests**:
   - Test that evaluation works across theory boundaries
   - Verify that all examples continue to work

3. **Regression Testing**:
   - Run existing theory tests to ensure behavior is preserved
   - Compare model outputs before and after changes

## 5. Implementation Plan

### Phase 1: Preparation

1. Create helper functions for parameter extraction:
   ```python
   def get_world(eval_point):
       """Extract world from eval_point dict."""
       return eval_point["world"]
       
   def get_time(eval_point):
       """Extract time from eval_point dict, if present."""
       return eval_point.get("time")
   ```

2. Create utility functions for backward compatibility (if needed)

### Phase 2: Exclusion Theory Fix

1. Update inconsistent methods to use consistent parameter naming

### Phase 3: Bimodal Theory Refactoring

1. Update the main `true_at` and `false_at` methods in semantic.py
2. Update all operator methods in operators.py
3. Update proposition class to handle the dictionary approach
4. Update model structure class to consistently use the dictionary format

### Phase 4: Verification and Testing

1. Run all theory tests to ensure behavior is preserved
2. Test with mixed theories to verify cross-theory compatibility
3. Fix any regressions or issues

## 6. Example Transformations

### 6.1 Function Signature Changes

From:
```python
def true_at(self, sentence, eval_world, eval_time):
    world_array = self.world_function(eval_world)
    eval_world_state = z3.Select(world_array, eval_time)
    # ...
```

To:
```python
def true_at(self, sentence, eval_point):
    eval_world = eval_point["world"]
    eval_time = eval_point["time"]
    world_array = self.world_function(eval_world)
    eval_world_state = z3.Select(world_array, eval_time)
    # ...
```

### 6.2 Parameter Passing in Recursion

From:
```python
def true_at(self, leftarg, rightarg, eval_world, eval_time):
    semantics = self.semantics
    return z3.And(
        semantics.true_at(leftarg, eval_world, eval_time),
        semantics.true_at(rightarg, eval_world, eval_time)
    )
```

To:
```python
def true_at(self, leftarg, rightarg, eval_point):
    semantics = self.semantics
    return z3.And(
        semantics.true_at(leftarg, eval_point),
        semantics.true_at(rightarg, eval_point)
    )
```

## 7. Advantages of Dictionary Approach

1. **Extensibility**: Adding new evaluation parameters doesn't require changing method signatures
2. **Consistency**: Single convention across all theories
3. **Flexibility**: Theories can add specialized parameters without breaking compatibility
4. **Clarity**: Clear parameter naming and extraction in implementations
5. **Future-proofing**: Easier to add new theories with different evaluation dimensions

## 8. Potential Challenges

1. **Performance Impact**: Dictionary lookups vs. direct parameters (likely negligible)
2. **Backward Compatibility**: Need to ensure existing code continues to work
3. **Documentation**: Need to update all documentation to reflect new approach
4. **Test Coverage**: Ensure all code paths are tested with the new approach

## 9. Conclusion

Standardizing on a dictionary-based `eval_point` approach will improve code maintainability, consistency, and flexibility. The proposed refactoring addresses the current inconsistencies and prepares the codebase for future extensibility while maintaining the project's design philosophy of explicit data flow and clear semantics.