# Implementation Plan for Theory-Agnostic Model Iteration

## 1. Overview

The goal is to refactor `builder/iterate.py` to be theory-agnostic by:
1. Extracting theory-specific code to theory subclasses
2. Creating a clear interface between base and theory-specific implementations
3. Ensuring the base class provides reusable infrastructure while theory-specific logic lives in theory modules

## 2. Architecture Design

### 2.1 Component Structure

```
builder/
  iterate.py          # Base ModelIterator class (theory-agnostic)
  
theory_lib/
  default/
    iterate.py        # DefaultModelIterator (theory-specific implementation)
    semantic.py       # (unchanged)
  bimodal/
    iterate.py        # BimodalModelIterator (future implementation)
    semantic.py       # (unchanged)
```

### 2.2 Class Hierarchy

```
ModelIterator (base class)
  │
  ├── DefaultModelIterator
  │
  ├── BimodalModelIterator 
  │
  └── [Other theory-specific iterators]
```

## 3. Base Class Design (`builder/iterate.py`)

### 3.1 Refactored ModelIterator Class

```python
class ModelIterator:
    """Base class for iterating through models, providing theory-agnostic functionality."""
    
    def __init__(self, build_example):
        # Basic validation (unchanged)
        if not isinstance(build_example, BuildExample):
            raise TypeError(f"Expected BuildExample instance, got {type(build_example).__name__}")
            
        # Model validation (unchanged)
        if not hasattr(build_example, 'model_structure') or build_example.model_structure is None:
            raise ValueError("BuildExample has no model_structure")
            
        if not hasattr(build_example.model_structure, 'z3_model_status') or \
           not build_example.model_structure.z3_model_status:
            raise ValueError("BuildExample does not have a valid model")
            
        if not hasattr(build_example.model_structure, 'z3_model') or \
           build_example.model_structure.z3_model is None:
            raise ValueError("BuildExample has no Z3 model")
            
        # Initialize properties
        self.build_example = build_example
        self.settings = self._get_iteration_settings()
        
        self.max_iterations = self.settings.get('iterate', 1)
        self.current_iteration = 1  # First model is already found
        
        # Store the initial model and model structure
        self.found_models = [build_example.model_structure.z3_model]
        self.model_structures = [build_example.model_structure]
        
        # Create a persistent solver that will accumulate constraints
        self.solver = self._create_persistent_solver()
        
        # Initialize graph representation for the model
        self.model_graphs = []
        if HAS_NETWORKX:
            try:
                initial_graph = ModelGraph(
                    self.build_example.model_structure,
                    self.found_models[0]
                )
                self.model_graphs.append(initial_graph)
                # Store the graph with the model structure for reference
                self.build_example.model_structure.model_graph = initial_graph
            except Exception as e:
                print(f"Warning: Could not create graph for initial model: {str(e)}")
    
    # Core iteration methods (unchanged)
    def iterate(self):
        """Main method to iterate through models."""
        # Most of this can stay unchanged
        # Changes needed:
        # - Remove theory-specific bits in constraint generation
        # - Use theory-specific methods via delegation instead
        # (Rest of method implementation remains largely the same)
        pass
    
    def reset_iterator(self):
        """Reset the iterator to its initial state."""
        # This can stay unchanged
        pass
    
    # -- THEORY-AGNOSTIC METHODS (unchanged) --
    def _create_persistent_solver(self):
        """Create a persistent solver with the initial model's constraints."""
        # This can stay unchanged
        pass
    
    def _get_iteration_settings(self):
        """Extract and validate iteration settings from BuildExample."""
        # This can stay unchanged
        pass
    
    def _generate_input_combinations(self, arity, domain_size):
        """Generate all relevant input combinations for a function of given arity."""
        # This can stay unchanged
        pass
    
    # -- DELEGATING METHODS THAT CALL THEORY-SPECIFIC CODE --
    
    def _display_model_differences(self, model_structure, output=sys.stdout):
        """Display differences between the current model and previous ones."""
        # Prioritize theory-specific implementations, fallback to base if needed
        if not hasattr(model_structure, 'model_differences') or not model_structure.model_differences:
            # Calculate differences on the fly if needed
            if hasattr(model_structure, 'previous_structure') and model_structure.previous_structure is not None:
                model_structure.model_differences = self._calculate_differences(
                    model_structure, model_structure.previous_structure)
            else:
                return
                
        # Try theory-specific difference formatting
        if hasattr(model_structure, 'format_model_differences'):
            try:
                model_structure.format_model_differences(model_structure.model_differences, output)
                return
            except Exception as e:
                logger.warning(f"Error in theory-specific difference formatting: {e}")
        
        # Delegate to theory-specific subclass (removes implementation from base class)
        self._theory_specific_display_differences(model_structure, output)
    
    def _calculate_differences(self, new_structure, previous_structure):
        """Calculate differences between two model structures."""
        # Try theory-specific difference detection
        if hasattr(new_structure, 'detect_model_differences'):
            try:
                differences = new_structure.detect_model_differences(previous_structure)
                if differences:
                    # Store the differences with the new structure
                    new_structure.model_differences = differences
                    new_structure.previous_structure = previous_structure
                    return differences
            except Exception as e:
                logger.warning(f"Error in theory-specific difference detection: {e}")
        
        # Delegate to theory-specific implementation
        differences = self._theory_specific_calculate_differences(new_structure, previous_structure)
        
        # Store the differences with the new structure
        new_structure.model_differences = differences
        new_structure.previous_structure = previous_structure
        
        return differences
    
    def _create_new_model_structure(self, z3_model):
        """Build a new model structure from a Z3 model using theory-specific logic."""
        original_build_example = self.build_example
        model_constraints = original_build_example.model_constraints
        
        # Create a new model structure
        klass = original_build_example.model_structure.__class__
        new_structure = object.__new__(klass)
        
        # Initialize base attributes (theory-agnostic)
        self._initialize_common_attributes(new_structure, model_constraints, original_build_example.settings)
        
        # Delegate to theory-specific initialization
        self._theory_specific_initialize(new_structure, z3_model)
        
        return new_structure
    
    def _initialize_common_attributes(self, model_structure, model_constraints, settings):
        """Initialize attributes common to all theories."""
        # Basic attributes (no theory-specific details)
        model_structure.model_constraints = model_constraints
        model_structure.settings = settings
        model_structure.max_time = settings.get("max_time", 1.0)
        model_structure.expectation = settings.get("expectation", True)
        
        # Set semantics and syntax references
        model_structure.semantics = model_constraints.semantics
        model_structure.syntax = model_constraints.syntax
        model_structure.start_time = model_structure.syntax.start_time
        model_structure.premises = model_structure.syntax.premises
        model_structure.conclusions = model_structure.syntax.conclusions
        model_structure.sentence_letters = model_structure.syntax.sentence_letters
        
        # Set proposition class and solver
        model_structure.proposition_class = model_constraints.proposition_class
        model_structure.solver = z3.Solver()
        for assertion in model_constraints.all_constraints:
            model_structure.solver.add(assertion)
        
        # Initialize Z3 model attributes as None
        model_structure.z3_model = None
        model_structure.z3_model_status = None
        model_structure.z3_model_runtime = None
        model_structure.timeout = None
        model_structure.unsat_core = None
        
        # Initialize difference tracking
        model_structure.model_differences = None
    
    def _create_difference_constraint(self, previous_models):
        """Create a Z3 constraint requiring difference from all previous models."""
        constraints = []
        
        # Get original constraints from the first model
        original_constraints = list(self.build_example.model_structure.solver.assertions())
        
        # Create difference constraints for all previous models
        for model in previous_models:
            # Delegate to theory-specific constraint generation
            theory_constraint = self._theory_specific_difference_constraint(model)
            if theory_constraint is not None:
                constraints.append(theory_constraint)
        
        # Combine original constraints with difference constraints
        return z3.And(original_constraints + constraints) if constraints else None
    
    def _check_isomorphism(self, new_structure, new_model):
        """Check if a model is isomorphic to any previous model."""
        # This can largely remain unchanged
        # The key is that ModelGraph should be theory-agnostic
        pass
    
    # -- ABSTRACT METHODS TO BE IMPLEMENTED BY THEORY-SPECIFIC SUBCLASSES --
    
    def _theory_specific_display_differences(self, model_structure, output):
        """Display differences in a theory-specific way."""
        # Default implementation - subclasses should override
        print("\nThis is a generic model difference display. For better formatting, implement a theory-specific subclass.")
        print("Differences detected:", model_structure.model_differences)
    
    def _theory_specific_calculate_differences(self, new_structure, previous_structure):
        """Calculate differences between models in a theory-specific way."""
        # Default minimalist implementation - subclasses should override
        return {
            "sentence_letters": {},  # Differences in letter valuations
            "semantic_functions": {} # Differences in function interpretations
        }
    
    def _theory_specific_initialize(self, model_structure, z3_model):
        """Initialize a model structure with theory-specific details."""
        # Basic implementation - subclasses should override
        model_structure.z3_model = z3_model
        model_structure.z3_model_status = True
    
    def _theory_specific_difference_constraint(self, model):
        """Create a theory-specific constraint requiring difference from a model."""
        # Default implementation - subclasses should override with theory-specific logic
        # This is a minimal constraint that requires at least one sentence letter to differ
        constraints = []
        for letter in self.build_example.model_constraints.sentence_letters:
            try:
                prev_value = model.eval(letter, model_completion=True)
                constraints.append(letter != prev_value)
            except Exception:
                pass
        
        return z3.Or(constraints) if constraints else None
    
    def _theory_specific_non_isomorphic_constraint(self, model):
        """Create a theory-specific constraint to avoid isomorphic models."""
        # Default implementation - subclasses should override
        return None  # No constraint by default
```

