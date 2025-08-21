"""
Generate pySLAMMER verification results by running analyses and caching results.

This module contains methods to:
1. Convert AnalysisRecord objects to pySLAMMER input parameters
2. Run verification analyses with pySLAMMER and cache results
"""

import gzip
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .data_loader import DataManager
from .schemas import AnalysisRecord

# Add default results path constant
DEFAULT_RESULTS_FILE = (
    Path(__file__).resolve().parent.parent
    / "verification_data"
    / "results"
    / "slammer_results.json.gz"
)


def analysis_record_to_pyslammer_inputs(record: AnalysisRecord) -> Dict[str, Any]:
    """Convert an AnalysisRecord object to pySLAMMER class and input dictionary.

    Args:
        record: AnalysisRecord object from verification data

    Returns:
        Dictionary with two entries:
        - "method_class": The pySLAMMER class for the analysis method
        - "input_dict": Dictionary of required inputs to run the analysis
    """
    # Import pySLAMMER classes dynamically to avoid circular imports
    try:
        from pyslammer.coupled_analysis import Coupled
        from pyslammer.decoupled_analysis import Decoupled
        from pyslammer.ground_motion import GroundMotion
        from pyslammer.rigid_analysis import RigidAnalysis
        from pyslammer.utilities import load_sample_ground_motion
    except ImportError:
        raise ImportError(
            "pySLAMMER package not found. Install pySLAMMER to run verification."
        )

    # Map method names to classes
    method_classes = {
        "rigid": RigidAnalysis,
        "decoupled": Decoupled,
        "coupled": Coupled,
    }

    method = record.analysis.method.lower()
    if method not in method_classes:
        raise ValueError(f"Unknown analysis method: {method}")

    method_class = method_classes[method]

    # Create GroundMotion object from file
    ground_motion_file = record.ground_motion_parameters.ground_motion_file
    try:
        ground_motion = load_sample_ground_motion(ground_motion_file)
        # Update the name to match the earthquake name from the record
        ground_motion.name = record.ground_motion_parameters.earthquake
    except Exception as e:
        raise ValueError(f"Failed to load ground motion file {ground_motion_file}: {e}")

    # Build common input dictionary
    input_dict = {
        "ky": record.site_parameters.ky_g,  # Note: parameter is 'ky' not 'ky_g'
        "ground_motion": ground_motion,
        "target_pga": record.ground_motion_parameters.target_pga_g,
    }

    # Add method-specific parameters
    if method in ["decoupled", "coupled"]:
        input_dict.update(
            {
                "height": record.site_parameters.height_m,
                "vs_slope": record.site_parameters.vs_slope_mps,
                "vs_base": record.site_parameters.vs_base_mps,
                "damp_ratio": record.site_parameters.damping_ratio,
            }
        )

        if record.analysis.mode:
            input_dict["soil_model"] = record.analysis.mode

        if record.site_parameters.reference_strain is not None:
            input_dict["ref_strain"] = record.site_parameters.reference_strain / 100

    return {"method_class": method_class, "input_dict": input_dict}


