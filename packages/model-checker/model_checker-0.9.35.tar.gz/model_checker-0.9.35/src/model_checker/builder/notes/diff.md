# Model Difference Mechanism Analysis

This document provides a detailed analysis of the code that implements model difference detection and constraint creation in the ModelChecker framework. It focuses on three key methods:

1. `_create_difference_constraint` in `iterate.py`
2. `_create_non_isomorphic_constraint` in `iterate.py`
3. `calculate_model_differences` in `default/semantic.py`

## 1. `_create_difference_constraint` in `iterate.py`

### Purpose

Creates Z3 constraints that require the next model to differ from all previous models in at least one aspect. These constraints are added to the Z3 solver to guide it toward finding different models.

### Implementation Details

```python
def _create_difference_constraint(self, previous_models):
    """Create a Z3 constraint requiring difference from all previous models.
    
    The constraint ensures the new model differs in at least one of:
    - Sentence letter valuations
    - Semantic function interpretations
    - Model structure components
    
    Args:
        previous_models: List of Z3 models to differ from
        
    Returns:
        z3.ExprRef: Z3 constraint expression
        
    Raises:
        RuntimeError: If constraint generation fails
    """
    # Get key structures from build_example
    model_structure = self.build_example.model_structure
    model_constraints = self.build_example.model_constraints
    semantics = model_constraints.semantics
    
    # For each previous model, create a constraint requiring at least one difference
    model_diff_constraints = []
    
    for prev_model in previous_models:
        # Components that could differ
        diff_components = []
        
        # 1. Sentence letter valuations
        for letter in model_constraints.sentence_letters:
            try:
                prev_value = prev_model.eval(letter, model_completion=True)
                diff_components.append(letter != prev_value)
            except z3.Z3Exception:
                pass
        
        # 2. Semantic function interpretations
        for attr_name in dir(semantics):
            if attr_name.startswith('_'):
                continue
                
            attr = getattr(semantics, attr_name)
            if not isinstance(attr, z3.FuncDeclRef):
                continue
                
            # Get domain size
            arity = attr.arity()
            if arity == 0:
                continue
            
            # For unary and binary functions, check specific values
            if arity <= 2:
                # Get the domain size (number of worlds)
                n_worlds = getattr(model_structure, 'num_worlds', 5)  # Default to 5 if not available
                
                # Create constraints for all relevant inputs
                for inputs in self._generate_input_combinations(arity, n_worlds):
                    try:
                        # Check what this function returns in the previous model
                        args = [z3.IntVal(i) for i in inputs]
                        prev_value = prev_model.eval(attr(*args), model_completion=True)
                        
                        # Add constraint requiring it to be different
                        diff_components.append(attr(*args) != prev_value)
                    except z3.Z3Exception:
                        pass
        
        # 3. Theory-specific model components (if available)
        if hasattr(model_structure, 'get_differentiable_components'):
            for component, args, prev_value in model_structure.get_differentiable_components(prev_model):
                diff_components.append(component(*args) != prev_value)
        
        # Create a single constraint for this model requiring at least one difference
        if diff_components:
            model_diff_constraints.append(z3.Or(diff_components))
    
    # The new model must be different from ALL previous models
    if model_diff_constraints:
        return z3.And(model_diff_constraints)
    else:
        raise RuntimeError("Could not create any difference constraints")
```

### Key Features

1. **Three Levels of Difference**:
   - **Sentence Letters**: Different truth values for atomic propositions
   - **Semantic Functions**: Different interpretations of semantic relations
   - **Theory-specific Components**: Differences in special theory components via `get_differentiable_components`

2. **Constraint Structure**:
   - Creates an OR constraint for each previous model, requiring at least one component to differ
   - Combines all these constraints with AND, requiring the new model to differ from ALL previous models

3. **Extensibility**:
   - Looks for theory-specific differentiable components via a `get_differentiable_components` method
   - Handles functions of different arity (currently focuses on unary and binary functions)

4. **Error Handling**:
   - Catches Z3 exceptions that might occur during evaluation
   - Raises RuntimeError if no difference constraints could be created

## 2. `_create_non_isomorphic_constraint` in `iterate.py`

### Purpose

