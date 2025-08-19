#!/usr/bin/env python3
"""
Command-line interface for the pySLAMMER verification framework.

This module provides CLI commands for running verification tests, generating reports,
and managing cached results.
"""

import sys
import json
import click
from pathlib import Path
from typing import List, Optional, Dict, Any
import time

from .data_loader import DataManager, ConfigManager
from .comparisons import ComparisonEngine
from .schemas import TestRecord, Results, VerificationData


class VerificationRunner:
    """Main verification runner that orchestrates the comparison process."""
    
    def __init__(self):
        """Initialize the verification runner."""
        self.data_manager = DataManager()
        self.config_manager = ConfigManager()
        self.comparison_engine = ComparisonEngine(self.config_manager)
        self.reference_data: Optional[VerificationData] = None
    
    def load_reference_data(self) -> VerificationData:
        """Load reference data, caching it for multiple operations."""
        if self.reference_data is None:
            click.echo("Loading reference data...")
            self.reference_data = self.data_manager.load_reference_data()
            click.echo(f"Loaded {len(self.reference_data.tests)} reference tests")
        return self.reference_data
    
    def run_verification(self, 
                        methods: Optional[List[str]] = None,
                        earthquakes: Optional[List[str]] = None,
                        test_ids: Optional[List[str]] = None,
                        force_recompute: bool = False,
                        max_tests: Optional[int] = None) -> Dict[str, Any]:
        """Run verification against selected test cases.
        
        Args:
            methods: Filter by analysis methods
            earthquakes: Filter by earthquake names  
            test_ids: Filter by specific test IDs
            force_recompute: Force recomputation of all results
            max_tests: Maximum number of tests to run
            
        Returns:
            Dictionary containing verification results
        """
        # Load and filter reference data
        reference_data = self.load_reference_data()
        test_records = self.data_manager.filter_tests(
            reference_data, methods, earthquakes, test_ids
        )
        
        if max_tests:
            test_records = test_records[:max_tests]
        
        click.echo(f"Running verification on {len(test_records)} test cases...")
        
        individual_results = []
        processed = 0
        
        with click.progressbar(test_records, label="Processing tests") as bar:
            for test_record in bar:
                try:
                    # Check cache first (unless force recompute)
                    cache_key = self.data_manager.generate_cache_key(test_record, "dev")
                    cached_result = None
                    
                    if not force_recompute:
                        cached_result = self.data_manager.load_cached_results(cache_key)
                    
                    if cached_result:
                        # Use cached results
                        pyslammer_results = Results(**cached_result['results'])
                    else:
                        # Simulate pySLAMMER computation
                        # NOTE: This is where actual pySLAMMER analysis would be called
                        pyslammer_results = self._simulate_pyslammer_analysis(test_record)
                        
                        # Cache the results
                        cache_data = {
                            'test_id': test_record.test_id,
                            'timestamp': time.time(),
                            'pyslammer_version': 'dev',
                            'results': {
                                'normal_displacement_cm': pyslammer_results.normal_displacement_cm,
                                'inverse_displacement_cm': pyslammer_results.inverse_displacement_cm,
                                'kmax': pyslammer_results.kmax,
                                'vs_final_mps': pyslammer_results.vs_final_mps,
                                'damping_final': pyslammer_results.damping_final
                            }
                        }
                        self.data_manager.save_cached_results(cache_key, cache_data)
                    
                    # Compare results
                    comparisons = self.comparison_engine.compare_test_record(
                        test_record, pyslammer_results
                    )
                    individual_results.extend(comparisons)
                    processed += 1
                    
                except Exception as e:
                    click.echo(f"Error processing {test_record.test_id}: {e}", err=True)
                    continue
        
        click.echo(f"Successfully processed {processed}/{len(test_records)} tests")
        
        # Generate comprehensive summary
        summary = self.comparison_engine.generate_verification_summary(individual_results)
        
        return {
            'summary': summary,
            'individual_results': individual_results,
            'metadata': {
                'total_reference_tests': len(test_records),
                'processed_tests': processed,
                'timestamp': time.time(),
                'filters': {
                    'methods': methods,
                    'earthquakes': earthquakes,
                    'test_ids': test_ids,
                    'max_tests': max_tests
                },
                'force_recompute': force_recompute
            }
        }
    
    def _simulate_pyslammer_analysis(self, test_record: TestRecord) -> Results:
        """Simulate pySLAMMER analysis for demonstration.
        
        In real implementation, this would call the actual pySLAMMER analysis functions.
        For now, we add small perturbations to reference values to simulate computation.
        """
        import random
        
        # Add small random perturbations to simulate real computation differences
        normal_factor = 1.0 + random.uniform(-0.03, 0.03)  # ±3% variation
        inverse_factor = 1.0 + random.uniform(-0.03, 0.03)  # ±3% variation
        
        return Results(
            normal_displacement_cm=test_record.results.normal_displacement_cm * normal_factor,
            inverse_displacement_cm=test_record.results.inverse_displacement_cm * inverse_factor,
            kmax=test_record.results.kmax,
            vs_final_mps=test_record.results.vs_final_mps,
            damping_final=test_record.results.damping_final
        )


