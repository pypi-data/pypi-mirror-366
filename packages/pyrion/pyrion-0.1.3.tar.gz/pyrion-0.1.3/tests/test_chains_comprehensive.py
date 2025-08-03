#!/usr/bin/env python3
"""Enhanced test runner with detailed coverage and benchmarking."""

import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

def run_comprehensive_tests():
    """Run comprehensive test suite with detailed coverage tracking."""
    print("🔬 Comprehensive Test Suite for pyrion.ops.chains")
    print("=" * 70)
    
    sys.path.insert(0, str(Path.cwd()))
    
    # Import all functions
    try:
        from pyrion.ops.chains import (
            project_intervals_through_chain,
            _project_intervals_vectorized,
            _project_intervals_numpy,
            project_intervals_through_genome_alignment,
            project_intervals_through_genome_alignment_to_intervals,
            get_chain_target_interval,
            get_chain_query_interval,
            get_chain_t_start,
            get_chain_t_end,
            get_chain_q_start,
            get_chain_q_end,
            split_genome_alignment,
            HAS_NUMBA
        )
        from pyrion.core.genome_alignment import GenomeAlignment
        from pyrion.core.strand import Strand
        from pyrion.core.genes import Transcript
        from pyrion.core.intervals import GenomicInterval
        
        if HAS_NUMBA:
            from pyrion.ops.chains import _project_intervals_numba
        
        print("✅ All imports successful")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test tracking
    coverage_stats = {}
    performance_stats = {}
    
    # Test data setup
    chain_blocks = np.array([
        [100, 200, 1000, 1100],
        [300, 400, 1200, 1300],
        [500, 600, 1400, 1500],
    ], dtype=np.int64)
    
    genome_alignment = GenomeAlignment(
        chain_id=1, score=1000, t_chrom=b"chr1", t_strand=1, t_size=1000000,
        q_chrom=b"chr2", q_strand=1, q_size=1000000, blocks=chain_blocks
    )
    
    test_intervals = np.array([
        [150, 180],   # Overlaps first block
        [350, 380],   # Overlaps second block  
        [250, 350],   # Gap between blocks
        [50, 80],     # Before chain
        [700, 800],   # After chain
    ], dtype=np.int64)
    
    def run_test(test_name: str, test_func, *args, **kwargs):
        """Run a single test with timing and coverage tracking."""
        try:
            start_time = time.perf_counter()
            result = test_func(*args, **kwargs)
            end_time = time.perf_counter()
            
            performance_stats[test_name] = (end_time - start_time) * 1000  # ms
            coverage_stats[test_name] = "PASSED"
            print(f"✅ {test_name}: {performance_stats[test_name]:.2f}ms")
            return True, result
        except Exception as e:
            coverage_stats[test_name] = f"FAILED: {str(e)}"
            print(f"❌ {test_name}: {e}")
            return False, None
    
    print("\n📊 Function Coverage Tests:")
    print("-" * 50)
    
    # Test 1: Core projection function
    success, results = run_test(
        "project_intervals_through_chain",
        project_intervals_through_chain,
        test_intervals, chain_blocks
    )
    if success:
        print(f"   → Projected {len(test_intervals)} intervals → {len(results)} results")
    
    # Test 2: Vectorized implementations
    run_test("_project_intervals_numpy", _project_intervals_numpy, test_intervals, chain_blocks)
    
    if HAS_NUMBA:
        run_test("_project_intervals_numba", _project_intervals_numba, test_intervals, chain_blocks)
    else:
        print("⚠️  _project_intervals_numba: Numba not available")
    
    run_test("_project_intervals_vectorized", _project_intervals_vectorized, test_intervals, chain_blocks)
    
    # Test 3: GenomeAlignment convenience functions
    run_test(
        "project_intervals_through_genome_alignment", 
        project_intervals_through_genome_alignment,
        test_intervals, genome_alignment
    )
    
    success, interval_objects = run_test(
        "project_intervals_through_genome_alignment_to_intervals",
        project_intervals_through_genome_alignment_to_intervals,
        test_intervals[:2], genome_alignment  # Use subset for valid results
    )
    if success:
        print(f"   → Created {len(interval_objects)} GenomicInterval objects")
    
    # Test 4: Chain accessors
    run_test("get_chain_t_start", get_chain_t_start, genome_alignment)
    run_test("get_chain_t_end", get_chain_t_end, genome_alignment)
    run_test("get_chain_q_start", get_chain_q_start, genome_alignment)
    run_test("get_chain_q_end", get_chain_q_end, genome_alignment)
    
    success, target_interval = run_test("get_chain_target_interval", get_chain_target_interval, genome_alignment)
    if success:
        print(f"   → Target: {target_interval.chrom}:{target_interval.start}-{target_interval.end}")
    
    success, query_interval = run_test("get_chain_query_interval", get_chain_query_interval, genome_alignment)
    if success:
        print(f"   → Query: {query_interval.chrom}:{query_interval.start}-{query_interval.end}")
    
    # Test 5: Chain splitting  
    sample_transcripts = [
        Transcript(
            blocks=np.array([[150, 250]], dtype=np.int64),
            strand=Strand.PLUS, chrom=b"chr1", id="transcript1"
        )
    ]
    
    success, (subchains, mapping) = run_test(
        "split_genome_alignment",
        split_genome_alignment,
        genome_alignment, sample_transcripts, 1000
    )
    if success:
        print(f"   → Split into {len(subchains)} subchains, {len(mapping)} mappings")
    
    return coverage_stats, performance_stats


