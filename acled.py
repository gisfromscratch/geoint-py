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

def aggregate_locations(acled_data_spatial, area_data):
    grid_locations = []
    for index, area_row in area_data.iterrows():
        area_envelope = area_row['SHAPE'].envelope
        grid_location = { 
            'hitCount': area_row['hitCount'], 
            'locations': acled_data_spatial[(area_envelope.xmin <= acled_data_spatial['x']) \
                                            & (acled_data_spatial['x'] <= area_envelope.xmax) \
                                            & (area_envelope.ymin <= acled_data_spatial['y']) \
                                            & (acled_data_spatial['y'] <= area_envelope.ymax) \
                                           ]
        }           
        grid_locations.append(grid_location)
    
    return grid_locations

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

def find_duplicates_by_coordinates(acled_data):
    """Finds all coordinates having more than one location name."""
    unique_counts = acled_data.groupby(['latitude', 'longitude']).location.transform('nunique')
    return acled_data[1 < unique_counts].groupby(['latitude', 'longitude', unique_counts]).location.unique()

def write_excel_sheet(acled_data, writer, sheet_name):
    if acled_data.empty:
        print('Data is empty no excel sheet {} was created!'.format(sheet_name))
        return

    acled_data.to_excel(writer, sheet_name)
    

def write_excel_report(acled_data, file_name):
    if acled_data.empty:
        print('Data is empty no excel report was created!')
        return

    spatial_grid = geoint.create_spatial_grid(spacing_meters=5e4)
    acled_spatial = assign_points(acled_data)
    grid_aggregation = geoint.create_mercator_bins(spatial_grid, acled_spatial['y'], acled_spatial['x'])
    grid_featureset = grid_aggregation.to_featureset()
    hot_spots = grid_featureset.sdf.nlargest(3, 'hitCount')[['hitCount', 'SHAPE']]
        
    filepath = os.path.join(tempfile.gettempdir(), file_name)
    with pandas.ExcelWriter(filepath) as writer:
        write_excel_sheet(size_by_country(acled_data), writer, sheet_name='countries')
        write_excel_sheet(size_by_admin1(acled_data), writer, sheet_name='admin1')
        write_excel_sheet(size_by_admin2(acled_data), writer, sheet_name='admin2')
        write_excel_sheet(size_by_admin3(acled_data), writer, sheet_name='admin3')
        write_excel_sheet(size_by_locations(acled_data), writer, sheet_name='locations')
        write_excel_sheet(find_duplicates_by_coordinates(acled_data), writer, sheet_name='duplicates')
        write_excel_sheet(count_by_subevents(acled_data), writer, sheet_name='event_types')
        write_excel_sheet(count_by_event_date(acled_data), writer, sheet_name='event_dates')

        aggregations = aggregate_locations(acled_spatial, hot_spots)
        for index in range(0, len(aggregations)):
            aggregation = aggregations[index]
            write_excel_sheet(aggregation['locations'], writer, sheet_name='hot_spots_{}'.format(index + 1))

    print(filepath)



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
    
    print('Create ACLED reports...')
    acled_data = pandas.read_csv(acled_filepath, encoding='utf_8')
    acled_data_demonstrations = acled_data[(acled_data['event_type'] == 'Protests') | (acled_data['event_type'] == 'Riots')]
    write_excel_report(acled_data_demonstrations, 'acled_stats.xlsx')

    acled_data_germany = acled_data[(acled_data['country'] == 'Germany')]
    write_excel_report(acled_data_germany, 'acled_stats_germany.xlsx')