def run_verification_analyses(
    source_file: Optional[Union[str, Path]] = DEFAULT_RESULTS_FILE,
    max_analyses: Union[int, str] = "all",
    methods: Optional[List[str]] = None,
    data_manager: Optional[DataManager] = None,
    pyslammer_version: str = "unknown",
    force_recompute: bool = False,
) -> int:
    """Run pySLAMMER analyses from completed suite and cache results.

    Args:
        source_file: Path to results file (defaults to slammer_results.json.gz)
        max_analyses: Number of analyses to run, or "all" for all
        methods: List of methods to filter by (e.g., ["rigid", "decoupled"])
        data_manager: DataManager instance (creates new if None)
        pyslammer_version: Version of pySLAMMER for caching
        force_recompute: If True, recompute even if cached results exist

    Returns:
        Number of analyses actually run (excluding cached/skipped)

    Raises:
        ImportError: If pySLAMMER is not available
        FileNotFoundError: If source file doesn't exist
        ValueError: If invalid parameters provided
    """
    if data_manager is None:
        data_manager = DataManager()

    # Load source file (JSON or gzipped JSON)
    source_path = Path(source_file)
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_file}")

    if source_path.suffix == ".gz":
        with gzip.open(source_path, "rt", encoding="utf-8") as f:
            data = json.load(f)
    else:
        with open(source_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    if pyslammer_version == "unknown":
        try:
            import pyslammer

            pyslammer_version = pyslammer.__version__
        except ImportError:
            pyslammer_version = "unknown"

    # Parse analyses from data (assumes same schema as reference data)
    analyses = [
        AnalysisRecord.from_dict(analysis) for analysis in data.get("analyses", [])
    ]

    # Apply filtering
    if methods:
        analyses = [
            a
            for a in analyses
            if a.analysis.method.lower() in [m.lower() for m in methods]
        ]

    if not analyses:
        print("No analyses found matching criteria.")
        return 0

    print(f"Found {len(analyses)} analyses matching criteria")

    # Validity check for max_analyses
    if max_analyses != "all":
        if not isinstance(max_analyses, int) or max_analyses <= 0:
            raise ValueError("max_analyses must be positive integer or 'all'")
    else:
        max_analyses = len(analyses)

    # Process each analysis
    run_count = 0

    for analysis_record in analyses:
        if run_count >= max_analyses:
            break
        # Generate cache key
        cache_key = data_manager.generate_cache_key(analysis_record, pyslammer_version)

        # Check if result already cached
        if not force_recompute:
            cached_result = data_manager.load_cached_results(cache_key)
            if cached_result is not None:
                print(f"  Skipping (cached): {analysis_record.analysis_id}")
                continue

        # Convert to pySLAMMER inputs
        try:
            pyslammer_inputs = analysis_record_to_pyslammer_inputs(analysis_record)
        except Exception as e:
            print(f"  Error converting inputs for {analysis_record.analysis_id}: {e}")
            continue

        # Run pySLAMMER analysis
        try:
            method_class = pyslammer_inputs["method_class"]
            input_dict = pyslammer_inputs["input_dict"]

            # Create and run the analysis (normal and inverse)
            print(f"  Running analysis for {analysis_record.analysis_id}...")
            normal_analysis = method_class(**input_dict)
            inverse_analysis = method_class(**input_dict, inverse=True)

            # Extract results from instance attributes
            results = {
                "normal_displacement_cm": getattr(
                    normal_analysis, "max_sliding_disp", 0.0
                )
                * 100,  # Convert m to cm
                "inverse_displacement_cm": getattr(
                    inverse_analysis, "max_sliding_disp", 0.0
                )
                * 100,  # Convert m to cm
            }

            # Create result record matching schema structure
            result_record = {
                "analysis_id": analysis_record.analysis_id,
                "ground_motion_parameters": {
                    "earthquake": analysis_record.ground_motion_parameters.earthquake,
                    "record_station": analysis_record.ground_motion_parameters.record_station,
                    "target_pga_g": analysis_record.ground_motion_parameters.target_pga_g,
                    "ground_motion_file": analysis_record.ground_motion_parameters.ground_motion_file,
                },
                "analysis": {
                    "method": analysis_record.analysis.method,
                },
                "site_parameters": {
                    "ky_g": analysis_record.site_parameters.ky_g,
                },
                "results": {
                    "normal_displacement_cm": results.get(
                        "normal_displacement_cm", 0.0
                    ),
                    "inverse_displacement_cm": results.get(
                        "inverse_displacement_cm", 0.0
                    ),
                },
            }

            # Add optional fields if present
            if analysis_record.analysis.mode:
                result_record["analysis"]["mode"] = analysis_record.analysis.mode

            for param in [
                "height_m",
                "vs_slope_mps",
                "vs_base_mps",
                "damping_ratio",
                "reference_strain",
            ]:
                value = getattr(analysis_record.site_parameters, param)
                if value is not None:
                    result_record["site_parameters"][param] = value

            for result_field in ["kmax", "vs_final_mps", "damping_final"]:
                if result_field in results:
                    result_record["results"][result_field] = results[result_field]

            # Cache the result
            data_manager.save_cached_results(cache_key, result_record)
            run_count += 1
            print(f"  Completed: {analysis_record.analysis_id}")

        except Exception as e:
            print(f"  Error running analysis for {analysis_record.analysis_id}: {e}")
            continue

    print(f"Successfully ran {run_count} new analyses")
    return run_count


def collect_and_save_pyslammer_results(
    pyslammer_version: str,
    data_manager: Optional[DataManager] = None,
    include_methods: Optional[List[str]] = None,
) -> Path:
    """Collect all cached pySLAMMER results and save to versioned file.

    Args:
        pyslammer_version: Version string for filename generation
        data_manager: DataManager instance (creates new if None)
        include_methods: Methods to include (defaults to all)

    Returns:
        Path to saved results file

    Raises:
        ValueError: If no cached results found
    """
    if data_manager is None:
        data_manager = DataManager()

    # Load reference data to get all analysis records
    verification_data = data_manager.load_reference_data()
    all_analyses = verification_data.analyses

    # Filter by methods if specified
    if include_methods:
        all_analyses = [
            a
            for a in all_analyses
            if a.analysis.method.lower() in [m.lower() for m in include_methods]
        ]

    # Collect cached results
    cached_analyses = []

    for analysis_record in all_analyses:
        cache_key = data_manager.generate_cache_key(analysis_record, pyslammer_version)
        cached_result = data_manager.load_cached_results(cache_key)

        if cached_result is not None:
            cached_analyses.append(cached_result)

    if not cached_analyses:
        raise ValueError("No cached pySLAMMER results found")

    # Build results file structure
    results_data = {
        "schema_version": "1.0",
        "metadata": {
            "source_program": "pySLAMMER",
            "source_version": pyslammer_version,
            "date_extracted": verification_data.metadata.get(
                "date_extracted", "unknown"
            ),
            "total_analyses": len(cached_analyses),
            "description": f"pySLAMMER verification results v{pyslammer_version}",
        },
        "analyses": cached_analyses,
    }

    # Save results file
    output_path = data_manager.save_results(
        results_data, pyslammer_version=pyslammer_version
    )

    print(f"Saved {len(cached_analyses)} pySLAMMER results to {output_path}")
    return output_path


if __name__ == "__main__":
    run_verification_analyses(max_analyses=1000)
