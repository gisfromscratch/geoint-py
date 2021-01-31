# geoint-py is a simple python module for geospatial intelligence workflows.
# Copyright (C) 2021 Jan Tschada (gisfromscratch@live.de)
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

import geoint
from geoint import geospatial
import os
import pandas
import sys
import tempfile

def assign_points(acled_data):
    with geospatial.geospatial_engine_factory.create_cloud_engine() as geospatial_engine:
        points = geospatial_engine.create_points(acled_data['latitude'], acled_data['longitude'])
        WGS84 = 4326
        WEB_MERCATOR = 3857
        mercator_points = geospatial_engine.project(points, WGS84, WEB_MERCATOR)
        x = [mercator_point.x for mercator_point in mercator_points]
        y = [mercator_point.y for mercator_point in mercator_points]
        return acled_data.assign(x=x, y=y)

def size_by(acled_data, columns):
    """Group by drops None values!"""
    return acled_data.groupby(columns).size().nlargest(10)

def size_by_country(acled_data):
    return size_by(acled_data, ['country'])

def size_by_admin1(acled_data):
    return size_by(acled_data, ['country', 'admin1'])

def size_by_admin2(acled_data):
    return size_by(acled_data, ['country', 'admin1', 'admin2'])

def size_by_admin3(acled_data):
    return size_by(acled_data, ['country', 'admin1', 'admin2', 'admin3'])

def size_by_locations(acled_data):
    return size_by(acled_data, ['country', 'location'])

def count_by_subevents(acled_data):
    sizes = size_by_locations(acled_data)
    min_size = sizes[-1]
    return acled_data.groupby(['country', 'location']).filter(lambda group: min_size <= len(group))['sub_event_type'].value_counts()

def count_by_event_date(acled_data):
    return acled_data.groupby(['country', 'location'])['event_date'].nunique().nlargest(5)



if __name__ == '__main__':
    acled_filepath = None

    if 1 < len(sys.argv):
        acled_filepath = sys.argv[1]

    acled_environ_key = 'acled.data.filepath'
    if None is acled_filepath \
        and acled_environ_key in os.environ:
            acled_filepath = os.environ[acled_environ_key]

    if None is acled_filepath:
        raise ValueError('Define an environment variable named \'%s\' or pass an argument representing the full qualified filepath to the *.csv file containing the ACLED events!' % (acled_environ_key))
    
    print('Create ACLED report...')
    acled_data = pandas.read_csv(acled_filepath, encoding='utf_8')
    acled_data_demonstrations = acled_data[(acled_data['event_type'] == 'Protests') | (acled_data['event_type'] == 'Riots')]

    filepath = os.path.join(tempfile.gettempdir(), 'acled_stats.xlsx')
    with pandas.ExcelWriter(filepath) as writer:
        size_by_country(acled_data_demonstrations).to_excel(writer, sheet_name='countries')
        size_by_admin1(acled_data_demonstrations).to_excel(writer, sheet_name='admin1')
        size_by_admin2(acled_data_demonstrations).to_excel(writer, sheet_name='admin2')
        size_by_admin3(acled_data_demonstrations).to_excel(writer, sheet_name='admin3')
        size_by_locations(acled_data_demonstrations).to_excel(writer, sheet_name='locations')
        count_by_subevents(acled_data_demonstrations).to_excel(writer, sheet_name='event_types')
        count_by_event_date(acled_data_demonstrations).to_excel(writer, sheet_name='event_dates')

    print(filepath)