## 4. Theory-Specific Implementation (`default/iterate.py`)

### 4.1 DefaultModelIterator Class

```python
from model_checker.builder.iterate import ModelIterator
import z3
import sys

class DefaultModelIterator(ModelIterator):
    """Default theory implementation of ModelIterator."""
    
    def _theory_specific_display_differences(self, model_structure, output=sys.stdout):
        """Display model differences using default theory semantics."""
        differences = model_structure.model_differences
        if not differences:
            return
            
        print("\n=== MODEL DIFFERENCES ===\n", file=output)
        
        # Print sentence letter differences with more detail
        if 'sentence_letters' in differences and differences['sentence_letters']:
            print("Sentence Letter Changes:", file=output)
            for letter, change in differences['sentence_letters'].items():
                letter_name = letter
                if isinstance(change, dict) and 'old' in change and 'new' in change:
                    old_val, new_val = change['old'], change['new']
                    
                    # Handle tuple format (verifiers, falsifiers)
                    if isinstance(old_val, tuple) and isinstance(new_val, tuple):
                        old_verifiers, old_falsifiers = old_val
                        new_verifiers, new_falsifiers = new_val
                        
                        print(f"  {letter_name}:", file=output)
                        print(f"    Verifiers: changed from {old_verifiers} to {new_verifiers}", file=output)
                        print(f"    Falsifiers: changed from {old_falsifiers} to {new_falsifiers}", file=output)
                    else:
                        # Handle simple value changes
                        print(f"  {letter_name}: {old_val} -> {new_val}", file=output)
                else:
                    # Fallback for simpler change format
                    print(f"  {letter_name}: changed from previous model", file=output)
        
        # Print world changes - DEFAULT THEORY SPECIFIC
        if 'worlds' in differences:
            print("\nWorld Changes:", file=output)
            worlds = differences['worlds']
            if 'added' in worlds and worlds['added']:
                from model_checker.utils import bitvec_to_substates
                for world in worlds['added']:
                    try:
                        state_repr = bitvec_to_substates(world, model_structure.semantics.N)
                        print(f"  + {state_repr} (world)", file=output)
                    except:
                        print(f"  + {world} (world)", file=output)
                        
            if 'removed' in worlds and worlds['removed']:
                from model_checker.utils import bitvec_to_substates
                for world in worlds['removed']:
                    try:
                        state_repr = bitvec_to_substates(world, model_structure.semantics.N)
                        print(f"  - {state_repr} (world)", file=output)
                    except:
                        print(f"  - {world} (world)", file=output)
        
        # Print possible state changes - DEFAULT THEORY SPECIFIC
        if 'possible_states' in differences:
            print("\nPossible State Changes:", file=output)
            states = differences['possible_states']
            if 'added' in states and states['added']:
                from model_checker.utils import bitvec_to_substates
                for state in states['added']:
                    try:
                        state_repr = bitvec_to_substates(state, model_structure.semantics.N)
                        print(f"  + {state_repr}", file=output)
                    except:
                        print(f"  + {state}", file=output)
                        
            if 'removed' in states and states['removed']:
                from model_checker.utils import bitvec_to_substates
                for state in states['removed']:
                    try:
                        state_repr = bitvec_to_substates(state, model_structure.semantics.N)
                        print(f"  - {state_repr}", file=output)
                    except:
                        print(f"  - {state}", file=output)
        
        # Print semantic function differences
        if 'semantic_functions' in differences and differences['semantic_functions']:
            print("\nSemantic Function Changes:", file=output)
            for func, changes in differences['semantic_functions'].items():
                if isinstance(changes, dict) and changes:
                    print(f"  {func}:", file=output)
                    sample_count = 0
                    for input_vals, change in changes.items():
                        if sample_count < 5:  # Limit to 5 examples
                            if isinstance(change, dict) and 'old' in change and 'new' in change:
                                print(f"    Input {input_vals}: {change['old']} -> {change['new']}", file=output)
                            else:
                                print(f"    Input {input_vals}: changed", file=output)
                            sample_count += 1
                    
                    # Show count if there are more changes
                    total_changes = len(changes)
                    if total_changes > 5:
                        print(f"    ... and {total_changes - 5} more changes", file=output)
                else:
                    print(f"  {func}: {len(changes) if isinstance(changes, dict) else 'unknown'} input(s) changed", file=output)
        
        # Print model structure differences
        if 'model_structure' in differences and differences['model_structure']:
            print("\nModel Structure Changes:", file=output)
            for component, change in differences['model_structure'].items():
                if isinstance(change, dict) and 'old' in change and 'new' in change:
                    print(f"  {component}: {change['old']} -> {change['new']}", file=output)
                else:
                    print(f"  {component}: changed", file=output)
                    
        # Print part-whole relationship changes - DEFAULT THEORY SPECIFIC
        if 'parthood' in differences and differences.get('parthood'):
            print("\nPart-Whole Relationship Changes:", file=output)
            for pair, change in differences['parthood'].items():
                if isinstance(change, dict) and 'old' in change and 'new' in change:
                    status = "now part of" if change['new'] else "no longer part of"
                    print(f"  {pair}: {status}", file=output)
    
    def _theory_specific_calculate_differences(self, new_structure, previous_structure):
        """Calculate differences between models using default theory semantics."""
        # Get Z3 models
        new_model = new_structure.z3_model
        previous_model = previous_structure.z3_model
        semantics = new_structure.semantics
        
        # Initialize differences structure with default theory components
        differences = {
            "sentence_letters": {},
            "semantic_functions": {},
            "worlds": {"added": [], "removed": []},
            "possible_states": {"added": [], "removed": []},
            "parthood": {}
        }
        
        # Compare sentence letter valuations (same as base implementation)
        for letter in self.build_example.model_constraints.sentence_letters:
            try:
                prev_value = previous_model.eval(letter, model_completion=True)
                new_value = new_model.eval(letter, model_completion=True)
                
                if str(prev_value) != str(new_value):
                    differences["sentence_letters"][str(letter)] = {
                        "old": prev_value,
                        "new": new_value
                    }
            except z3.Z3Exception:
                pass
        
        # Compare possible states (DEFAULT THEORY SPECIFIC)
        prev_possible = set(str(s) for s in previous_structure.z3_possible_states)
        new_possible = set(str(s) for s in new_structure.z3_possible_states)
        
        for state in new_possible.difference(prev_possible):
            differences["possible_states"]["added"].append(state)
            
        for state in prev_possible.difference(new_possible):
            differences["possible_states"]["removed"].append(state)
        
        # Compare worlds (DEFAULT THEORY SPECIFIC)
        prev_worlds = set(str(w) for w in previous_structure.z3_world_states)
        new_worlds = set(str(w) for w in new_structure.z3_world_states)
        
        for world in new_worlds.difference(prev_worlds):
            differences["worlds"]["added"].append(world)
            
        for world in prev_worlds.difference(new_worlds):
            differences["worlds"]["removed"].append(world)
        
        # Compare parthood relationships (DEFAULT THEORY SPECIFIC)
        all_states = new_structure.all_states
        for s1 in all_states:
            for s2 in all_states:
                try:
                    # Check if s1 is part of s2
                    prev_parthood = bool(previous_model.eval(semantics.is_part_of(s1, s2), model_completion=True))
                    new_parthood = bool(new_model.eval(semantics.is_part_of(s1, s2), model_completion=True))
                    
                    if prev_parthood != new_parthood:
                        pair_key = f"({s1}, {s2})"
                        differences["parthood"][pair_key] = {
                            "old": prev_parthood,
                            "new": new_parthood
                        }
                except z3.Z3Exception:
                    pass
        
        # Check semantic functions (similar to base implementation but with more detail)
        for attr_name in dir(semantics):
            if attr_name.startswith('_'):
                continue
                
            attr = getattr(semantics, attr_name)
            if not isinstance(attr, z3.FuncDeclRef):
                continue
                
            arity = attr.arity()
            if arity == 0:
                continue
            
            # For unary and binary functions, check specific values
            if arity <= 2:
                n_worlds = len(new_structure.z3_world_states)
                
                func_diffs = {}
                for inputs in self._generate_input_combinations(arity, n_worlds):
                    try:
                        args = [z3.IntVal(i) for i in inputs]
                        prev_value = previous_model.eval(attr(*args), model_completion=True)
                        new_value = new_model.eval(attr(*args), model_completion=True)
                        
                        if str(prev_value) != str(new_value):
                            func_diffs[str(inputs)] = {
                                "old": prev_value,
                                "new": new_value
                            }
                    except z3.Z3Exception:
                        pass
                
                if func_diffs:
                    differences["semantic_functions"][attr_name] = func_diffs
        
        return differences
    
    def _theory_specific_initialize(self, model_structure, z3_model):
        """Initialize a model structure with default theory semantics."""
        # Set the Z3 model
        model_structure.z3_model = z3_model
        model_structure.z3_model_status = True
        
        # Transfer runtime from original model structure
        original_structure = self.build_example.model_structure
        model_structure.z3_model_runtime = original_structure.z3_model_runtime
        
        # -- DEFAULT THEORY SPECIFIC --
        # Set default theory color codes
        model_structure.COLORS = {
            "default": "\033[37m",  # WHITE
            "world": "\033[34m",    # BLUE
            "possible": "\033[36m", # CYAN
            "impossible": "\033[35m", # MAGENTA
            "initial": "\033[33m",  # YELLOW
        }
        model_structure.RESET = "\033[0m"
        model_structure.WHITE = model_structure.COLORS["default"]
        
        # Set default theory specific attributes
        semantics = model_structure.semantics
        model_structure.main_point = semantics.main_point
        model_structure.all_states = semantics.all_states
        model_structure.N = semantics.N
        
        # Get main world from main_point
        if hasattr(model_structure.main_point, "get"):
            model_structure.main_world = model_structure.main_point.get("world")
        
        # Initialize Z3 values for default theory
        model_structure.z3_main_world = z3_model.eval(model_structure.main_world, model_completion=True) 
        model_structure.main_point["world"] = model_structure.z3_main_world
        
        # Initialize possible states (DEFAULT THEORY SPECIFIC)
        model_structure.z3_possible_states = [
            state for state in model_structure.all_states
            if bool(z3_model.eval(semantics.possible(state), model_completion=True))
        ]
        
        # Initialize world states (DEFAULT THEORY SPECIFIC)
        model_structure.z3_world_states = [
            state for state in model_structure.z3_possible_states
            if bool(z3_model.eval(semantics.is_world(state), model_completion=True))
        ]
        
        # Interpret sentences
        sentence_objects = model_structure.premises + model_structure.conclusions
        model_structure.interpret(sentence_objects)
    
    def _theory_specific_difference_constraint(self, model):
        """Create a constraint requiring difference from a model using default theory semantics."""
        semantics = self.build_example.model_structure.semantics
        
        diff_components = []
        
        # Add constraints for default theory's differentiable functions
        differentiable_functions = [
            (semantics.verify, 2, "verification"),
            (semantics.falsify, 2, "falsification"),
            (semantics.possible, 1, "possibility"),
            (semantics.is_world, 1, "world state")
        ]
        
        # Add constraint for parthood if available
        if hasattr(semantics, 'is_part_of'):
            differentiable_functions.append((semantics.is_part_of, 2, "part-whole relation"))
        
        # Create constraints for each function
        for func, arity, description in differentiable_functions:
            # Number of worlds to use for inputs
            n_worlds = len(self.build_example.model_structure.z3_world_states)
            
            for inputs in self._generate_input_combinations(arity, n_worlds):
                try:
                    # Check function value in previous model
                    args = [z3.IntVal(i) for i in inputs]
                    prev_value = model.eval(func(*args), model_completion=True)
                    
                    # Add constraint requiring different value
                    diff_components.append(func(*args) != prev_value)
                except z3.Z3Exception:
                    pass
        
        # Also add sentence letter constraints
        for letter in self.build_example.model_constraints.sentence_letters:
            try:
                prev_value = model.eval(letter, model_completion=True)
                diff_components.append(letter != prev_value)
            except Exception:
                pass
        
        # Combine all difference components
        return z3.Or(diff_components) if diff_components else None
    
    def _theory_specific_non_isomorphic_constraint(self, model):
        """Create a constraint to avoid isomorphic models using default theory semantics."""
        semantics = self.build_example.model_structure.semantics
        
        # Get world states from the model (DEFAULT THEORY SPECIFIC)
        world_states = self.build_example.model_structure.z3_world_states
        if not world_states:
            return None
        
        constraints = []
        
        # Force different truth value patterns at each world (DEFAULT THEORY SPECIFIC)
        for i, world in enumerate(world_states):
            world_constraints = []
            for letter in self.build_example.model_constraints.sentence_letters:
                try:
                    if hasattr(semantics, 'true_at'):
                        # Use semantic evaluation
                        from model_checker.syntactic import Sentence
                        letter_sentence = Sentence(sentence_letter=letter)
                        current_value = bool(model.eval(semantics.true_at(letter_sentence, world), model_completion=True))
                        
                        if current_value:
                            world_constraints.append(z3.Not(semantics.true_at(letter_sentence, world)))
                        else:
                            world_constraints.append(semantics.true_at(letter_sentence, world))
                except Exception:
                    pass
            
            # Add the constraints for this world
            constraints.extend(world_constraints)
        
        # Force different parthood structure (DEFAULT THEORY SPECIFIC)
        if hasattr(semantics, 'is_part_of'):
            all_states = self.build_example.model_structure.all_states
            for s1 in all_states:
                for s2 in all_states:
                    try:
                        current_value = bool(model.eval(semantics.is_part_of(s1, s2), model_completion=True))
                        
                        if current_value:
                            constraints.append(z3.Not(semantics.is_part_of(s1, s2)))
                        else:
                            constraints.append(semantics.is_part_of(s1, s2))
                    except Exception:
                        pass
        
        # Return combined constraint
        return z3.Or(constraints) if constraints else None
```

