# Documentation Revision TODO List

This file tracks the systematic revision of all documentation files in the ModelChecker repository to ensure consistency, accuracy, minimal redundancy, and working cross-links.

**Content Preservation Policy**: During revision, preserve all valuable content while reducing redundancy. The goal is to improve organization, clarity, and accessibility without losing important information. Consolidate duplicate material and restructure for better flow, but maintain comprehensive coverage of each topic.

## Revision Approach: Topic-Based Bottom-Up

**Strategy**: Organize documentation revision by natural topic areas (theories, components, framework), working from deepest to shallowest within each topic. This ensures accuracy propagates upward while maintaining topical coherence and focus.

### Topic Organization Principle
1. Complete each topic area from deepest level to topic root
2. Move to next topic only after completing previous topic entirely
3. Within each topic, work from code-adjacent to overview documentation
4. Finish all individual topics before proceeding to framework-level documentation

## Revision Process

1. **Phase 1: Topic Mapping** - Organize all documentation by natural topic areas and depth
2. **Phase 2: Theory Topics** - Complete all theory documentation (logos → exclusion → imposition → bimodal)
3. **Phase 3: Component Topics** - Complete all component documentation (builder → iterate → jupyter → settings)
4. **Phase 4: Library Integration** - Complete theory_lib and core model_checker documentation
5. **Phase 5: Framework Documentation** - Complete docs/, tests/, and framework-level documentation
6. **Phase 6: Root Documentation** - Complete root-level documentation
7. **Phase 7: Cross-link Verification** - Verify all links work correctly

## Status Legend
- ⬜ Not started
- 🟨 In progress  
- ✅ Completed
- ⭐ Exemplary (use as reference)
- ❌ Needs major revision

## Phase 1: Topic Mapping Complete

Documentation organized by natural topic areas with clear depth hierarchies within each topic.

## Phase 2: Theory Topics (Bottom-Up by Theory)

**Status**: ⬜ Not Started

### Topic 2.1: Logos Theory (`/Code/src/model_checker/theory_lib/logos/`)

**Approach**: Start with deepest subtheory components, work up to logos root documentation.

#### Level 2.1.4 (Deepest): Individual Subtheories
- ✅ `subtheories/extensional/README.md` - Extensional operators
- ✅ `subtheories/extensional/tests/README.md` - Extensional test documentation
- ✅ `subtheories/modal/README.md` - Modal operators  
- ✅ `subtheories/modal/tests/README.md` - Modal test documentation
- ✅ `subtheories/constitutive/README.md` - Constitutive relations
- ✅ `subtheories/constitutive/tests/README.md` - Constitutive test documentation
- ✅ `subtheories/counterfactual/README.md` - Counterfactual operators
- ✅ `subtheories/counterfactual/tests/README.md` - Counterfactual test documentation
- ✅ `subtheories/relevance/README.md` - Relevance logic
- ✅ `subtheories/relevance/tests/README.md` - Relevance test documentation

#### Level 2.1.3: Subtheory Integration
- ✅ `subtheories/README.md` - Subtheories overview and coordination

#### Level 2.1.2: Theory Support Documentation
- ✅ `docs/API_REFERENCE.md` - Logos API reference
- ✅ `docs/ARCHITECTURE.md` - Logos technical architecture  
- ✅ `docs/ITERATE.md` - Logos model iteration
- ✅ `docs/SETTINGS.md` - Logos configuration
- ✅ `docs/USER_GUIDE.md` - Logos user guide
- ✅ `notebooks/README.md` - Logos notebooks guide
- ✅ `tests/README.md` - Logos test documentation
- ✅ `docs/README.md` - Logos documentation hub

#### Level 2.1.1: Theory Root
- ✅ `README.md` - Logos theory overview

### Topic 2.2: Exclusion Theory (`/Code/src/model_checker/theory_lib/exclusion/`)

**Approach**: Start with archive components, work up to exclusion root documentation.

#### Level 2.2.4 (Deepest): Archive Components
- ✅ `archive/strategy1_multi/README.md` - Multi-witness strategy documentation
- ✅ `archive/strategy2_witness/README.md` - Witness predicate strategy documentation

#### Level 2.2.3: Implementation History
- ✅ `history/IMPLEMENTATION_STORY.md` - Development narrative
- ✅ `history/LESSONS_LEARNED.md` - Implementation insights
- ✅ `history/STRATEGIES.md` - Implementation strategies

