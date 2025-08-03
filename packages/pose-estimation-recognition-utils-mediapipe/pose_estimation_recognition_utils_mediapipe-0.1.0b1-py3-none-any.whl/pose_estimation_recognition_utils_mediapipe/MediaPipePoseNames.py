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
MediaPipePoseNames.py

This module defines a class to represent the landmark names for MediaPipe's pose and hand models.

Author: Jonas David Stephan
Date: 2025-01-28
License: Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
"""
from typing import Dict


class MediaPipePoseNames:
    """
    Represents the landmark names for MediaPipe's pose and hand models.

    Attributes:
        landmark_names_pose (dict): Landmark names for the pose model.
        landmark_names_hand_right (dict): Landmark names for the right hand model.
        landmark_names_hand_left (dict): Landmark names for the left hand model.
    """
    def __init__(self):
        self.landmark_names_pose: Dict[int, str] = {
            0: "nose",
            1: "left eye (inner)",
            2: "left eye",
            3: "left eye (outer)",
            4: "right eye (inner)",
            5: "right eye",
            6: "right eye (outer)",
            7: "left ear",
            8: "right ear",
            9: "mouth (left)",
            10: "mouth (right)",
            11: "left shoulder",
            12: "right shoulder",
            13: "left elbow",
            14: "right elbow",
            15: "left wrist",
            16: "right wrist",
            17: "left pinky",
            18: "right pinky",
            19: "left index",
            20: "right index",
            21: "left thumb",
            22: "right thumb",
            23: "left hip",
            24: "right hip",
            25: "left knee",
            26: "right knee",
            27: "left ankle",
            28: "right ankle",
            29: "left heel",
            30: "right heel",
            31: "left foot index",
            32: "right foot index"
        }

        self.landmark_names_hand_right: Dict[int, str] = {
            0: "right wrist",
            1: "right thumb cmc",
            2: "right thumb mcp",
            3: "right thumb ip",
            4: "right thumb tip",
            5: "right index finger mcp",
            6: "right index finger pip",
            7: "right index finger dip",
            8: "right index finger tip",
            9: "right middle finger mcp",
            10: "right middle finger pip",
            11: "right middle finger dip",
            12: "right middle finger tip",
            13: "right ring finger mcp",
            14: "right ring finger pip",
            15: "right ring finger dip",
            16: "right ring finger tip",
            17: "right pinky mcp",
            18: "right pinky pip",
            19: "right pinky dip",
            20: "right pinky tip"
        }

        self.landmark_names_hand_left: Dict[int, str] = {
            0: "left wrist",
            1: "left thumb cmc",
            2: "left thumb mcp",
            3: "left thumb ip",
            4: "left thumb tip",
            5: "left index finger mcp",
            6: "left index finger pip",
            7: "left index finger dip",
            8: "left index finger tip",
            9: "left middle finger mcp",
            10: "left middle finger pip",
            11: "left middle finger dip",
            12: "left middle finger tip",
            13: "left ring finger mcp",
            14: "left ring finger pip",
            15: "left ring finger dip",
            16: "left ring finger tip",
            17: "left pinky mcp",
            18: "left pinky pip",
            19: "left pinky dip",
            20: "left pinky tip"
        }

    def get_pose_names(self) -> Dict[int, str]:
        """
            Retrieve the landmark names for the pose model.

            Returns:
                dict: A dictionary mapping landmark IDs to their names for the pose model.
        """
        return self.landmark_names_pose

    def get_right_hand_names(self) -> Dict[int, str]:
        """
            Retrieve the landmark names for the right hand model.

            Returns:
                dict: A dictionary mapping landmark IDs to their names for the right hand model.
        """
        return self.landmark_names_hand_right

    def get_left_hand_names(self) -> Dict[int, str]:
        """
        Retrieve the landmark names for the left hand model.

        Returns:
            dict: A dictionary mapping landmark IDs to their names for the left hand model.
        """
        return self.landmark_names_hand_left