## 5. Integration Plan

### 5.1 Changes to Base ModelIterator Class (`builder/iterate.py`)

1. Extract the theory-agnostic core functionality
2. Convert theory-specific methods to abstract methods
3. Create delegation methods that call theory-specific implementations
4. Implement minimal default implementations for abstract methods

### 5.2 Creation of DefaultModelIterator (`theory_lib/default/iterate.py`)

1. Implement the DefaultModelIterator class
2. Move all default theory logic from the base class to this implementation
3. Focus on world states, possible states, and parthood relationships

### 5.3 Direct Use of Theory-Specific Iterators

Instead of using a factory method, the theory-specific iterators can be imported directly where needed. Since we're only dealing with one theory at a time when processing an example, this simplifies the architecture.

In `builder/example.py` or wherever model iteration is triggered:

```python
# For Default theory
from model_checker.theory_lib.default.iterate import DefaultModelIterator

# Creating a specific iterator
iterator = DefaultModelIterator(build_example)
models = iterator.iterate()
```

Or adding a dynamic import in the iterate_example function:

```python
def iterate_example(build_example, max_iterations=None):
    """Iterate an example and find multiple models."""
    # Determine which iterator to use based on the theory
    theory_name = build_example.model_constraints.semantics.__class__.__module__.split('.')[-2]
    
    # Import the appropriate iterator class
    if theory_name == 'default':
        from model_checker.theory_lib.default.iterate import DefaultModelIterator
        iterator_class = DefaultModelIterator
    elif theory_name == 'bimodal':
        from model_checker.theory_lib.bimodal.iterate import BimodalModelIterator
        iterator_class = BimodalModelIterator
    else:
        # Fall back to base class for theories without specific implementations
        from model_checker.builder.iterate import ModelIterator
        iterator_class = ModelIterator
    
    # Create and use the appropriate iterator
    iterator = iterator_class(build_example)
    
    # Override max_iterations if provided
    if max_iterations is not None:
        if not isinstance(max_iterations, int) or max_iterations < 1:
            raise ValueError(f"max_iterations must be a positive integer, got {max_iterations}")
        iterator.max_iterations = max_iterations
    
    return iterator.iterate()
```

