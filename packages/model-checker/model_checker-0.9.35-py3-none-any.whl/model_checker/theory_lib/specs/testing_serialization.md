# Serialization Testing Framework

This document outlines the test framework for validating the new serialization approach implemented in Phase 9.

## Test Components

The `test_serialization.py` script provides comprehensive validation of the serialization approach:

1. **Serialization Tests**: Verify that model structures from all theories can be properly serialized
   - Directly runs each example from each theory
   - Creates a printable representation of the model
   - Verifies the representation can be serialized to JSON and back
   - Checks that key information is present in the representation
   - Compares original printing with serialization-based printing

2. **dev_cli.py Integration Tests**: Verify that examples run correctly through process isolation
   - Executes the dev_cli.py script with example files from each theory
   - Validates successful execution without errors
   - Ensures models are correctly displayed

3. **Performance Tests**: Compare direct execution vs. process-based execution
   - Measures execution time for both approaches
   - Calculates speedup ratios
   - Reports average performance across theories

## Running the Tests

```bash
# Basic test run
./test_serialization.py

# Test specific theories
./test_serialization.py --theories default bimodal

# Verbose output
./test_serialization.py -v

# Only run serialization tests
./test_serialization.py --serialization-only

# Only run dev_cli.py integration tests
./test_serialization.py --dev-cli-only

# Only run performance tests
./test_serialization.py --performance
```

## Expected Results

1. Serialization tests should show all examples can be properly serialized with their key information preserved.
2. dev_cli.py integration tests should run without errors for all examples.
3. Performance tests should show that process-based execution does not significantly slow down example execution.

## Validation Criteria

The following criteria determine if the serialization approach is successful:

1. **Completeness**: All model structures across all theories can be serialized
2. **Correctness**: All key information is preserved after serialization
3. **Compatibility**: The serialized representations work with the printing functions
4. **Reliability**: All examples run successfully through dev_cli.py
5. **Performance**: Process isolation doesn't significantly impact performance

## Remaining Test Tasks

Initial testing of the implementation has confirmed that the serialization issues with ctypes objects exist as expected. The following tasks remain to complete the testing phase:

### 1. Direct Example Testing

We need to test specific examples directly through the proper channels to verify behavior:

- **Select Test Examples**: Choose 2-3 examples from each theory (default, bimodal, exclusion, imposition)
- **Run Through dev_cli.py**: Use dev_cli.py to run these examples with both the original and new implementation
- **Compare Outputs**: Ensure the printed model details match between implementations
- **Verify Z3 Object Handling**: Confirm that Z3 objects are properly handled in the serialization process

### 2. Edge Case Testing

To ensure robustness, we need to test edge cases:

- **Large Models**: Test examples with many worlds to test memory usage
- **Complex Relations**: Test examples with complex fusion/temporal relations
- **Error Handling**: Test examples that produce errors to verify proper propagation

### 3. BuildModule Integration Testing

Verify that our serialization approach works correctly with BuildModule:

- **Multiple Example Test**: Test running multiple examples together
- **Order Preservation**: Ensure results are displayed in the original submission order
- **Parallel Execution**: Test parallel execution of examples

### 4. Performance Testing

Measure the impact of our approach on performance:

- **Execution Time**: Measure execution time with and without process isolation
- **Serialization Overhead**: Quantify the overhead of serialization/deserialization
- **Parallel Benefits**: Measure speedup from parallel execution on multi-core systems

## Troubleshooting

If tests fail, look for these common issues:

1. **JSON Serialization Failures**: 
   - Objects that cannot be serialized to JSON
   - Custom types that need special handling

2. **Missing Information**:
   - Theory-specific details not being extracted
   - Z3 object values not being captured

3. **Process Isolation Issues**:
   - Communication failures between processes
   - Errors in transmitting large data structures
   - Memory issues with multiple processes

4. **Printing Differences**:
   - Formatting changes between original and serialized
   - Missing details in serialized representation

## Next Steps

After completing the comprehensive testing in Phase 6, we will proceed to:

1. **Phase 7: Z3 Context Management Cleanup**
   - Remove remaining redundant Z3 context calls
   - Add deprecation warnings for direct Z3ContextManager usage
   - Update documentation on recommended approaches

2. **Phase 10: Optimization and Finalization**
   - Optimize serialization performance
   - Implement dynamic worker pool sizing
   - Reduce memory usage
   - Complete documentation and examples