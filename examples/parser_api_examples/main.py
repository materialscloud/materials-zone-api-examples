"""
main.py

This is the main script that runs the full example workflow.

It contains examples on how to use the parser APIs.
For additional examples and information, please go to https://developer.materials.zone/
"""
from requests import HTTPError

from mz_operations import (
    create_parser
)


def main():
    try:
        parser = create_parser(
            name="keithley_iv",
            description="Parses I–V sweep data produced by Keithley"
                        " SourceMeter instruments and calculates resistance"
                        " from voltage and current.",
            physical_measurement="I–V Measurement",
            instrument_manufacturer="Keithley Instruments",
            instrument_model="Keithley 2450 SourceMeter®",
            supported_file_extensions=["csv"],
            view_type="VIEW_2D_CUSTOM_AXES",
            configuration_columns=[
                {
                    "columnNameInFile": "Voltage (V)",
                    "columnNameInResult": "Voltage",
                    "unit": "V"
                },
                {
                    "columnNameInFile": "Current (A)",
                    "columnNameInResult": "Current",
                    "unit": "A"
                }
            ],
            computed_columns=[
                {
                    "inputColumnNames": ["Voltage", "Current"],
                    "function": "DIVIDE",
                    "computedColumnName": "Resistance",
                    "unit": "Ω"
                }
            ],
            metadata_expected=True,
            footer_expected=False
        )
        print("Your parser was created successfully!")
        print(f"Use it with the code [{parser["code"]}]")

    except HTTPError as exception:
        print("There was an error creating your parser, it was not created!")
        print(exception)


if __name__ == "__main__":
    main()
