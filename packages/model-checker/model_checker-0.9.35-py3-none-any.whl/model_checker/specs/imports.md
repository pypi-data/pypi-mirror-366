# Import Strategies for Generated Projects

## The Problem

When a user generates a new theory project using `model-checker -l bimodal`, the generated `examples.py` file includes imports for `semantic.py` and `operators.py`. These imports need to work in multiple contexts:

1. When running directly with `model-checker examples.py`
2. When imported as a module from another file
3. When running from a different directory
4. Across different operating systems and Python environments

Currently, the imports fail in some contexts, causing errors like:
```
ModuleNotFoundError: No module named 'project_again'
```

## Import Strategies

Here are different import strategies that can be used in `examples.py`:

### 1. Relative Imports

```python
# Relative imports - work when imported as part of a package
from .semantic import *
from .operators import *
```

**When they work**: When the file is part of a properly structured Python package with `__init__.py` files and is imported from another module.

**When they fail**: When running the file directly or when the parent directory is not in the Python path.

### 2. Local Imports

```python
# Local imports - work when in the same directory
from semantic import *
from operators import *
```

**When they work**: When the `.py` files are in the same directory and you're running the file from that directory.

**When they fail**: When running from a different directory or when imported as part of a package.

### 3. Absolute Imports

```python
# Absolute imports - specific to the project name
from project_name.semantic import *
from project_name.operators import *
```

**When they work**: When the project is installed as a package or the project's parent directory is in the Python path.

**When they fail**: When the project is not installed or when the parent directory is not in the Python path.

### 4. Path Manipulation with sys.path

```python
# Path manipulation - more reliable but not ideal
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from semantic import *
from operators import *
```

**When they work**: In most situations, as it dynamically adds the current directory to the Python path.

**When they fail**: Can cause issues in complex package structures or when multiple packages have the same module names.

### 5. Try/Except with Multiple Strategies

```python
# Flexible import strategy using try/except
import sys
import os

try:
    # Try package-relative imports first
    from .semantic import *
    from .operators import *
except ImportError:
    try:
        # Try direct imports next
        from semantic import *
        from operators import *
    except ImportError:
        # Add current directory to path and try again
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.append(current_dir)
        from semantic import *
        from operators import *
```

**When they work**: This approach is the most robust, as it tries multiple strategies in order of preference.

**When they fail**: Can be confusing for debugging and may mask real import issues.

### 6. Environment Variable for Path

```python
# Using environment variables
import sys
import os

# Use PYTHONPATH environment variable or current directory
module_dir = os.environ.get('MODEL_CHECKER_PROJECT_DIR', os.path.dirname(os.path.abspath(__file__)))
if module_dir not in sys.path:
    sys.path.append(module_dir)

from semantic import *
from operators import * 
```

**When they work**: When the environment variable is set or when running from the project directory.

**When they fail**: When the environment variable is not set and running from a different directory.

## Recommendation

The most robust solution is a simplified version of approach #5 (try/except with multiple strategies):

```python
# === Start of import handling ===
import sys
import os

# Flexible import strategy to support various execution contexts
try:
    # Try direct imports first (when in same directory)
    from semantic import *
    from operators import *
except ImportError:
    # Try adding the current directory to the path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    # Now try the imports again
    from semantic import *
    from operators import *
# === End of import handling ===
```

This approach:
1. Tries direct imports first, which is the most common case when running with `model-checker examples.py`
2. Falls back to adding the current directory to the path if that fails
3. Is simpler than the full try/except strategy, which makes debugging easier
4. Works in most real-world scenarios
5. Avoids relative imports which are causing the most problems

## Implementation Plan

To implement this solution:

1. Modify `BuildProject._update_file_contents()` to replace imports in generated `examples.py` files
2. Add a comment in the generated files explaining the import strategy
3. Document this approach in the README.md for users who create their own files

This approach follows the debugging philosophy by addressing the root cause of the import issues while providing a clear, deterministic solution that fails explicitly when it can't find the modules rather than failing silently.