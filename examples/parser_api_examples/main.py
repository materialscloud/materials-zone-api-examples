"""
main.py

This is the main script that runs the full example workflow.

It contains examples on how to use the parser APIs.
For additional examples and information, please go to https://developer.materials.zone/
"""
from requests import HTTPError

from examples.parser_api_examples.mz_operations import (create_parser)
from examples.parser_api_examples.mz_request_helpers import build_computed_column, build_configuration_column

# ---------------------------------------------------------------------------------------------
# Please define the configuration for your parser here
# When running this script a parser will be created with these details
# All of these fields will be editable later, so don't worry about missing something
# Don't worry about making mistakes. If there is any issue, an error message will be printed explaining the issue

# Give a name to your parser, so it would be easy to recognize
parser_name = "My New Parser"

# Give an optional description to your parser, to explain any details
parser_description = "A new parser I've just created"

# Write the physical measurement that will be parsed by your new parser.
# If you're not sure, "Generic" is also a good option
physical_measurement = "Fourier-Transform Infrared Spectroscopy"

# Write the instrument manufacturer which outputs the files that your parser parses.
# If you're not sure, "Generic" is also a good option
instrument_manufacturer = "JEOL"

# Write the instrument model which outputs the files that your parser parses.
# If you're not sure, "Generic" is also a good option
instrument_model = "JSM IT700HR"

# Write a list of all the file extensions that you expect to use this parser with
# They should be in this format ["csv", "txt"]
# Each value should be in quotes, without a dot ("csv" and not ".csv")
# The values should be separated with commas
# You can find the extension of the file at the end of it
# Some exotic files might be blocked by our system, in which case please contact a MaterialsZone representative
# Common file extensions:
# "xlsx", "xls" - Microsoft Excel files
# "csv" - Generic tabular files
# "txt" - Text files
supported_file_extensions = ["csv", "txt"]

# Choose which view type your parser will use by default
# This changes how the website shows the file by default after parsing
# All values may be changed on the fly in the website when viewing the file
# If you are not sure what to use "VIEW_2D_CUSTOM_AXES" is a great start point
# The options are:
# "VIEW_2D_CUSTOM_AXES" - This displays a line graph with an X axis and up to 2 Y axes,
#                       all of which may be linear or logarithmic
# "VIEW_BOX_PLOT" - This displays a 1 column box plot, used to view the spread and distribution
#                 of the values for that column
# "VIEW_CORRELATION_MATRIX" - This displays a multi-column to multi-column correlation matrix
# "VIEW_HEATMAP" - This displays a 3 axis heatmap
# "VIEW_HISTOGRAM_SINGLE" - This displays for a selected column, the number of appearances of each value
# "VIEW_SCATTER_PLOT" - This displays a 2 axis scatter plot
# "VIEW_VECTOR_WAFER_MAP" - This displays a 2 axis vector wafer map, with an overlay vector for
#                         each axis and optional offsets for either axis
# "VIEW_WAFER_MAP" - This displays a 3 axis wafer map
view_type = 'VIEW_2D_CUSTOM_AXES'

# This changes whether the parser expects anything written in the file before the tabular data
# Change it to True if there is anything written before the tabular data, and False if there isn't
metadata_expected = False

# This changes whether the parser expects anything written in the file after the tabular data
# Change it to True if there is anything written after the tabular data, and False if there isn't
footer_expected = False

# Here you define the configuration columns of your new parser
# The parser uses these to map columns from the file to the results
# For each column, use the function build_configuration_column like in the example below
# This function gets as input the following variables:

# 1. column_name_in_file or column_index_in_file - This is the start point, the column in the file
# You can point to it using its index, starting with 0
# You can also point to it using its name, if right above the tabular data is a row of column names
# Across all columns, you can only use either column_name_in_file or column_index_in_file.
# You cant point to one column by its name and another by its index
# You can only map a specific column to one result
#    if you wish to have multiple columns with identical data and different column names
#    please create a computed column with the IDENTITY function
#    this is explained below above the computed_columns field

