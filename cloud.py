# geoint-py is a simple python module for geospatial intelligence workflows.
# Copyright (C) 2022 Jan Tschada (gisfromscratch@live.de)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

from datetime import datetime, timedelta
import os
import unittest
from geoint.cloud.geoprotests import GeoProtestClient, OutFormat

class TestGeoProtestClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        url = os.environ['x_rapidapi_url']
        host = os.environ['x_rapidapi_host']
        key = os.environ['x_rapidapi_key']
        auth_headers = {
            'x-rapidapi-host': host,
            'x-rapidapi-key': key
        }
        cls._client = GeoProtestClient(url, auth_headers)

    def test_aggregate_yesterday(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        geojson_features = self._client.aggregate(yesterday, OutFormat.GEOJSON)
        self.assertIsNotNone(geojson_features, 'The returned features must be initialized!')
        self.assertTrue('type' in geojson_features, 'The returned geojson must have a type!')
        geojson_type = geojson_features['type']
        self.assertTrue('FeatureCollection' == geojson_type, 'The returned geojson must have a type of FeatureCollection!')
        self.assertTrue('features' in geojson_features, 'The returned geojson must have a features key!')

if __name__ == '__main__':
    unittest.main()