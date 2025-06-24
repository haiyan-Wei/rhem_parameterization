# RHEM Parameterization Tool
A Python tool for generating RHEM (Rangeland Hydrology and Erosion Model) parameter files from input data. 

## Input Format

Check out inputs/rhem_inputs.csv for the example input format.
Your CSV should include columns for:
- HillslopeID
- Ground cover percentages (GroundRock, GroundLitter, GroundBasal, GroundCrust)
- Foliar cover percentages (FoliarSod, FoliarBunch, FoliarForbAnnual, FoliarShrub)
- Slope in percentage
- Slope Length
- Soil texture

## Files

- run.py - Main script to execute
- inputs/rhem_inputs.csv - Example input format
- data/ - Reference lookup tables for RHEM calculations
- requirements.txt - Python dependencies