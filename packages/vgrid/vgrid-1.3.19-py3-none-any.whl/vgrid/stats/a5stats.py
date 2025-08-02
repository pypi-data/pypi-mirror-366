"""
This module provides functions for generating statistics for A5 DGGS cells.
"""
import locale
import argparse
import csv
import math
from texttable import Texttable
from a5.core.cell_info import get_num_cells, cell_area
from pyproj import Geod
geod = Geod(ellps="WGS84")

locale.setlocale(locale.LC_ALL, "")


def a5_metrics(res):
    num_cells = get_num_cells(res)
    avg_area = cell_area(res)
    k = math.sqrt(5*(5+2*math.sqrt(5)))
    avg_edge_length = round(math.sqrt(4*avg_area/k), 3)
    return num_cells, avg_edge_length, avg_area


def a5stats(output_file=None):
    """
    Generate statistics for A5 DGGS cells.
    """
    min_res = 0
    max_res = 29
    # Create a Texttable object for displaying in the terminal
    t = Texttable()

    # Add header to the table, including the new 'Cell Width' and 'Cell Area' columns
    t.add_row(
        ["Resolution", "Number of Cells", "Avg Edge Length (m)", "Avg Cell Area (sq m)"]
    )

    # Check if an output file is specified (for CSV export)
    if output_file:
        # Open the output CSV file for writing
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Resolution",
                    "Number of Cells",
                    "Avg Edge Length (m)",
                    "Avg Cell Area (sq m)",
                ]
            )
            for res in range(min_res, max_res + 1):
                num_cells, avg_edge_length, avg_area = a5_metrics(res)
                writer.writerow([res, num_cells, avg_edge_length, avg_area])
    else:
        for res in range(min_res, max_res + 1):
            num_cells, avg_edge_length, avg_area = a5_metrics(res)
            formatted_num_cells = locale.format_string("%d", num_cells, grouping=True)
            formatted_length = locale.format_string(
                "%.3f", avg_edge_length, grouping=True
            )
            formatted_area = locale.format_string("%.3f", avg_area, grouping=True)

            t.add_row([res, formatted_num_cells, formatted_length, formatted_area])

        print(t.draw())


def a5stats_cli():
    """
    Command-line interface for generating A5 DGGS statistics.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Export or display A5 DGGS stats.")
    parser.add_argument("-o", "--output", help="Output CSV file name.")
    args = parser.parse_args()

    # Call the function with the provided output file (if any)
    a5stats(args.output)


if __name__ == "__main__":
    a5stats_cli()
