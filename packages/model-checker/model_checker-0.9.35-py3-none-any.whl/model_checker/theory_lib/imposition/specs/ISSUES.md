# Known Issues and Implementation Notes

[← Back to Documentation](README.md) | [Architecture →](ARCHITECTURE.md) | [Imposition Theory →](../README.md)

## Directory Structure

```
docs/
├── API_REFERENCE.md   # Complete technical reference
├── ARCHITECTURE.md    # Design and implementation
├── ISSUES.md          # This file - known issues and bugs
├── ITERATE.md         # Model iteration for counterfactuals
├── README.md          # Documentation hub
├── SETTINGS.md        # Configuration parameters
└── USER_GUIDE.md      # Tutorial and introduction
```

## Overview

The **Issues** document tracks known bugs, edge cases, and implementation challenges in the imposition theory. This includes detailed investigations, workarounds, and ongoing research into resolving these issues.

This document serves developers and researchers working with the imposition theory, providing transparency about current limitations and guidance for avoiding or working around known problems.

## Known Issues

### 1. Counterfactual Truth Evaluation Bug

#### Summary
The imposition operator's `true_at` method incorrectly evaluates to True in certain cases where it should evaluate to False. This occurs when a counterfactual A ⊡ B is evaluated at a world where A is true but B is false at all A-alternatives.

#### Symptoms
- Formula A ⊡ B shows as true at world w even when:
  - A is true at w (verified by some state)
  - B is false at all A-alternatives to w
  - According to Fine's semantics, A ⊡ B should be false

#### Affected Examples
- IM_CM_24: NECESSITY OF COUNTERFACTUALS
- Various PROBE tests created during debugging
- Any example where the consequent has limited or no verifiers

#### Investigation Details

##### Test Cases
Multiple test cases were created to isolate the issue:

1. **DEBUG**: Simple test with A true and B false
   - Result: Works correctly when evaluation world is null (□)

2. **DEBUG2**: Tests matching IM_CM_24 scenario
   - Result: Shows the bug - A ⊡ B true when it should be false

3. **PROBE1-5**: Systematic tests of different scenarios
   - PROBE1: Works correctly (evaluation at null world)
   - PROBE2: Shows the bug
   - PROBE4: Works correctly with disjoint propositions
   - MINIMAL: Works correctly with single atom

##### Key Findings

1. **Pattern of Failure**: The bug appears specifically when:
   - Evaluating at non-null worlds
   - The antecedent A is true at the evaluation world
   - The consequent B is false at the imposition outcomes
   - The issue persists even with `non_empty=True` setting

2. **Z3 Model Peculiarities**: 
   - In problematic cases, the falsify relation often has "else -> True" as default
   - This may indicate Z3 is finding unexpected ways to satisfy constraints
   - Impossible states may be interacting with verify/falsify relations in unexpected ways

3. **Verification Conditions**: 
   - The `extended_verify` and `extended_falsify` methods were correctly updated to check for null state
   - However, the issue persists, suggesting the problem is deeper

##### Root Cause Analysis

The issue appears to be in how Z3 evaluates the universal quantification in the `true_at` method:

```python
def true_at(self, leftarg, rightarg, eval_point):
    # ForAll x,u: (x verifies A AND imposition(x, eval_world, u)) → B true at u
    return ForAll([x, u],
        z3.Implies(
            z3.And(
                semantics.extended_verify(x, leftarg, eval_point),
                semantics.imposition(x, eval_world, u)
            ),
            semantics.true_at(rightarg, {"world": u})
        )
    )
```

Despite the correct implementation according to Fine's semantics, Z3 is finding models where this constraint is satisfied even when B is false at all relevant worlds.

#### Workarounds

1. **Use Constraints**: When possible, use settings that avoid edge cases:
   - Set `disjoint=True` to force disjoint verifier sets
   - Use `contingent=True` to avoid edge cases with necessary/impossible propositions
   - Be cautious with examples where propositions have very limited verifiers

2. **Alternative Formulations**: Consider reformulating problematic counterfactuals or using the might-counterfactual (⟂) operator instead

3. **Manual Verification**: For critical applications, manually verify counterfactual evaluations by examining the model output

#### Status
**OPEN** - Under investigation

This appears to be a complex interaction between:
- Fine's bilateral semantics
- Z3's constraint solving
- The specific formulation of universal quantification
- Edge cases with impossible states

Further investigation needed, potentially requiring:
- Alternative formulations of the truth conditions
- Additional constraints to prevent problematic models
- Consultation with Z3 experts or Fine's original work
- Comparison with other implementations of Fine's semantics

### 2. Empty Verifier Sets

#### Summary
When propositions have empty verifier sets, the semantics may behave unexpectedly. While this is technically allowed in bilateral semantics, it can lead to counterintuitive results.

#### Workaround
Use the `non_empty=True` setting to ensure all propositions have non-empty verifier and falsifier sets.

#### Status
**DOCUMENTED** - This is expected behavior but may be counterintuitive

## Implementation Notes

### Bilateral Semantics Considerations

The implementation follows Fine's bilateral truthmaker semantics, which means:
- Every proposition has both verifiers and falsifiers
- A state cannot both verify and falsify the same proposition (no gluts)
- Every possible state must be compatible with either a verifier or falsifier (no gaps)

However, edge cases arise when:
- Propositions have empty verifier or falsifier sets
- Impossible states are involved in the evaluation
- Complex nested quantifications are used

### Z3 Integration Challenges

The integration with Z3 introduces several challenges:

1. **Quantifier Handling**: Nested universal and existential quantifiers can behave unexpectedly
2. **Default Values**: Z3's choice of default values for functions can affect results
3. **Constraint Complexity**: The interaction of multiple constraints can lead to unexpected models

## Reporting New Issues

When reporting new issues with the imposition theory:

1. **Provide Minimal Example**: Create the simplest example that demonstrates the issue
2. **Include Settings**: Specify all settings used (N, contingent, non_empty, etc.)
3. **Show Expected vs Actual**: Clearly state what should happen vs what does happen
4. **Include Model Output**: Run with `-p` flag to show the model details

## References

### Related Documentation
- **[Architecture](ARCHITECTURE.md)** - Design and implementation details
- **[User Guide](USER_GUIDE.md)** - Usage instructions and examples
- **[API Reference](API_REFERENCE.md)** - Complete technical reference

### External Resources
- Fine, K. (2012). "Counterfactuals without Possible Worlds"
- Z3 Documentation on Quantifiers
- ModelChecker Framework Issues

---

[← Back to Documentation](README.md) | [Architecture →](ARCHITECTURE.md) | [Imposition Theory →](../README.md)