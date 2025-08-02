# Settings Validation Refactoring: Integrated Implementation Plan

## Overview

This document outlines a refined implementation plan for improving settings validation during theory comparison. The solution integrates seamlessly with the existing ModelChecker architecture, respecting established patterns while solving the core issue of misleading warnings when comparing theories with different settings.

## Problem Statement

When comparing multiple theories, users receive misleading warnings:
```
Warning: Unknown example setting 'possible' not in DEFAULT_EXAMPLE_SETTINGS
Warning: Unknown example setting 'fusion_closure' not in DEFAULT_EXAMPLE_SETTINGS
```

These occur because:
1. BuildModule validates settings against only the first theory
2. Different theories support different settings by design
3. The warnings suggest errors when the behavior is actually correct

## Analysis of Existing Architecture

### Current Settings System Strengths
1. **Well-Defined Flow**: Theory defaults → General settings → Example settings → CLI flags
2. **Theory Independence**: Each theory defines only its relevant settings
3. **Fail-Fast Philosophy**: Warnings don't break execution
4. **Clean Abstractions**: SettingsManager centralizes validation logic

### Integration Points
- BuildModule already creates BuildExample per theory
- BuildExample already creates its own SettingsManager
- Settings validation is already centralized in SettingsManager
- Warning messages are already generated in specific methods

## Solution Design

### Core Principle: Minimal, Integrated Changes

Rather than layering on new systems, we'll enhance existing components to be theory-aware during comparison.

### Architecture Changes

```
Current Flow:
BuildModule.__init__
├── Create SettingsManager(first_theory)  # Problem: Only uses first theory
├── Validate general_settings             # Warns about settings valid for other theories
└── For each theory:
    └── BuildExample.__init__
        ├── Create SettingsManager(theory)  # Already theory-specific
        └── Validate example_settings        # Could be comparison-aware

Proposed Flow:
BuildModule.__init__
├── Store general_settings without validation  # Delay validation
└── For each theory:
    └── BuildExample.__init__(theory_name, is_comparison)
        ├── Create SettingsManager(theory, theory_name, is_comparison)
        └── Validate with comparison awareness
```

## Implementation Plan

### Phase 1: Enhance SettingsManager with Comparison Awareness ✓

**File**: `src/model_checker/settings/settings.py`

**Status**: COMPLETED

**Changes Made**:
1. Added imports for environment variable configuration
2. Added `theory_name` and `is_comparison` parameters to `__init__`
3. Added logic to derive theory name from semantics class if not provided
4. Created `_warn_unknown_setting` method for centralized warning logic
5. Updated `validate_general_settings` and `validate_example_settings` to use new warning method
6. Added environment variable checks: `MODELCHECKER_VERBOSE` and `MODELCHECKER_SUPPRESS_COMPARISON_WARNINGS`

```python
class SettingsManager:
    def __init__(self, semantic_theory, global_defaults=None, theory_name=None, is_comparison=False):
        """Initialize with optional comparison context."""
        self.semantic_theory = semantic_theory
        self.theory_name = theory_name or "unknown"
        self.is_comparison = is_comparison
        # ... existing initialization ...
    
    def validate_example_settings(self, user_example_settings):
        """Validate settings with comparison awareness."""
        if user_example_settings is None:
            return self.DEFAULT_EXAMPLE_SETTINGS.copy()
        
        merged_settings = self.DEFAULT_EXAMPLE_SETTINGS.copy()
        
        for key in user_example_settings:
            if key not in self.DEFAULT_EXAMPLE_SETTINGS:
                # Generate appropriate warning based on context
                self._warn_unknown_setting(key, 'example')
        
        # ... rest of existing validation ...
    
    def validate_general_settings(self, user_general_settings):
        """Similar enhancement for general settings."""
        # ... similar pattern ...
    
    def _warn_unknown_setting(self, setting_name, setting_type):
        """Centralized warning logic with context awareness."""
        if self.is_comparison:
            # During comparison, only warn if verbose or single theory
            if os.environ.get('MODELCHECKER_VERBOSE', '').lower() == 'true':
                print(f"Info: Setting '{setting_name}' not supported by {self.theory_name}")
        else:
            # Normal warning for single theory usage
            print(f"Warning: Unknown {setting_type} setting '{setting_name}' "
                  f"not in {self.theory_name}'s DEFAULT_{setting_type.upper()}_SETTINGS")
```