# Now that we've found what columns we want to use in the file, we need to know what name to give the result
# 2. column_name_in_result - This is the name that the column will have in the result
# It may be the same as the column name in the file, but you can use it to rename columns
# You cant give multiple columns the same result name, they must be unique

# 3. unit - This is the unit that the result will have
# Examples of units: "mm", "nm", "v", "mA", etc...
# You may also use "arbitrary_units" or "Count"
configuration_columns = [
    build_configuration_column(column_name_in_file="Wavelength (nm)",
                               column_name_in_result="Wavelength",
                               unit="nm"),
    build_configuration_column(column_name_in_file="Abs",
                               column_name_in_result="Absorbtion",
                               unit="Count"),
]

# Here you define the computed columns of your new parser, if you want them
# These can create new columns not originally in your data using various math functions
# For each column, use the function build_computed_column like in the example below
# This function gets as input the following variables:

# 1. input_column_names - This is the list of columns used in the function
# Each function supports a specific amount of input columns
# The order of the input columns matter
# The input column names should all be column_name_in_result from configuration columns
# You may also use results (computed_column_name) from other computed columns as inputs to another computed column
#   if you do, the order of the computed columns in the list matters
#   each result must be defined before it is used as an input

# 2. function - This is the function used to compute the new column
# If there are any functions that you wish to have but don't appear here, please contact your MaterialsZone rep.
# The options are:
# "ABSOLUTE_DELTA" - For each row it computes the absolute value of the difference between subsequent cells of the
#    column, the first cell is set to null. It should have exactly one input column.
# "ABSOLUTE_TIMES_SIGN" - For each row it multiplies the absolute value of one column by the sign of the second one.
#    It should have exactly two input columns.
# "ABSOLUTE_TO_RELATIVE_TIME" - For each row it computes the relative time in seconds from an absolute time column by
#    subtracting the first element of the column from the column, the first cell is set to 0.
#    It should have exactly one input column.
# "DELTA" - For each row it computes the difference between subsequent cells of the column,
#    the first cell is set to null.
#    It should have exactly one input column.
# "DIVIDE" - For each row it divides the value of the first column by the value of the second column.
#    It should have exactly two input columns.
# "DIVIDE_BY_TWO_ROUND_UP" - For each row it divides the value of the column by 2 and rounds up to the closest integer.
#    It should have exactly one input column.
# "HHMMSS_TO_SECONDS" - For each row it converts a HH:MM:SS string to seconds as an integer.
#    It should have exactly one input column.
# "IDENTITY" - For each row it sets the same value as the one in the input column.
#    It should have exactly one input column.

# 3. computed_column_name - This is the name given to the computed column in the result
# You cant give multiple computed columns the same name, they must be unique
# Additionally, you cant give them a name of a configuration column's result column name

# 4. unit - This is the unit that the result will have
# Examples of units: "mm", "nm", "v", "mA", etc...
# You may also use "arbitrary_units" or "Count"
computed_columns = [
    build_computed_column(input_column_names=['Wavelength'],  # please read the comment below
                          # input_column_names should be from one of:
                          # configuration_columns.column_name_in_result
                          # computed_columns.computed_column_name- it should be defined before the function that uses it
                          function="IDENTITY",
                          computed_column_name="Wavelength Clone",
                          unit="nm")
]
# ---------------------------------------------------------------------------------------------


print("=" * 60)
print("🚀  Creating a new parser accessible only to my organization")
print("=" * 60)

try:
    created_parser = create_parser(name=parser_name,
                                    description=parser_description,
                                    physical_measurement=physical_measurement,
                                    instrument_manufacturer=instrument_manufacturer,
                                    instrument_model=instrument_model,
                                    supported_file_extensions=supported_file_extensions,
                                    view_type=view_type,
                                    configuration_columns=configuration_columns,
                                    computed_columns=computed_columns,
                                    metadata_expected=metadata_expected,
                                    footer_expected=footer_expected)
    print("Your parser was created successfully!")
    print(f"Use it with the code [{created_parser['code']}]")

except HTTPError as exception:
    print("There was an error creating your parser, it was not created!")
    print(exception)
