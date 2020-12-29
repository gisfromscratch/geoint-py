# Copyright 2020 Jan Tschada
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

from arcgis.gis import GIS
from arcgis.geometry import Envelope
from arcgis.geometry import project as ago_project
from math import ceil

class spatial_grid:
    """
    Represents a spatial grid.
    """
    def __init__(self, geometries):
        self._geometries = geometries



class rectangular_spatial_grid(spatial_grid):
    """
    Represents a rectangular spatial grid.
    """

    def __init__(self, geometries):
        super().__init__(geometries)



class geospatial_engine:
    """
    Represents a geospatial engine offering geospatial operations.
    """

    def create_spatial_grid(self, spacing_meters):
        """
        Create a spatial grid with the defined grid cell size in meters.
        """
        raise NotImplementedError

    def project(self, geometries, in_sr, out_sr):
        """
        Projects the list of geometries from in_sr into out_sr.
        """
        raise NotImplementedError



class ago_geospatial_engine(geospatial_engine):
    """
    Represents a geospatial engine using ArcGIS Online.
    """

    def __init__(self):
        super().__init__()
        self.gis = GIS()

    def create_spatial_grid(self, spacing_meters):
        # Use WGS84
        envelope_wgs84 = Envelope({
            'xmin': -180.0, 
            'ymin': -90.0, 
            'xmax': 180.0, 
            'ymax': 90.0, 
            'spatialReference': {'wkid': 4326}
        })
        input_geometries = [envelope_wgs84]
        projected_geometries = self.project(input_geometries, in_sr='4326', out_sr='3857')
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
                    
                geometries.append(recbin_mercator)

                # Creating a polygon takes some time
                #geometries.append(recbin_mercator.polygon)
        
        return rectangular_spatial_grid(geometries)
    
    def project(self, geometries, in_sr, out_sr):
        return ago_project(geometries, in_sr, out_sr)



class geospatial_engine_factory:
    """
    Represents a factory creating different geospatial engines.
    """

    @staticmethod
    def create_cloud_engine():
        """
        Creates a geospatial engine using ArcGIS Online.
        """
        return ago_geospatial_engine()