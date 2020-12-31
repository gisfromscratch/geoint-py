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
    with geospatial.geospatial_engine_factory.create_cloud_engine() as geospatial_engine:
        return geospatial_engine.create_spatial_grid(spacing_meters)



def create_bins(spatial_gid, latitudes, longitudes):
    with geospatial.geospatial_engine_factory.create_cloud_engine() as geospatial_engine:
        points = geospatial_engine.create_points(latitudes, longitudes)
        WGS84 = 4326
        if (WGS84 != spatial_gid.wkid()):
            # We need to reproject the points
            points = geospatial_engine.project(points, WGS84, spatial_gid.wkid())
        
        return geospatial_engine.aggregate(spatial_gid, points, spatial_gid.wkid())