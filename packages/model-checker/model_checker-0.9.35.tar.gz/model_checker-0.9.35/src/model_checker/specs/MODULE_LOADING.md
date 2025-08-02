# Module Loading and Import Fix

## Problem

Users have been experiencing import errors when running examples.py files that were generated using `model-checker -l bimodal`. The specific error is:

```
ModuleNotFoundError: No module named 'semantic'
```

This occurs because of a mismatch between how model-checker loads modules and how Python's import system works.

## Root Cause

The BuildModule._load_module() method in model-checker loads the examples.py file but doesn't add the file's directory to sys.path unless it's part of a proper Python package structure with __init__.py files. This means that when running a standalone file with `model-checker examples.py`, the imports for 'semantic' and 'operators' modules in the same directory fail.

## Solution

We've implemented a two-part solution:

1. **Fixed existing templates**: Added path handling code to all example files in theory_lib:
   - Added dynamic path handling to all existing examples.py templates 
   - This ensures they have the code needed to add their directory to sys.path

2. **Fixed project generation**: Modified BuildProject._update_file_contents() to:
   - Add the same path handling code to any newly generated examples.py files
   - Adjust the code placement based on the file's existing structure
   - Ensure proper modules can be imported from the examples.py file

## How It Works

The added code looks like this:

```python
# Standard imports
import sys
import os

# Add current directory to path before importing modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
```

This does the following:
1. Gets the directory where the examples.py file is located
2. Adds that directory to sys.path if it's not already there
3. Ensures that local imports like `from semantic import *` work properly

## Testing

To test this fix:

1. Generate a new theory project:
   ```
   model-checker -l bimodal
   ```

2. Verify the generated examples.py file contains the path handling code

3. Run the examples.py file directly:
   ```
   model-checker examples.py
   ```

4. The imports should now work correctly without errors

## Long-Term Improvement

While this solution fixes the immediate issue, a more robust approach for future versions could be:

1. Modify BuildModule._load_module() to always add the file's directory to sys.path
2. Create a more robust module loading system that handles different execution contexts
3. Document the expected project structure and import requirements more clearly

## References

This change is inspired by the debugging philosophy described in CLAUDE.md, focusing on:
- Addressing the root cause rather than symptoms
- Providing a clear, structural solution
- Making failures explicit rather than implicit
- Preserving deterministic behavior