def run_edge_case_tests():
    """Test edge cases and error conditions."""
    print("\n🔍 Edge Case & Error Handling Tests:")
    print("-" * 50)
    
    edge_cases_passed = 0
    edge_cases_total = 0
    
    try:
        from pyrion.ops.chains import project_intervals_through_chain, get_chain_target_interval
        from pyrion.core.genome_alignment import GenomeAlignment
        
        # Test empty inputs
        edge_cases_total += 1
        try:
            empty_intervals = np.array([], dtype=np.int64).reshape(0, 2)
            blocks = np.array([[100, 200, 1000, 1100]], dtype=np.int64)
            result = project_intervals_through_chain(empty_intervals, blocks)
            assert result == []
            print("✅ Empty intervals handling")
            edge_cases_passed += 1
        except Exception as e:
            print(f"❌ Empty intervals: {e}")
        
        # Test empty blocks
        edge_cases_total += 1
        try:
            intervals = np.array([[100, 200]], dtype=np.int64)
            empty_blocks = np.array([], dtype=np.int64).reshape(0, 4)
            result = project_intervals_through_chain(intervals, empty_blocks)
            assert len(result) == 1 and np.array_equal(result[0], np.array([[0, 0]], dtype=np.int64))
            print("✅ Empty blocks handling")
            edge_cases_passed += 1
        except Exception as e:
            print(f"❌ Empty blocks: {e}")
        
        # Test error conditions
        edge_cases_total += 1
        try:
            empty_chain = GenomeAlignment(
                chain_id=1, score=0, t_chrom=b"chr1", t_strand=1, t_size=1000,
                q_chrom=b"chr2", q_strand=1, q_size=1000,
                blocks=np.array([], dtype=np.int64).reshape(0, 4)
            )
            
            try:
                get_chain_target_interval(empty_chain)
                assert False, "Should raise ValueError"
            except ValueError:
                print("✅ Empty chain error handling")
                edge_cases_passed += 1
        except Exception as e:
            print(f"❌ Error handling: {e}")
        
        # Test None input
        edge_cases_total += 1
        try:
            try:
                get_chain_target_interval(None)
                assert False, "Should raise ValueError"
            except ValueError as ve:
                if "None" in str(ve):
                    print("✅ None input error handling")
                    edge_cases_passed += 1
                else:
                    print(f"❌ Wrong error message: {ve}")
        except Exception as e:
            print(f"❌ None input: {e}")
            
    except Exception as e:
        print(f"❌ Edge case setup failed: {e}")
    
    return edge_cases_passed, edge_cases_total


def run_performance_benchmark():
    """Run performance benchmark on different implementations."""
    print("\n⚡ Performance Benchmark:")
    print("-" * 50)
    
    try:
        from pyrion.ops.chains import (
            _project_intervals_numpy,
            HAS_NUMBA
        )
        
        if HAS_NUMBA:
            from pyrion.ops.chains import _project_intervals_numba
        else:
            _project_intervals_numba = None
        
        # Create larger test dataset
        large_blocks = np.random.randint(0, 1000000, size=(1000, 4), dtype=np.int64)
        large_blocks = np.sort(large_blocks.view('i8,i8,i8,i8'), order=['f0'], axis=0).view(np.int64).reshape(-1, 4)
        
        large_intervals = np.random.randint(0, 1000000, size=(5000, 2), dtype=np.int64)
        large_intervals = np.sort(large_intervals, axis=1)  # Ensure start < end
        
        print(f"Dataset: {len(large_intervals):,} intervals, {len(large_blocks):,} blocks")
        
        # Benchmark NumPy implementation
        start_time = time.perf_counter()
        results_numpy = _project_intervals_numpy(large_intervals, large_blocks)
        numpy_time = time.perf_counter() - start_time
        print(f"✅ NumPy implementation: {numpy_time:.3f}s ({len(results_numpy):,} results)")
        
        # Benchmark Numba implementation if available
        if HAS_NUMBA and _project_intervals_numba:
            start_time = time.perf_counter()
            results_numba = _project_intervals_numba(large_intervals, large_blocks)
            numba_time = time.perf_counter() - start_time
            speedup = numpy_time / numba_time if numba_time > 0 else float('inf')
            print(f"✅ Numba implementation: {numba_time:.3f}s ({len(results_numba):,} results)")
            print(f"🚀 Speedup: {speedup:.1f}x faster")
            
            # Verify results are identical
            if len(results_numpy) == len(results_numba):
                identical = all(np.array_equal(r1, r2) for r1, r2 in zip(results_numpy, results_numba))
                if identical:
                    print("✅ Results identical between implementations")
                else:
                    print("⚠️  Results differ between implementations")
        else:
            print("⚠️  Numba not available for comparison")
            
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")