This approach is simpler because:
1. It avoids an additional factory function
2. The import and instantiation happen in the same place
3. It's more explicit about which iterator is being used

## 6. Implementation Steps

### 6.1 Phase 1: Refactor Base Class
1. Create a new branch for the refactoring
2. Extract theory-agnostic core from `builder/iterate.py`
3. Create abstract methods for theory-specific functionality
4. Add delegation methods to handle theory-specific logic

### 6.2 Phase 2: Implement Default Iterator
1. Create `theory_lib/default/iterate.py`
2. Implement DefaultModelIterator with all default theory logic
3. Ensure it properly uses worlds, possible_states, and parthood

### 6.3 Phase 3: Update Integration Points
1. Update the iterate_example function in `builder/iterate.py` to use the appropriate iterator class
2. Update import references in `builder/module.py` and other files 
3. Update any other code that directly instantiates ModelIterator

### 6.4 Phase 4: Testing
1. Run existing tests to validate core functionality
2. Add specific tests for DefaultModelIterator
3. Verify the refactoring does not change behavior

## 7. Benefits of This Approach

1. **Modularity**: Each theory contains its specific model iteration logic
2. **Extensibility**: New theories can easily implement their own iterators
3. **Clarity**: Clear separation between general and theory-specific logic
4. **Reusability**: Common iteration logic is preserved in the base class
5. **Maintainability**: Changes to one theory don't affect others

## 8. Risks and Mitigations

1. **Risk**: Breaking existing functionality
   **Mitigation**: Comprehensive testing and phased implementation

2. **Risk**: Increased complexity due to class hierarchy
   **Mitigation**: Clear documentation and consistent design patterns

3. **Risk**: Performance impact from indirection
   **Mitigation**: Profile key operations to ensure no significant slowdown

## 9. Documentation Updates

1. Update `builder/README.md` to describe the new architecture
2. Add documentation for theory developers on extending ModelIterator
3. Update example code to show proper usage
