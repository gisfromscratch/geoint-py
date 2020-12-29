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
from geoint import create_spatial_grid
from geoint import geospatial

class TestSpatialBinning(unittest.TestCase):
   
    def test_kilometer_grid(self):
        grid = create_spatial_grid(1e6)
        self.assertIsNotNone(grid, 'The grid must not be none!')

        rings = grid.cells_as_rings()
        self.assertIsNotNone(rings, 'Rings must not be none!')
 
if __name__ == '__main__':
    unittest.main()
