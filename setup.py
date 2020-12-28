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

import setuptools

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name="geoint",
    version="0.1",
    author="Jan Tschada",
    author_email="gisfromscratch@live.de",
    description="Simple python module for geospatial intelligence workflows.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gisfromscratch/geoint-py",
    packages=["geoint"],
    install_requires=["arcgis>=1.8.0", "pandas>=1.0.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "LICENSE :: OSI APPROVED :: GNU LESSER GENERAL PUBLIC LICENSE V3",
        "Operating System :: OS Independent",
     ]
 )