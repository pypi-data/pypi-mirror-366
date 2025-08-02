"""
Tilecode DGGS Grid Generator Module
"""

import argparse
import json
from shapely.geometry import shape, Polygon
from tqdm import tqdm
from shapely.ops import unary_union
from vgrid.dggs import mercantile
from vgrid.generator.settings import MAX_CELLS
from vgrid.utils.geometry import graticule_dggs_to_geoseries
from vgrid.utils.io import convert_to_output_format


def generate_grid(resolution, bbox):
    tilecode_records = []
    min_lon, min_lat, max_lon, max_lat = (
        bbox  # or [-180.0, -85.05112878,180.0,85.05112878]
    )
    tiles = mercantile.tiles(min_lon, min_lat, max_lon, max_lat, resolution)

    for tile in tqdm(tiles, desc="Generating Tilecode DGGS", unit=" cells"):
        z, x, y = tile.z, tile.x, tile.y
        tilecode_id = f"z{tile.z}x{tile.x}y{tile.y}"
        bounds = mercantile.bounds(x, y, z)
        if bounds:
            # Create the bounding box coordinates for the polygon
            min_lat, min_lon = bounds.south, bounds.west
            max_lat, max_lon = bounds.north, bounds.east

            cell_polygon = Polygon(
                [
                    [min_lon, min_lat],  # Bottom-left corner
                    [max_lon, min_lat],  # Bottom-right corner
                    [max_lon, max_lat],  # Top-right corner
                    [min_lon, max_lat],  # Top-left corner
                    [min_lon, min_lat],  # Closing the polygon (same as the first point)
                ]
            )
            tilecode_record = graticule_dggs_to_geoseries(
                "tilecode", tilecode_id, resolution, cell_polygon
            )
            tilecode_records.append(tilecode_record)

    import geopandas as gpd
    return gpd.GeoDataFrame(tilecode_records, geometry="geometry", crs="EPSG:4326")


def generate_grid_resample(resolution, geojson_features):
    tilecode_records = []

    geometries = [
        shape(feature["geometry"]) for feature in geojson_features["features"]
    ]
    unified_geom = unary_union(geometries)

    min_lon, min_lat, max_lon, max_lat = unified_geom.bounds

    tiles = mercantile.tiles(min_lon, min_lat, max_lon, max_lat, resolution)

    # Step 4: Filter by actual geometry intersection
    for tile in tqdm(tiles, desc="Generating Tilecode DGGS", unit=" cells"):
        z, x, y = tile.z, tile.x, tile.y
        tilecode_id = f"z{z}x{x}y{y}"
        bounds = mercantile.bounds(x, y, z)

        # Build tile polygon
        tile_polygon = Polygon(
            [
                [bounds.west, bounds.south],
                [bounds.east, bounds.south],
                [bounds.east, bounds.north],
                [bounds.west, bounds.north],
                [bounds.west, bounds.south],
            ]
        )

        # Check if tile polygon intersects the input geometry
        if tile_polygon.intersects(unified_geom):
            tilecode_record = graticule_dggs_to_geoseries(
                "tilecode", tilecode_id, resolution, tile_polygon
            )
            tilecode_records.append(tilecode_record)

    return gpd.GeoDataFrame(tilecode_records, geometry="geometry", crs="EPSG:4326")


def tilecodegrid(resolution, bbox=None, output_format=None, output_path=None):
    """
    Generate Tilecode grid for pure Python usage.

    Args:
        resolution (int): Tilecode resolution [0..26]
        bbox (list, optional): Bounding box [min_lon, min_lat, max_lon, max_lat]. Defaults to None (whole world).
        output_format (str, optional): Output format ('geojson', 'csv', etc.). Defaults to None (list of Tilecode IDs).
        output_path (str, optional): Output file path. Defaults to None.

    Returns:
        dict, list, or str: Output depending on output_format
    """
    if resolution < 0 or resolution > 26:
        raise ValueError("Resolution must be in range [0..26]")

    if bbox is None:
        bbox = [-180.0, -85.05112878, 180.0, 85.05112878]
        num_cells = 4 ** resolution
        if num_cells > MAX_CELLS:
            raise ValueError(
                f"Resolution {resolution} will generate {num_cells} cells which exceeds the limit of {MAX_CELLS}"
            )
        gdf = generate_grid(resolution, bbox)
    else:
        gdf = generate_grid(resolution, bbox)

    return convert_to_output_format(gdf, output_format, output_path)


def tilecodegrid_cli():
    parser = argparse.ArgumentParser(description="Generate Tilecode DGGS.")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="resolution [0..26]"
    )
    parser.add_argument(
        "-b",
        "--bbox",
        type=float,
        nargs=4,
        help="Bounding box in the output_format: min_lon min_lat max_lon max_lat (default is the whole world)",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=["geojson", "csv", "geo", "gpd", "shapefile", "gpkg", "parquet", None],
        default=None,
        help="Output output_format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of Tilecode IDs)",
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Output file path (optional)", default=None
    )
    args = parser.parse_args()
    if args.output_format == "None":
        args.output_format = None
    resolution = args.resolution
    bbox = args.bbox if args.bbox else [-180.0, -85.05112878, 180.0, 85.05112878]
    if resolution < 0 or resolution > 26:
        print("Please select a resolution in [0..26] range and try again ")
        return
    if bbox == [-180.0, -85.05112878, 180.0, 85.05112878]:
        num_cells = 4**resolution
        if num_cells > MAX_CELLS:
            print(f"Resolution {resolution} will generate {num_cells} cells "
                  f"which exceeds the limit of {MAX_CELLS}.")
            print("Please select a smaller resolution and try again.")
            return
    gdf = generate_grid(resolution, bbox)
    try:
        result = convert_to_output_format(gdf, args.output_format, args.output)
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
            print(f"Output saved as {args.output}")
    except ValueError as e:
        print(f"Error: {str(e)}")
        return


if __name__ == "__main__":
    tilecodegrid_cli()
