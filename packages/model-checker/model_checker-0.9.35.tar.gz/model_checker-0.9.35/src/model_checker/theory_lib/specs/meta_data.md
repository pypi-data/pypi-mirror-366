# Versioning and Licensing Implementation Plan

## Overview

This document outlines a comprehensive implementation plan for versioning and licensing in the ModelChecker project. It addresses two key requirements:

1. **Versioning System**: A dual-versioning approach for both the core package and individual theories
2. **Licensing System**: A multi-tiered licensing strategy with a main package license and theory-specific licenses

## 1. Versioning Implementation

### 1.1 Core Package Versioning

The core `model-checker` package already has a versioning system implemented through:
- `pyproject.toml` for build-time versioning
- `__init__.py` for runtime version detection

This implementation should be maintained, but with additional features to expose it to theory implementations.

#### Required Changes:

1. **Version Utility Function**:
   - Create `get_model_checker_version()` in `utils.py` to unify version access
   - Update `__init__.py` to use this function
   - Ensure version is properly exposed in the public API

2. **Version Access from Theory Libraries**:
   - Ensure all theory implementations can access the core package version

### 1.2 Theory-Specific Versioning

Each theory in `theory_lib/` should maintain its own versioning system independent of the core package version.

#### Required Changes:

1. **Theory Version Attribute**:
   - Add `__version__` attribute to each theory's `__init__.py`
   - Define a standardized version format for theories (SemVer recommended)
   - Add version documentation in each theory's README.md

2. **BuildProject Integration**:
   - Modify `builder/project.py` to copy both the core package version and set a new theory version
   - Template version for new theories should start at "0.1.0"

3. **Version Registry**:
   - Implement a version registry within `theory_lib/__init__.py`
   - Create `get_theory_version(theory_name)` function to query versions

### 1.3 Version Compatibility Checking

Add functionality to check compatibility between core package and theory versions.

#### Required Changes:

1. **Compatibility Logic**:
   - Implement `check_theory_compatibility(theory_name)` in theory_lib/__init__.py
   - Document compatibility requirements for each theory

## 2. Licensing Implementation

### 2.1 Open Source License Comparison

Before selecting a license for the ModelChecker project, it's important to understand the differences between common open source licenses, with special attention to their patent provisions:

#### MIT License (Current License)

**Overview**: A permissive license that allows anyone to do almost anything with the code.

**Patent Rights**:
- **No Explicit Patent Grant**: The MIT License does not explicitly address patents
- **Implicit License Only**: May provide an implicit patent license, but this is legally uncertain
- **No Patent Protection**: Does not protect users from patent litigation by contributors
- **No Defensive Termination**: Contains no mechanism to discourage patent litigation

**Pros**:
- Simple and widely understood
- Compatible with most other licenses
- Minimal restrictions on usage
- Business-friendly (can be used in commercial products)
- No requirement to share modifications

**Cons**:
- No copyleft provisions (derivatives can be made proprietary)
- Provides limited protection for original authors
- No explicit patent protection
- May allow others to build proprietary extensions without contributing back

**Appropriate for**: Simple libraries, frameworks, and tools where maximum adoption is the priority and patent concerns are minimal.

#### GNU General Public License (GPL v3)

**Overview**: A strong copyleft license requiring that all derivative works also be licensed under the GPL.

**Patent Rights**:
- **Explicit Patent Grant**: Automatically grants a patent license for any patents held by contributors that would be infringed by the normal use of the software
- **Patent Retaliation**: License terminates if you initiate patent litigation claiming the covered work infringes your patents
- **Strong Protection**: Comprehensive protection against patent litigation from contributors
- **Anti-Tivoization**: Prevents using patents to limit users' ability to modify and run modified versions

**Pros**:
- Ensures all derivatives remain open source
- Requires sharing of modifications
- Strong patent protection
- Prevents proprietary forks of the software
- Protects user freedom

**Cons**:
- Can limit commercial adoption
- May create compatibility issues with other licenses
- Complex compliance requirements
- Can be difficult to integrate with proprietary software

**Appropriate for**: Software where maintaining freedom and preventing proprietary derivatives is critical, and where patent protection is a significant concern.

#### GNU Lesser General Public License (LGPL v3)

