# core/standards/spwla.py

def validate_version_section(las):
    """
    SPWLA Section 2.3.1 compliance: requires VERS, WRAP, DLM in the Version section.
    Returns a list of missing keys, or None if all present.
    """
    required = ['VERS', 'WRAP', 'DLM']
    missing = [req for req in required if req not in las.sections.get('Version', {})]
    return missing if missing else None

def validate_gr_curve(curve_data):
    """
    Checks if GR curve values exceed 200 API.
    Returns an error message if so, or None otherwise.
    """
    # Don’t use bare truthiness on arrays—check length explicitly.
    if curve_data is None or len(curve_data) == 0:
        return "GR curve data is empty"

    max_val = max(curve_data)
    if max_val > 200:
        return f"GR exceeds 200 API: max={max_val}"
    return None
