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

from arcgis.gis import GIS
from arcgis.geometry import Envelope, Point, Polygon, SpatialReference
from arcgis.geometry import project as ago_project
from arcgis.geometry.functions import relation as ago_relation
import itertools
from math import ceil



class grid_cell:
    """
    Represents a rectangular spatial grid cell.
    """
    def __init__(self, xmin, ymin, xmax, ymax, wkid):
        self._xmin = xmin
        self._ymin = ymin
        self._xmax = xmax
        self._ymax = ymax
        self._wkid = wkid

    def as_ring(self):
        return [
            [self._xmin, self._ymin],
            [self._xmin, self._ymax],
            [self._xmax, self._ymax],
            [self._xmax, self._ymin],
            [self._xmin, self._ymin]
            ]



class spatial_grid:
    """
    Represents a spatial grid.
    """
    def __init__(self, cells):
        self._cells = cells

    def cells_as_rings(self):
        """
        Returns all cells as a ring array used for constructing polygons.
        """
        raise NotImplementedError



class rectangular_spatial_grid(spatial_grid):
    """
    Represents a rectangular spatial grid.
    """
    def __init__(self, cells):
        super().__init__(cells)

    def cells_as_rings(self):
        return [[cell.as_ring()] for cell in self._cells]



class geospatial_engine:
    """
    Represents a geospatial engine offering geospatial operations.
    """

    def create_points(self, latitudes, longitudes):
        """
        Creates a list of points using the latitude and longitude arrays.
        """
        raise NotImplementedError

    def create_spatial_grid(self, spacing_meters):
        """
        Create a spatial grid with the defined grid cell size in meters.
        """
        raise NotImplementedError

    def intersections(self, grid, geometries, wkid):
        """
        Returns the grid cells which intersects the specified list of geometries.
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

    def __enter__(self):
        self._gis = GIS()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self._gis
        self._gis = None

    def create_points(self, latitudes, longitudes):
        if (len(latitudes) != len(longitudes)):
            raise ValueError("Coordinate arrays must have equal length!")

        return [Point({
            'x': longitude,
            'y': latitude
        }) for (longitude, latitude) in zip(longitudes, latitudes)]
    
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
                xmin = envelope_mercator.xmin + (column * spacing_meters)
                ymin = envelope_mercator.ymin + (row * spacing_meters)
                xmax = envelope_mercator.xmin + ((column + 1) * spacing_meters)
                ymax = envelope_mercator.ymin + ((row + 1) * spacing_meters)         

                if columns == column + 1:
                    xmax = envelope_mercator.xmax
                if rows == row + 1:
                    ymax = envelope_mercator.ymax

                recbin_mercator = grid_cell(xmin, ymin, xmax, ymax, wkid=3857)    
                geometries.append(recbin_mercator)
        
        return rectangular_spatial_grid(geometries)
    
    def project(self, geometries, in_sr, out_sr):
        return ago_project(geometries, in_sr, out_sr)

    def intersections(self, grid, geometries, wkid):
        # Create valid Esri polygons using rings
        cell_polygons = []
        for cell_rings in grid.cells_as_rings():
            cell_polygon = Polygon({
                'rings': cell_rings
            })
            cell_polygons.append(cell_polygon)
        
        related_result = ago_relation(cell_polygons, geometries, spatial_ref=wkid, spatial_relation='esriGeometryRelationIntersection', gis=self._gis)
        if not ('relations' in related_result):
            return None

        bins = dict()
        for relation in related_result['relations']:
            grid_index = relation['geometry1Index']
            if not (grid_index in bins):
                bins[grid_index] = {
                    'geometry': cell_polygons[grid_index],
                    'hitCount': 1
                }
            else:
                bin_entry = bins[grid_index]
                bin_entry['hitCount'] += 1
        
        return list(bins.values())




class geospatial_engine_factory:
    """
    Represents a factory creating different geospatial engines.
    """

    @staticmethod
    def create_cloud_engine():
        """
        Creates a geospatial engine using ArcGIS Online.
        You have to ensure using the with statement, otherwise the underlying GIS instance is not initialized correctly! 
        """
        return ago_geospatial_engine()