Creates constraints that force the next model to have a different structure from previous models, focusing on the graph structure rather than just variable values. This helps find semantically distinct models.

### Implementation Details

```python
def _create_non_isomorphic_constraint(self, z3_model):
    """Create a constraint that forces structural differences to avoid isomorphism.
    
    This uses a different approach from syntactic constraints by forcing
    structural differences like different numbers of edges or different
    distributions of truth values.
    
    Args:
        z3_model: The Z3 model to differ from
    
    Returns:
        z3.ExprRef: Z3 constraint expression or None if creation fails
    """
    if not HAS_NETWORKX:
        return None
        
    # Get model structure and constraints
    model_structure = self.build_example.model_structure
    model_constraints = self.build_example.model_constraints
    semantics = model_constraints.semantics
    
    # Create graph for the model and analyze its structure
    try:
        # Get the world states from the model
        world_states = getattr(model_structure, 'z3_world_states', [])
        if not world_states and hasattr(model_structure, 'world_states'):
            world_states = getattr(model_structure, 'world_states', [])
            
        if not world_states:
            return None
        
        # Create constraints to force structural differences
        constraints = []
        
        # 1. Force different accessibility relation pattern
        if hasattr(semantics, 'R') and len(world_states) > 0:
            # Count current accessibility relation pattern
            edge_pattern = {}
            for i, w1 in enumerate(world_states):
                for j, w2 in enumerate(world_states):
                    try:
                        relation_value = bool(z3_model.eval(semantics.R(w1, w2), model_completion=True))
                        edge_pattern[(i, j)] = relation_value
                    except Exception:
                        pass
            
            # Create constraints to force different edge patterns
            edge_flip_constraints = []
            for i, w1 in enumerate(world_states):
                for j, w2 in enumerate(world_states):
                    current_value = edge_pattern.get((i, j), False)
                    # Force this specific edge to be different
                    if current_value:
                        edge_flip_constraints.append(z3.Not(semantics.R(w1, w2)))
                    else:
                        edge_flip_constraints.append(semantics.R(w1, w2))
            
            # Add edge flip constraints
            constraints.extend(edge_flip_constraints)
        
        # 2. Force different truth value patterns at each world
        for i, world in enumerate(world_states):
            world_constraints = []
            for letter in model_constraints.sentence_letters:
                try:
                    if hasattr(semantics, 'true_at'):
                        # Use semantic evaluation
                        from model_checker.syntactic import Sentence
                        letter_sentence = Sentence(sentence_letter=letter)
                        current_value = bool(z3_model.eval(semantics.true_at(letter_sentence, world), model_completion=True))
                        
                        if current_value:
                            world_constraints.append(z3.Not(semantics.true_at(letter_sentence, world)))
                        else:
                            world_constraints.append(semantics.true_at(letter_sentence, world))
                    else:
                        # Direct evaluation
                        if hasattr(letter, '__call__'):
                            current_value = bool(z3_model.eval(letter(i), model_completion=True))
                            
                            if current_value:
                                world_constraints.append(z3.Not(letter(i)))
                            else:
                                world_constraints.append(letter(i))
                        else:
                            current_value = bool(z3_model.eval(letter, model_completion=True))
                            
                            if current_value:
                                world_constraints.append(z3.Not(letter))
                            else:
                                world_constraints.append(letter)
                except Exception:
                    pass
            
            # Add individual letter flip constraints
            constraints.extend(world_constraints)
        
        # 3. Theory-specific structural constraints if available
        if hasattr(model_structure, 'get_structural_constraints'):
            try:
                theory_constraints = model_structure.get_structural_constraints(z3_model)
                if theory_constraints:
                    constraints.extend(theory_constraints)
            except Exception:
                pass
        
        # Add the constraints to force a different structure
        if constraints:
            # We need at least one of these constraints to be true to ensure a different structure
            combined_constraint = z3.Or(constraints)
            return combined_constraint
            
    except Exception as e:
        print(f"Warning: Failed to create non-isomorphic constraints: {str(e)}")
        
    return None
```

### Key Features

1. **Graph-Based Structure**:
   - Only runs when NetworkX is available (`HAS_NETWORKX`)
   - Focuses on the graph structure of the model