# CLI Commands

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def cli(verbose):
    """pySLAMMER Verification Framework CLI
    
    Automated verification system for comparing pySLAMMER results 
    against legacy SLAMMER data.
    """
    if verbose:
        click.echo("Verbose mode enabled")


@cli.command()
@click.option('--methods', '-m', multiple=True, 
              help='Filter by analysis methods (rigid, decoupled, coupled)')
@click.option('--earthquakes', '-e', multiple=True,
              help='Filter by earthquake names')
@click.option('--test-ids', '-t', multiple=True,
              help='Filter by specific test IDs')
@click.option('--force-recompute', '-f', is_flag=True,
              help='Force recomputation of all results (ignore cache)')
@click.option('--max-tests', '-n', type=int,
              help='Maximum number of tests to run')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for results (JSON format)')
def run(methods, earthquakes, test_ids, force_recompute, max_tests, output):
    """Run verification tests against reference data."""
    
    try:
        runner = VerificationRunner()
        
        # Convert tuple to list for methods
        methods_list = list(methods) if methods else None
        earthquakes_list = list(earthquakes) if earthquakes else None
        test_ids_list = list(test_ids) if test_ids else None
        
        # Run verification
        results = runner.run_verification(
            methods=methods_list,
            earthquakes=earthquakes_list, 
            test_ids=test_ids_list,
            force_recompute=force_recompute,
            max_tests=max_tests
        )
        
        # Display summary
        summary = results['summary']
        click.echo("\n" + "="*60)
        click.echo("VERIFICATION RESULTS SUMMARY")
        click.echo("="*60)
        click.echo(f"Total Tests: {summary.total_tests}")
        click.echo(f"Passing: {summary.passing_tests} ({summary.overall_pass_rate:.1f}%)")
        click.echo(f"Failing: {summary.failing_tests}")
        
        # Method breakdown
        click.echo("\nMethod Breakdown:")
        for method, stats in summary.method_summaries.items():
            click.echo(f"  {method.upper()}: {stats['passing_tests']}/{stats['total_tests']} "
                      f"({stats['pass_rate']:.1f}%)")
        
        # Save results if output specified
        if output:
            # Convert summary to serializable format
            output_data = {
                'metadata': results['metadata'],
                'summary': {
                    'total_tests': summary.total_tests,
                    'passing_tests': summary.passing_tests,
                    'failing_tests': summary.failing_tests,
                    'overall_pass_rate': summary.overall_pass_rate,
                    'method_summaries': summary.method_summaries
                },
                'individual_results': [
                    {
                        'test_id': r.test_id,
                        'method': r.method,
                        'direction': r.direction,
                        'legacy_value': r.legacy_value,
                        'pyslammer_value': r.pyslammer_value,
                        'absolute_error': r.absolute_error,
                        'relative_error': r.relative_error,
                        'passes_tolerance': r.passes_tolerance
                    }
                    for r in summary.individual_results
                ]
            }
            
            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2)
            click.echo(f"\nResults saved to: {output}")
        
        # Exit with appropriate code
        if summary.overall_pass_rate < 100.0:
            click.echo(f"\nWARNING: {summary.failing_tests} tests failed!")
            sys.exit(1)
        else:
            click.echo("\nAll tests passed!")
            sys.exit(0)
            
    except Exception as e:
        click.echo(f"Error running verification: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', type=click.Path(exists=True),
              help='Input JSON file from previous run')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'csv']),
              default='text', help='Output format')
@click.option('--include-passed', is_flag=True,
              help='Include passed tests in detailed output')
@click.option('--detailed', is_flag=True, default=True,
              help='Include detailed statistical analysis')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for report')
