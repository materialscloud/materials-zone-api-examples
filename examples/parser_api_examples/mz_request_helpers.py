def build_configuration_column(column_name_in_result: str, unit: str,
                               column_name_in_file: str | None = None,
                               column_index_in_file: int | None = None) -> dict[str, str | int]:
    if (column_name_in_file is None and column_index_in_file is None) or \
            (column_name_in_file is not None and column_index_in_file is not None):
        raise ValueError('You must provide exactly one of columnNameInFile or columnIndexInFile')

    configuration_column: dict[str, str | int] = {
        'columnNameInResult': column_name_in_result,
        'unit': unit,
    }
    if column_name_in_file is not None:
        configuration_column['columnNameInFile'] = column_name_in_file
    if column_index_in_file is not None:
        configuration_column['columnIndexInFile'] = column_index_in_file

    return configuration_column


def build_computed_column(input_column_names: list[str], function: str, computed_column_name: str, unit: str) \
        -> dict[str, str | list[str]]:
    return {
        'inputColumnNames': input_column_names,
        'function': function,
        'computedColumnName': computed_column_name,
        'unit': unit
    }
