"""
GEOREF DGGS Grid Generator Module
"""
import json
import argparse
from tqdm import tqdm
from shapely.geometry import Polygon, box
import numpy as np
from vgrid.dggs import georef
from vgrid.generator.settings import MAX_CELLS
from vgrid.utils.geometry import graticule_dggs_to_geoseries
from vgrid.utils.io import convert_to_output_format
import geopandas as gpd
from shapely.geometry import shape

RESOLUTION_DEGREES = {
    0: 15.0,  # 15° x 15°
    1: 1.0,  # 1° x 1°
    2: 1 / 60,  # 1-minute
    3: 1 / 600,  # 0.1-minute
    4: 1 / 6000,  # 0.01-minute
}

# RESOLUTION_DEGREES = {
#     0: 15.0,       # 15° x 15°
#     1: 1.0,        # 1° x 1°
#     2: 1 / 60,     # 1-minute
#     3: 1 / 600,    # 0.1-minute
#     5: 1 / 6000,   # 0.01-minute
#     5: 1 / 60_000,  # 0.001-minute
#     # 5: 1 / 600_000  # 0.0001-minute
# }


def generate_grid(bbox, resolution):
    lon_min, lat_min, lon_max, lat_max = bbox
    resolution_degrees = RESOLUTION_DEGREES[resolution]
    longitudes = np.arange(lon_min, lon_max, resolution_degrees)
    latitudes = np.arange(lat_min, lat_max, resolution_degrees)
    num_cells = len(longitudes) * len(latitudes)

    print(f"Resolution {resolution} will generate {num_cells} cells ")
    if num_cells > MAX_CELLS:
        print(f"which exceeds the limit of {MAX_CELLS}.")
        print("Please select a smaller resolution and try again.")
        return
    georef_records = []

    with tqdm(total=num_cells, desc="Generating GEOREF DGGS", unit=" cells") as pbar:
        for lon in longitudes:
            for lat in latitudes:
                cell_polygon = Polygon(
                    box(lon, lat, lon + resolution_degrees, lat + resolution_degrees)
                )
                georef_id = georef.encode(lat, lon, resolution)
                georef_record = graticule_dggs_to_geoseries(
                    "georef", georef_id, resolution, cell_polygon
                )
                georef_records.append(georef_record)
                pbar.update(1)

    return gpd.GeoDataFrame(georef_records, geometry="geometry", crs="EPSG:4326")


def georefgrid(resolution, bbox=None, output_format=None):
    """
    Generate GEOREF grid for pure Python usage.

    Args:
        resolution (int): GEOREF resolution [0..4]
        bbox (list, optional): Bounding box [min_lon, min_lat, max_lon, max_lat]. Defaults to None (whole world).
        output_format (str, optional): Output format ('geojson', 'csv', 'geo', 'gpd', 'shapefile', 'gpkg', 'parquet', or None for list of GEOREF IDs).

    Returns:
        dict, list, or str: Output in the requested format or file path.
    """
    if resolution < 0 or resolution > 4:
        raise ValueError("Resolution must be in range [0..4]")
    if bbox is None:
        bbox = [-180, -90, 180, 90]
    gdf = generate_grid(bbox, resolution)
    base_name = f"georef_grid_{resolution}"
    if output_format is None:
        return gdf.to_dict(orient="records")
    elif output_format in ["gpd", "geo"]:
        return gdf
    elif output_format == "geojson_dict":
        return gdf.__geo_interface__
    elif output_format == "geojson":
        output_name = base_name + ".geojson"
        geojson = gdf.__geo_interface__
        with open(output_name, "w", encoding="utf-8") as f:
            json.dump(geojson, f, indent=2)

        return output_name
    elif output_format == "csv":
        output_name = base_name + ".csv"
        return convert_to_output_format(gdf, output_format, output_name=output_name)
    elif output_format == "shapefile":
        output_name = base_name + ".shp"
        return convert_to_output_format(gdf, output_format, output_name=output_name)
    elif output_format == "gpkg":
        output_name = base_name + ".gpkg"
        return convert_to_output_format(gdf, output_format, output_name=output_name)
    elif output_format in ["geoparquet", "parquet"]:
        output_name = base_name + ".parquet"
        return convert_to_output_format(gdf, output_format, output_name=output_name)
    else:
        return convert_to_output_format(gdf, output_format)


def georefgrid_cli():
    parser = argparse.ArgumentParser(description="Generate GEOREF DGGS")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="Resolution [0..4]"
    )
    parser.add_argument(
        "-b",
        "--bbox",
        type=float,
        nargs=4,
        help="Bounding box in the format: min_lon min_lat max_lon max_lat (default is the whole world)",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=["geojson", "csv", "geo", "gpd", "shapefile", "gpkg", "parquet", None],
        default=None,
        help="Output format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of GEOREF IDs)",
    )
    args = parser.parse_args()
    if args.output_format == "None":
        args.output_format = None
    try:
        result = georefgrid(args.resolution, args.bbox, args.output_format)
        if result is None:
            return
        if args.output_format is None:
            print(result)
        elif args.output_format in ["geo", "gpd"]:
            print(result)
        elif args.output_format in ["csv", "parquet", "gpkg", "shapefile", "geojson"] and isinstance(result, str):
            print(f"Output saved as {result}")
        elif args.output_format == "geojson" and isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(f"Output saved in current directory.")
    except ValueError as e:
        print(f"Error: {str(e)}")
        return


if __name__ == "__main__":
    georefgrid_cli()