**Overview**: A weaker copyleft license that allows linking to the library from non-GPL software.

**Patent Rights**:
- **Same as GPL**: Inherits the same patent provisions as GPL v3
- **Explicit Patent Grant**: Automatically grants a patent license for covered patents
- **Patent Retaliation**: License terminates if you initiate patent litigation
- **Protection Scope**: Patent protection extends to the LGPL code but not necessarily to the larger work that links to it

**Pros**:
- Allows use in commercial products without requiring the entire product to be GPL
- Still requires modifications to the library itself to be shared
- Provides patent protection for the library code
- More business-friendly than GPL

**Cons**:
- More complex than permissive licenses
- Less protection for user freedom than GPL
- Can still create compliance challenges
- May deter some commercial users

**Appropriate for**: Libraries and frameworks that should remain open but need wider adoption, especially when patent concerns exist for the core library.

#### Mozilla Public License 2.0 (MPL-2.0)

**Overview**: A file-level copyleft license that requires modifications to existing files to be shared.

**Patent Rights**:
- **Explicit Patent Grant**: Each contributor automatically grants a patent license for their contributions
- **Limited Scope**: Patent grant covers the specific contribution and necessary combinations with the original work
- **Defensive Termination**: Patent grant terminates if you initiate patent litigation against the covered software
- **Proportional Response**: If you sue a contributor for patent infringement, you lose patent rights only from that specific contributor

**Pros**:
- Balanced approach between permissive and copyleft
- Only requires sharing modifications to MPL-licensed files
- Explicitly grants patent rights with nuanced defensive provisions
- Compatible with GPL and commercial software
- Allows embedding in larger works under different licenses

**Cons**:
- More complex than MIT/BSD
- File-level approach can be confusing
- Less common than MIT or GPL

**Appropriate for**: Libraries, frameworks, and applications that want to ensure contributions to the core code while allowing flexible usage in larger projects, with well-balanced patent protection.

#### Apache License 2.0

**Overview**: A permissive license with explicit patent grants and contribution terms.

**Patent Rights**:
- **Broad Patent Grant**: Each contributor explicitly grants a patent license covering their contributions
- **Strong Patent Retaliation**: Patent grant terminates if you initiate patent litigation against the work
- **Explicit Mechanism**: Clearly defines the scope and conditions of the patent grant
- **Contributor Focus**: Patent provisions focus on protecting against contributor patent claims

**Pros**:
- Explicitly grants patent rights with detailed terms
- Contains a patent retaliation clause specifically targeting litigation
- Allows modifications without requiring source sharing
- Business-friendly while maintaining patent protection
- Includes clear contribution guidelines

**Cons**:
- More complex than MIT/BSD
- No copyleft provisions
- Derivatives can be made proprietary
- Patent retaliation only applies to litigation against the specific work

**Appropriate for**: Corporate-backed open source projects where patent protection is important, especially when multiple organizations with patent portfolios are involved.

#### Eclipse Public License 2.0

**Overview**: A weak copyleft license with explicit patent grants.

**Patent Rights**:
- **Explicit Patent Grant**: Contributors grant patent licenses covering their contributions
- **Commercial-Friendly**: Designed to be business-friendly while providing patent protection
- **Defensive Termination**: Includes patent retaliation provisions if you initiate litigation
- **Compatibility Clause**: Special provisions to allow compatibility with GPL

**Pros**:
- Balanced approach with some copyleft provisions
- Strong patent protection designed for enterprise use
- Compatible with many other licenses through special provisions
- Business-friendly while maintaining core protections

**Cons**:
- More complex than permissive licenses
- Less known than GPL or Apache
- Patent provisions require careful review in multi-vendor contexts

**Appropriate for**: Frameworks and tools where controlled extensibility is important, especially in enterprise environments with patent concerns.

#### BSL (Business Source License)

**Overview**: A time-delayed commercial license that converts to an open source license after a specified period.

**Patent Rights**:
- **Commercial Control**: Initially retains full patent rights for commercial use
- **Conversion Provision**: Patent rights transition to open source terms after the change date
- **Flexible Structure**: Can be configured with different patent terms for the initial period
- **Eventual Open Access**: Eventually provides open patent licenses like Apache or GPL

