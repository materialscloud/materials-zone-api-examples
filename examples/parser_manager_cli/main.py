"""
main.py

This is the main script that runs the full example workflow.

It contains examples on how to use the parser APIs.
For additional examples and information, please go to https://developer.materials.zone/
"""
import json

from requests import HTTPError

from mz_operations import (
    get_all_parsers,
    create_parser,
    update_parser,
    delete_parser,
)


EXAMPLE_PARSER_CONFIG_PATH = "new_parsers/keithley_iv.json"


def find_parser_by_code(all_parsers: list, parser_code: str) -> dict | None:
    return next(
        (parser for parser in all_parsers if parser.get("code") == parser_code),
        None
    )


def print_parsers(title: str, group: list[dict]) -> None:
    print(f"{title} ({len(group)})")
    for index, parser in enumerate(group, start=1):
        code = parser.get("code", "N/A")
        name = parser.get("name", "N/A")
        print(f"  - {index}. {code} | {name}")


def format_value(key: str, value: object) -> str:
    if value in (None, [], {}):
        return "N/A"
    if key == "supportedFileExtensions" and isinstance(value, list):
        return ", ".join(value)
    if key in ("configurationColumns", "computedColumns") and isinstance(value, list):
        formatted_rows: list[str] = []
        for index, item in enumerate(value, start=1):
            if key == "configurationColumns":
                entry = [
                    f"{index}. columnNameInFile: {item.get('columnNameInFile', 'N/A')}",
                    f"   columnIndexInFile: {item.get('columnIndexInFile', 'N/A')}",
                    f"   columnNameInResult: {item.get('columnNameInResult', 'N/A')}",
                    f"   unit: {item.get('unit', 'N/A')}",
                ]
            else:
                entry = [
                    f"{index}. inputColumnNames: {item.get('inputColumnNames', 'N/A')}",
                    f"   computedColumnName: {item.get('computedColumnName', 'N/A')}",
                    f"   function: {item.get('function', 'N/A')}",
                    f"   unit: {item.get('unit', 'N/A')}",
                ]
            formatted_rows.append("\n".join(entry))
        return "\n".join(formatted_rows)
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2)
    return str(value)


def load_parser_config(action: str) -> dict | None:
    parser_config_path = input(
        f"Enter the path to the parser configuration JSON for {action} "
        f"(leave blank for {EXAMPLE_PARSER_CONFIG_PATH}): "
    ).strip() or EXAMPLE_PARSER_CONFIG_PATH

    try:
        with open(parser_config_path, "r", encoding="utf-8") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        print("Parser configuration file was not found.")
    except json.JSONDecodeError as exception:
        print("Parser configuration file is not valid JSON.")
        print(exception)
    return None


while True:
    try:
        all_parsers = get_all_parsers()
    except HTTPError as exception:
        print("There was an error retrieving the parsers!")
        print(exception)
        break

    sorted_parsers = sorted(
        all_parsers,
        key=lambda parser: parser.get("systemParser", False)
    )
    organization_parsers = [
        parser for parser in sorted_parsers
        if not parser.get("systemParser", False)
    ]
    system_parsers = [
        parser for parser in sorted_parsers
        if parser.get("systemParser", False)
    ]

    print("\n1. Show my organization parsers")
    print("2. Show system parsers")
    print("3. Show parser details")
    print("4. Create a new parser")
    print("5. Update a parser")
    print("6. Delete a parser")
    print("7. Quit")
    choice = input("Choose an option: ").strip()

    if choice == "7":
        print("Goodbye!")
        break

    if choice == "1":
        print_parsers("Organization Parsers", organization_parsers)
        continue

    if choice == "2":
        print_parsers("System Parsers", system_parsers)
        continue

    if choice == "3":
        parser_code = input("Enter the parser code: ").strip()
        parser = find_parser_by_code(all_parsers, parser_code)
        if parser is None:
            print("No parser with that code was found.")
            continue
        indent = "  "
        fields = [
            ("code", "Code", parser),
            ("name", "Name", parser),
            ("description", "Description", parser),
            ("physicalMeasurement", "Physical Measurement", parser),
            ("instrumentManufacturer", "Instrument Manufacturer", parser),
            ("instrumentModel", "Instrument Model", parser),
            ("supportedFileExtensions", "Supported File Extensions", parser),
            ("viewType", "View Type", parser)
        ]
        parser_configuration = parser.get("parserConfiguration") or {}
        if parser_configuration:
            fields += [
                ("configurationColumns", "Configuration Columns", parser_configuration),
                ("computedColumns", "Computed Columns", parser_configuration),
                ("metadataExpected", "Metadata Expected", parser_configuration),
                ("footerExpected", "Footer Expected", parser_configuration),
            ]

        for index, (key, label, source) in enumerate(fields):
            formatted_value = format_value(key, source.get(key))
            if "\n" in formatted_value:
                print(f"{indent}{label}:")
                for line in formatted_value.splitlines():
                    print(f"{indent}  {line}")
            else:
                print(f"{indent}{label}: {formatted_value}")
        continue

    if choice == "4":
        parser_config = load_parser_config("creating a parser")
        if parser_config is None:
            continue

        try:
            parser = create_parser(parser_config)
            print("Your parser was created successfully!")
            print(f"Use it with the code [{parser["code"]}]")

        except HTTPError as exception:
            print("There was an error creating your parser, it was not created!")
            print(exception)
        continue

    if choice == "5":
        parser_code = input("Enter the parser code to update: ").strip()
        parser_to_update = find_parser_by_code(all_parsers, parser_code)
        if parser_to_update is None:
            print("No parser with that code was found.")
            continue

        parser_config = load_parser_config("updating the parser")
        if parser_config is None:
            continue

        try:
            update_parser(parser_to_update["id"], parser_config)
            print("Parser updated successfully.")
        except HTTPError as exception:
            print("There was an error updating the parser!")
            print(exception)
        continue

    if choice == "6":
        parser_code = input("Enter the parser code to delete: ").strip()
        parser_to_delete = find_parser_by_code(all_parsers, parser_code)
        if parser_to_delete is None:
            print("No parser with that code was found.")
            continue

        try:
            delete_parser(parser_to_delete["id"])
        except HTTPError as exception:
            print("There was an error deleting the parser!")
            print(exception)
            continue

        print("Parser deleted successfully.")
        continue

    print("Invalid choice")
