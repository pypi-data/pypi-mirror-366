# Settings Architecture in ModelChecker

This document provides a comprehensive analysis of the settings architecture in the ModelChecker framework, focusing on how `general_settings`, `example_settings`, and `module_flags` are combined to create a configurable system that aligns with the project's design philosophy.

## Overview

The ModelChecker uses a multi-layered settings system that implements the design philosophy of "Clear Data Flow" and "No Silent Failures" by making configuration explicit rather than relying on defaults. The settings architecture consists of three primary components that are merged in a specific order of precedence:

1. **DEFAULT_GENERAL_SETTINGS**: Theory-specific general defaults defined in each semantic theory
2. **DEFAULT_EXAMPLE_SETTINGS**: Theory-specific example defaults defined in each semantic theory
3. **general_settings**: Global module-level settings defined by the user
4. **example_settings**: Example-level settings defined by the user
5. **module_flags**: Command-line flags that override all other settings

This architecture ensures that all parameters are explicitly passed and allows for clear tracking of where each setting originated.

## Settings Components

### 1. DEFAULT_EXAMPLE_SETTINGS

Each semantic theory defines its own `DEFAULT_EXAMPLE_SETTINGS` dictionary in its `semantic.py` file to establish baseline settings for that theory. These defaults include:

#### Default Theory
```python
DEFAULT_EXAMPLE_SETTINGS = {
    'N': 3,               # Number of states
    'contingent': False,  # Whether sentence letters are contingent
    'non_empty': False,   # Whether propositions must be non-empty
    'non_null': False,    # Whether propositions must be non-null
    'disjoint': False,    # Whether propositions have disjoint subject-matters
    'max_time': 1,        # Maximum solving time in seconds
    'iterate': 1,         # Number of models to generate
    'expectation': None,  # Expected model existence
}
```

#### Bimodal Theory
```python
DEFAULT_EXAMPLE_SETTINGS = {
    'N': 2,               # Number of world_states
    'M': 2,               # Number of times
    'contingent': False,  # Whether sentence letters are contingent
    'disjoint': False,    # Whether sentence letters are assigned to distinct world_states
    'max_time': 1,        # Maximum solving time in seconds
    'expectation': True,  # Whether a model is expected or not (for testing)
}
```

### 2. general_settings

Module-level settings defined by the user in their example files. These settings apply globally to all examples in the module. The default values are defined in `BuildModule.DEFAULT_GENERAL_SETTINGS`:

```python
DEFAULT_GENERAL_SETTINGS = {
    "print_impossible": False,
    "print_constraints": False,
    "print_z3": False,
    "save_output": False,
    "maximize": False,
    "align_vertically": False,
}
```

### 3. module_flags

Command-line flags that override both the example and general settings. These are parsed by the `ParseFileFlags` class in `__main__.py`, which includes:

```python
# Examples of module flags:
--contingent (-c)      # Make all propositions contingent
--disjoint (-d)        # Make all propositions have disjoint subject-matters
--non_empty (-e)       # Make all propositions non-empty
--maximize (-m)        # Compare semantic theories
--non_null (-n)        # Make all propositions non-null
--print_constraints (-p) # Print Z3 constraints
--save_output (-s)     # Save model output
--print_z3 (-z)        # Print Z3 model or unsat_core
```

## Current Settings Merge Flow

The settings are currently merged in the following sequence:

1. **Default Base**: Start with the semantic theory's `DEFAULT_EXAMPLE_SETTINGS`
2. **Example Override**: Update with specific example's settings
3. **Global Override**: Update with module's `general_settings`
4. **Flag Override**: Override with any command-line `module_flags`

## Current Implementation Details

### 1. BuildModule._load_general_settings()

This method in the `BuildModule` class handles combining module-level settings with command-line flags.

### 2. BuildExample._validate_settings()

This method validates and merges example-specific settings with general settings and applies flag overrides.

### 3. ModelConstraints and Settings

The merged settings are passed to the `ModelConstraints` class during instantiation.

## Prioritization Logic

The system follows a clear priority order when resolving conflicts:

1. Command-line flags (`module_flags`) have the highest priority
2. Example-specific settings (`example_settings`) have the next highest priority
3. Module-level settings (`general_settings`) come next
4. Theory-specific defaults (`DEFAULT_EXAMPLE_SETTINGS`) have the lowest priority

# Refactor Settings and Flags

## Guidelines for Refactoring

Upon running `model-checker examples.py -p -z ...` settings are combined by:

- The `general_settings` override `DEFAULT_GENERAL_SETTINGS` if `general_settings` is provided in the `examples.py`
    - If a general setting does not exist in the defaults, that general setting is skipped and a warning is raised
    - The result is called `combined_general_settings`
- The `example_settings` override `DEFAULT_EXAMPLE_SETTINGS` if `example_settings` is provided in the `examples.py`
    - If an example setting does not exist in the defaults, that example setting is skipped and a warning is raised
    - The result is called `combined_example_settings`