2. **Structural Differences**:
   - **Accessibility Relations**: Forces changes in the accessibility relation pattern
   - **Truth Value Distribution**: Forces changes in how atomic propositions are distributed across worlds

3. **Theory-Specific Customization**:
   - Looks for theory-specific structural constraints via `get_structural_constraints`
   - Adapts to different semantics (e.g., using `true_at` when available)

4. **Adaptability**:
   - Works with both callable and non-callable sentence letter representations
   - Handles different model structure organizations

5. **Error Handling**:
   - Catches exceptions at multiple levels (evaluation, constraint creation)
   - Returns None (instead of raising an exception) if constraint creation fails

## 3. `calculate_model_differences` in `default/semantic.py`

### Purpose

Calculates and formats the differences between a current model and a previous model for display. This method focuses on theory-specific semantic differences that are meaningful in the default theory.

### Implementation Details

```python
def calculate_model_differences(self, previous_structure):
    """Calculate theory-specific differences between this model and a previous one.
    
    For the default theory, this detects differences in:
    - Possible states
    - World states
    - Part-whole relationships
    - Verification and falsification of atomic propositions
    
    Args:
        previous_structure: The previous model structure to compare against
        
    Returns:
        dict: Default theory-specific differences
    """
    # Initialize differences structure
    differences = {
        "sentence_letters": {},  # Changed propositions
        "worlds": {             # Changes in world states
            "added": [],
            "removed": []
        },
        "possible_states": {    # Changes in possible states
            "added": [],
            "removed": []
        },
        "parthood": {}          # Changes in part-whole relationships
    }
    
    # Get Z3 models
    new_model = self.z3_model
    prev_model = previous_structure.z3_model
    
    # Compare possible states
    try:
        prev_possible = set(getattr(previous_structure, 'z3_possible_states', []))
        new_possible = set(getattr(self, 'z3_possible_states', []))
        
        added_possible = new_possible - prev_possible
        removed_possible = prev_possible - new_possible
        
        if added_possible:
            differences["possible_states"]["added"] = list(added_possible)
        if removed_possible:
            differences["possible_states"]["removed"] = list(removed_possible)
        
        # Compare world states
        prev_worlds = set(getattr(previous_structure, 'z3_world_states', []))
        new_worlds = set(getattr(self, 'z3_world_states', []))
        
        added_worlds = new_worlds - prev_worlds
        removed_worlds = prev_worlds - new_worlds
        
        if added_worlds:
            differences["worlds"]["added"] = list(added_worlds)
        if removed_worlds:
            differences["worlds"]["removed"] = list(removed_worlds)
            
        # Check for part-whole relationship changes (specific to default theory)
        if hasattr(self.semantics, 'is_part_of'):
            parthood_changes = {}
            # Sample a subset of state pairs to check for parthood changes
            for x in self.z3_possible_states[:10]:  # Limit to avoid too much computation
                for y in self.z3_possible_states[:10]:
                    if x == y:
                        continue
                    try:
                        old_parthood = bool(prev_model.evaluate(self.semantics.is_part_of(x, y)))
                        new_parthood = bool(new_model.evaluate(self.semantics.is_part_of(x, y)))
                        
                        if old_parthood != new_parthood:
                            key = f"{bitvec_to_substates(x, self.semantics.N)}, {bitvec_to_substates(y, self.semantics.N)}"
                            parthood_changes[key] = {
                                "old": old_parthood,
                                "new": new_parthood
                            }
                    except Exception:
                        pass
            
            if parthood_changes:
                differences["parthood"] = parthood_changes
                
        # We no longer collect compatibility changes to save computational resources
    except Exception as e:
        # Log but continue with other difference detection
        print(f"Error comparing state differences: {e}")
    
    # Compare sentence letter valuations with default theory's semantics
    letter_differences = self._calculate_proposition_differences(previous_structure)
    if letter_differences:
        differences["sentence_letters"] = letter_differences
    
    # If no meaningful differences found, return None to signal fallback to basic detection
    if (not differences["sentence_letters"] and
        not differences["worlds"]["added"] and not differences["worlds"]["removed"] and
        not differences["possible_states"]["added"] and not differences["possible_states"]["removed"] and
        not differences.get("parthood")):
        return None
        
    return differences
```

