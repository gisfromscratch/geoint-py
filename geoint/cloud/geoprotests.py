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

from enum import Enum, unique
from datetime import datetime
import requests



@unique
class OutFormat(Enum):
    """Represents the supported output formats."""
    ESRI=0
    GEOJSON=1
    JSON=2

    def __str__(self) -> str:
        if 0 == self.value:
            return 'esri'
        elif 1 == self.value:
            return 'geojson'
        elif 2 == self.value:
            return 'json'
        
        return self.name



class GeoProtestClient(object):
    """
    Represents a client accessing the geoprotests API being hosted at Rapid API.
    """

    def __init__(self, url, auth_headers) -> None:
        """
        Initializes this instance using an url and an authorization header dictionary.
        The dictionary must contain 'x-rapidapi-host' and 'x-rapidapi-host' as keys.
        """
        self._url = url
        if not 'x-rapidapi-host' in auth_headers:
            raise ValueError("'x-rapidapi-host' must be specified in the authorization header!")
        if not 'x-rapidapi-key' in auth_headers:
            raise ValueError("'x-rapidapi-key' must be specified in the authorization header!")

        self._auth_headers = auth_headers

    def aggregate(self, date=None, format=OutFormat.GEOJSON):
        """
        Aggregates the broadcasted news using a spatial grid and returns the features as hexagonal bins.
        The date is optional, when not specified the features of the last 24 hours are returned.
        The underlying hosted feature service saves the last 90 days and yesterday should be the latest availabe date.
        """
        endpoint = '{0}/aggregate'.format(self._url)
        params = {
            'format': str(format)
        }
        if date:
            params['date'] = datetime.strftime(date, '%Y-%m-%d')

        return requests.request('GET', endpoint, headers=self._auth_headers, params=params).json()