def report(input, format, include_passed, detailed, output):
    """Generate verification report from results."""
    
    try:
        if input:
            # Load results from file
            with open(input, 'r') as f:
                data = json.load(f)
            
            # Extract summary info
            summary_data = data['summary']
            individual_data = data['individual_results']
            
            click.echo(f"Loaded results from: {input}")
            click.echo(f"Total tests: {summary_data['total_tests']}")
        else:
            # Run fresh verification for report
            runner = VerificationRunner()
            results = runner.run_verification(max_tests=10)  # Small sample for demo
            summary = results['summary']
            
            if format == 'text':
                report_text = runner.comparison_engine.format_comparison_report(
                    summary, include_passed, detailed
                )
                
                if output:
                    with open(output, 'w') as f:
                        f.write(report_text)
                    click.echo(f"Report saved to: {output}")
                else:
                    click.echo(report_text)
            
            elif format == 'json':
                # JSON format report
                json_report = {
                    'summary': {
                        'total_tests': summary.total_tests,
                        'passing_tests': summary.passing_tests,
                        'overall_pass_rate': summary.overall_pass_rate
                    },
                    'method_summaries': summary.method_summaries,
                    'group_results': [
                        {
                            'method': g.method,
                            'direction': g.direction,
                            'samples': g.number_of_samples,
                            'pass_rate': g.percent_passing_individual_tests,
                            'regression_slope': g.lin_regression_slope,
                            'regression_r_squared': g.lin_regression_r_squared,
                            'passes': g.passes_tolerance
                        }
                        for g in summary.group_results
                    ]
                }
                
                if output:
                    with open(output, 'w') as f:
                        json.dump(json_report, f, indent=2)
                    click.echo(f"JSON report saved to: {output}")
                else:
                    click.echo(json.dumps(json_report, indent=2))
            
            elif format == 'csv':
                # CSV format (individual results)
                import csv
                import io
                
                output_buffer = io.StringIO()
                writer = csv.writer(output_buffer)
                
                # Write header
                writer.writerow([
                    'test_id', 'method', 'direction', 'legacy_value', 
                    'pyslammer_value', 'absolute_error', 'relative_error', 'passes'
                ])
                
                # Write data
                for result in summary.individual_results:
                    writer.writerow([
                        result.test_id, result.method, result.direction,
                        result.legacy_value, result.pyslammer_value,
                        result.absolute_error, result.relative_error,
                        result.passes_tolerance
                    ])
                
                csv_content = output_buffer.getvalue()
                
                if output:
                    with open(output, 'w') as f:
                        f.write(csv_content)
                    click.echo(f"CSV report saved to: {output}")
                else:
                    click.echo(csv_content)
        
    except Exception as e:
        click.echo(f"Error generating report: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--status', is_flag=True, help='Show cache status')
@click.option('--clear', is_flag=True, help='Clear all cached results')
@click.option('--list', 'list_files', is_flag=True, help='List cached files')
def cache(status, clear, list_files):
    """Manage cached verification results."""
    
    try:
        data_manager = DataManager()
        cache_dir = data_manager.data_path / "cache"
        
        if status:
            # Show cache status
            if cache_dir.exists():
                cache_files = list(cache_dir.glob("*.json.gz"))
                total_size = sum(f.stat().st_size for f in cache_files)
                
                click.echo(f"Cache Directory: {cache_dir}")
                click.echo(f"Cached Files: {len(cache_files)}")
                click.echo(f"Total Size: {total_size / 1024:.1f} KB")
            else:
                click.echo("Cache directory does not exist")
        
        elif clear:
            # Clear cache
            if cache_dir.exists():
                import shutil
                cache_files = list(cache_dir.glob("*.json.gz"))
                for cache_file in cache_files:
                    cache_file.unlink()
                click.echo(f"Cleared {len(cache_files)} cached files")
            else:
                click.echo("Cache directory does not exist")
        
        elif list_files:
            # List cache files
            if cache_dir.exists():
                cache_files = sorted(cache_dir.glob("*.json.gz"))
                if cache_files:
                    click.echo("Cached Files:")
                    for cache_file in cache_files:
                        size_kb = cache_file.stat().st_size / 1024
                        mtime = cache_file.stat().st_mtime
                        import datetime
                        mtime_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                        click.echo(f"  {cache_file.name} ({size_kb:.1f} KB, {mtime_str})")
                else:
                    click.echo("No cached files found")
            else:
                click.echo("Cache directory does not exist")
        
        else:
            click.echo("Specify --status, --clear, or --list")
    
    except Exception as e:
        click.echo(f"Error managing cache: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--from-excel', type=click.Path(exists=True),
              help='Excel file to migrate from')
@click.option('--output-dir', type=click.Path(),
              help='Output directory for migrated data')
def migrate(from_excel, output_dir):
    """Migrate legacy Excel data to JSON format (one-time operation)."""
    
    if not from_excel:
        click.echo("Error: --from-excel is required", err=True)
        sys.exit(1)
    
    click.echo(f"Migration from {from_excel} is not yet implemented.")
    click.echo("This would convert Excel data to the new JSON schema format.")
    # TODO: Implement Excel migration logic


if __name__ == '__main__':
    cli()