#### Level 2.2.2: Theory Support Documentation  
- ✅ `docs/API_REFERENCE.md` - Exclusion API reference
- ✅ `docs/ARCHITECTURE.md` - Exclusion technical details
- ✅ `docs/DATA.md` - Test data analysis
- ✅ `docs/ITERATE.md` - Exclusion model iteration
- ✅ `docs/SETTINGS.md` - Exclusion configuration
- ✅ `docs/USER_GUIDE.md` - Exclusion user guide
- ✅ `notebooks/README.md` - Exclusion notebooks guide
- ✅ `tests/README.md` - Exclusion test documentation
- ✅ `docs/README.md` - Exclusion documentation hub

#### Level 2.2.1: Theory Root
- ✅ `README.md` - Exclusion theory overview

### Topic 2.3: Imposition Theory (`/Code/src/model_checker/theory_lib/imposition/`)

**Approach**: Work from support documentation to theory root.

#### Level 2.3.2: Theory Support Documentation
- ✅ `docs/API_REFERENCE.md` - Imposition API reference
- ✅ `docs/ARCHITECTURE.md` - Imposition technical details
- ✅ `docs/ITERATE.md` - Imposition model iteration
- ✅ `docs/SETTINGS.md` - Imposition configuration  
- ✅ `docs/USER_GUIDE.md` - Imposition user guide
- ✅ `notebooks/README.md` - Imposition notebooks guide
- N/A `tests/README.md` - No test documentation file exists
- ✅ `docs/README.md` - Imposition documentation hub

#### Level 2.3.1: Theory Root
- ✅ `README.md` - Imposition theory overview

### Topic 2.4: Bimodal Theory (`/Code/src/model_checker/theory_lib/bimodal/`)

**Approach**: Work from support documentation to theory root.

#### Level 2.4.2: Theory Support Documentation
- ⬜ `docs/API_REFERENCE.md` - Bimodal API reference
- ⬜ `docs/ARCHITECTURE.md` - Bimodal technical details
- ⬜ `docs/ITERATE.md` - Bimodal model iteration
- ⬜ `docs/SETTINGS.md` - Bimodal configuration
- ⬜ `docs/USER_GUIDE.md` - Bimodal user guide
- ⬜ `tests/README.md` - Bimodal test documentation
- ⬜ `docs/README.md` - Bimodal documentation hub

#### Level 2.4.1: Theory Root
- ⬜ `README.md` - Bimodal theory overview

## Phase 3: Component Topics (Bottom-Up by Component)

**Status**: ⬜ Not Started

### Topic 3.1: Builder Component (`/Code/src/model_checker/builder/`)

**Approach**: Work from test documentation to component root.

#### Level 3.1.2: Component Support Documentation
- ⬜ `tests/README.md` - Builder test documentation (if exists)

#### Level 3.1.1: Component Root
- ⬜ `README.md` - Builder component overview

### Topic 3.2: Iterate Component (`/Code/src/model_checker/iterate/`)

**Approach**: Work from test documentation to component root.

#### Level 3.2.2: Component Support Documentation
- ⬜ `tests/README.md` - Iterate test documentation (if exists)

#### Level 3.2.1: Component Root
- ⬜ `README.md` - Iterate component overview

### Topic 3.3: Jupyter Component (`/Code/src/model_checker/jupyter/`)

**Approach**: Work from debug documentation to component root.

#### Level 3.3.2: Component Support Documentation
- ⬜ `debug/DEBUGGING.md` - Jupyter debugging methodology
- ⬜ `debug/README.md` - Jupyter debugging guide

#### Level 3.3.1: Component Root
- ⬜ `README.md` - Jupyter component overview

### Topic 3.4: Settings Component (`/Code/src/model_checker/settings/`)

**Approach**: Work from test documentation to component root.

#### Level 3.4.2: Component Support Documentation
- ⬜ `tests/README.md` - Settings test documentation (if exists)

#### Level 3.4.1: Component Root
- ⬜ `README.md` - Settings component overview

## Phase 4: Library Integration Topics

**Status**: ⬜ Not Started

### Topic 4.1: Theory Library (`/Code/src/model_checker/theory_lib/`)

**Approach**: Complete theory library aggregation documentation after all individual theories are complete.

#### Level 4.1.2: Library Support Documentation
- ⬜ `docs/USAGE_GUIDE.md` - Theory library usage patterns
- ⬜ `docs/CONTRIBUTING.md` - Theory contribution guide
- ⬜ `docs/THEORY_ARCHITECTURE.md` - Architecture patterns
- ⬜ `tests/README.md` - Theory testing framework
- ⬜ `docs/README.md` - Theory library documentation hub