- The `combined_example_settings` are then folded into `combined_general_settings` where `combined_example_settings` take precedence
    - The result is called `all_combined_settings`
- The flags are then used to override settings in `all_combined_settings` if they exist, skipping any flags that don't exist and raising a warning

The settings processing should follow this specific workflow:

1. First, handle general settings:
   - Start with `DEFAULT_GENERAL_SETTINGS` from the theory
   - If user-defined `general_settings` exist, override settings from `DEFAULT_GENERAL_SETTINGS` with those in `general_settings`
   - Print a warning for any keys in `general_settings` that don't exist in `DEFAULT_GENERAL_SETTINGS`
   - Only include keys that are defined in `DEFAULT_GENERAL_SETTINGS` in the final general settings

2. Next, handle example settings:
   - Start with `DEFAULT_EXAMPLE_SETTINGS` from the theory
   - If user-defined `example_settings` exist for an example, override settings from `DEFAULT_EXAMPLE_SETTINGS` with those in `example_settings`
   - Print a warning for any keys in `example_settings` that don't exist in `DEFAULT_EXAMPLE_SETTINGS`
   - Only include keys that are defined in `DEFAULT_EXAMPLE_SETTINGS` in the final example settings

3. Then, combine general and example settings:
   - Start with validated general settings
   - Override with validated example settings (example settings take priority for any overlapping keys)

