# Copyright 2025 Nathalie Dollmann, Jonas David Stephan
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
SAD.py

This module defines a class for the implementation of SAD algorithm.

Author: Nathalie Dollmann, Jonas David Stephan
Date: 2025-07-18
License: Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
"""

from .SkeletonDataPoint import SkeletonDataPoint
from .SkeletonDataPointWithName import SkeletonDataPointWithName
from .Save2DData import Save2DData

class SAD:
    def __init__(self, distance, focal_length, cx_left, cy_left):
        self.focal_length = focal_length
        self.fB = focal_length * distance
        self.cx_left = cx_left
        self.cy_left = cy_left

    def merge_pixel(self, pixel_list_left, pixel_list_right):
        back = []
        l = len(pixel_list_left)
        for i in range(l):
            x_left = pixel_list_left[i].data['x']
            x_right = pixel_list_right[i].data['x']
            
            if x_left != 0 and x_right != 0:
                difference = x_left - x_right
                z = self.fB / difference
            
                y_left = pixel_list_left[i].data['y']
                x = ((x_left - self.cx_left) * z) / self.focal_length
                y = ((y_left - self.cy_left) * z) / self.focal_length
                
                if isinstance(pixel_list_left[i], Save2DData):
                    back.append(SkeletonDataPoint(pixel_list_left[i].data['id'], x, y, z))
                else:
                    back.append(SkeletonDataPointWithName(pixel_list_left[i].data['id'], pixel_list_left[i].data['name'], x, y, z))
            else:
                if isinstance(pixel_list_left[i], Save2DData):
                    back.append(SkeletonDataPoint(pixel_list_left[i].data['id'], 0, 0, 0))
                else:
                    back.append(SkeletonDataPointWithName(pixel_list_left[i].data['id'], pixel_list_left[i].data['name'], 0, 0, 0))

        return back