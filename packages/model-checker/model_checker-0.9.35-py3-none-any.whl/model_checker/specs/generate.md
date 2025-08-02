# Constraint Generation Process Modification

This is from `constraints.md`

## Current Approach

Currently, the model_constraints system combines several types of constraints:
1. Frame constraints (task relation, world properties)
2. Premise constraints (requiring premises be true at main_point)
3. Conclusion constraints (requiring conclusions be false at main_point)

These are all added to the solver when an example is tested, but there's no systematic approach to ensure that only necessary worlds/times are created.

## Proposed Modification

The key insight is adding a system to track which worlds and times are directly needed by the formulas being tested. This happens **once** during constraint generation, not dynamically during evaluation.

```python
def build_model_constraints(self, premises, conclusions):
    """Build all constraints for the model in a single pass."""
    
    # Step 1: Initialize world requirements tracking
    self.required_worlds = set([self.main_world])  # Main world is always required
    self.required_times = {self.main_world: set([self.main_time])}  # Main time is always required
    
    # Step 2: Create basic frame constraints
    constraints = self.frame_constraints.copy()
    
    # Step 3: Add premise and conclusion constraints directly
    # These use existing operator semantics in true_at/false_at with no changes
    premise_constraints = []
    for premise in premises:
        premise_constraints.append(self.premise_behavior(premise))
        
    conclusion_constraints = []
    for conclusion in conclusions:
        conclusion_constraints.append(self.conclusion_behavior(conclusion))
    
    # Step 4: Extract world necessity information from formulas
    # This doesn't modify the operators, just analyzes the formula structure
    world_necessity_constraints = self._generate_world_necessity_constraints(premises, conclusions)
    
    # Step 5: Combine all constraints
    constraints.extend(premise_constraints)
    constraints.extend(conclusion_constraints)
    constraints.extend(world_necessity_constraints)
    
    return constraints
```

## World Necessity Constraint Generation

This is the core new functionality. It doesn't modify operator.py semantics, but extracts information about which worlds and times will be needed.

```python
def _generate_world_necessity_constraints(self, premises, conclusions):
    """Generate constraints that ensure only necessary worlds/times are created."""
    
    # Initialize world requirement tracking
    world_requirements = {}  # Maps world IDs to a formula requiring it
    
    # Analyze formulas to determine required worlds
    for premise in premises:
        self._analyze_formula_requirements(premise, is_premise=True, world_requirements=world_requirements)
        
    for conclusion in conclusions:
        self._analyze_formula_requirements(conclusion, is_premise=False, world_requirements=world_requirements)
    
    # Convert requirements to Z3 constraints
    necessity_constraints = []
    
    # Define the requirement predicate used in constraints
    required_by_formula = z3.Function('required_by_formula', self.WorldIdSort, z3.BoolSort())
    
    # For each world that might be required
    for world_id, requiring_formula in world_requirements.items():
        # Add constraint that this world is required
        necessity_constraints.append(required_by_formula(world_id))
    
    # Add constraint that only required worlds exist
    any_world = z3.Int('any_world')
    necessity_constraints.append(
        z3.ForAll(
            [any_world],
            z3.Implies(
                self.is_world(any_world),
                z3.Or(
                    # Either it's the main world
                    any_world == self.main_world,
                    # Or it's explicitly required by some formula
                    required_by_formula(any_world)
                )
            )
        )
    )
    
    return necessity_constraints
```

## Formula Analysis (Without Modifying Operators)

This analysis function extracts necessity information without changing operator semantics:

```python
def _analyze_formula_requirements(self, formula, is_premise, world_requirements):
    """Analyze a formula to determine which worlds it requires.
    
    This doesn't modify operator semantics but extracts structural requirements.
    """
    # Base case: Atomic formula doesn't require additional worlds
    if formula.sentence_letter is not None:
        return
    
    # Extract operator and arguments
    operator = formula.operator
    arguments = formula.arguments or ()
    
    # Check if this is a modal operator
    if hasattr(operator, 'name') and operator.name in ['Box', 'Diamond']:
        if operator.name == 'Box':
            # For Box operator (□)
            if is_premise:
                # If □φ is a premise (must be true), then all worlds must satisfy φ
                # This doesn't add specific world requirements, but subformulas might
                for arg in arguments:
                    self._analyze_formula_requirements(arg, is_premise, world_requirements)
            else:
                # If □φ is a conclusion (must be false), there must be some world where φ is false
                # Generate a new counter-witness world (unless we already have one)
                counter_world = self._get_or_create_counter_world(world_requirements)
                world_requirements[counter_world] = f"Counter-example for {formula}"
                
                # Analyze subformula in the counter-world context
                for arg in arguments:
                    self._analyze_formula_requirements(arg, not is_premise, world_requirements)
                
        elif operator.name == 'Diamond':
            # For Diamond operator (◇)
            if is_premise:
                # If ◇φ is a premise (must be true), there must be some world where φ is true
                witness_world = self._get_or_create_witness_world(world_requirements)
                world_requirements[witness_world] = f"Witness for {formula}"
                
                # Analyze subformula in the witness world context
                for arg in arguments:
                    self._analyze_formula_requirements(arg, is_premise, world_requirements)
            else:
                # If ◇φ is a conclusion (must be false), then φ must be false in all worlds
                # This doesn't add specific world requirements, but subformulas might
                for arg in arguments:
                    self._analyze_formula_requirements(arg, not is_premise, world_requirements)
    else:
        # Non-modal operator - analyze subformulas
        for arg in arguments:
            if hasattr(arg, 'operator') and arg.operator is not None:
                self._analyze_formula_requirements(arg, is_premise, world_requirements)
```
