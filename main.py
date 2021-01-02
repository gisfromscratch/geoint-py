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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import unittest
from geoint import *

class TestSpatialBinning(unittest.TestCase):
   
    @unittest.skip("Tryouts...")
    def test_kilometer_grid(self):
        grid = create_spatial_grid(10e6)
        self.assertIsNotNone(grid, 'The grid must not be none!')

        rings = grid.cells_as_rings()
        self.assertIsNotNone(rings, 'Rings must not be none!')

    @unittest.skip("Tryouts...")
    def test_binning_grid(self):
        grid = create_spatial_grid(10e6)
        self.assertIsNotNone(grid, 'The grid must not be none!')

        aggregation = create_bins(grid, [51.83864], [12.24555])
        one_bin = aggregation.bins()
        self.assertIsNotNone(one_bin, 'Bins must not be none!')

        self.assertEqual(1, len(one_bin), 'One bin was expected!')

        aggregation = create_bins(grid, [51.83864, 50.73438], [12.24555, 7.09549])
        one_bin = aggregation.bins()
        self.assertIsNotNone(one_bin, 'Bins must not be none!')

        self.assertEqual(1, len(one_bin), 'One bin was expected!')
        first_bin = one_bin[0]
        self.assertTrue('hitCount' in first_bin, 'Bin must have a hit count property!')
        self.assertEqual(2, first_bin['hitCount'], 'Hit count of 2 was expected!')

        feature_set = aggregation.to_featureset()
        self.assertIsNotNone(feature_set, 'The feature set must not be none!')

    def test_reproject_locations(self):
        WGS84 = 4326
        WEB_MERCATOR = 3857
        latitudes = [51.83864, 50.73438]
        longitudes = [12.24555, 7.09549]
        with geospatial.geospatial_engine_factory.create_cloud_engine() as geospatial_engine:
            points = geospatial_engine.create_points(latitudes, longitudes)
            self.assertIsNotNone(points, 'The points must not be none!')
            self.assertEqual(2, len(points), 'Two points were expected!')

            projected_points = geospatial_engine.project(points, WGS84, WEB_MERCATOR)
            self.assertIsNotNone(projected_points, 'The projected points must not be none!')
            self.assertEqual(len(points), len(projected_points), 'The same number of points must be returned!')

            expected_latitudes = [6771001.917079877, 6574442.434743122]
            expected_longitudes = [1363168.390483571, 789866.3337287647]
            self.assertListEqual(expected_latitudes, [projected_points[0].y, projected_points[1].y], 'The latitudes do not match!')
            self.assertListEqual(expected_longitudes, [projected_points[0].x, projected_points[1].x], 'The longitudes do not match!')



if __name__ == '__main__':
    unittest.main()
