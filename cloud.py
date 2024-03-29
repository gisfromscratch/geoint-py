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

from arcgis.features import FeatureSet
from datetime import datetime, timedelta
import json
import os
import unittest
from geoint.cloud import protests_aggregate_as_featureset, protests_articles, protests_hotspots_as_featureset
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

    #@unittest.skip('DEBUG')
    def test_aggregate_yesterday(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        geojson_features = self._client.aggregate(yesterday, OutFormat.GEOJSON)
        self.assertIsNotNone(geojson_features, 'The returned features must be initialized!')
        self.assertTrue('type' in geojson_features, 'The returned geojson must have a type!')
        geojson_type = geojson_features['type']
        self.assertTrue('FeatureCollection' == geojson_type, 'The returned geojson must have a type of FeatureCollection!')
        self.assertTrue('features' in geojson_features, 'The returned geojson must have a features key!')

        esri_features = self._client.aggregate(yesterday, OutFormat.ESRI)
        self.assertIsNotNone(esri_features, 'The returned features must be initialized!')
        self.assertTrue('geometryType' in esri_features, 'The returned esri result must have a geometry type!')
        geometry_type = esri_features['geometryType']
        self.assertTrue('esriGeometryPolygon' == geometry_type, 'The returned geometry type must be polygon!')
        self.assertTrue('features' in esri_features, 'The returned esri result must have a features key!')
        
        esri_featureset = FeatureSet.from_json(json.dumps(esri_features))
        spatial_dataframe = esri_featureset.sdf
        self.assertIsNotNone(spatial_dataframe, 'The returned features must represent a valid esri feature set!')

    #@unittest.skip('DEBUG')
    def test_articles_yesterday(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        articles = self._client.articles(yesterday)
        self.assertIsNotNone(articles, 'The returned articles must be initialized!')

    #@unittest.skip('DEBUG')
    def test_hotspots_yesterday(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        geojson_features = self._client.hotspots(yesterday, OutFormat.GEOJSON)
        self.assertIsNotNone(geojson_features, 'The returned features must be initialized!')
        self.assertTrue('type' in geojson_features, 'The returned geojson must have a type!')
        geojson_type = geojson_features['type']
        self.assertTrue('FeatureCollection' == geojson_type, 'The returned geojson must have a type of FeatureCollection!')
        self.assertTrue('features' in geojson_features, 'The returned geojson must have a features key!')

        esri_features = self._client.hotspots(yesterday, OutFormat.ESRI)
        self.assertIsNotNone(esri_features, 'The returned features must be initialized!')
        self.assertTrue('geometryType' in esri_features, 'The returned esri result must have a geometry type!')
        geometry_type = esri_features['geometryType']
        self.assertTrue('esriGeometryPoint' == geometry_type, 'The returned geometry type must be point!')
        self.assertTrue('features' in esri_features, 'The returned esri result must have a features key!')
        
        esri_featureset = FeatureSet.from_json(json.dumps(esri_features))
        spatial_dataframe = esri_featureset.sdf
        self.assertIsNotNone(spatial_dataframe, 'The returned features must represent a valid esri feature set!')



class TestEnvironmentFactory(unittest.TestCase):

    def test_aggregate_yesterday(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        esri_featureset = protests_aggregate_as_featureset(yesterday)
        spatial_dataframe = esri_featureset.sdf
        self.assertIsNotNone(spatial_dataframe, 'The returned features must represent a valid esri feature set!')

    def test_articles_yesterday(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        articles = protests_articles(yesterday)
        self.assertIsNotNone(articles, 'The returned articles must be initialized!')

    def test_hotspots_yesterday(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        esri_featureset = protests_hotspots_as_featureset(yesterday)
        spatial_dataframe = esri_featureset.sdf
        self.assertIsNotNone(spatial_dataframe, 'The returned features must represent a valid esri feature set!')



if __name__ == '__main__':
    unittest.main()