**Pros**:
- Balances commercial interests with eventual open access
- Provides time-limited commercial exclusivity
- Eventually becomes fully open source
- Can work well for academic software commercialization

**Cons**:
- Complex to implement correctly
- Not a standard OSI-approved license
- May deter some contributors during the commercial period
- Requires careful drafting of patent provisions

**Appropriate for**: Academic software that needs initial commercial revenue while planning for eventual open source availability.

### 2.2 Main Package License

Based on project requirements, the model-checker package will use the GNU General Public License v3.0 (GPL-3.0) to ensure all derivative works remain open source and that future versions maintain the same license terms.

#### Required Changes:

1. **Update Root License File**:
   - Replace the current MIT license with GPL-3.0 at the project root
   - Ensure the license clearly states the requirement that all derivative works must also be licensed under GPL-3.0
   - Include appropriate copyright notices and author attributions

2. **License Documentation**:
   - Add GPL-3.0 license information to the project README.md
   - Document the license choice with emphasis on:
     - Strong copyleft provisions requiring all derivatives to remain open
     - Patent protection for all users
     - Protection against tivoization (preventing modified versions from running)
     - Academic attribution requirements
     - Ensuring future versions cannot change to a less restrictive license

### 2.3 Theory-Specific Licensing

All theories in the theory_lib/ directory will also use the GPL-3.0 license to maintain consistency and ensure the entire project remains open source.

#### Required Changes:

1. **Theory License Files**:
   - Create a standardized GPL-3.0 template for theory-specific LICENSE.md files
   - Add LICENSE.md to each theory directory
   - Ensure theory license files explicitly reference the main project's license
   - Include language that preserves GPL-3.0 for all future versions of the theory

2. **Theory Citation Requirements**:
   - Create CITATION.md files with proper academic citations for each theory
   - Document citation requirements in theory README files
   - Ensure the citation requirements work in conjunction with GPL-3.0

3. **BuildProject Integration**:
   - Modify `builder/project.py` to automatically include GPL-3.0 license in all new theory projects
   - Update theory creation process to add required license files and headers
   - Ensure license information is properly displayed in generated theory documentation

### 2.4 License Templates

Create standardized license templates for:

1. **GPL-3.0 Package Template** (for the main model-checker package)
2. **GPL-3.0 Theory Template** (for individual theories, including author attribution)
3. **Combined Attribution Template** (for theories with multiple contributors)
4. **Academic Citation Template** (for proper academic attribution alongside GPL)

#### License Implementation Guidelines

Since the entire project will use GPL-3.0, all new theory implementations must adhere to the following guidelines:

1. **Academic Work**: For theories based on published academic work:
   - Use GPL-3.0 for all code components
   - Include appropriate academic citations in CITATION.md
   - Make explicit reference to the original papers and authors
   - Documentation may use CC BY-SA 4.0 which is compatible with GPL-3.0

2. **Collaborative Work**: For theories developed collaboratively:
   - Use GPL-3.0 with clear attribution to all contributors
   - Include a CONTRIBUTORS.md file listing all contributors and their roles
   - Ensure all contributors agree to the GPL-3.0 license terms

3. **Pedagogical Work**: For theories developed primarily for educational purposes:
   - Use GPL-3.0 to ensure educational derivatives remain open
   - Include clear educational notes and references
   - Consider additional educational resources under CC BY-SA 4.0

4. **Institutional Affiliations**: When contributors have institutional affiliations:
   - Ensure institutional copyright policies are compatible with GPL-3.0
   - Include appropriate institutional attribution when required
   - Address any institutional patent policies explicitly

#### Documentation Licensing

Documentation will use a compatible license:

1. **Code Comments**: Included under the same GPL-3.0 license as the code
2. **Markdown Files**: Licensed under GPL-3.0 or CC BY-SA 4.0 (GPL-compatible)
3. **Notebooks**: Jupyter notebooks should be explicitly licensed under GPL-3.0
4. **Example Files**: All examples must be GPL-3.0 to ensure users can modify them

## 3. Implementation Plan

### 3.1 Directory Structure Changes

