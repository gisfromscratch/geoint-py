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

from arcgis.features import Feature, FeatureSet
from arcgis.gis import GIS
from arcgis.geometry import Envelope, Point, Polygon, SpatialReference
from arcgis.geometry import project as ago_project
from arcgis.geometry.functions import relation as ago_relation
from itertools import chain
from math import ceil, floor, log, pi, tan



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

    def wkid(self):
        return self._wkid

    def height(self):
        return self._ymax - self._ymin

    def width(self):
        return self._xmax - self._xmin

    def center_x(self):
        return self._xmin + (0.5 * self.width())

    def center_y(self):
        return self._ymin + (0.5 * self.height())

    def intersects(self, x, y):
        return (self._xmin <= x and x <= self._xmax and self._ymin <= y and y <= self._ymax)

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
    def __init__(self, cells, wkid):
        self._cells = cells
        self._wkid = wkid

    def wkid(self):
        """
        Returns the well-known id of the spatial reference.
        """
        return self._wkid

    def cells(self):
        """
        Returns all cells of this grid.
        """
        raise NotImplementedError
    
    def cells_as_rings(self):
        """
        Returns all cells as a ring array used for constructing polygons.
        """
        raise NotImplementedError

    def find_index(self, x, y):
        """
        Returns the cell index or -1 when the specified coordinates do not intersect
        with any of these cells.
        """
        raise NotImplementedError
    
    def intersect(self, x, y):
        """
        Returns the first cell which intersects with the specified coordinates.
        The coordinates must have the same spatial reference!
        """
        raise NotImplementedError



class rectangular_construct_params():
    """
    Represents the parameters for constructing a rectangular spatial grid.
    The extent is defined by a grid_cell representing the full extent.
    """
    def __init__(self, extent, cell_size):
        self._extent = extent
        self._cell_size = cell_size
        self._row_count = int(ceil(self._extent.height() / self._cell_size))
        self._column_count = int(ceil(self._extent.width() / self._cell_size))

    def rows(self):
        return self._row_count

    def columns(self):
        return self._column_count

    def wkid(self):
        return self._extent.wkid()

    def construct_cell(self, row, column):
        cell_xmin = self._extent._xmin + (column * self._cell_size)
        cell_ymin = self._extent._ymin + (row * self._cell_size)
        cell_xmax = self._extent._xmin + ((column + 1) * self._cell_size)
        cell_ymax = self._extent._ymin + ((row + 1) * self._cell_size)         

        if self._column_count == column + 1:
            cell_xmax = self._extent._xmax
        if self._row_count == row + 1:
            cell_ymax = self._extent._ymax

        return grid_cell(cell_xmin, cell_ymin, cell_xmax, cell_ymax, self._extent.wkid())

    def construct_cells(self):
        """
        Construct all cells in a column-wise manner.
        """
        cells = []
        for column in range(0, self._column_count):
            for row in range(0, self._row_count):
                cell = self.construct_cell(row, column)
                cells.append(cell)
        
        return cells

    def find_index(self, x, y):
        """
        Returns the cell index.
        Expects the cells were constructed column-wise!
        """
        if not self._extent.intersects(x, y):
            return -1

        column_index = int(floor((x - self._extent._xmin) / self._cell_size))
        row_index = int(floor((y - self._extent._ymin) / self._cell_size))
        return row_index + (self._row_count * column_index)



class rectangular_spatial_grid(spatial_grid):
    """
    Represents a rectangular spatial grid.
    """
    def __init__(self, cells, wkid):
        super().__init__(cells, wkid)

    @staticmethod
    def build_from_params(construct_params):
        # Create all cells
        cells = construct_params.construct_cells()
        
        # Create the grid and set the construction params
        # these can be used for finding the cells intersecting with points later
        grid = rectangular_spatial_grid(cells, construct_params.wkid())
        grid._construct = construct_params
        return grid

    def cells(self):
        return self._cells
    
    def cells_as_rings(self):
        return [[cell.as_ring()] for cell in self._cells]

    def find_index(self, x, y):
        return self._construct.find_index(x, y)
    
    def intersect(self, x, y):
        if not self._construct:
            return None

        cell_index = self.find_index(x, y)
        if -1 == cell_index:
            return None
        
        return self._cells[cell_index]