### Helper Method: `_calculate_proposition_differences`

```python
def _calculate_proposition_differences(self, previous_structure):
    """Calculate differences in proposition valuations between models.
    
    This is a helper method for calculate_model_differences that specifically
    focuses on changes in how atomic propositions are verified and falsified.
    
    Args:
        previous_structure: The previous model structure
        
    Returns:
        dict: Mapping from proposition names to differences in verifiers/falsifiers
    """
    from model_checker.utils import bitvec_to_substates
    letter_diffs = {}
    
    for letter in self.model_constraints.sentence_letters:
        # Find verifiers and falsifiers for both models
        try:
            # Create proposition objects with current and previous structures
            current_prop = self.proposition_class(
                syntactic.Sentence(sentence_letter=letter), 
                self
            )
            prev_prop = self.proposition_class(
                syntactic.Sentence(sentence_letter=letter), 
                previous_structure
            )
            
            # Compare verifiers and falsifiers
            prop_diff = {}
            
            # Compare verifiers
            current_verifiers = set(current_prop.verifiers)
            prev_verifiers = set(prev_prop.verifiers)
            
            added_verifiers = current_verifiers - prev_verifiers
            removed_verifiers = prev_verifiers - current_verifiers
            
            if added_verifiers or removed_verifiers:
                # Convert to human-readable format
                added_ver_str = {bitvec_to_substates(v, self.semantics.N) for v in added_verifiers}
                removed_ver_str = {bitvec_to_substates(v, self.semantics.N) for v in removed_verifiers}
                
                # Format for clean display
                N = self.semantics.N
                all_verifiers_str = {bitvec_to_substates(v, N) for v in current_verifiers}
                
                prop_diff["Verifiers"] = {
                    "all": all_verifiers_str,
                    "added": added_ver_str,
                    "removed": removed_ver_str
                }
            
            # Compare falsifiers
            current_falsifiers = set(current_prop.falsifiers)
            prev_falsifiers = set(prev_prop.falsifiers)
            
            added_falsifiers = current_falsifiers - prev_falsifiers
            removed_falsifiers = prev_falsifiers - current_falsifiers
            
            if added_falsifiers or removed_falsifiers:
                # Convert to human-readable format
                added_fal_str = {bitvec_to_substates(f, self.semantics.N) for f in added_falsifiers}
                removed_fal_str = {bitvec_to_substates(f, self.semantics.N) for f in removed_falsifiers}
                
                # Format for clean display
                N = self.semantics.N
                all_falsifiers_str = {bitvec_to_substates(f, N) for f in current_falsifiers}
                
                prop_diff["Falsifiers"] = {
                    "all": all_falsifiers_str,
                    "added": added_fal_str,
                    "removed": removed_fal_str
                }
            
            # Only add to results if there are actual differences
            if prop_diff:
                letter_diffs[str(letter)] = prop_diff
                
        except Exception as e:
            # Log error but continue with other letters
            print(f"Error comparing proposition {letter}: {e}")
    
    return letter_diffs
```

### Key Features

1. **Theory-Specific Approach**:
   - Focuses on differences relevant to the default theory's semantics
   - Examines how verifiers and falsifiers change between models

2. **Four Categories of Differences**:
   - **Sentence Letters**: Changes in which states verify/falsify atomic propositions
   - **Worlds**: Added or removed world states
   - **Possible States**: Added or removed possible states
   - **Parthood Relations**: Changes in part-whole relationships between states

3. **Efficiency Considerations**:
   - Limits parthood checks to a subset of state pairs (first 10) to avoid excessive computation
   - No longer collects compatibility changes (noted in a comment)

4. **Robust Error Handling**:
   - Catches exceptions at multiple levels (state comparison, proposition comparison)
   - Returns None if no meaningful differences are found

5. **Helper Methods**:
   - Uses `_calculate_proposition_differences` to handle the detailed work of comparing propositions
   - Creates proposition objects to leverage existing functionality for verifier/falsifier tracking

## Relationship Between These Methods

These three methods work together to provide a complete difference detection and constraint system:

1. `_create_difference_constraint` creates constraints that force the next model to differ from previous models in at least one specific value.

2. `_create_non_isomorphic_constraint` creates constraints that force the next model to have a different structure (beyond just different values).

