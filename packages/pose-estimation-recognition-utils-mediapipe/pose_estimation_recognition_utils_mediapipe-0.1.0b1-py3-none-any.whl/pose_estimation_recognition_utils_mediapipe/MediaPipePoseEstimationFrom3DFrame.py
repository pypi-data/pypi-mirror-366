# Copyright 2025 Chanyut Boonkhamsaen, Nathalie Dollmann, Jonas David Stephan
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
MediaPipePoseEstimationFrom3DFrame.py

This module defines a class for extracting Pose Estimation from 3D frames with MediaPipe.

Author: Chanyut Boonkhamsaen, Nathalie Dollmann, Jonas David Stephan
Date: 2025-07-18
License: Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
"""

import mediapipe as mp
from pose_estimation_recognition_utils import (Save2DData, Save2DDataWithName, SAD, SkeletonDataPoint, SkeletonDataPointWithName)
from pose_estimation_recognition_utils_mediapipe.MediaPipePoseNames import MediaPipePoseNames
import numpy as np
from typing import List, Union, Tuple
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList

class MediaPipePoseEstimationFrom3DFrame:
    
    """
    Extracts pose estimation from a 3D frame with MediaPipe.

    Attributes:
        mode (str): mode for pose estimation: pose, holistic or hands.
        mp_model (Union[mp.solutions.holistic.Holistic, mp.solutions.pose.Pose, mp.solutions.hands.Hands]): MediaPipe model for pose estimation
        sad (SAD): instance for calculating 3D coordinates of the frame
        with_names (bool): value for saving data with names
        MediaPipePoseNames (MediaPipePoseNames): MediaPipe pose names
    """
    
    
    def __init__(self, mode: str, min_detection_confidence: float, min_tracking_confidence: float, focal_length: float, distance: float, cx_left: int, cy_left: int, with_names: bool = False):
        
        """
        Initialize a new SkeletonDataPoint instance.

        Args:
            mode (str): mode for pose estimation: pose, holistic or hands.
            min_detection_confidence (float): MediaPipe minimum detection confidence
            min_tracking_confidence (float): MediaPipe minimum tracking confidence
            focal_length (float): focal_length of camera
            distance (float): between the two cameras
            cx_left (int): principal point x
            cy_left (int): principal point y
            with_names (bool): value for saving data with names

        Raises:
            ValueError: If mode is not allowed.
        """
        
        # Initialize pose estimation class
        self.mode: str = mode
        allowed_modes = {"holistic", "pose", "hand"}
        if mode not in allowed_modes:
            raise ValueError(f"Invalid mode: {mode}. Allowed values are: {allowed_modes}")
        
        if mode == 'holistic':
            self.mp_model: Union[mp.solutions.holistic.Holistic, mp.solutions.pose.Pose, mp.solutions.hands.Hands] = mp.solutions.holistic.Holistic(min_detection_confidence=min_detection_confidence, min_tracking_confidence=min_tracking_confidence)
        elif mode == 'pose':
            self.mp_model: Union[mp.solutions.holistic.Holistic, mp.solutions.pose.Pose, mp.solutions.hands.Hands] = mp.solutions.pose.Pose(min_detection_confidence=min_detection_confidence, min_tracking_confidence=min_tracking_confidence)
        elif mode == 'hands':
            self.mp_model: Union[mp.solutions.holistic.Holistic, mp.solutions.pose.Pose, mp.solutions.hands.Hands] = mp.solutions.hands.Hands(min_detection_confidence=min_detection_confidence, min_tracking_confidence=min_tracking_confidence)
        
        self.sad: SAD = SAD(focal_length, distance, cx_left, cy_left)
       
        self.with_names: bool = with_names
        if with_names:
            self.MediaPipePoseNames = MediaPipePoseNames()

    def extract_frame(self, frame: np.ndarray) -> List[Union[SkeletonDataPoint, SkeletonDataPointWithName]]:

        """
        Extracts frames in two frames with pixel.

        Args:
            frame (np.ndarray): Video frame

        Returns:
            List[Union[SkeletonDataPoint, SkeletonDataPointWithName]]: 3D coordinates
        """

        frame_left, frame_right = self.divide_3Dframe(frame)

        #detecting the object using mediapipe
        results_left = self.mp_model.process(frame_left)
        results_right = self.mp_model.process(frame_right)
        
        if self.mode == 'holistic':
            pixel_list_right = self.create2Dlist(results_right.pose_landmarks, results_right.right_hand_landmarks, results_right.left_hand_landmarks, results_right.face_landmarks, frame_right)
            pixel_list_left = self.create2Dlist(results_left.pose_landmarks, results_left.right_hand_landmarks, results_left.left_hand_landmarks, results_left.face_landmarks, frame_left)
        elif self.mode == 'pose':
            pixel_list_right = self.create2Dlist(results_right.pose_landmarks, None, None, None, frame_right)
            pixel_list_left = self.create2Dlist(results_left.pose_landmarks, None, None, None, frame_left)
        elif self.mode == 'hands':        
            pixel_list_right = self.create2Dlist(None, results_right.right_hand_landmarks, results_right.left_hand_landmarks, None, frame_right)
            pixel_list_left = self.create2Dlist(None, results_left.right_hand_landmarks, results_left.left_hand_landmarks, None, frame_left)
        
        return self.sad.merge_pixel(pixel_list_left, pixel_list_right)
     
    def create2Dlist(self, result_pose: NormalizedLandmarkList, result_right_hand: NormalizedLandmarkList, result_left_hand: NormalizedLandmarkList, result_face: NormalizedLandmarkList, frame: np.ndarray) -> List[Union[Save2DData, Save2DDataWithName]]: 
        
        """
        Creates a 2D list of all recognized pose estimation points.

        Args:
            result_pose (NormalizedLandmarkList): landmark list of pose results
            result_right_hand (NormalizedLandmarkList): landmark list of right hand results
            result_left_hand (NormalizedLandmarkList): landmark list of left hand results
            result_face (NormalizedLandmarkList): landmark list of face results
            frame (np.ndarray): Video frame

        Returns:
            List[Union[save2Ddata, save2DdataWithName]]: 2D coordinates
        """

        pixel_list = []
        if result_pose is not None:
            for idx, landmark in enumerate(result_pose.landmark): 
                pixel_x = landmark.x * frame.shape[1]
                pixel_y = landmark.y * frame.shape[0]
                if self.with_names:
                    name = self.MediaPipePoseNames.landmark_names_pose.get(idx, f"Landmark {idx}")
                    object = Save2DDataWithName(idx, name, pixel_x, pixel_y)
                else:
                    object = Save2DData(idx, pixel_x, pixel_y)
                pixel_list.append(object)

        if result_right_hand is not None:
            try:
                for idx, landmark in enumerate(result_right_hand.landmark): 
                    pixel_x = landmark.x * frame.shape[1]
                    pixel_y = landmark.y * frame.shape[0]
                    if self.with_names:
                        name = self.MediaPipePoseNames.landmark_names_hand_right.get(idx, f"Landmark {idx}")
                        object = Save2DDataWithName((idx + 100), name, pixel_x, pixel_y)
                    else:
                        object = Save2DData(idx, pixel_x, pixel_y)
                    pixel_list.append(object)
            except:
                for i in range(len(self.MediaPipePoseNames.landmark_names_hand_right)):
                    if self.with_names:
                        name = self.MediaPipePoseNames.landmark_names_hand_right.get(idx, f"Landmark {idx}")
                        object = Save2DDataWithName((idx + 100), name, 0, 0)
                    else:
                        object = Save2DData(idx, 0, 0)
                    pixel_list.append(object)
            
        if result_left_hand is not None:
            try:
                for idx, landmark in enumerate(result_left_hand.landmark): 
                    pixel_x = landmark.x * frame.shape[1]
                    pixel_y = landmark.y * frame.shape[0]
                    if self.with_names:
                        name = self.MediaPipePoseNames.landmark_names_hand_left.get(idx, f"Landmark {idx}")
                        object = Save2DDataWithName((idx + 200), name, pixel_x, pixel_y)
                    else:
                        object = Save2DData(idx, pixel_x, pixel_y)
                    pixel_list.append(object)
            except:
                for i in range(len(self.MediaPipePoseNames.landmark_names_hand_left)):
                    if self.with_names:
                        name = self.MediaPipePoseNames.landmark_names_hand_left.get(idx, f"Landmark {idx}")
                        object = Save2DDataWithName((idx + 200), name, 0, 0)
                    else:
                        object = Save2DData(idx, 0, 0)
                    pixel_list.append(object)

        if result_face is not None:
            try:
                for idx, landmark in enumerate(result_face.landmark): 
                    pixel_x = landmark.x * frame.shape[1]
                    pixel_y = landmark.y * frame.shape[0]
                    if self.with_names:
                        object = Save2DDataWithName((idx + 1000), f'Face {idx}', pixel_x, pixel_y)
                    else:
                        object = Save2DData(idx, pixel_x, pixel_y)
                    pixel_list.append(object)
            except:
                for i in range(478):
                    if self.with_names:
                        object = Save2DDataWithName((idx + 1000), f'Face {idx}', 0, 0)
                    else:
                        object = Save2DData(idx, 0, 0)
                    pixel_list.append(object)

        return pixel_list
        
    def divide_3Dframe(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:

        """
        Divides 3D frame in two frames.

        Args:
            frame (np.ndarray): Video frame

        Returns:
            Tuple[np.ndarray, np.ndarray]: left frame and right frame
        """

        frame_width = frame.shape[1]
        dividing_point = frame_width//2
        frame_left = frame[:, :dividing_point]
        frame_right = frame[:, dividing_point:]
        return (frame_left, frame_right)