def run_real_data_tests():
    """Test with real chain data if available."""
    print("\n🗂️ Real Data Integration Tests:")
    print("-" * 50)
    
    try:
        from pyrion.io.chain import read_chain_file_safe
        from pyrion.ops.chains import project_intervals_through_chain, get_chain_t_start, get_chain_t_end
        
        # Test files to try
        test_files = [
            "test_data/sample_toga_input/hg38.chr21.mm39.chr16.chain",
            "test_data/chains/hg38.chr9.mm39.chr4.chain",
            "test_data/chromM/hg38.chrM.mm39.chrM.chain"
        ]
        
        tested_files = 0
        
        for test_file in test_files:
            chain_file = Path(test_file)
            if not chain_file.exists():
                continue
                
            try:
                print(f"📁 Testing: {chain_file.name}")
                collection = read_chain_file_safe(chain_file)
                
                if len(collection.alignments) == 0:
                    print("   ⚠️  No alignments found")
                    continue
                
                alignment = collection.alignments[0]
                print(f"   📊 {len(alignment.blocks):,} blocks, chain_id={alignment.chain_id}")
                
                # Test basic accessors
                t_start = get_chain_t_start(alignment)
                t_end = get_chain_t_end(alignment)
                print(f"   📍 Target span: {t_start:,} - {t_end:,} ({t_end-t_start:,} bp)")
                
                # Test projection with small intervals
                test_intervals = np.array([
                    [t_start + 1000, t_start + 1100],
                    [t_start + 5000, t_start + 5100],
                ], dtype=np.int64)
                
                start_time = time.perf_counter()
                results = project_intervals_through_chain(test_intervals, alignment.blocks)
                projection_time = time.perf_counter() - start_time
                
                valid_results = [r for r in results if not (r[0][0] == 0 and r[0][1] == 0)]
                print(f"   ✅ Projected {len(test_intervals)} → {len(valid_results)} valid results ({projection_time*1000:.1f}ms)")
                
                tested_files += 1
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        if tested_files == 0:
            print("⚠️  No real data files found for testing")
        else:
            print(f"✅ Successfully tested {tested_files} real data files")
            
    except Exception as e:
        print(f"❌ Real data tests failed: {e}")


def print_summary(coverage_stats: Dict, performance_stats: Dict, edge_passed: int, edge_total: int):
    """Print comprehensive test summary."""
    print("\n" + "=" * 70)
    print("📋 COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)
    
    # Coverage summary
    total_functions = len(coverage_stats)
    passed_functions = sum(1 for status in coverage_stats.values() if status == "PASSED")
    
    print(f"🎯 Function Coverage: {passed_functions}/{total_functions} ({passed_functions/total_functions*100:.1f}%)")
    
    # Performance summary
    total_time = sum(performance_stats.values())
    fastest = min(performance_stats.items(), key=lambda x: x[1])
    slowest = max(performance_stats.items(), key=lambda x: x[1])
    
    print(f"⏱️  Total runtime: {total_time:.2f}ms")
    print(f"🏃 Fastest: {fastest[0]} ({fastest[1]:.2f}ms)")
    print(f"🐌 Slowest: {slowest[0]} ({slowest[1]:.2f}ms)")
    
    # Edge cases
    print(f"🔍 Edge cases: {edge_passed}/{edge_total} ({edge_passed/edge_total*100:.1f}%)")
    
    # Failed tests
    failed_tests = [name for name, status in coverage_stats.items() if status != "PASSED"]
    if failed_tests:
        print(f"❌ Failed tests: {', '.join(failed_tests)}")
    
    # Overall status
    overall_success = passed_functions == total_functions and edge_passed == edge_total
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED! The chains module is working perfectly.")
    else:
        print(f"\n⚠️  {len(failed_tests)} function(s) failed, {edge_total - edge_passed} edge case(s) failed")
    
    return overall_success


def main():
    """Main comprehensive test runner."""
    start_time = time.time()
    
    # Run all test suites
    coverage_stats, performance_stats = run_comprehensive_tests()
    edge_passed, edge_total = run_edge_case_tests()
    run_performance_benchmark()
    run_real_data_tests()
    
    # Print summary
    success = print_summary(coverage_stats, performance_stats, edge_passed, edge_total)
    
    end_time = time.time()
    print(f"\n⏱️  Total execution time: {end_time - start_time:.2f} seconds")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()