"""
analysis.py

This module handles analysis and processing of measurement data, such as emission spectra.
It includes functions to detect peaks in measurement files and upload the results
back to the MaterialsZone platform.

You can use this after uploading your experiment items to automatically extract
meaningful results from CSV files and attach them to the right items.
"""

import os
import glob
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from mz_operations import create_measurement, update_item

MEASUREMENT_FOLDER = "measurements"  # Folder containing measurement CSV files

def find_emission_spectrum_peak_wavelength(file_path: str) -> float | None:
    """Return the peak wavelength from an emission spectrum CSV file, or None if not found."""
    df = pd.read_csv(file_path)
    x = df.iloc[:, 0].values
    y = df.iloc[:, 1].values

    # Simple peak detection
    peaks, _ = find_peaks(y)
    peak_x = x[peaks[np.argmax(y[peaks])]] if len(peaks) > 0 else None

    return peak_x

def upload_emission_spectrum_measurements(exp_col_param_map: dict[str, str], experiments_ids_map: dict[str, str]):
    """Analyze emission spectrum files, extract peak wavelengths, upload results and raw measurements."""
    for file_path in glob.glob(f"{MEASUREMENT_FOLDER}/experiment_*_measurement.csv"):
        peak_x = find_emission_spectrum_peak_wavelength(file_path)

        # Match file to experiment
        name = os.path.basename(file_path).split("_")[1]  # e.g., "01" from "experiment_01_measurement.csv"
        experiment_title = f"QD_EXP_{int(name):02d}"

        # Upload the analysis result as an item value
        if peak_x is not None:
            values = [{"parameterId": exp_col_param_map["Peak Wavelength (nm)"], "value": str(peak_x)}]
            update_item(experiments_ids_map[experiment_title], values)
            parser_code = "PL-AG-E-CC"
            file = (os.path.basename(file_path), open(file_path, "rb"), "text/csv")
            measurement_title = "Emission Spectrum"
            create_measurement(experiments_ids_map[experiment_title], measurement_title, parser_code, file)