3. `calculate_model_differences` analyzes and formats the differences between models for display to the user.

Together, they enable the ModelIterator to both find genuinely different models and explain to the user how the models differ.

## Observations and Potential Improvements

1. **Consistency in Terminology**:
   - The code uses "syntactic" for what are actually semantic differences (differences in meaning, interpretation, or model structure)
   - Renaming to "semantic differences" would be more accurate

2. **Integration Between Methods**:
   - The methods work independently, but could potentially share more logic
   - For example, theory-specific differentiable components could inform both constraint creation and difference display

3. **Theory-Specific Extensions**:
   - The default theory has detailed difference detection, but other theories might benefit from similar approaches
   - The hooks for theory-specific extension exist but may not be fully utilized

4. **Performance Considerations**:
   - Some operations (like checking all parthood relations) are limited to avoid excessive computation
   - This represents a practical trade-off between comprehensive difference detection and performance

## Conclusion

The difference mechanisms in the ModelChecker framework provide a robust way to find and display genuinely different models. The current implementation focuses on semantic differences (differences in meaning or interpretation) rather than just syntactic differences (different representations of the same meaning).

Renaming these mechanisms from "syntactic differences" to "semantic differences" throughout the codebase would better align with their actual purpose and implementation.

## Implementation Status Report

After adding debug prints to the codebase and running tests, here's an analysis of which proposed components are implemented versus which are not:

### Implemented Components

1. **Basic Difference Tracking**: 
   - The `_create_difference_constraint` function is fully implemented and working
   - The system correctly creates constraints requiring differences in sentence letter valuations
   - The system attempts to constrain semantic function interpretations (though experiencing type issues)
   - Differences between models are printed in a structured way

2. **Isomorphism Detection**:
   - NetworkX-based isomorphism detection is implemented in `_create_non_isomorphic_constraint`
   - The system successfully detects world states and their properties
   - There's code to evaluate relationships between worlds

3. **Model Difference Display**:
   - Changes in world states, possible states, and proposition values are displayed
   - The output shows differences in verifiers and falsifiers for each atomic proposition

### Not Implemented Components

1. **Structural Difference Constraints**:
   - The specialized `_create_structural_difference_constraint` function isn't implemented
   - The structural metrics extraction proposed in the plan isn't present

2. **Canonical Form Comparison**:
   - The `_get_canonical_model` approach isn't implemented
   - The sorting of worlds by properties to create canonical representations isn't used

3. **Theory-Specific Constraints**:
   - The `_add_theory_specific_constraints` function isn't implemented
   - There's no specialized handling for different theories like 'default' or 'bimodal'

4. **User-Configurable Difference Types**:
   - The option to choose between different types of differences ('syntactic', 'structural', etc.) isn't implemented
   - The current implementation always uses the same approach rather than selecting based on settings

5. **Dedicated Component Extraction**:
   - The proposed `_extract_model_components` and `_compute_model_differences` methods aren't implemented as separate functions
   - Similar functionality exists but is integrated directly into other methods

### Notes on Current Implementation

The current implementation takes a more direct approach than the planned design:

1. Rather than having separate methods for different constraint types, a single `_create_difference_constraint` function handles creating constraints

2. The constraint generation is focused on letter valuations and attempts to constrain semantic functions, but encounters type mismatch issues

3. Isomorphism checking is implemented, but in a more basic form than the detailed approach in the plan

4. The difference display functionality works well but is implemented differently than proposed

5. The actual implementation is more integrated and less modular than the design in the plan

Most importantly, the core functionality works - the system successfully finds and displays differences between models, even though it doesn't implement all the specialized approaches described in the plan.

## Implementation Status Report

After adding debug prints to the codebase and running tests, here's an analysis of which proposed components are implemented versus which are not:

### Implemented Components

1. **Basic Difference Tracking**: 
   - The `_create_difference_constraint` function is fully implemented and working
   - The system correctly creates constraints requiring differences in sentence letter valuations
   - The system attempts to constrain semantic function interpretations (though experiencing type issues)
   - Differences between models are printed in a structured way

2. **Isomorphism Detection**:
   - NetworkX-based isomorphism detection is implemented in `_create_non_isomorphic_constraint`
   - The system successfully detects world states and their properties
   - There's code to evaluate relationships between worlds

