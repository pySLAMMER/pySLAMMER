"""
Schema validation and data models for the verification framework.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema


class ValidationError(Exception):
    """Raised when data fails schema validation."""

    pass


@dataclass
class GroundMotionParameters:
    """Ground motion parameters for a test case."""

    earthquake: str
    record_station: str
    target_pga_g: float
    ground_motion_file: str
    description: Optional[str] = None


@dataclass
class Analysis:
    """Analysis configuration."""

    method: str  # rigid, decoupled, coupled
    mode: Optional[str] = (
        None  # linear_elastic, equivalent_linear (for decoupled/coupled)
    )


@dataclass
class SiteParameters:
    """Site-specific parameters."""

    ky_g: float
    height_m: Optional[float] = None
    vs_slope_mps: Optional[float] = None
    vs_base_mps: Optional[float] = None
    damping_ratio: Optional[float] = None
    reference_strain: Optional[float] = None


@dataclass
class Results:
    """Test results."""

    normal_displacement_cm: float
    inverse_displacement_cm: float
    kmax: Optional[float] = None
    vs_final_mps: Optional[float] = None
    damping_final: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Results":
        """Create Results from dictionary."""
        return cls(
            normal_displacement_cm=data["normal_displacement_cm"],
            inverse_displacement_cm=data["inverse_displacement_cm"],
            kmax=data.get("kmax"),
            vs_final_mps=data.get("vs_final_mps"),
            damping_final=data.get("damping_final"),
        )


@dataclass
class AnalysisRecord:
    """Complete test record."""

    analysis_id: str
    ground_motion_parameters: GroundMotionParameters
    analysis: Analysis
    site_parameters: SiteParameters
    results: Results

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisRecord":
        """Create TestRecord from dictionary."""
        return cls(
            analysis_id=data["analysis_id"],
            ground_motion_parameters=GroundMotionParameters(
                **data["ground_motion_parameters"]
            ),
            analysis=Analysis(**data["analysis"]),
            site_parameters=SiteParameters(**data["site_parameters"]),
            results=Results(**data["results"]),
        )


@dataclass
class VerificationData:
    """Complete verification dataset."""

    schema_version: str
    metadata: Dict[str, Any]
    analyses: List[AnalysisRecord]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VerificationData":
        """Create VerificationData from dictionary."""
        return cls(
            schema_version=data["schema_version"],
            metadata=data["metadata"],
            analyses=[AnalysisRecord.from_dict(analysis) for analysis in data["analyses"]],
        )


class SchemaValidator:
    """Handles JSON schema validation for verification data."""

    def __init__(self, schema_path: Path):
        """Initialize with schema file path."""
        self.schema_path = schema_path
        self._schema = None

    @property
    def schema(self) -> Dict[str, Any]:
        """Load and cache the JSON schema."""
        if self._schema is None:
            with open(self.schema_path, "r") as f:
                self._schema = json.load(f)
        return self._schema

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate data against the schema.

        Args:
            data: Data to validate

        Raises:
            ValidationError: If validation fails
        """
        try:
            jsonschema.validate(data, self.schema)
        except jsonschema.ValidationError as e:
            raise ValidationError(f"Schema validation failed: {e.message}") from e
        except jsonschema.SchemaError as e:
            raise ValidationError(f"Invalid schema: {e.message}") from e

    def validate_analysis_record(self, analysis_data: Dict[str, Any]) -> None:
        """Validate a single analysis record.

        Args:
            analysis_data: Analysis record data to validate

        Raises:
            ValidationError: If validation fails
        """
        # Create a minimal document with just the analysis record for validation
        analysis_document = {
            "schema_version": "1.0",
            "metadata": {"source_program": "test", "date_extracted": "2024-01-01"},
            "analyses": [analysis_data],
        }
        self.validate(analysis_document)