```
model_checker/
├── LICENSE                        # Root package license (MPL 2.0 recommended)
├── CITATION.md                    # Root package citation information
├── src/
    ├── model_checker/
        ├── __init__.py            # Updated with version utility
        ├── utils.py               # Add version and license utilities
        ├── builder/
        │   └── project.py         # Updated to handle versions and licenses
        ├── theory_lib/
            ├── __init__.py        # Add version registry
            ├── LICENSE_TEMPLATE.md # Template for theory licenses
            ├── VERSION.md         # Version compatibility documentation
            ├── default/
            │   ├── __init__.py    # Updated with theory version
            │   ├── LICENSE.md     # Theory-specific license
            │   └── CITATION.md    # Theory citation information
            ├── other_theories/...
```

### 3.2 Implementation Sequence

1. **Core Version System**:
   - Update `utils.py` with version functions
   - Update `__init__.py` to use the new functions

2. **Core License System**:
   - Select and implement appropriate main license
   - Create license templates

3. **Theory Version Integration**:
   - Implement version registry in theory_lib
   - Update theory `__init__.py` files

4. **Theory License Integration**:
   - Add license files to each theory
   - Add citation files to each theory

5. **BuildProject Updates**:
   - Modify to include version and license information
   - Add license selection during project creation

6. **Documentation**:
   - Update READMEs with licensing and versioning information
   - Create developer guidelines for versioning and licensing

### 3.3 BuildProject Function Updates

The following changes should be made to `builder/project.py`:

```python
def _update_file_contents(self, project_dir):
    """Update file contents with project-specific information."""
    # Update __init__.py with current version information
    init_path = os.path.join(project_dir, "__init__.py")
    if os.path.exists(init_path):
        with open(init_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Get core package version
        model_checker_version = self._get_current_version()
        
        # Set initial theory version
        theory_version = "0.1.0"  # Initial version for all new theories
        
        # Replace version information
        content = self._update_version_info(content, model_checker_version, theory_version)
        
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    # Add license file if it doesn't exist
    license_path = os.path.join(project_dir, "LICENSE.md")
    if not os.path.exists(license_path):
        self._create_license_file(license_path)

def _update_version_info(self, content, model_checker_version, theory_version):
    """Update version information in content."""
    import re
    
    # Update model_checker_version
    mc_version_pattern = re.compile(
        r'__model_checker_version__\s*=\s*["\'].*?["\']'
    )
    content = mc_version_pattern.sub(
        f'__model_checker_version__ = "{model_checker_version}"', 
        content
    )
    
    # If no replacement was made, add it before the __all__ list
    if '__model_checker_version__' not in content:
        content = content.replace(
            '__version__ = ',
            f'__model_checker_version__ = "{model_checker_version}"\n__version__ = '
        )
    
    # Update theory version
    version_pattern = re.compile(r'__version__\s*=\s*["\'].*?["\']')
    content = version_pattern.sub(f'__version__ = "{theory_version}"', content)
    
    return content

def _create_license_file(self, license_path):
    """Create a license file for the theory."""
    # Get license template
    license_template = self._get_license_template()
    
    # Write license file
    with open(license_path, 'w', encoding='utf-8') as f:
        f.write(license_template)
        
def _get_license_template(self):
    """Return the GPL-3.0 license template for new theories.
    
    Returns:
        str: The GPL-3.0 license template text with academic attribution
    """
    year = datetime.datetime.now().year
    
    return f"""# GNU General Public License v3.0

Copyright (c) {year} [Author Name]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

## Academic Attribution

If you use this theory implementation in academic work, please cite:

[Author]. ({year}). [Theory Name]: A semantic theory implementation for the
ModelChecker framework.

## Theory Implementation Notes

This theory implementation is part of the ModelChecker framework,
which is also licensed under the GNU General Public License v3.0.
All derivative works must maintain this license to ensure the 
continued openness of this software.

For more detailed information about the theory's mathematical foundations,
please see the accompanying CITATION.md file.
"""
```

## 4. API and Function Specifications

### 4.1 Version Utility Functions

```python
def get_model_checker_version():
    """Get the current model_checker package version.
    
    Returns:
        str: Current version as defined in pyproject.toml or "unknown"
    """
    pass

def get_theory_version(theory_name):
    """Get the version of a specific theory.
    
    Args:
        theory_name (str): Name of the theory
        
    Returns:
        str: Theory version or "unknown" if not found
        
    Raises:
        ValueError: If theory_name is not a valid registered theory
    """
    pass

def check_theory_compatibility(theory_name):
    """Check if a theory is compatible with the current model_checker version.
    
    Args:
        theory_name (str): Name of the theory
        
    Returns:
        bool: True if compatible, False otherwise
        
    Raises:
        ValueError: If theory_name is not a valid registered theory
    """
    pass
```

