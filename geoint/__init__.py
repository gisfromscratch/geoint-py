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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from . import geospatial

def create_spatial_grid(spacing_meters):
    """
    Creates a new spatial grid using Web Mercator as spatial reference.
    """
    with geospatial.geospatial_engine_factory.create_cloud_engine() as geospatial_engine:
        return geospatial_engine.create_spatial_grid(spacing_meters)



def create_bins(spatial_grid, latitudes, longitudes):
    """
    Creates bins using a spatial grid and WGS84 coordinates.
    """
    with geospatial.geospatial_engine_factory.create_cloud_engine() as geospatial_engine:
        points = geospatial_engine.create_points(latitudes, longitudes)
        WGS84 = 4326
        if (WGS84 != spatial_grid.wkid()):
            # We need to reproject the points
            points = geospatial_engine.project(points, WGS84, spatial_grid.wkid())
        
        return geospatial_engine.aggregate(spatial_grid, points, spatial_grid.wkid())



def create_mercator_bins(spatial_grid, y, x):
    """
    Creates bins using a spatial grid and Web Mercator coordinates.
    """
    with geospatial.geospatial_engine_factory.create_cloud_engine() as geospatial_engine:
        points = geospatial_engine.create_points(y, x)
        WEB_MERCATOR = 3857
        if (WEB_MERCATOR != spatial_grid.wkid()):
            # We need to reproject the points
            raise ValueError('A spatial grid with a web mercator spatial reference was expected!')
        
        return geospatial_engine.aggregate(spatial_grid, points, spatial_grid.wkid())