"""
Data loading and management for the verification framework.
"""

import json
import gzip
import toml
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict

from .schemas import SchemaValidator, VerificationData, TestRecord, ValidationError


@dataclass
class ToleranceSettings:
    """Tolerance settings for verification comparisons."""
    relative: float
    absolute: float


class ConfigManager:
    """Manages verification configuration settings."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize with config file path."""
        if config_path is None:
            # Default to the config file in verification_data
            config_path = Path(__file__).parent.parent / "verification_data" / "config" / "verification_config.toml"
        
        self.config_path = config_path
        self._config = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """Load and cache the configuration."""
        if self._config is None:
            with open(self.config_path, 'r') as f:
                self._config = toml.load(f)
        return self._config
    
    def get_tolerance(self, method: str, displacement_value: Optional[float] = None) -> ToleranceSettings:
        """Get tolerance settings for a specific method and displacement value.
        
        Args:
            method: Analysis method (rigid, decoupled, coupled)
            displacement_value: Optional displacement value for value-dependent tolerances
            
        Returns:
            ToleranceSettings with relative and absolute tolerances
        """
        config = self.config
        
        # Start with method-specific tolerances
        method_tolerances = config.get("tolerances", {}).get("method_specific", {}).get(method, {})
        relative = method_tolerances.get("relative", config["tolerances"]["default_relative"])
        absolute = method_tolerances.get("absolute", config["tolerances"]["default_absolute"])
        
        # Apply value-dependent adjustments if displacement is provided
        if displacement_value is not None:
            value_dep = config.get("tolerances", {}).get("value_dependent", {})
            
            if displacement_value <= value_dep.get("small_displacement_threshold", 1.0):
                # Small displacement - use more lenient tolerances
                relative = value_dep.get("small_displacement_relative", relative)
                absolute = value_dep.get("small_displacement_absolute", absolute)
            elif displacement_value >= value_dep.get("large_displacement_threshold", 50.0):
                # Large displacement - use stricter tolerances
                relative = value_dep.get("large_displacement_relative", relative)
                absolute = value_dep.get("large_displacement_absolute", absolute)
        
        return ToleranceSettings(relative=relative, absolute=absolute)
    
    def get_additional_output_tolerance(self, output_type: str) -> float:
        """Get tolerance for additional outputs (kmax, vs, damping).
        
        Args:
            output_type: Type of output (kmax, vs, damping)
            
        Returns:
            Relative tolerance for the output type
        """
        output_tolerances = self.config.get("tolerances", {}).get("additional_outputs", {})
        return output_tolerances.get(f"{output_type}_relative", 0.05)  # Default 5%


class DataManager:
    """Manages loading, saving, and validation of verification data."""
    
    def __init__(self, verification_data_path: Optional[Path] = None):
        """Initialize with verification data directory path."""
        if verification_data_path is None:
            # Default to verification_data directory
            verification_data_path = Path(__file__).parent.parent / "verification_data"
        
        self.data_path = verification_data_path
        self.schema_validator = SchemaValidator(
            self.data_path / "schemas" / "legacy_results_schema.json"
        )
        self.config_manager = ConfigManager(
            self.data_path / "config" / "verification_config.toml"
        )
    
    def load_reference_data(self, validate: bool = True) -> VerificationData:
        """Load the reference SLAMMER results.
        
        Args:
            validate: Whether to validate against schema
            
        Returns:
            VerificationData containing all reference test cases
            
        Raises:
            ValidationError: If data fails validation
            FileNotFoundError: If reference file doesn't exist
        """
        reference_path = self.data_path / "reference" / "slammer_results.json.gz"
        
        try:
            with gzip.open(reference_path, 'rt', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Reference data not found at {reference_path}")
        
        if validate:
            self.schema_validator.validate(data)
        
        return VerificationData.from_dict(data)
    
    def save_results(self, results: Dict[str, Any], filename: str, compress: bool = True) -> Path:
        """Save verification results to file.
        
        Args:
            results: Results data to save
            filename: Output filename
            compress: Whether to compress the output
            
        Returns:
            Path to saved file
        """
        results_dir = self.data_path / "results"
        results_dir.mkdir(exist_ok=True)
        
        if compress and not filename.endswith('.gz'):
            filename += '.gz'
        
        output_path = results_dir / filename
        
        if compress:
            with gzip.open(output_path, 'wt', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
        
        return output_path
    
    def load_cached_results(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load cached results if they exist.
        
        Args:
            cache_key: Unique identifier for the cached results
            
        Returns:
            Cached results or None if not found/expired
        """
        cache_dir = self.data_path / "cache"
        cache_file = cache_dir / f"{cache_key}.json.gz"
        
        if not cache_file.exists():
            return None
        
        try:
            with gzip.open(cache_file, 'rt', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # TODO: Check cache expiry based on config settings
            # For now, just return the data
            return cached_data
        except (json.JSONDecodeError, OSError):
            # Cache file is corrupted, ignore it
            return None
    
    def save_cached_results(self, cache_key: str, results: Dict[str, Any]) -> None:
        """Save results to cache.
        
        Args:
            cache_key: Unique identifier for the results
            results: Results data to cache
        """
        cache_dir = self.data_path / "cache"
        cache_dir.mkdir(exist_ok=True)
        
        cache_file = cache_dir / f"{cache_key}.json.gz"
        
        with gzip.open(cache_file, 'wt', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
    
    def generate_cache_key(self, test_record: TestRecord, pyslammer_version: str = "unknown") -> str:
        """Generate a unique cache key for a test record.
        
        Args:
            test_record: Test record to generate key for
            pyslammer_version: Version of pySLAMMER being tested
            
        Returns:
            Unique cache key string
        """
        # Create a deterministic hash from test parameters and version
        key_data = {
            "test_id": test_record.test_id,
            "ground_motion": asdict(test_record.ground_motion_parameters),
            "analysis": asdict(test_record.analysis),
            "site_parameters": asdict(test_record.site_parameters),
            "pyslammer_version": pyslammer_version
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def filter_tests(self, 
                    verification_data: VerificationData,
                    methods: Optional[List[str]] = None,
                    earthquakes: Optional[List[str]] = None,
                    test_ids: Optional[List[str]] = None) -> List[TestRecord]:
        """Filter test records based on criteria.
        
        Args:
            verification_data: Source verification data
            methods: Filter by analysis methods
            earthquakes: Filter by earthquake names
            test_ids: Filter by specific test IDs
            
        Returns:
            Filtered list of test records
        """
        tests = verification_data.tests
        
        if methods:
            tests = [t for t in tests if t.analysis.method in methods]
        
        if earthquakes:
            tests = [t for t in tests if t.ground_motion_parameters.earthquake in earthquakes]
        
        if test_ids:
            tests = [t for t in tests if t.test_id in test_ids]
        
        return tests