### 4.2 License Utility Functions

```python
def get_license_text(license_type="MPL-2.0", author_info=None):
    """Get license text for a specified license type.
    
    Args:
        license_type (str): Type of license (MPL-2.0, MIT, etc.)
        author_info (dict): Author information (name, email, year)
        
    Returns:
        str: License text with author information filled in
    """
    pass

def add_license_to_theory(theory_name, license_type="MPL-2.0", author_info=None):
    """Add a license file to a theory directory.
    
    Args:
        theory_name (str): Name of the theory
        license_type (str): Type of license (MPL-2.0, MIT, etc.)
        author_info (dict): Author information (name, email, year)
        
    Returns:
        bool: True if license was added successfully, False otherwise
    """
    pass
```

## 5. Theory Template Changes

### 5.1 Updated `__init__.py` Template

```python
"""[Theory Name] - A semantic theory implementation for the ModelChecker framework.

[Description of theory and key features]

Classes:
    [TheoryName]Semantics: Configures the semantic framework and evaluation rules
    [TheoryName]Proposition: Represents and evaluates logical formulas
    [TheoryName]ModelStructure: Manages the model's state space and relations
    
Operators:
    [theory_name]_operators: Dictionary of logical operators

Version Information:
    __version__: Theory-specific version
    __model_checker_version__: Version of model_checker this was built with
"""

# Import specific items from semantic
from .semantic import (
    Semantics,
    Proposition,
    ModelStructure,
)

# Import operators
from .operators import theory_operators

# Version information
__version__ = "0.1.0"  # Theory version
__model_checker_version__ = "0.9.20"  # ModelChecker version this was built with

# Define the public API
__all__ = [
    "Semantics",
    "Proposition",
    "ModelStructure",
    "theory_operators",
    "__version__",
    "__model_checker_version__",
]
```

## 6. Testing and Validation

### 6.1 Test Cases

1. **Version Extraction Tests**:
   - Test core package version is correctly identified
   - Test theory versions are correctly identified

2. **BuildProject Tests**:
   - Test version information is correctly included in new projects
   - Test license files are correctly created

3. **Compatibility Tests**:
   - Test compatibility checking functions

### 6.2 Manual Validation Checklist

- [ ] Version information is correctly displayed in `model-checker --version`
- [ ] Theory version is correctly displayed in module docstrings
- [ ] License files are correctly created in new theory projects
- [ ] Project templates include all required files with correct versions

## 7. Documentation Updates

### 7.1 Updated READMEs

Add sections on versioning and licensing to:

- Main README.md
- theory_lib/README.md
- Each theory's README.md

### 7.2 Developer Guidelines

Create a comprehensive developer guide that explains:

- How to version theories
- When to increment version numbers
- How licensing works
- Citation requirements

## 8. Migration Plan

1. **Build Version Registry**:
   - First, implement the version registry in theory_lib/__init__.py
   - Add version information to each theory

2. **Update BuildProject**:
   - Modify BuildProject to include version information
   - Test with new project creation

3. **Add License Files**:
   - Create license templates
   - Add license files to each theory
   - Update main license if needed

4. **Documentation Updates**:
   - Update all documentation with version and license information
   - Create migration guide for theory authors

## 9. License Compatibility Considerations

When integrating theories with different licenses, compatibility must be considered:

### 9.1 License Compatibility Matrix

| License      | Can be combined with                                             | Patent Protection Level |
|--------------|------------------------------------------------------------------|-----------------------|
| MIT          | MIT, Apache 2.0, LGPL, GPL, MPL 2.0                             | None (implicit only) |
| Apache 2.0   | MIT, Apache 2.0, MPL 2.0 (caution with GPL)                     | Strong explicit grant |
| MPL 2.0      | MIT, Apache 2.0, MPL 2.0, LGPL, GPL (file-level separation)     | Moderate with defensive termination |
| LGPL v3      | MIT, LGPL, MPL 2.0 (as library), GPL                           | Strong (same as GPL) |
| GPL v3       | MIT, LGPL, MPL 2.0 (if GPL is the final license), GPL          | Strong with anti-tivoization |
| BSL          | Depends on the license it converts to after change date         | Variable (commercial initially) |