#### Level 4.1.1: Library Root
- ⬜ `README.md` - Theory library overview

### Topic 4.2: Core API (`/Code/src/model_checker/`)

**Approach**: Complete core API documentation after all components are complete.

#### Level 4.2.1: API Root
- ⬜ `README.md` - ModelChecker API documentation

## Phase 5: Framework Documentation Topics

**Status**: ⬜ Not Started

### Topic 5.1: Development Documentation (`/Code/docs/`)

**Approach**: Work from individual guides to development hub.

#### Level 5.1.2: Development Support Documentation  
- ⬜ `ARCHITECTURE.md` - System architecture
- ⬜ `DEVELOPMENT.md` - Development workflow
- ⬜ `INSTALLATION.md` - Installation guide
- ⬜ `STYLE_GUIDE.md` - Python style guide
- ⬜ `TESTS.md` - Testing methodology

#### Level 5.1.1: Development Hub
- ⬜ `README.md` - Development documentation hub

### Topic 5.2: Integration Testing (`/Code/tests/`)

**Approach**: Complete integration test documentation.

#### Level 5.2.1: Testing Root
- ⬜ `README.md` - Integration test suite overview

## Phase 6: Root Documentation Topics

**Status**: ⬜ Not Started

### Topic 6.1: Examples Documentation (`/Code/examples/`)

**Approach**: Complete example documentation.

#### Level 6.1.1: Examples Root
- ⬜ `README.md` - Examples overview
- ⬜ `README_jupyter.md` - Jupyter examples

### Topic 6.2: Notebooks Documentation (`/Code/notebooks/`)

**Approach**: Complete notebook documentation.

#### Level 6.2.1: Notebooks Root
- ⬜ `README.md` - Notebooks overview

### Topic 6.3: Root Package Documentation (`/Code/`)

**Approach**: Complete root-level package documentation.

#### Level 6.3.1: Package Root
- ⬜ `README.md` - Package overview (PyPI special case)
- ⬜ `ARCHITECTURE.md` - System architecture overview
- ⬜ `CLAUDE.md` - AI assistant guide
- ⬜ `MAINTENANCE.md` - Coding and documentation standards

## Phase 7: Cross-link Verification

**Status**: ⬜ Not Started

### Link Categories to Check
- Internal repository links (relative paths)
- Links to code files
- Links to external resources  
- Links between theories and components
- Navigation links (forward/backward)
- Table of contents links

### Verification Approach
1. **Topic-Internal Links**: Verify links within each completed topic
2. **Cross-Topic Links**: Verify links between completed topics
3. **Framework Links**: Verify framework-level navigation
4. **External Links**: Verify external resource links

## Topic Completion Rules

### Within-Topic Rules
1. **Complete Deepest Level First**: Finish all Level X.Y.4 before starting X.Y.3
2. **Verify Accuracy**: Check each document against actual code/implementation
3. **Maintain Topic Focus**: Stay within topic boundaries until topic is complete
4. **Update Cross-References**: Ensure internal topic links are accurate

### Between-Topic Rules  
1. **Complete Full Topic**: Finish entire topic (all levels) before moving to next topic
2. **Topic Dependencies**: Theories complete before components, components before integration
3. **Propagate Changes**: Update cross-topic references as topics are completed

## Summary Statistics

- **Total Topics**: 14 topic areas
- **Theory Topics**: 4 (logos, exclusion, imposition, bimodal)
- **Component Topics**: 4 (builder, iterate, jupyter, settings)  
- **Integration Topics**: 2 (theory_lib, model_checker)
- **Framework Topics**: 2 (docs, tests)
- **Root Topics**: 2 (examples/notebooks, package root)

## Topic Progress Tracking

- **Phase 2 (Theories)**: 🟨 3/4 topics complete (Logos ✅, Exclusion ✅, Imposition ✅)
- **Phase 3 (Components)**: ⬜ 0/4 topics complete  
- **Phase 4 (Integration)**: ⬜ 0/2 topics complete
- **Phase 5 (Framework)**: ⬜ 0/2 topics complete
- **Phase 6 (Root)**: ⬜ 0/2 topics complete

## Notes

- Work one topic at a time from deepest to shallowest within topic
- Complete entire topic before moving to next topic  
- Verify accuracy against actual implementation at each level
- Maintain MAINTENANCE.md standards throughout all topics
- Remember `/Code/README.md` is special for PyPI display
