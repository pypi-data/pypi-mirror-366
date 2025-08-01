# swatoutpy

A lightweight Python package to read and parse SWAT model (Rev 681) output files: `.rch`, `.sub`, and `.hru`.

## Installation

```bash
pip install swatoutpy


from swatoutpy.reader import read_rch

df = read_rch("output_monthly.rch", timestep="monthly")
print(df.head())
