from .schemas import ColumnMapping, ColumnRole, DatasetMapping
from .validator import MappingValidator


class MappingService:
    """
    Responsible for creating and validating dataset mappings.

    This service contains no business logic.
    It simply creates a scientific representation of the dataset
    that can be consumed by the Analysis Engine.
    """

    def __init__(self):
        self.validator = MappingValidator()

    def create_mapping(
        self,
        dataset_name: str,
        mappings: list[tuple[str, ColumnRole]],
    ) -> DatasetMapping:
        """
        Create a DatasetMapping from user supplied mappings.

        Args:
            dataset_name:
                Name of the uploaded dataset.

            mappings:
                List of tuples in the format (use domain-agnostic examples):

                [
                    ("Metric A", ColumnRole.TARGET),
                    ("Category A", ColumnRole.CATEGORY),
                    ("Date A", ColumnRole.DATE)
                ]
        """

        dataset_mapping = DatasetMapping(
            dataset_name=dataset_name,
            columns=[
                ColumnMapping(
                    column_name=column_name,
                    role=role,
                )
                for column_name, role in mappings
            ],
        )

        errors = self.validator.validate(dataset_mapping)

        if errors:
            raise ValueError(
                "\n".join(errors)
            )

        return dataset_mapping