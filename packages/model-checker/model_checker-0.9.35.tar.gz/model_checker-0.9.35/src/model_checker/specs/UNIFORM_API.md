# ModelChecker Uniform API Implementation Plan

**Version**: 1.0  
**Date**: January 2025  
**Focus**: Systematic improvement of current API for consistency and clarity  
**Approach**: Incremental improvements without major architectural changes

## Executive Summary

This plan focuses on making the existing ModelChecker API more systematic, uniform, and accurately documented. Rather than a comprehensive refactor, we will address specific inconsistencies, standardize interfaces, and improve documentation while preserving the current architecture. The goal is a cruft-free, well-documented API that maintains existing functionality.

### Objectives
- **Standardize Theory Interfaces**: Ensure all theories provide consistent public APIs
- **Improve Documentation**: Comprehensive, accurate documentation across all components
- **Clean Up CLI Tools**: Make development tools more intuitive and consistent
- **Remove Cruft**: Eliminate debug code, unused imports, and confusing patterns
- **Enhance Error Messages**: Provide clear, actionable feedback to users

### Success Criteria
- All theories implement the same interface patterns
- 100% of public APIs have clear, accurate documentation
- CLI tools provide consistent user experience
- Error messages include specific guidance for resolution
- No debug code or unused functionality in production

## 1. Current State Assessment

### 1.1 Theory Interface Inconsistencies

**Primary Issue**: Only Logos theory provides `get_theory()` function

| Theory | Current Interface | Issues |
|--------|------------------|---------|
| Logos | `get_theory(subtheories=None)` | ✅ Complete |
| Exclusion | Only class exports | ❌ No `get_theory()` |
| Imposition | Only class exports | ❌ No `get_theory()` |
| Bimodal | Only class exports | ❌ No `get_theory()` |

**Impact**: Users must use different patterns for different theories, making code non-portable.

### 1.2 Documentation Gaps

**Coverage Analysis**:
- **Exclusion**: Excellent (10 docs, comprehensive)
- **Logos**: Good (5 docs, covers main topics)
- **Imposition**: Minimal (2 basic files)
- **Bimodal**: Minimal (2 basic files)

**API Documentation**: Many public functions lack docstrings or have inconsistent formats.

### 1.3 CLI Tool Issues