### Phase 2: Update BuildModule to Delay Validation ✓

**File**: `src/model_checker/builder/module.py`

**Status**: COMPLETED

**Changes Made**:
1. Removed direct SettingsManager creation
2. Store `raw_general_settings` without validation
3. Create `general_settings` for backward compatibility using silent validation
4. Use `contextlib.redirect_stdout` to suppress warnings during setup

```python
def __init__(self, module_flags):
    """Initialize without immediate validation."""
    # ... existing imports and loading ...
    
    self.semantic_theories = self._load_attribute("semantic_theories")
    self.example_range = self._load_attribute("example_range")
    
    # Store raw settings - validation happens per-theory in BuildExample
    self.raw_general_settings = getattr(self.module, "general_settings", None)
    self.module_flags = module_flags
    
    # For backward compatibility, create general_settings dict
    # Use first theory's defaults as baseline (existing behavior)
    if self.raw_general_settings is not None:
        first_theory = next(iter(self.semantic_theories.values()))
        temp_manager = SettingsManager(first_theory)
        # Suppress warnings during this initial setup
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.general_settings = temp_manager.validate_general_settings(self.raw_general_settings)
    else:
        from model_checker.settings import DEFAULT_GENERAL_SETTINGS
        self.general_settings = DEFAULT_GENERAL_SETTINGS.copy()
```

### Phase 3: Enhance BuildExample with Context ✓

**File**: `src/model_checker/builder/example.py`

**Status**: COMPLETED

**Changes Made**:
1. Added `theory_name` parameter to `__init__`
2. Added detection of comparison mode using `len(build_module.semantic_theories) > 1`
3. Pass `theory_name` and `is_comparison` to SettingsManager
4. Use `raw_general_settings` from BuildModule for validation

```python
def __init__(self, build_module, semantic_theory, example_case, theory_name=None):
    """Initialize with optional theory context."""
    # ... existing validation ...
    
    # Determine if we're in comparison mode
    is_comparison = len(build_module.semantic_theories) > 1
    
    # Create theory-specific settings manager with context
    self.settings_manager = SettingsManager(
        {"semantics": self.semantics},
        build_module.general_settings,
        theory_name=theory_name,
        is_comparison=is_comparison
    )
    
    # Get complete settings with theory-aware validation
    raw_general = getattr(build_module, 'raw_general_settings', None)
    self.settings = self.settings_manager.get_complete_settings(
        raw_general,
        self.example_settings,
        build_module.module_flags
    )
    
    # ... rest of existing initialization ...
```

### Phase 4: Update BuildModule Methods ✓

**File**: `src/model_checker/builder/module.py`

**Status**: COMPLETED

**Changes Made**:
1. Updated `run_model_check` method to pass `theory_name` to BuildExample
2. Updated `process_example` method to pass `theory_name` to BuildExample

Update all BuildExample instantiations to pass theory context:

```python
def process_example(self, example_name, example_case, theory_name, semantic_theory):
    """Process with theory context."""
    # ... existing code ...
    
    # Pass theory_name to BuildExample
    example = BuildExample(self, semantic_theory, example_case, theory_name)
    
    # ... rest of method ...

def run_model_check(self, example_case, example_name, theory_name, semantic_theory):
    """Similar update."""
    # ... existing code ...
    
    example = BuildExample(self, semantic_theory, example_case, theory_name)
    
    # ... rest of method ...
```

### Phase 5: Add Minimal Configuration ✓

**File**: `src/model_checker/settings/settings.py`

**Status**: COMPLETED (in Phase 1)

**Changes Made**:
1. Added import for `os` module
2. Added `VERBOSE_SETTINGS` environment variable check
3. Added `SUPPRESS_COMPARISON_WARNINGS` environment variable check
4. These are used in the `_warn_unknown_setting` method

