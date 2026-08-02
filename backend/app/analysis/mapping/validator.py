from .schemas import ColumnRole, DatasetMapping


class MappingValidator:
    """
    Validates a dataset mapping before it is used
    by the Scientific Analysis Engine.
    """

    def validate(self, mapping: DatasetMapping) -> list[str]:
        """
        Returns a list of validation errors.
        An empty list means the mapping is valid.
        """

        errors: list[str] = []

        if not mapping.columns:
            errors.append("Dataset contains no mapped columns.")
            return errors

        column_names = [column.column_name for column in mapping.columns]

        if len(column_names) != len(set(column_names)):
            errors.append("Duplicate column mappings detected.")

        roles = [column.role for column in mapping.columns]

        if ColumnRole.TARGET not in roles:
            errors.append("At least one TARGET column is required.")

        if ColumnRole.METRIC not in roles:
            errors.append("At least one METRIC column is required.")

        if all(role == ColumnRole.IGNORE for role in roles):
            errors.append("All columns are marked as IGNORE.")

        return errors