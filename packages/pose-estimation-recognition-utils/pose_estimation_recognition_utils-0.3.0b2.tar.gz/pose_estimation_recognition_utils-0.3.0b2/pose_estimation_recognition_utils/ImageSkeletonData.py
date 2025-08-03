# Copyright 2025 Jonas David Stephan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
ImageSkeletonData.py

This module defines a class for managing skeleton data, including data points.

Author: Jonas David Stephan
Date: 2025-04-25
License: Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
"""

import json

from typing import List, Union

from .SkeletonDataPoint import SkeletonDataPoint
from .SkeletonDataPointWithName import SkeletonDataPointWithName


class ImageSkeletonData:
    """
    Represents skeleton data for a specific frame, including multiple data points.

    Attributes:
        data_points (list): A list of data points associated with the skeleton. Each data point can be either a
            SkeletonDataPoint or a SkeletonDataPointWithName instance.
    """
    def __init__(self):
        """
        Initialize the SkeletonData instance with a frame number.

        """
        self.data_points: List[Union[SkeletonDataPoint, SkeletonDataPointWithName]] = []

    def add_data_point(self, data_point: Union[SkeletonDataPoint, SkeletonDataPointWithName]) -> None:
        """
        Add a data point to the skeleton.

        Args:
            data_point (Union[SkeletonDataPoint, SkeletonDataPointWithName]): A data point representing a part of the skeleton.
        """
        self.data_points.append(data_point)

    def get_data_points(self) -> List[Union[SkeletonDataPoint, SkeletonDataPointWithName]]:
        """
        Retrieve all data points in the skeleton.

        Returns:
            list: A list of data points.
        """
        return self.data_points

    def to_json(self) -> str:
        """
        Convert the skeleton data to a JSON string.

        Returns:
            str: A JSON-formatted string representing the skeleton data.
        """
        data_list = [json.loads(data_point.to_json()) for data_point in self.data_points]
        data = {"skeletonpoints": data_list}

        return json.dumps(data)
