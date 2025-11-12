"""
main.py

This is the main script that runs the full example workflow.

It contains examples on how to use the parser APIs.
For additional examples and information, please go to https://developer.materials.zone/
"""
from typing import Any

from examples.parser_api_examples.mz_operations import (create_parser, delete_parser, get_all_accessible_parsers,
                                                        get_parser, update_parser)
from examples.parser_api_examples.mz_request_helpers import build_computed_column, build_configuration_column

print("=" * 60)
print("🚀  Managing parsers API example")
print("=" * 60)

print("\n=== Step 1: Get all parsers accessible to my organization - These are system parsers and the users "
      "organization's parsers ===")
all_accessible_parsers: list[dict[str, Any]] = get_all_accessible_parsers()
print("Accessible parsers to this user's organization are:")
for parser in all_accessible_parsers:
    print(f"[{parser['name']}] with the code [{parser['code']}] - [{parser['description']}]")

print("\n=== Step 2: Create a new parser accessible only to my organization ===\n")
print("For an explanation of each field and its options, please go to https://developer.materials.zone/")
configuration_columns = [
    build_configuration_column(column_name_in_file="Wavelength (nm)",
                               column_name_in_result="Wavelength",
                               unit="nm"),
    build_configuration_column(column_name_in_file="Abs",
                               column_name_in_result="Absorbtion",
                               unit="Count"),
]
computed_columns = [
    build_computed_column(input_column_names=['Wavelength'],  # please read the comment below
                          # input_column_names should be from configuration_columns.column_name_in_result
                          function="IDENTITY",
                          computed_column_name="Wavelength Clone",
                          unit="nm")
]
created_parser = create_parser(name="My New Parser",
                               description="A new parser I've just created",
                               physical_measurement="Fourier-Transform Infrared Spectroscopy",
                               instrument_manufacturer="JEOL",
                               instrument_model="JSM IT700HR",
                               supported_file_extensions=["csv", "txt"],
                               view_type='VIEW_2D_CUSTOM_AXES',
                               configuration_columns=configuration_columns,
                               computed_columns=computed_columns,
                               metadata_expected=True,
                               footer_expected=False)

print("\n=== Step 3: Partially update my previously created parser ===\n")
computed_columns = [  # this will override all existing computed columns, so if we just want to add a new one and
    # not remove the existing one, we need to add the existing one here as well
    build_computed_column(input_column_names=['Wavelength'],
                          function="IDENTITY",
                          computed_column_name="Wavelength Clone",
                          unit="nm"),
    build_computed_column(input_column_names=['Wavelength'],
                          function="DIVIDE_BY_TWO_ROUND_UP",
                          computed_column_name="Wavelength Divided by 2",
                          unit="nm")
]
updated_parser = update_parser(parser_id=created_parser['id'],
                               description="The new parser has been updated",
                               supported_file_extensions=["csv", "txt", "xlsx"],
                               computed_columns=computed_columns,
                               footer_expected=True)

print("\n=== Step 4: Get my previously created parser ===\n")
get_parser = get_parser(parser_id=updated_parser['id'])

print("\n=== Step 5: Delete my previously created parser ===\n")
delete_parser(parser_id=get_parser['id'])
