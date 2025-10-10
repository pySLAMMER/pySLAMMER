"""
Data loading and management for the verification framework.
"""

import gzip
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .comparisons import ConfigManager
from .schemas import AnalysisRecord, SchemaValidator, VerificationData


class DataManager:
    """Manages loading, saving, and validation of verification data."""

    def __init__(self, verification_data_path: Optional[Path] = None):
        """Initialize with verification data directory path."""
        if verification_data_path is None:
            # Default to verification_data directory
            verification_data_path = Path(__file__).parent.parent / "verification_data"

        self.data_path = verification_data_path
        self.schema_validator = SchemaValidator(
            self.data_path / "schemas" / "results_schema.json"
        )
        self.config_manager = ConfigManager()

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
        return self.load_results("slammer", validate=validate)

    def load_results(self, source: str, version: Optional[str] = None, validate: bool = True) -> VerificationData:
        """Load results from either SLAMMER or pySLAMMER.

        Args:
            source: Either "slammer" for reference data or "pyslammer" for test data
            version: Version string (required for pySLAMMER, ignored for SLAMMER)
            validate: Whether to validate against schema

        Returns:
            VerificationData containing test results

        Raises:
            ValidationError: If data fails validation
            FileNotFoundError: If results file doesn't exist
        """
        if source == "slammer":
            results_path = self.data_path / "results" / "slammer_results.json.gz"
        elif source == "pyslammer":
            if version is None:
                raise ValueError("Version required for pySLAMMER results")
            # Use version directly in filename (keeping periods)
            results_path = self.data_path / "results" / f"pyslammer_{version}_results.json.gz"
        else:
            raise ValueError(f"Unknown source: {source}. Must be 'slammer' or 'pyslammer'")

        try:
            with gzip.open(results_path, "rt", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"{source.upper()} results not found at {results_path}")

        if validate:
            self.schema_validator.validate(data)

        return VerificationData.from_dict(data)

    def save_results(
        self,
        results: Dict[str, Any],
        filename: str = None,
        pyslammer_version: str = "unknown",
        compress: bool = True,
    ) -> Path:
        """Save verification results to file with pyslammer version in filename.

        Args:
            results: Results data to save (should follow results_schema.json format)
            filename: Optional custom filename, defaults to pyslammer_{version}_results.json.gz
            pyslammer_version: Version of pySLAMMER for filename generation
            compress: Whether to compress the output

        Returns:
            Path to saved file
        """
        # Validate results against schema before saving
        self.schema_validator.validate(results)

        if filename is None:
            # Generate filename with version (keeping periods)
            filename = f"pyslammer_{pyslammer_version}_results.json"

        results_dir = self.data_path / "results"
        results_dir.mkdir(exist_ok=True)

        if compress and not filename.endswith(".gz"):
            filename += ".gz"

        output_path = results_dir / filename

        if compress:
            with gzip.open(output_path, "wt", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        else:
            with open(output_path, "w", encoding="utf-8") as f:
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
            with gzip.open(cache_file, "rt", encoding="utf-8") as f:
                cached_data = json.load(f)

            # TODO: Check cache expiry based on config settings
            # For now, just return the data
            return cached_data
        except (json.JSONDecodeError, OSError):
            # Cache file is corrupted, ignore it
            return None

    def save_cached_results(self, cache_key: str, results: Dict[str, Any]) -> None:
        """Save results to cache with schema validation.

        Args:
            cache_key: Unique identifier for the results
            results: Results data to cache (individual analysis result)

        Raises:
            ValidationError: If the individual result doesn't match schema requirements
        """
        # Validate individual cached result against schema
        self.schema_validator.validate_analysis_record(results)

        cache_dir = self.data_path / "cache"
        cache_dir.mkdir(exist_ok=True)

        cache_file = cache_dir / f"{cache_key}.json.gz"

        with gzip.open(cache_file, "wt", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    def generate_cache_key(
        self, analysis_record: AnalysisRecord, pyslammer_version: str = "unknown"
    ) -> str:
        """Generate a unique cache key for an analysis record.

        Args:
            analysis_record: Analysis record to generate key for
            pyslammer_version: Version of pySLAMMER being tested

        Returns:
            Unique cache key string
        """
        # Create a deterministic hash from analysis parameters and version
        key_data = {
            "analysis_id": analysis_record.analysis_id,
            "ground_motion_parameters": asdict(
                analysis_record.ground_motion_parameters
            ),
            "analysis": asdict(analysis_record.analysis),
            "site_parameters": asdict(analysis_record.site_parameters),
            "pyslammer_version": pyslammer_version,
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]

    def filter_analyses(
        self,
        verification_data: VerificationData,
        methods: Optional[List[str]] = None,
        earthquakes: Optional[List[str]] = None,
        analysis_ids: Optional[List[str]] = None,
    ) -> List[AnalysisRecord]:
        """Filter analysis records based on criteria.

        Args:
            verification_data: Source verification data
            methods: Filter by analysis methods
            earthquakes: Filter by earthquake names
            analysis_ids: Filter by specific analysis IDs

        Returns:
            Filtered list of analysis records
        """
        analyses = verification_data.analyses

        if methods:
            analyses = [a for a in analyses if a.analysis.method in methods]

        if earthquakes:
            analyses = [
                a
                for a in analyses
                if a.ground_motion_parameters.earthquake in earthquakes
            ]

        if analysis_ids:
            analyses = [a for a in analyses if a.analysis_id in analysis_ids]

        return analyses
