"""
Generator module for vgrid.

This module provides functions to generate discrete global grid systems (DGGS)
for various coordinate systems and geographic areas.
"""

import platform

# Main grid generation functions
from .h3grid import h3grid, h3_grid, h3_grid_within_bbox, h3_grid_resample
from .s2grid import s2grid, s2_grid, s2_grid_resample
from .a5grid import a5grid, a5_grid
from .rhealpixgrid import rhealpixgrid, rhealpix_grid, rhealpix_grid_within_bbox, rhealpix_grid_resample

# ISEA grid functions (uncommented)
from .isea4tgrid import isea4tgrid, isea4t_grid, isea4t_grid_within_bbox, isea4t_grid_resample
from .isea3hgrid import isea3hgrid, isea3h_grid, isea3h_grid_within_bbox

from .easegrid import easegrid, ease_grid, ease_grid_within_bbox
from .qtmgrid import qtmgrid, qtm_grid, qtm_grid_within_bbox, qtm_grid_resample
from .olcgrid import olcgrid, olc_grid, olc_grid_within_bbox, olc_grid_resample
from .geohashgrid import geohashgrid, geohash_grid, geohash_grid_within_bbox, geohash_grid_resample
from .georefgrid import georefgrid, georef_grid
from .mgrsgrid import mgrsgrid, mgrs_grid
from .tilecodegrid import tilecodegrid, tilecode_grid, tilecode_grid_resample
from .quadkeygrid import quadkeygrid, quadkey_grid, quadkey_grid_resample
from .maidenheadgrid import maidenheadgrid, maidenhead_grid, maidenhead_grid_within_bbox
from .garsgrid import garsgrid, gars_grid, gars_grid_within_bbox
from .settings import (
    MAX_CELLS, CHUNK_SIZE, ISEA4T_BASE_CELLS, ISEA3H_BASE_CELLS,
    ISEA4T_RES_ACCURACY_DICT, ISEA3H_RES_ACCURACY_DICT, ISEA3H_ACCURACY_RES_DICT,
    MGRS_GZD_LON_DICT, MGRS_GZD_LAT_DICT
)

__all__ = [
    # Main grid functions
    'h3grid', 's2grid', 'a5grid', 'rhealpixgrid', 'isea4tgrid', 'isea3hgrid',
    'easegrid', 'qtmgrid', 'olcgrid', 'geohashgrid', 'georefgrid', 'mgrsgrid',
    'tilecodegrid', 'quadkeygrid', 'maidenheadgrid', 'garsgrid',
    # Grid generation with specific parameters
    'h3_grid', 'h3_grid_within_bbox', 'h3_grid_resample',
    's2_grid', 's2_grid_resample', 
    'a5_grid', 
    'rhealpix_grid', 'rhealpix_grid_within_bbox', 'rhealpix_grid_resample',
    'isea4t_grid', 'isea4t_grid_within_bbox', 'isea4t_grid_resample',
    'isea3h_grid', 'isea3h_grid_within_bbox', 
    'ease_grid', 'ease_grid_within_bbox',
    'qtm_grid', 'qtm_grid_within_bbox', 'qtm_grid_resample',
    'olc_grid', 'olc_grid_within_bbox', 'olc_grid_resample',
    'geohash_grid', 'geohash_grid_within_bbox', 'geohash_grid_resample',
    'georef_grid',  
    'mgrs_grid',  
    'tilecode_grid', 'tilecode_grid_resample',
    'quadkey_grid', 'quadkey_grid_resample',
    'maidenhead_grid', 'maidenhead_grid_within_bbox',
    'gars_grid', 'gars_grid_within_bbox',   
]
__all__ += [
    'MAX_CELLS', 'CHUNK_SIZE', 'ISEA4T_BASE_CELLS', 'ISEA3H_BASE_CELLS',
    'ISEA4T_RES_ACCURACY_DICT', 'ISEA3H_RES_ACCURACY_DICT', 'ISEA3H_ACCURACY_RES_DICT',
    'MGRS_GZD_LON_DICT', 'MGRS_GZD_LAT_DICT'
]
