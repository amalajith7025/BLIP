from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ColumnRole(str, Enum):
    """
    Scientific roles understood by the Analysis Engine.
    These are domain-agnostic and independent of any industry.
    """

    IDENTIFIER = "identifier"
    METRIC = "metric"
    CATEGORY = "category"
    DATE = "date"
    TARGET = "target"
    FEATURE = "feature"
    IGNORE = "ignore"


@dataclass
class ColumnMapping:
    """
    Represents the user's mapping for a single dataset column.
    """

    column_name: str
    role: ColumnRole


@dataclass
class DatasetMapping:
    """
    Represents the complete mapping for a dataset.
    """

    dataset_name: str

    columns: List[ColumnMapping] = field(default_factory=list)