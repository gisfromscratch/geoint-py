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

import unittest
from geoint import *

class TestSpatialBinning(unittest.TestCase):
   
    #@unittest.skip("Tryouts...")
    def test_kilometer_grid(self):
        grid = create_spatial_grid(10e6)
        self.assertIsNotNone(grid, 'The grid must not be none!')

        rings = grid.cells_as_rings()
        self.assertIsNotNone(rings, 'Rings must not be none!')

    def test_binning_grid(self):
        grid = create_spatial_grid(10e6)
        self.assertIsNotNone(grid, 'The grid must not be none!')

        one_bin = create_bins(grid, [51.83864], [12.24555])
        self.assertIsNotNone(one_bin, 'Bins must not be none!')

        self.assertEqual(1, len(one_bin), 'One bin was expected!')

        one_bin = create_bins(grid, [51.83864, 50.73438], [12.24555, 7.09549])
        self.assertIsNotNone(one_bin, 'Bins must not be none!')

        self.assertEqual(1, len(one_bin), 'One bin was expected!')
        first_bin = one_bin[0]
        self.assertTrue('hitCount' in first_bin, 'Bin must have a hit count property!')
        self.assertEqual(2, first_bin['hitCount'], 'Hit count of 2 was expected!')



if __name__ == '__main__':
    unittest.main()
