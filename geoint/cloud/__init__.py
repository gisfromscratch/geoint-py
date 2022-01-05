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

import arcgis
import os
from . import geoprotests



class EnvironmentClientFactory(object):
    """
    Represents a factory creating client instances using the system environment.
    The environment must offer various variables for authenticating against the web service endpoints.
    """

    @staticmethod
    def create_geoprotest_client():
        """
        Creates a new client using 'x_rapidapi_url', 'x_rapidapi_host' and 'x_rapidapi_key'.
        Raises a ValueError when these variables are not defined!
        """
        if not 'x_rapidapi_url' in os.environ:
            raise ValueError("'x_rapidapi_url' is not defined in the current environment!")
        if not 'x_rapidapi_host' in os.environ:
            raise ValueError("'x_rapidapi_host' is not defined in the current environment!")
        if not 'x_rapidapi_key' in os.environ:
            raise ValueError("'x_rapidapi_key' is not defined in the current environment!")

        url = os.environ['x_rapidapi_url']
        host = os.environ['x_rapidapi_host']
        key = os.environ['x_rapidapi_key']
        auth_headers = {
            'x-rapidapi-host': host,
            'x-rapidapi-key': key
        }

        return geoprotests.GeoProtestClient(url, auth_headers)



def protests_aggregate_as_geojson(date=None):
    """
    Aggregates the broadcasted news related to protests/demonstrations using a spatial grid and returns the features as hexagonal bins using the GeoJSON format.
    The date is optional. When not specified, we return the features of the last 24 hours.
    The underlying hosted feature service saves the last 90 days and yesterday should be the latest available date.
    """
    client = EnvironmentClientFactory.create_geoprotest_client()
    return client.aggregate(date, geoprotests.OutFormat.GEOJSON)

def protests_aggregate_as_featureset(date=None):
    """
    Aggregates the broadcasted news related to protests/demonstrations using a spatial grid and returns a Esri FeatureSet containing the features as hexagonal bins.
    The date is optional. When not specified, we return the features of the last 24 hours.
    The underlying hosted feature service saves the last 90 days and yesterday should be the latest available date.
    """
    client = EnvironmentClientFactory.create_geoprotest_client()
    return arcgis.features.FeatureSet.from_json(client.aggregate_as_text(date, geoprotests.OutFormat.ESRI))

def protests_articles(date=None):
    """
    Returns a list of broadcasted articles related to protests/demonstrations.
    The date is optional. When not specified, we return the articles of the last 24 hours.
    The underlying web service saves the last 90 days and yesterday should be the latest available date.
    """
    client = EnvironmentClientFactory.create_geoprotest_client()
    return client.articles(date)

def protests_hotspots_as_geojson(date=None):
    """
    Returns the hotspot locations related to protests/demonstrations using the GeoJSON format.
    The date is optional. When not specified, we return the features of the last 24 hours.
    The underlying hosted feature service saves the last 90 days and yesterday should be the latest availabe date.
    """
    client = EnvironmentClientFactory.create_geoprotest_client()
    return client.hotspots(date, geoprotests.OutFormat.GEOJSON)

def protests_hotspots_as_featureset(date=None):
    """
    Returns the hotspot locations related to protests/demonstrations as a Esri FeatureSet.
    The date is optional. When not specified, we return the features of the last 24 hours.
    The underlying hosted feature service saves the last 90 days and yesterday should be the latest availabe date.
    """
    client = EnvironmentClientFactory.create_geoprotest_client()
    return arcgis.features.FeatureSet.from_json(client.hotspots_as_text(date, geoprotests.OutFormat.ESRI))