4. Finally, apply flag overrides:
   - Override any settings in the combined dictionary with values from command-line flags
   - Only override existing settings (don't add new keys from flags)
   - Print a warning for any flag that doesn't correspond to an existing setting

This approach ensures that:
- Settings are always validated against their defaults
- Unknown settings generate warnings for the user to correct
- The settings flow follows a clear hierarchy (defaults → user-defined → flags)
- Settings stay within their correct domains (general vs example)
- Both `true` and `false` flag values should override corresponding settings

## Understanding the align_vertically Warning

The specific warning message `"Warning: Unknown example setting 'align_vertically' not in DEFAULT_EXAMPLE_SETTINGS"` occurs because:

1. In the bimodal theory, `align_vertically` is defined in `general_settings` in the example file:
   ```python
   # In bimodal/examples.py
   general_settings = {
       "print_constraints": False,
       "print_z3": False,
       "save_output": False,
       "align_vertically": False,  # This is a general setting
   }
   ```

2. When we added `DEFAULT_GENERAL_SETTINGS` to BimodalSemantics, we correctly put it there:
   ```python
   # In bimodal/semantic.py
   DEFAULT_GENERAL_SETTINGS = {
       "print_impossible": False,
       "print_constraints": False,
       "print_z3": False, 
       "save_output": False,
       "maximize": False,
       "align_vertically": True,  # This is correct - it's a general setting
   }
   ```

3. But in `BuildModule.process_example()` at lines 488-492, the code directly propagates a general setting `align_vertically` to the example settings:

```python
# Add the align_vertically setting from general settings to example settings
premises, conclusions, settings = translated_case
if "align_vertically" not in settings:
    settings["align_vertically"] = self.general_settings.get("align_vertically", False)
translated_case = [premises, conclusions, settings]
```

This is the cause of the warning. The code takes `align_vertically` from general_settings and injects it into example_settings. Then when our SettingsManager validates these example settings, it correctly warns that `align_vertically` isn't in DEFAULT_EXAMPLE_SETTINGS.

## Implementation Plan for SettingsManager

### Phase 1: Create the SettingsManager

1. Create a dedicated `settings` package with:
   - `settings.py` containing the core `SettingsManager` class
   - `__init__.py` to export the key components
   - `README.md` for documentation

2. Implement the core `SettingsManager` class with:
   - Proper validation of general and example settings
   - Warning for unknown settings
   - Clear domain separation
   - Flag override handling
   - Support for theory-specific defaults

### Phase 2: Update BuildModule and BuildExample

3. Refactor `BuildModule`:
   - Remove existing settings handling
   - Use SettingsManager for general settings
   - Maintain backward compatibility

4. Refactor `BuildExample`:
   - Remove the direct injection of align_vertically
   - Use SettingsManager for all settings handling
   - Support theory-specific settings

### Phase 3: Fix BimodalSemantics DEFAULT_GENERAL_SETTINGS

5. Update `BimodalSemantics`:
   - Keep `align_vertically` in DEFAULT_GENERAL_SETTINGS
   - Make sure it's not also in DEFAULT_EXAMPLE_SETTINGS
   - Consider adding DEFAULT_GENERAL_SETTINGS to other theories

### Phase 4: Add Tests and Documentation

6. Create unit tests for `SettingsManager`
7. Add integration tests for the settings pipeline
8. Update documentation
9. Add examples of proper settings usage

This implementation will solve the immediate issue with the align_vertically warning while also providing a robust, maintainable settings management system that aligns with the project's design philosophy of explicit data flow and no silent failures.

# Implementation Strategy for Settings Refactoring

After a thorough review of the codebase, I can see that the `settings` package has already been created with a functioning `SettingsManager` class that follows the specified guidelines in this document. The implementation looks solid, with proper validation, explicit warning messages, and clear priority order for settings.

However, there are still several areas that need improvement to fully integrate this system and ensure it works consistently throughout the codebase. Here's a detailed implementation strategy:

## 1. Fix the `align_vertically` Warning

The immediate issue with the `align_vertically` warning comes from `BuildModule.process_example()` which directly propagates a general setting into example settings at lines 488-492. This breaks the domain separation principle for settings.

```python
# Add the align_vertically setting from general settings to example settings
premises, conclusions, settings = translated_case
if "align_vertically" not in settings:
    settings["align_vertically"] = self.general_settings.get("align_vertically", False)
translated_case = [premises, conclusions, settings]
```

**Solution:**
1. Remove this direct injection in `builder.py`
2. Modify `BimodalStructure.print_all()` to access the general setting directly rather than expecting it in example settings:
   ```python
   align_vertically = self.settings.get("align_vertically", False)
   ```
   instead of:
   ```python
   align_vertically = default_settings.get("align_vertically", False)
   ```

## 2. Ensure Consistent Theory DEFAULT_GENERAL_SETTINGS

Currently, `BimodalSemantics` defines `DEFAULT_GENERAL_SETTINGS` but other theories may not. We need to ensure all theories:

1. Define their own `DEFAULT_GENERAL_SETTINGS` (if theory-specific defaults are needed)
2. The integration with `SettingsManager` happens consistently

**Actions:**
1. Add `DEFAULT_GENERAL_SETTINGS` to any theory that needs specific defaults
2. Verify that `SettingsManager` correctly falls back to global defaults when a theory doesn't define its own

## 3. Update BuildModule Integration

While `BuildModule` has been updated to use `SettingsManager` for validating general settings, there are a few improvements needed:

1. The constructor initializes `SettingsManager` with the first semantic theory, but this should be updated for each theory
2. The `process_example()` method should update the settings manager when processing examples with different theories
3. Remove the direct propagation of `align_vertically` as mentioned in step 1

**Actions:**
1. Update `BuildModule.process_example()` to use a theory-specific `SettingsManager` for each example
2. Ensure all settings access goes through proper validation
3. Make BuildModule store only the final merged settings, not separate general and example settings

## 4. Update BuildExample Integration

The `BuildExample` class has been updated to use `SettingsManager`, but there are inconsistencies:

1. It has a redundant `_validate_settings()` method that should be removed
2. It should ensure all settings access goes through the properly validated settings
3. It should consistently use `self.settings` rather than direct access to module flags

**Actions:**
1. Remove the redundant `_validate_settings()` method 
2. Ensure the class consistently uses `self.settings` for all settings access
3. Add proper docstrings explaining the settings flow

## 5. Fix Settings Flow in ModelStructure Classes

Classes like `BimodalStructure` currently receive settings in potentially inconsistent ways:

1. Some methods get settings via explicit parameters (`default_settings`)
2. Others access settings through `self.settings`
3. This inconsistency leads to potential settings leakage between domains

**Actions:**
1. Make all model structure classes consistently use `self.settings`
2. Remove any direct passing of settings between methods when a central `self.settings` is available
3. Update method signatures to remove redundant settings parameters

## 6. Add Settings Validation in Theory Init Methods

Currently, when theories define their `__init__` methods, they often directly use settings without validation:

1. Add validation in each theory's initialization method to ensure settings are properly validated
2. Ensure that theory-specific validation happens consistently

**Actions:**
1. Update theory `__init__` methods to use `SettingsManager` for settings validation
2. Ensure proper type checking for critical settings (e.g., N, M in bimodal theory)

## 7. Improve Settings Documentation & Tests

While the basic test infrastructure is in place, we should expand it:

1. Add more unit tests for edge cases in settings
2. Add integration tests for the entire settings pipeline
3. Add comprehensive documentation about the settings system

**Actions:**
1. Expand test coverage for settings behavior
2. Add docstrings and comments explaining the settings system
3. Update user-facing documentation on how to use settings correctly

## 8. Audit CLI Flags Integration

Ensure that CLI flags are correctly integrated with the settings system:

1. Verify that flags in `__main__.py` properly map to settings
2. Ensure all flag handling is consistent with the settings domain model

**Actions:**
1. Audit flag definitions to ensure they align with expected settings
2. Update flag docstrings to clarify which domain they affect (general vs. example)
3. Implement proper validation for flag values

By following this implementation strategy, we'll create a robust, consistent settings system that follows the project's design philosophy of explicit data flow and no silent failures, while fixing the immediate issue with the `align_vertically` warning.