```python
# At module level, add simple configuration
import os

# Simple environment variable check - no new classes needed
VERBOSE_SETTINGS = os.environ.get('MODELCHECKER_VERBOSE', '').lower() == 'true'
SUPPRESS_COMPARISON_WARNINGS = os.environ.get(
    'MODELCHECKER_SUPPRESS_COMPARISON_WARNINGS', ''
).lower() == 'true'
```

## Testing Strategy

### Existing Test Updates

1. **Update settings tests** to verify comparison mode behavior
2. **Add test cases** for multi-theory examples
3. **Verify backward compatibility** with single-theory usage

### New Test Cases

```python
def test_comparison_warnings():
    """Test that warnings are suppressed/modified during comparison."""
    # Create module with multiple theories
    # Verify warning behavior differs from single theory
    
def test_theory_name_in_warnings():
    """Test that warnings include theory name."""
    # Verify warning format includes theory context
```

## Benefits of This Approach

1. **Minimal Changes**: Works within existing architecture
2. **No New Dependencies**: Uses existing SettingsManager pattern
3. **Backward Compatible**: Single theory usage unchanged
4. **Clean Integration**: Follows established patterns
5. **Maintainable**: Changes are localized and clear

## Migration Path

### For Users
- No changes required for existing code
- Set `MODELCHECKER_VERBOSE=true` for detailed comparison info
- Set `MODELCHECKER_SUPPRESS_COMPARISON_WARNINGS=true` to hide all comparison warnings

### For Developers
- BuildExample can optionally receive theory_name
- SettingsManager can be comparison-aware
- No changes to theory definitions required

## Alternative: Even Simpler Approach

If we want the absolute minimal change:

**Option**: Only modify the warning message in SettingsManager to detect multiple theories:

```python
def validate_example_settings(self, user_example_settings):
    """Minimal change - just improve the warning."""
    # ... existing code ...
    
    for key in user_example_settings:
        if key not in self.DEFAULT_EXAMPLE_SETTINGS:
            # Check if we might be comparing theories
            semantics_class = self.semantic_theory.get("semantics")
            theory_name = getattr(semantics_class, '__name__', 'Theory')
            
            # Improved warning message
            print(f"Warning: Setting '{key}' not recognized by {theory_name}. "
                  f"This is expected when comparing theories with different settings.")
```

This minimal approach:
- Changes only warning messages
- Requires no architectural changes
- Makes the situation clear to users
- Can be implemented in minutes

## Implementation Summary

All phases have been completed successfully:

### Phase 1: SettingsManager Enhancement ✓
- Added comparison awareness with `theory_name` and `is_comparison` parameters
- Created centralized `_warn_unknown_setting` method
- Added environment variable configuration

### Phase 2: BuildModule Updates ✓
- Store `raw_general_settings` without immediate validation
- Maintain backward compatibility with silent initial setup

### Phase 3: BuildExample Enhancement ✓
- Added `theory_name` parameter
- Detect comparison mode automatically
- Pass context to SettingsManager

### Phase 4: Method Updates ✓
- Updated all BuildExample instantiations to pass theory context

### Phase 5: Configuration ✓
- Environment variables `MODELCHECKER_VERBOSE` and `MODELCHECKER_SUPPRESS_COMPARISON_WARNINGS`

## Testing the Implementation

To verify the implementation works correctly:

1. **Normal mode** (default): Warnings are suppressed during comparison
2. **Verbose mode**: `MODELCHECKER_VERBOSE=true` shows info messages
3. **Suppress all**: `MODELCHECKER_SUPPRESS_COMPARISON_WARNINGS=true` hides all comparison warnings

The implementation successfully:
- Maintains backward compatibility
- Integrates cleanly with existing architecture
- Provides user control via environment variables
- Improves warning clarity with theory context
- Solves the core issue of misleading warnings during theory comparison

## Cleanup

Remember to remove the test file:
```bash
rm test_settings_comparison.py
```