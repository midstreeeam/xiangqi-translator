#!/usr/bin/env python3
"""
Comprehensive test runner for Xiangqi Translator.
Runs all test suites and provides detailed reporting for CI/CD integration.
"""

import sys
import os
import unittest
import time
import subprocess

# Add the parent src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def run_comprehensive_tests():
    """Run the comprehensive test suite."""
    print("=" * 80)
    print("RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    # Import and run the comprehensive tests
    from test_comprehensive import run_all_tests
    
    start_time = time.time()
    result = run_all_tests()
    end_time = time.time()
    
    duration = end_time - start_time
    
    print(f"\nComprehensive tests completed in {duration:.3f} seconds")
    return result


def run_ambiguous_move_tests():
    """Run the ambiguous move tests."""
    print("\n" + "=" * 80)
    print("RUNNING AMBIGUOUS MOVE TESTS")
    print("=" * 80)
    
    try:
        # Run the ambiguous test script
        result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), "test_ambiguous_moves.py")
        ], capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        print(f"Ambiguous move tests: {'PASS' if success else 'FAIL'}")
        return success
        
    except subprocess.TimeoutExpired:
        print("✗ Ambiguous move tests timed out")
        return False
    except Exception as e:
        print(f"✗ Error running ambiguous move tests: {e}")
        return False


def run_examples():
    """Run the examples to ensure they work."""
    print("\n" + "=" * 80)
    print("RUNNING EXAMPLES")
    print("=" * 80)
    
    try:
        # Run the basic usage examples
        examples_path = os.path.join(os.path.dirname(__file__), "..", "examples", "basic_usage.py")
        result = subprocess.run([
            sys.executable, 
            examples_path
        ], capture_output=True, text=True, timeout=60)
        
        # Don't print all the output as it's quite verbose
        print("Examples output (first 1000 chars):")
        print(result.stdout[:1000])
        if len(result.stdout) > 1000:
            print("... (output truncated)")
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        print(f"\nExamples execution: {'PASS' if success else 'FAIL'}")
        return success
        
    except subprocess.TimeoutExpired:
        print("✗ Examples timed out")
        return False
    except Exception as e:
        print(f"✗ Error running examples: {e}")
        return False


def run_basic_import_test():
    """Test that basic imports work correctly."""
    print("\n" + "=" * 80)
    print("RUNNING BASIC IMPORT TEST")
    print("=" * 80)
    
    try:
        # Test main imports
        from xiangqi_translator import (
            XiangqiBoard, 
            XiangqiTranslator, 
            translate_from_fen,
            get_initial_board,
            validate_move,
            get_legal_moves,
            Color,
            PieceType,
            Position
        )
        
        print("✓ Main imports successful")
        
        # Test basic functionality
        board = get_initial_board()
        print(f"✓ Initial board created: {board.to_fen()[:50]}...")
        
        result = translate_from_fen(board.to_fen(), "炮二平五")
        if result.success:
            print(f"✓ Basic translation works: {result.iccs_move}")
        else:
            print(f"✗ Basic translation failed: {result.error_message}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Basic functionality error: {e}")
        return False


def run_performance_benchmark():
    """Run basic performance benchmarks."""
    print("\n" + "=" * 80)
    print("RUNNING PERFORMANCE BENCHMARKS")
    print("=" * 80)
    
    try:
        from xiangqi_translator import translate_from_fen, get_initial_board
        
        board = get_initial_board()
        fen = board.to_fen()
        
        # Benchmark translation speed
        num_iterations = 1000
        start_time = time.time()
        
        for _ in range(num_iterations):
            translate_from_fen(fen, "炮二平五")
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / num_iterations
        
        print(f"Translation performance ({num_iterations} iterations):")
        print(f"  Total time: {total_time:.3f} seconds")
        print(f"  Average time: {avg_time * 1000:.3f} ms per translation")
        print(f"  Translations per second: {1.0 / avg_time:.0f}")
        
        # Performance thresholds
        if avg_time > 0.01:  # 10ms threshold
            print("⚠️  Warning: Translation speed slower than expected")
            return False
        else:
            print("✓ Performance within acceptable limits")
            return True
            
    except Exception as e:
        print(f"✗ Performance benchmark error: {e}")
        return False


def run_memory_usage_test():
    """Basic memory usage test."""
    print("\n" + "=" * 80)
    print("RUNNING MEMORY USAGE TEST")
    print("=" * 80)
    
    try:
        import psutil
        import gc
        
        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Initial memory usage: {initial_memory:.1f} MB")
        
        # Import and use the library
        from xiangqi_translator import translate_from_fen, get_initial_board
        
        board = get_initial_board()
        fen = board.to_fen()
        
        # Perform many operations
        for _ in range(1000):
            translate_from_fen(fen, "炮二平五")
        
        gc.collect()  # Force garbage collection
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Final memory usage: {final_memory:.1f} MB")
        print(f"Memory increase: {memory_increase:.1f} MB")
        
        # Memory threshold - shouldn't increase by more than 50MB
        if memory_increase > 50:
            print("⚠️  Warning: Significant memory increase detected")
            return False
        else:
            print("✓ Memory usage within acceptable limits")
            return True
            
    except ImportError:
        print("⚠️  psutil not available, skipping memory test")
        return True
    except Exception as e:
        print(f"✗ Memory test error: {e}")
        return False


def generate_test_report(results):
    """Generate a comprehensive test report."""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TEST REPORT")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"Total test suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {(passed_tests / total_tests) * 100:.1f}%")
    
    print("\nDetailed Results:")
    print("-" * 50)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        icon = "✓" if result else "✗"
        print(f"{icon} {test_name:<30} {status}")
    
    overall_success = all(results.values())
    print(f"\nOVERALL RESULT: {'PASS' if overall_success else 'FAIL'}")
    
    return overall_success


def main():
    """Run all tests and generate report."""
    print("XIANGQI TRANSLATOR - COMPREHENSIVE TEST RUNNER")
    print("Version: 1.0.0")
    print("=" * 80)
    
    start_time = time.time()
    
    # Dictionary to store test results
    results = {}
    
    # Run all test suites
    try:
        results['Basic Import Test'] = run_basic_import_test()
        results['Comprehensive Tests'] = run_comprehensive_tests().testsRun > 0 and len(run_comprehensive_tests().failures) == 0 and len(run_comprehensive_tests().errors) == 0
        results['Ambiguous Move Tests'] = run_ambiguous_move_tests()
        results['Examples Execution'] = run_examples()
        results['Performance Benchmark'] = run_performance_benchmark()
        results['Memory Usage Test'] = run_memory_usage_test()
        
    except KeyboardInterrupt:
        print("\n✗ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error during testing: {e}")
        sys.exit(1)
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    print(f"\nTotal test duration: {total_duration:.3f} seconds")
    
    # Generate comprehensive report
    overall_success = generate_test_report(results)
    
    # Exit with appropriate code for CI/CD
    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main() 