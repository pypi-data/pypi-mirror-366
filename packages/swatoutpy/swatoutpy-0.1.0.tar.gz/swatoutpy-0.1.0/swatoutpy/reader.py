import pandas as pd
from pathlib import Path
from .utils import get_column_names


def read_rch(filepath: str, timestep: str = "monthly") -> pd.DataFrame:
    """
    Read SWAT2020 (v681) .rch output and return a cleaned DataFrame.

    Parameters:
    - filepath: Path to .rch file
    - timestep: 'monthly' or 'annual'

    Returns:
    - df: Cleaned pandas DataFrame with datetime index
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"{filepath} does not exist.")

    columns = get_column_names()["rch"]
    df = pd.read_csv(filepath, sep=r"\s+", skiprows=9, header=None, engine="python")
    df.columns = columns

    n_reaches = df["RCH"].nunique()

    # Always drop final summary rows (1 per reach)
    df = df.iloc[:-n_reaches].copy()

    if timestep == "monthly":
        # Detect simulation years (MON > 12)
        year_rows = df[df["MON"] > 12]
        sim_years = sorted(year_rows["MON"].unique())
        start_year, end_year = sim_years[0], sim_years[-1]

        # Remove annual rows
        df = df[df["MON"] <= 12].copy()
        df.reset_index(drop=True, inplace=True)

        # Create date list dynamically
        n_months = len(df) // n_reaches
        date_list = []

        year = int(start_year)
        month = 1

        for _ in range(n_months):
            date_list.extend([f"{int(year)}-{month:02d}-01"] * n_reaches)
            month += 1
            if month > 12:
                month = 1
                year += 1

        df["Date"] = pd.to_datetime(date_list, format="%Y-%m-%d")


        if len(date_list) != len(df):
            raise ValueError(f"Expected {len(df)} rows, but generated {len(date_list)} dates.")

        df["Date"] = pd.to_datetime(date_list)
        df.set_index("Date", inplace=True)

    elif timestep == "annual":
        df = df[df["MON"] > 12].copy()
        df["Date"] = pd.to_datetime(df["MON"].astype(int).astype(str), format="%Y")
        df.set_index("Date", inplace=True)

    else:
        raise ValueError("timestep must be 'monthly' or 'annual'.")

    return df


from datetime import datetime
import os
import pandas as pd
from swatoutpy.utils import get_column_names, get_column_widths

from datetime import datetime
import os
import pandas as pd
from swatoutpy.utils import get_column_names, get_column_widths

def read_sub(filepath, timestep="monthly"):
    """
    Read SWAT2020 .sub output file using fixed-width format.

    Args:
        filepath (str): Path to the .sub file (e.g., 'C:/.../output_monthly.sub').
        timestep (str): 'monthly' or 'annual'.

    Returns:
        pd.DataFrame: DataFrame with parsed SWAT SUB output.
    """
    # Step 1: Read all lines to find where data starts
    with open(filepath, "r") as f:
        lines = f.readlines()

    # Step 2: Find start of data (after column header)
    start_line = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("SUB"):
            start_line = i + 1
            break

    # Step 3: Retrieve column names and widths
    colnames = get_column_names()["sub"]
    widths = get_column_widths()["sub"]

    if len(widths) != len(colnames):
        raise ValueError("Mismatch in number of widths and column names")

    # Step 4: Read file with fixed-width formatting
    df = pd.read_fwf(filepath, skiprows=start_line, names=colnames, widths=widths)

    # Step 5: Type conversions
    df["SUB"] = df["SUB"].astype(int)
    df["GIS"] = df["GIS"].astype(int)

    n_subs = df["SUB"].nunique()
    n_rows = len(df)

    # Step 6: Determine simulation start year dynamically
    # Extract MON column and find rows where MON > 12 (yearly summaries)
    annual_rows = df[df["MON"] > 12]
    if not annual_rows.empty:
        start_year = int(annual_rows["MON"].min())
    else:
        raise ValueError("Could not detect start year from MON column.")

    # Step 7: Generate datetime column
    if timestep == "monthly":
        n_months = n_rows // n_subs
        dates = pd.date_range(start=f"{start_year}-01-01", periods=n_months, freq="MS")
        full_dates = sorted(dates.tolist() * n_subs)

        if len(full_dates) != len(df):
            raise ValueError(f"Mismatch in rows and generated dates. Got {len(df)} rows and {len(full_dates)} dates.")

        df["Date"] = full_dates

    elif timestep == "annual":
        n_years = n_rows // n_subs
        years = list(range(start_year, start_year + n_years))
        full_dates = sorted([datetime(y, 1, 1) for y in years] * n_subs)
        df["Date"] = full_dates

    else:
        raise ValueError("Invalid timestep. Use 'monthly' or 'annual'.")

    return df


from datetime import datetime
import pandas as pd
import os
from .utils import get_column_names, get_column_widths

def read_hru(filepath, timestep="monthly"):
    """
    Read SWAT2020 .hru output file using fixed-width format.

    Args:
        filepath (str): Path to the .hru file (e.g., 'C:/.../output_monthly.hru').
        timestep (str): 'monthly' or 'annual'.

    Returns:
        pd.DataFrame: DataFrame with parsed SWAT HRU output.
    """
    # Step 1: Read lines and find data start
    with open(filepath, "r") as f:
        lines = f.readlines()

    start_line = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("HRU") or line.strip().startswith("LULC"):
            start_line = i + 1
            break

    # Step 2: Column names and widths
    colnames = get_column_names()["hru"]
    widths = get_column_widths()["hru"]

    if len(colnames) != len(widths):
        raise ValueError("Mismatch between number of HRU column names and widths.")

    # Step 3: Read fixed-width data
    df = pd.read_fwf(filepath, skiprows=start_line, widths=widths, names=colnames)

    # Step 4: Parse dates
    n_hru = df["HRU"].nunique()
    n_rows = len(df)

    if timestep == "monthly":
        n_months = n_rows // n_hru

        # Detect start year from MON column
        annual_rows = df[df["MON"] > 12]
        if not annual_rows.empty:
            start_year = int(annual_rows["MON"].min())
        else:
            raise ValueError("Could not detect start year from MON column.")

        dates = pd.date_range(start=f"{start_year}-01-01", periods=n_months, freq="MS")
        full_dates = sorted(dates.tolist() * n_hru)

        if len(full_dates) != len(df):
            raise ValueError(f"Mismatch: {len(df)} rows vs {len(full_dates)} dates.")

        df["Date"] = full_dates

    elif timestep == "annual":
        annual_rows = df[df["MON"] > 12]
        if not annual_rows.empty:
            start_year = int(annual_rows["MON"].min())
        else:
            raise ValueError("Could not detect start year from MON column.")

        n_years = n_rows // n_hru
        years = list(range(start_year, start_year + n_years))
        df["Date"] = sorted([datetime(y, 1, 1) for y in years] * n_hru)

    else:
        raise ValueError("Invalid timestep. Use 'monthly' or 'annual'.")

    return df
