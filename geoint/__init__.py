# geoint-py is a simple python module for geospatial intelligence workflows.
# Copyright (C) 2020 Jan Tschada (gisfromscratch@live.de)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http:#www.gnu.org/licenses/>.
#

import pandas as pd
from arcgis.features import Feature
from arcgis.features import FeatureSet
from arcgis.geometry import Envelope
from arcgis.geometry import intersect
from arcgis.geometry import Point
from arcgis.geometry import Polygon
from arcgis.geometry import project
from math import ceil, floor, isnan

def create_spatial_grid(spacing_meters):
    # Use WGS84
    envelope_wgs84 = Envelope({
        'xmin': -180.0, 
        'ymin': -90.0, 
        'xmax': 180.0, 
        'ymax': 90.0, 
        'spatialReference': {'wkid': 4326}
    })
    input_geometries = [envelope_wgs84]
    projected_geometries = project(input_geometries, in_sr='4326', out_sr='3857')
    envelope_mercator = projected_geometries[0]
    rows = int(ceil((envelope_mercator.ymax - envelope_mercator.ymin) / spacing_meters))
    columns = int(ceil((envelope_mercator.xmax - envelope_mercator.xmin) / spacing_meters)) - 1
    geometries = []
    for column in range(0, columns):
        for row in range(0, rows):
            recbin_mercator = Envelope({
                'xmin': envelope_mercator.xmin + (column * spacing_meters),
                'xmax': envelope_mercator.xmin + ((column + 1) * spacing_meters),
                'ymin': envelope_mercator.ymin + (row * spacing_meters),
                'ymax': envelope_mercator.ymin + ((row + 1) * spacing_meters),
                'spatialReference': {'wkid': 3857}
            })
            if columns == column + 1:
                recbin_mercator.xmax = envelope_mercator.xmax
            if rows == row + 1:
                recbin_mercator.ymax = envelope_mercator.ymax
                
            geometries.append(recbin_mercator.polygon)
    
    return geometries