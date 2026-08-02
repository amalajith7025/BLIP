from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ColumnProfile:
    """
    Represents everything BLIP knows about a single column
    after profiling.
    """

    # Basic Information
    name: str
    data_type: str

    # User Mapping
    role: Optional[str] = None

    # Data Quality
    nullable: bool = False
    missing_values: int = 0
    unique_values: int = 0

    # Sample Values
    sample_values: List = field(default_factory=list)

    # Characteristics
    continuous: bool = False
    discrete: bool = False
    categorical: bool = False
    datetime: bool = False
    boolean: bool = False
    text: bool = False

    # Statistical Capabilities
    can_average: bool = False
    can_group: bool = False
    can_count: bool = False
    can_correlate: bool = False
    can_forecast: bool = False
    can_pareto: bool = False

    # Engine Recommendations
    recommended_analyses: List[str] = field(default_factory=list)


@dataclass
class DatasetProfile:
    """
    Represents everything BLIP knows about an uploaded dataset.
    """

    name: str

    rows: int

    columns: int

    column_profiles: List[ColumnProfile] = field(default_factory=list)

    recommended_analyses: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)