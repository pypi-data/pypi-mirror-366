"""
Utilities for converting values into human-readable formats.
"""

def humanbytes(B, decimal: bool = False, sigfig: int = 2, strict_iec: bool = True):
    """Convert bytes to human-readable string format.

    Converts byte sizes into human-readable strings with appropriate unit prefixes.
    Supports both binary (1024-based) and decimal (1000-based) units, with options
    for IEC standard binary prefixes (Ki, Mi, etc) or traditional prefixes (K, M, etc).

    Args:
        B (int/float): Number of bytes to convert
        decimal (bool, optional): If True, uses 1000 as base (SI standard).
            If False, uses 1024 as base (Binary/IEC).
            Defaults to False.
        sigfig (int, optional): Number of decimal places to show in output.
            Defaults to 2.
        strict_iec (bool, optional): If True and decimal=False, uses IEC standard
            binary prefixes (KiB, MiB, etc).
            If False or decimal=True, uses SI prefixes (KB, MB, etc).
            Defaults to True.

    Returns:
        str: Formatted string with value and unit.
            Examples: "1.00 KiB", "2.50 MB", "1 Byte", "1024 Bytes"

    Unit Behavior:
        - decimal=True:  Uses 1000 as base with SI prefixes (KB, MB, GB, ...)
        - decimal=False, strict_iec=True:  Uses 1024 as base with IEC prefixes (KiB, MiB, GiB, ...)
        - decimal=False, strict_iec=False: Uses 1024 as base with SI prefixes (KB, MB, GB, ...)

    Available Units:
        Bytes → KB/KiB → MB/MiB → GB/GiB → TB/TiB → PB/PiB → 
        EB/EiB → ZB/ZiB → YB/YiB → RB/RiB → QB/QiB
    """
    # Define base unit and multipliers
    base = 1000 if decimal else 1024
    
    # Define units based on decimal/binary and IEC strictness
    si_units = ['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y', 'R', 'Q']
    if not decimal and strict_iec:
        # IEC binary units (KiB, MiB, etc)
        units = {
            0: ('Byte', 'Bytes'),
            **{i: f"{unit}iB" for i, unit in enumerate(si_units, 1)}
        }
    else:
        # SI decimal units (KB, MB, etc) or non-strict binary
        units = {
            0: ('Byte', 'Bytes'),
            **{i: f"{unit}B" for i, unit in enumerate(si_units, 1)}
        }
    
    # Calculate the appropriate unit level
    level = 0
    value = float(B)
    while value >= base and level < max(units.keys()):
        value /= base
        level += 1
    
    # Handle special case for bytes
    unit = units[0][0] if level == 0 and B == 1 else (units[0][1] if level == 0 else units[level])
        
    return f"{value:.{sigfig}f} {unit}"