#### 9.1.1 Understanding Patent Grants in Open Source Licenses

**What Patent Grants Mean for Contributors and Users:**

When a contributor grants patent licenses covering their contributions, it means:

1. **Permission to Practice**: The contributor is explicitly giving permission to users of the software to practice (use, make, sell, offer to sell, import) any patented inventions that are embodied in their code contributions.

2. **Legal Protection**: Without this grant, even though a contributor shared their code under an open source license, they could potentially sue users for patent infringement if the code implements a technique they've patented.

3. **Scope Limitations**: The patent grant typically only covers the specific contributions made by that contributor, not their entire patent portfolio.

4. **Implementation vs. Concept**: The patent grant covers the implementation contributed, not necessarily broader applications of the underlying concepts.

**Example Scenario:**

1. Professor A contributes code to ModelChecker that implements a novel algorithm for which they've filed a patent application
2. Without a patent grant:
   - Users could use the specific code (copyright license)
   - Professor A could still sue users for patent infringement when they run the software
3. With a patent grant (e.g., Apache 2.0 or MPL 2.0):
   - Users get both copyright permission and patent permission
   - Professor A cannot sue users for patent infringement for using the contributed code

**Institutional Implications:**

1. **University Policies**: Many universities have specific policies about how faculty can license patents in open source contributions
2. **Industry Contributors**: Corporate contributors need to ensure they have authority to make patent grants
3. **Defensive Value**: Patent grants protect the project ecosystem from potential "submarine patents" by contributors

#### 9.1.2 Patent Compatibility Considerations

When combining software with different licenses, special attention should be paid to patent provisions:

1. **Upgrading Patent Protection**: When combining MIT-licensed code with Apache or MPL code, consider relicensing the MIT portions to match the stronger patent protections
   
2. **Defensive Termination Compatibility**: Apache 2.0 and MPL 2.0 have different defensive termination provisions that may interact in complex ways
   
3. **GPL Integration**: When integrating GPL code with Apache code, the resulting work likely needs to be under GPL, which may affect patent rights
   
4. **Academic Patent Concerns**: Academic theories may have institutional patent policies that need to be considered alongside the software license

5. **Contribution Agreements**: For projects with many contributors, a Contributor License Agreement (CLA) can standardize patent grants beyond what's in the open source license

### 9.2 Handling Mixed-License Theories

When a project uses theories with different licenses:

1. **Proper Attribution**: All licenses must be properly attributed in documentation
2. **License Boundaries**: Clearly mark files with their respective licenses
3. **Compatibility Check**: Ensure the licenses are compatible for the intended use
4. **User Notification**: Clearly inform users about license requirements

### 9.3 Integrating Theories with Incompatible Licenses

If theories have potentially incompatible licenses:

1. **API Isolation**: Use clean API boundaries and avoid direct code mixing
2. **Module Separation**: Maintain separation between differently licensed code
3. **Alternative Implementation**: Consider creating a compatible implementation
4. **License Upgrade**: Consider contacting the theory author for relicensing

## 10. Conclusion

This implementation plan provides a systematic approach to adding versioning and licensing to the ModelChecker framework. It ensures that:

1. The core package maintains a global version while theories maintain their own versions
2. License requirements are clearly specified and properly enforced
3. New theories created with BuildProject automatically include the correct version and license information
4. Documentation is updated to reflect the new versioning and licensing systems
5. Theory authors have clear guidelines for selecting appropriate licenses
6. License compatibility is maintained across the project

The proposed MPL 2.0 license provides an appropriate balance between open-source requirements and permissiveness, ensuring that derivative works maintain openness while allowing flexibility for theory authors to specify their own attribution requirements.

By implementing this plan, the ModelChecker framework will have a robust system for tracking versions and managing licenses that:

1. Protects academic attribution and intellectual property rights
2. Encourages contribution and collaboration
3. Provides clarity for users regarding usage requirements
4. Maintains compatibility with academic and commercial use cases
5. Creates a sustainable model for ongoing theory development