class spatial_grid_aggregation:
    """
    Represents a geometries in spatial grid aggregation.
    """
    def __init__(self, bins, wkid):
        self._bins = bins
        self._wkid = wkid

    def bins(self):
        """
        Returns a list of all bins.
        """
        return list(self._bins.values())
    
    def to_featureset(self):
        """
        Return a feature set
        """
        bin_features = []
        for bin_entry in self.bins():
            bin_feature = Feature(
                geometry=bin_entry['geometry'],
                attributes={ 'hitCount': bin_entry['hitCount'] }
            )
            bin_features.append(bin_feature)

        bin_fields = ['hitCount']
        return FeatureSet(bin_features, bin_fields, geometry_type='esriGeometryPolygon', spatial_reference=self._wkid)



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

    def aggregate(self, grid, geometries, wkid):
        """
        Returns the aggregation between grid cells which intersects the specified list of geometries.
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
        if (self._gis._con and self._gis._con._session):
            self._gis._con._session.close()

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
        # Use WGS84 and reproject to Web Mercator
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

        extent_cell = grid_cell(envelope_mercator.xmin, envelope_mercator.ymin, envelope_mercator.xmax, envelope_mercator.ymax, 3857)
        construct_params = rectangular_construct_params(extent_cell, spacing_meters)
        return rectangular_spatial_grid.build_from_params(construct_params)
    
    def project(self, geometries, in_sr, out_sr):
        if (0 == len(geometries)):
            return []

        # Special cases (WGS84 points to Web Mercator)
        first_geometry = geometries[0]
        if ('Point' == first_geometry.type
            and 4326 == in_sr and 3857 == out_sr):
            return self._project_points_from_wgs84_to_web_mercator(geometries)

        chunk_size = 1000
        if (len(geometries) <= chunk_size):
            return ago_project(geometries, in_sr, out_sr)
        
        raise ValueError('Only {} geometries allowed!'.format(chunk_size))

        # Use an offline projection engine
        '''
        geometries_chunked = lambda geometries, chunk_size: [geometries[index: index + chunk_size] for index in range(0, len(geometries), chunk_size)]
        geometries_projected = []
        for chunk in geometries_chunked:
            chunk_projected = ago_project(chunk, in_sr, out_sr)
            geometries_projected.extend(chunk_projected)
        
        return geometries_projected
        '''
        #return list(chain(*[ago_project(chunk, in_sr, out_sr) for chunk in geometries_chunked]))

    def _project_points_from_wgs84_to_web_mercator(self, wgs84_points):
        major_axis = 6378137
        major_shift = pi * major_axis
        return [Point({
            'x': wgs84_point.x * major_shift / 180.0,
            'y': (log(tan((90.0 + wgs84_point.y) * pi / 360.0)) / (pi / 180.0)) * major_shift / 180.0
        }) for wgs84_point in wgs84_points]
    
    def aggregate(self, grid, geometries, wkid):
        if (0 == len(geometries)):
            return spatial_grid_aggregation(dict(), wkid)

        if (grid.wkid() != wkid):
            raise ValueError('The WKID of the grid must match the WKID of the geometries!')

        # Special cases (only points with grid aggregation)
        #"""
        first_geometry = geometries[0]
        if ('Point' == first_geometry.type):
            return self._aggregate_points(grid, geometries, wkid)
        #"""

        max_geometry_count = 1000
        if (max_geometry_count < len(geometries)):
            raise ValueError('Not more than {} geometries are supported with this implementation!'.format(max_geometry_count))

        # Create valid Esri polygons using rings
        cell_polygons = []
        for cell_rings in grid.cells_as_rings():
            cell_polygon = Polygon({
                'rings': cell_rings
            })
            cell_polygons.append(cell_polygon)

        # The aggregated bins
        bins = dict()
        
        related_result = ago_relation(cell_polygons, geometries, spatial_ref=wkid, spatial_relation='esriGeometryRelationIntersection', gis=self._gis)
        if not ('relations' in related_result):
            return None

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
        
        return spatial_grid_aggregation(bins, wkid)

    def _aggregate_points(self, grid, points, wkid):
        # Create valid Esri polygons using rings
        cell_polygons = []
        for cell_rings in grid.cells_as_rings():
            cell_polygon = Polygon({
                'rings': cell_rings
            })
            cell_polygons.append(cell_polygon)

        # The aggregated bins
        bins = dict()

        for point in points:
            if ('Point' != point.type):
                raise ValueError('Only points can be aggregated with this implementation!')

            x = point.x
            y = point.y
            grid_index = grid.find_index(x, y)
            if -1 != grid_index:
                if not (grid_index in bins):
                    bins[grid_index] = {
                        'geometry': cell_polygons[grid_index],
                        'hitCount': 1
                    }
                else:
                    bin_entry = bins[grid_index]
                    bin_entry['hitCount'] += 1

        return spatial_grid_aggregation(bins, wkid)



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