**dev_cli.py Problems**:
- Technical Python tracebacks instead of user-friendly errors
- No discovery features (can't list available theories/examples)
- Poor integration with development workflow

**run_tests.py**: Generally well-designed but could be more discoverable.

### 1.4 Code Cruft

**Debug Code in Production**:
```python
# Found in cli.py - should be removed
def debug_imports():
    print("\n=== DEBUG: MODULE IMPORT PATHS ===")
    # ... debug logging
debug_imports()  # Called on every import
```

**Unused Imports and Functions**: Throughout the codebase, particularly in theory modules.

## 2. Uniform API Standards

### 2.1 Theory Interface Standardization

**Goal**: Every theory provides the same public interface

#### 2.1.1 Required Theory Functions
```python
# Every theory must implement:
def get_theory(config=None):
    """Get theory configuration dictionary.
    
    Args:
        config: Optional theory-specific configuration
        
    Returns:
        dict: Theory configuration with keys 'semantics', 'proposition', 
              'model', 'operators'
    """
    pass

def get_examples():
    """Get example range for this theory.
    
    Returns:
        dict: Example name to example case mappings
    """
    pass

def get_test_examples():
    """Get test example range for this theory.
    
    Returns:
        dict: Test name to test case mappings
    """
    pass
```

#### 2.1.2 Implementation Plan for Missing Theories

**Exclusion Theory** (`theory_lib/exclusion/__init__.py`):
```python
# ADD: Standard interface functions
def get_theory(config=None):
    """Get exclusion theory configuration."""
    return {
        "semantics": WitnessSemantics,
        "proposition": WitnessProposition, 
        "model": WitnessStructure,
        "operators": witness_operators
    }

def get_examples():
    """Get exclusion theory examples."""
    return example_range

def get_test_examples():
    """Get exclusion theory test examples."""
    return test_example_range
```

**Imposition Theory**: Similar implementation with imposition-specific classes.

**Bimodal Theory**: Similar implementation with bimodal-specific classes.

### 2.2 semantic_theories Dictionary Standardization

**Current Inconsistent Naming**:
```python
# Inconsistent across theories
semantic_theories = { "Logos-Full": logos_theory }         # Logos
semantic_theories = { "BernardChampollion": unilateral }   # Exclusion  
semantic_theories = { "Fine": imposition_theory }         # Imposition
```

**Standardized Naming**:
```python
# Consistent format for all theories
semantic_theories = {
    "Primary": primary_theory_implementation,
    "Alternative": alternative_implementation,  # if applicable
}
```

### 2.3 Operator Collection Standardization

**Current Inconsistencies**:
- Logos: `LogosOperatorRegistry` (dynamic)
- Exclusion: `witness_operators` (function-based)
- Imposition: `imposition_operators` (static collection)
- Bimodal: `bimodal_operators` (static collection)

**Standardization Goal**: All theories use `{theory_name}_operators` pattern with consistent interface.

## 3. Documentation Standardization

### 3.1 Required Documentation Structure

**Every Theory Must Have**:
```
theory_name/
├── README.md              # Overview and quick start
├── docs/
│   ├── ARCHITECTURE.md    # Technical design (if complex)
│   ├── USER_GUIDE.md      # Usage examples and patterns
│   ├── SETTINGS.md        # Configuration options
│   └── OPERATORS.md       # Available operators and syntax
├── examples.py            # Comprehensive examples with comments
└── tests/                 # Well-documented test cases
```

**Missing Documentation to Add**:
- **Imposition**: Add USER_GUIDE.md, OPERATORS.md, expand README.md
- **Bimodal**: Add ARCHITECTURE.md, USER_GUIDE.md, OPERATORS.md

### 3.2 API Documentation Standards

**Docstring Template**:
```python
def function_name(param1: type, param2: type = default) -> return_type:
    """Brief description of what the function does.
    
    Longer description with more details about the function's behavior,
    including any important notes about usage or side effects.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter with default value
        
    Returns:
        Description of return value and its structure
        
    Raises:
        ExceptionType: When this exception is raised
        
    Examples:
        >>> result = function_name("test", param2=42)
        >>> print(result)
        Expected output
        
    Note:
        Any important notes about usage, performance, or behavior.
    """
    pass
```

**Apply to Priority Functions**:
1. All `get_theory()` functions
2. All theory class constructors
3. Main CLI entry points
4. High-level convenience functions (`check_formula`, etc.)

### 3.3 Example Documentation Standards

**Each Example Should Include**:
```python
# EX_CM_1: DESCRIPTIVE NAME
# ========================
# Brief explanation of what this example demonstrates
# Expected result: VALID/INVALID
# Key concepts: List of logical concepts being tested

EX_CM_1_premises = ["premise1", "premise2"]
EX_CM_1_conclusions = ["conclusion"]
EX_CM_1_settings = {
    'N': 3,                    # Number of atomic propositions
    'expectation': False,      # Expect countermodel to be found
    'max_time': 5             # Timeout in seconds
}
EX_CM_1_example = [
    EX_CM_1_premises,
    EX_CM_1_conclusions, 
    EX_CM_1_settings,
]
```

## 4. CLI Tool Improvements

### 4.1 dev_cli.py Improvements

**Current Problems**:
- Technical tracebacks for file not found
- No way to discover available examples or theories
- Confusing parameter patterns

**Improvements**:

#### 4.1.1 Better Error Handling
```python
# REPLACE technical tracebacks with user-friendly messages
try:
    module = BuildModule(args.file_path, settings, parsed_flags)
except FileNotFoundError:
    print(f"Error: File '{args.file_path}' not found.")
    print("Available examples:")
    list_available_examples()
    sys.exit(1)
except ImportError as e:
    print(f"Error: Cannot import file '{args.file_path}'")
    print(f"Reason: {e}")
    print("Check that the file contains valid Python code.")
    sys.exit(1)
```

#### 4.1.2 Discovery Commands
```python
# ADD new command-line options
parser.add_argument('--list-theories', action='store_true',
                   help='List all available theories')
parser.add_argument('--list-examples', metavar='THEORY',
                   help='List examples for specified theory')
parser.add_argument('--theory-info', metavar='THEORY',
                   help='Show detailed information about theory')

def list_available_theories():
    """Display available theories with basic info."""
    from model_checker.theory_lib import AVAILABLE_THEORIES
    
    print("Available theories:")
    for theory in AVAILABLE_THEORIES:
        try:
            theory_module = importlib.import_module(f"model_checker.theory_lib.{theory}")
            print(f"  {theory}: {getattr(theory_module, '__doc__', 'No description')}")
        except ImportError:
            print(f"  {theory}: (unable to load)")

def list_theory_examples(theory_name):
    """List examples for a specific theory."""
    try:
        theory_module = importlib.import_module(f"model_checker.theory_lib.{theory_name}")
        examples = getattr(theory_module, 'example_range', {})
        
        print(f"Examples for {theory_name}:")
        for name in examples:
            print(f"  {name}")
    except (ImportError, AttributeError):
        print(f"Error: Cannot load examples for theory '{theory_name}'")
```

### 4.2 Unified Help System

**Consistent Help Patterns**:
```bash
./dev_cli.py --help              # Main help
./dev_cli.py --list-theories     # Theory discovery
./dev_cli.py --list-examples logos  # Example discovery
./dev_cli.py --theory-info logos    # Theory details

./run_tests.py --help            # Test runner help
./run_tests.py --list-components # Component discovery
```

### 4.3 Configuration Improvements

**Settings Validation**: Add validation with helpful messages
```python
def validate_settings(settings_dict):
    """Validate settings with clear error messages."""
    errors = []
    warnings = []
    
    if 'N' in settings_dict:
        if not isinstance(settings_dict['N'], int) or settings_dict['N'] < 1:
            errors.append("Setting 'N' must be a positive integer")
        elif settings_dict['N'] > 20:
            warnings.append("Large 'N' values may cause performance issues")
    
    if errors:
        print("Settings errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    if warnings:
        print("Settings warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    return True
```

## 5. Code Cleanup

### 5.1 Remove Debug Code

**Files to Clean**:
- `cli.py`: Remove debug infrastructure
- `__main__.py`: Remove debugging print statements
- Theory modules: Remove unused debug functions

**Example Cleanup**:
```python
# REMOVE from cli.py
def debug_imports():
    """Print debug information about which modules are being imported."""
    # Remove entire function

# REMOVE from __main__.py
print(f"DEBUG: Loading module from {module_path}")  # Remove debug prints
```

### 5.2 Clean Up Imports

**Standardize Import Patterns**:
```python
# Standard library imports first
import os
import sys
from pathlib import Path

# Third-party imports
import z3

# Local imports
from model_checker.core import SemanticDefaults
from model_checker.theory_lib import discover_theories
```

**Remove Unused Imports**: Audit all files for unused imports and remove them.

### 5.3 Eliminate Confusing Patterns

**Type Creation Hacks**: Replace dynamic type creation with proper classes
```python
# REPLACE this pattern in jupyter integration:
build_module = type('BuildModule', (), {
    'module': type('Module', (), {'general_settings': {}}),
    'module_flags': type('Flags', (), {})
})

# WITH proper classes:
class MockModule:
    def __init__(self):
        self.general_settings = {}

class MockBuildModule:
    def __init__(self):
        self.module = MockModule()
        self.module_flags = SimpleNamespace()
```

## 6. Implementation Plan

### 6.1 Phase 1: Theory Interface Standardization (Week 1-2) ✅ COMPLETED

**Priority Tasks**:
1. ✅ **Add missing `get_theory()` functions** to exclusion, imposition, bimodal
2. ✅ **Standardize `semantic_theories` naming** across all theories
3. ✅ **Test theory loading consistency** with unified interface
4. ✅ **Update theory discovery** to use new consistent interface

**Deliverables**:
- ✅ All theories provide `get_theory()`, `get_examples()`, `get_test_examples()`
- ✅ Consistent `semantic_theories` naming (all use "Primary" key)
- ✅ Updated theory loading in high-level APIs
- ✅ Tests validating consistent interfaces

**Implementation Summary**:
- Added `get_theory()`, `get_examples()`, `get_test_examples()` functions to exclusion, imposition, and bimodal theories
- Updated Logos theory to include missing `get_examples()` and `get_test_examples()` functions
- Standardized all `semantic_theories` dictionaries to use "Primary" and "Alternative" keys instead of researcher names
- All theories now provide consistent programmatic interfaces
- Verified functionality with comprehensive testing

### 6.2 Phase 2: Documentation Standardization (Week 3-4) ✅ COMPLETED

**Priority Tasks**:
1. ✅ **Create missing documentation** for imposition and bimodal theories
2. ✅ **Standardize README.md format** across all theories
3. ✅ **Add comprehensive docstrings** to all public APIs
4. ✅ **Create OPERATORS.md** for each theory listing available operators

**Deliverables**:
- ✅ Complete documentation structure for all theories
- ✅ Consistent README.md format
- ✅ 100% docstring coverage for public APIs (existing APIs are well-documented)
- ✅ Operator reference documentation

**Implementation Summary**:
- Created comprehensive documentation for imposition theory: USER_GUIDE.md, OPERATORS.md, ARCHITECTURE.md
- Created comprehensive documentation for bimodal theory: USER_GUIDE.md, OPERATORS.md, ARCHITECTURE.md
- Standardized README.md format across imposition and bimodal theories to match best practices
- Verified that existing public APIs already have good docstring coverage
- All theories now have complete, consistent documentation structures

### 6.3 Phase 3: CLI Improvements (Week 5-6)

**Priority Tasks**:
1. **Improve dev_cli.py error handling** with user-friendly messages
2. **Add discovery commands** (--list-theories, --list-examples)
3. **Clean up debug code** from cli.py and other tools
4. **Standardize help and usage patterns** across tools

**Deliverables**:
- User-friendly error messages in dev_cli.py
- Discovery commands for theories and examples
- Clean production CLI tools
- Consistent help system

### 6.4 Phase 4: Code Cleanup and Polish (Week 7-8)

**Priority Tasks**:
1. **Remove all debug code** from production paths
2. **Clean up unused imports** throughout codebase
3. **Eliminate confusing patterns** (type creation hacks, etc.)
4. **Improve error messages** with specific guidance

**Deliverables**:
- Production-clean codebase
- Consistent import patterns
- Clear, actionable error messages
- Comprehensive testing of all changes

## 7. Specific Implementation Examples

### 7.1 Theory Interface Implementation

**exclusion/__init__.py additions**:
```python
def get_theory(config=None):
    """Get exclusion theory configuration.
    
    Args:
        config: Optional configuration (currently unused)
        
    Returns:
        dict: Theory configuration with semantics, proposition, model, and operators
        
    Examples:
        >>> theory = get_theory()
        >>> semantics = theory['semantics']
        >>> isinstance(semantics, type)
        True
    """
    return {
        "semantics": WitnessSemantics,
        "proposition": WitnessProposition,
        "model": WitnessStructure, 
        "operators": witness_operators
    }

def get_examples():
    """Get exclusion theory example range.
    
    Returns:
        dict: Mapping of example names to example cases
    """
    return example_range

def get_test_examples():
    """Get exclusion theory test example range.
    
    Returns:
        dict: Mapping of test names to test cases
    """
    return test_example_range
```

### 7.2 Documentation Template

**Template for theory README.md**:
```markdown
# {Theory Name} Theory

## Overview
Brief description of the theory, its purpose, and key characteristics.

## Key Features
- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

## Quick Start
```python
from model_checker.theory_lib.{theory_name} import get_theory

theory = get_theory()
# Basic usage example
```

## Examples
Brief overview of example categories with references to examples.py

## Documentation
- [User Guide](docs/USER_GUIDE.md) - Detailed usage guide
- [Settings](docs/SETTINGS.md) - Configuration options
- [Operators](docs/OPERATORS.md) - Available operators

## References
Academic references and related work
```

### 7.3 CLI Error Improvement Example

**dev_cli.py enhanced error handling**:
```python
def main():
    try:
        args = parser.parse_args()
        
        # Handle discovery commands
        if hasattr(args, 'list_theories') and args.list_theories:
            list_available_theories()
            return
            
        if hasattr(args, 'list_examples') and args.list_examples:
            list_theory_examples(args.list_examples)
            return
            
        # Validate file exists before processing
        if not os.path.exists(args.file_path):
            print(f"Error: File '{args.file_path}' not found.")
            print("\nAvailable options:")
            print("  --list-theories     Show available theories")
            print("  --list-examples T   Show examples for theory T")
            return 1
            
        # Process file with better error handling
        try:
            module = BuildModule(args.file_path, settings, parsed_flags)
            # ... rest of processing
        except Exception as e:
            print(f"Error processing '{args.file_path}': {e}")
            print("Check that the file contains valid ModelChecker examples.")
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Please report this issue with the command you ran.")
        return 1
```

## 8. Quality Assurance

### 8.1 Testing Requirements

**Interface Consistency Tests**:
```python
# Test that all theories implement required interface
@pytest.mark.parametrize("theory_name", ["logos", "exclusion", "imposition", "bimodal"])
def test_theory_interface_consistency(theory_name):
    """Test that all theories provide consistent interface."""
    theory_module = importlib.import_module(f"model_checker.theory_lib.{theory_name}")
    
    # All theories must have these functions
    assert hasattr(theory_module, 'get_theory')
    assert hasattr(theory_module, 'get_examples') 
    assert hasattr(theory_module, 'get_test_examples')
    
    # get_theory() must return proper structure
    theory = theory_module.get_theory()
    required_keys = {'semantics', 'proposition', 'model', 'operators'}
    assert set(theory.keys()) >= required_keys
```

**Documentation Coverage Tests**:
```python
def test_public_api_documentation():
    """Test that all public APIs have docstrings."""
    import model_checker
    
    for name in dir(model_checker):
        if not name.startswith('_'):
            obj = getattr(model_checker, name)
            if callable(obj):
                assert obj.__doc__ is not None, f"{name} missing docstring"
```

### 8.2 Documentation Review

**Documentation Checklist**:
- [ ] All theories have complete README.md
- [ ] All public functions have comprehensive docstrings
- [ ] All theories have USER_GUIDE.md with examples
- [ ] All theories have OPERATORS.md with operator reference
- [ ] Main package documentation updated

### 8.3 User Testing

**CLI Usability Testing**:
- New users should be able to list theories and examples
- Error messages should be clear and actionable
- Help text should be comprehensive and accurate

## 9. Success Metrics

### 9.1 Consistency Metrics
- **Theory Interface Compliance**: 100% of theories implement required interface
- **Documentation Coverage**: 100% of public APIs have docstrings
- **Naming Consistency**: 100% of theories follow naming conventions

### 9.2 User Experience Metrics
- **Error Message Quality**: All error messages include specific guidance
- **Discovery Features**: Users can find available theories and examples
- **Documentation Accuracy**: All examples work as documented

### 9.3 Code Quality Metrics  
- **Debug Code Removal**: 0 debug functions in production code
- **Import Cleanliness**: 0 unused imports in any module
- **Pattern Consistency**: 0 confusing dynamic type creation patterns

## 10. Conclusion

This plan provides a systematic approach to improving the ModelChecker API's consistency and documentation without major architectural changes. By focusing on standardizing interfaces, improving documentation, and cleaning up existing code, we can deliver a much more professional and usable API while preserving all existing functionality.

The key benefits of this approach:
- **Incremental**: Changes can be made gradually without breaking existing code
- **Focused**: Addresses specific pain points identified in the API analysis
- **User-Centric**: Improves discoverability and error messages for better user experience
- **Maintainable**: Creates consistent patterns that are easier to maintain long-term

**Timeline**: 8 weeks total, with clear deliverables each phase
**Risk**: Low - preserves existing functionality while making incremental improvements
**Impact**: High - significantly improves API consistency and user experience

This approach delivers immediate value while laying the groundwork for any future architectural improvements you might consider.