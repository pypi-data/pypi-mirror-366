#!/usr/bin/env python
import argparse
import sys

__all__ = ['validate_las', 'display_errors', 'main']

def validate_las(file_path: str):
    """
    Validate a LAS file and return a list of error messages.
    """
    errors = []
    try:
        with open(file_path, 'r', encoding='ascii') as f:
            lines = f.readlines()
    except Exception as e:
        errors.append(f"Error opening file: {e}")
        return errors

    # 1) Missing VERS
    if not any('VERS.' in l.upper() for l in lines):
        errors.append("Missing version items: ['VERS']")

    # 2) GR anomaly (>200)
    max_val = None
    for l in lines:
        if l.strip().startswith('~'):
            continue
        parts = l.split()
        if len(parts) < 2:
            continue
        try:
            v = float(parts[1])
        except ValueError:
            continue
        if max_val is None or v > max_val:
            max_val = v
    if max_val is not None and max_val > 200:
        errors.append(f"GR exceeds 200 API: max={max_val}")
        errors.append("GR anomaly detected")

    # 3) Curve mnemonic & unit
    curve_section = False
    found_gr = False
    gr_unit = None
    for l in lines:
        if l.lstrip().upper().startswith('~CURVE'):
            curve_section = True
            continue
        if curve_section:
            if not l.strip() or l.strip().startswith('~'):
                break
            parts = l.split()
            mnem = parts[0].split('.')[0].upper()
            if mnem == 'GR':
                found_gr = True
                if len(parts) >= 2:
                    gr_unit = parts[1].lstrip('.').upper()
                break
    if not found_gr:
        errors.append("Curve mnemonic mismatch: expected GR mnemonic")
    elif gr_unit != 'GAPI':
        errors.append(f"GR unit mismatch: found {gr_unit}")

    # 4) NULL value
    well_section = False
    null_val = None
    for l in lines:
        if l.lstrip().upper().startswith('~WELL'):
            well_section = True
            continue
        if well_section:
            if not l.strip() or l.strip().startswith('~'):
                break
            parts = l.split()
            key = parts[0].split('.')[0].upper()
            if key == 'NULL':
                null_val = parts[1]
                break
    if null_val is not None and null_val != '-999.25':
        errors.append(f"NULL value mismatch: found {null_val}")

    return errors


def display_errors(errors):
    try:
        from rich.console import Console
        from rich.table import Table
        console = Console()
        if not errors:
            console.print("✅ [green]Valid LAS file[/green]")
            return
        table = Table(title="Validation Errors")
        table.add_column("Error", style="red")
        for err in errors:
            table.add_row(err)
        console.print(table)
    except ImportError:
        if not errors:
            print("✅ Valid LAS file")
        else:
            for err in errors:
                print(err)


def main():
    parser = argparse.ArgumentParser(
        prog='geolapis-core',
        description='Validate LAS files against GeolapisCore standards.'
    )
    parser.add_argument('las_file',
                        metavar='LAS_FILE',
                        type=str,
                        help='Path to the LAS file to validate')
    args = parser.parse_args()

    errors = validate_las(args.las_file)
    display_errors(errors)
    sys.exit(0 if not errors else 2)


if __name__ == "__main__":
    main()
