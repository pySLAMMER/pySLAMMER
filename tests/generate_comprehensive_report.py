#!/usr/bin/env python3
"""
Generate comprehensive report from complete verification results.
"""

import json
import sys
from pathlib import Path

def generate_report_from_json(json_file):
    """Generate text report from JSON verification results."""
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    metadata = data['metadata']
    summary = data['summary']
    individual_results = data['individual_results']
    
    # Generate report
    report = []
    report.append("=" * 80)
    report.append("COMPREHENSIVE PYSLAMMER VERIFICATION REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Metadata
    report.append("Verification Metadata:")
    report.append(f"  Total Reference Tests: {metadata['total_reference_tests']}")
    report.append(f"  Processed Tests: {metadata['processed_tests']}")
    report.append(f"  Force Recompute: {metadata['force_recompute']}")
    report.append("")
    
    # Overall summary
    report.append("Overall Results:")
    report.append(f"  Total Tests: {summary['total_tests']}")
    report.append(f"  Passing: {summary['passing_tests']} ({summary['overall_pass_rate']:.1f}%)")
    report.append(f"  Failing: {summary['failing_tests']}")
    report.append("")
    
    # Method-specific summaries
    report.append("Method-Specific Results:")
    for method, stats in summary['method_summaries'].items():
        report.append(f"  {method.upper()}:")
        report.append(f"    Tests: {stats['total_tests']}")
        report.append(f"    Passing: {stats['passing_tests']}")
        report.append(f"    Pass Rate: {stats['pass_rate']:.1f}%")
        report.append(f"    Mean Absolute Error: {stats['mean_absolute_error']:.3f} cm")
        report.append(f"    Mean Relative Error: {stats['mean_relative_error']:.1%}")
    report.append("")
    
    # Failed tests summary (top 20)
    failed_tests = [r for r in individual_results if not r['passes_tolerance']]
    if failed_tests:
        report.append(f"Failed Tests Summary (showing first 20 of {len(failed_tests)}):")
        for i, test in enumerate(failed_tests[:20]):
            report.append(f"  {i+1}. {test['test_id']}:")
            report.append(f"     Expected: {test['legacy_value']:.3f} cm")
            report.append(f"     Actual: {test['pyslammer_value']:.3f} cm")
            report.append(f"     Error: {test['absolute_error']:.3f} cm ({test['relative_error']:.1%})")
        
        if len(failed_tests) > 20:
            report.append(f"  ... and {len(failed_tests) - 20} more failed tests")
        report.append("")
    
    # Error distribution analysis
    all_errors = [r['relative_error'] for r in individual_results if r['relative_error'] != float('inf')]
    if all_errors:
        import statistics
        
        report.append("Error Distribution Analysis:")
        report.append(f"  Mean Relative Error: {statistics.mean(all_errors):.1%}")
        report.append(f"  Median Relative Error: {statistics.median(all_errors):.1%}")
        report.append(f"  Std Dev Relative Error: {statistics.stdev(all_errors):.1%}")
        
        # Error ranges
        small_errors = [e for e in all_errors if e <= 0.02]  # ≤2%
        medium_errors = [e for e in all_errors if 0.02 < e <= 0.05]  # 2-5%
        large_errors = [e for e in all_errors if e > 0.05]  # >5%
        
        total_count = len(all_errors)
        report.append(f"  Error Distribution:")
        report.append(f"    ≤2% error: {len(small_errors)} tests ({len(small_errors)/total_count:.1%})")
        report.append(f"    2-5% error: {len(medium_errors)} tests ({len(medium_errors)/total_count:.1%})")
        report.append(f"    >5% error: {len(large_errors)} tests ({len(large_errors)/total_count:.1%})")
        report.append("")
    
    # Method comparison
    report.append("Method Performance Comparison:")
    methods = summary['method_summaries']
    
    # Sort methods by pass rate
    sorted_methods = sorted(methods.items(), key=lambda x: x[1]['pass_rate'], reverse=True)
    
    for i, (method, stats) in enumerate(sorted_methods):
        rank = i + 1
        report.append(f"  #{rank}. {method.upper()}: {stats['pass_rate']:.1f}% pass rate")
        report.append(f"      Mean Error: {stats['mean_relative_error']:.1%}")
        report.append(f"      Total Tests: {stats['total_tests']}")
    
    report.append("")
    
    # Summary and recommendations
    report.append("Summary and Recommendations:")
    report.append(f"• Overall verification shows {summary['overall_pass_rate']:.1f}% compatibility")
    
    if summary['overall_pass_rate'] >= 70:
        report.append("• ✅ GOOD: Pass rate indicates strong compatibility with legacy SLAMMER")
    elif summary['overall_pass_rate'] >= 50:
        report.append("• ⚠️  MODERATE: Pass rate suggests some differences, review tolerance settings")
    else:
        report.append("• ❌ POOR: Low pass rate indicates significant differences, investigate implementation")
    
    # Best/worst performing methods
    best_method = max(methods.keys(), key=lambda m: methods[m]['pass_rate'])
    worst_method = min(methods.keys(), key=lambda m: methods[m]['pass_rate'])
    
    report.append(f"• Best performing method: {best_method.upper()} ({methods[best_method]['pass_rate']:.1f}%)")
    report.append(f"• Lowest performing method: {worst_method.upper()} ({methods[worst_method]['pass_rate']:.1f}%)")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_comprehensive_report.py <verification_results.json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    if not Path(json_file).exists():
        print(f"Error: File {json_file} not found")
        sys.exit(1)
    
    try:
        report = generate_report_from_json(json_file)
        
        # Save to file
        output_file = json_file.replace('.json', '_report.txt')
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"📄 Comprehensive report generated: {output_file}")
        print("\n" + "="*60)
        print("REPORT PREVIEW:")
        print("="*60)
        
        # Show first part of report
        lines = report.split('\n')
        for line in lines[:50]:  # Show first 50 lines
            print(line)
        
        if len(lines) > 50:
            print(f"\n... and {len(lines) - 50} more lines in the full report")
        
    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)