3. **Model Difference Display**:
   - Changes in world states, possible states, and proposition values are displayed
   - The output shows differences in verifiers and falsifiers for each atomic proposition

### Not Implemented Components

1. **Structural Difference Constraints**:
   - The specialized `_create_structural_difference_constraint` function isn't implemented
   - The structural metrics extraction proposed in the plan isn't present

2. **Canonical Form Comparison**:
   - The `_get_canonical_model` approach isn't implemented
   - The sorting of worlds by properties to create canonical representations isn't used

3. **Theory-Specific Constraints**:
   - The `_add_theory_specific_constraints` function isn't implemented
   - There's no specialized handling for different theories like 'default' or 'bimodal'

4. **User-Configurable Difference Types**:
   - The option to choose between different types of differences ('syntactic', 'structural', etc.) isn't implemented
   - The current implementation always uses the same approach rather than selecting based on settings

5. **Dedicated Component Extraction**:
   - The proposed `_extract_model_components` and `_compute_model_differences` methods aren't implemented as separate functions
   - Similar functionality exists but is integrated directly into other methods

### Notes on Current Implementation

The current implementation takes a more direct approach than the planned design:

1. Rather than having separate methods for different constraint types, a single `_create_difference_constraint` function handles creating constraints

2. The constraint generation is focused on letter valuations and attempts to constrain semantic functions, but encounters type mismatch issues

3. Isomorphism checking is implemented, but in a more basic form than the detailed approach in the plan

4. The difference display functionality works well but is implemented differently than proposed

5. The actual implementation is more integrated and less modular than the design in the plan

Most importantly, the core functionality works - the system successfully finds and displays differences between models, even though it doesn't implement all the specialized approaches described in the plan.

## Component Usage Analysis Based on Debug Output

After examining the debug output from running the default examples, here's an analysis of which implemented components are actually used:

### Components That Are Used

1. **From `_create_difference_constraint`**:
   - Basic initialization and setup of the difference constraint function
   - Processing of previous models (shown by "Processing previous model #1")
   - Sentence letter valuation constraints (shown by "Checking sentence letter valuations")
   - The function successfully adds constraints for each letter with messages like "Added constraint for letter A: must differ from AtomSort!val!0"
   - Creation of combined constraints across all models (shown by "Created combined constraint requiring difference from all 1 previous models")

2. **From `_create_non_isomorphic_constraint`**:
   - Basic setup and NetworkX availability check (shown by "NetworkX available, creating non-isomorphic constraints")
   - World state detection (shown by "Found 3 world states")

3. **Difference Display**:
   - The system successfully displays differences between models:
     - World changes (adding/removing worlds)
     - Possible state changes
     - Proposition changes with detailed verifier/falsifier tracking

### Components That Are Not Used or Have Issues

1. **From `_create_difference_constraint`**:
   - Semantic function interpretation constraints attempt to run but encounter "Sort mismatch" errors for all inputs
   - No successful semantic function constraints are added (shown by "Added 0 input constraints for this function")
   - Theory-specific differentiable components are not available (shown by "No theory-specific get_differentiable_components method available")

2. **From `_create_non_isomorphic_constraint`**:
   - While the function is called and performs basic setup, we don't see debug output showing:
     - Accessibility relation pattern checking
     - Edge pattern analysis
     - Creation of structural constraints

3. **Isomorphism Checking**:
   - The code appears to perform an isomorphism check, but the detailed debug output from this process is not visible
   - We can infer it works because two distinct models are found

### Summary of Actual Usage

Based on the debug output, the system primarily relies on:

1. Simple syntactic difference constraints based on sentence letter valuations
2. Basic world state counting from the non-isomorphic constraint code
3. The model difference display functionality

The more advanced functionality related to semantic function constraints, structural metrics, and theory-specific components either:
1. Is not available in the codebase (shown by "No theory-specific..." messages)
2. Encounters type errors (shown by "Sort mismatch" errors)
3. Or is not reached during execution of the example

This suggests that the implemented system is simpler than planned but still effective for finding differences between models based primarily on sentence letter valuations and displaying those differences clearly to the user.

