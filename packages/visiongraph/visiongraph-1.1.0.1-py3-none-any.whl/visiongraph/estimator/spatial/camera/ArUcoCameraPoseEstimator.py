from argparse import ArgumentParser, Namespace
from typing import Optional

import cv2
import numpy as np
import vector
from cv2 import aruco

from visiongraph.estimator.VisionEstimator import VisionEstimator
from visiongraph.result.ArUcoCameraPose import ArUcoCameraPose
from visiongraph.result.ArUcoMarkerDetection import ArUcoMarkerDetection


class ArUcoCameraPoseEstimator(VisionEstimator[Optional[ArUcoCameraPose]]):
    """
    A class to estimate camera pose using ArUco markers.

    It provides a way to detect and track ArUco markers in an image or video stream,
    estimate the corresponding 3D pose, and draw the marker corners on the original image.
    """

    def __init__(self,
                 camera_matrix: np.ndarray,
                 fisheye_distortion: np.ndarray,
                 aruco_config: int = aruco.DICT_6X6_50,
                 marker_length_in_m: float = 0.1):
        """
        Initializes the ArUcoCameraPoseEstimator object.

        :param camera_matrix: The camera intrinsic matrix.
        :param fisheye_distortion: The camera distortion coefficients.
        :param aruco_config: The configuration of the ArUco dictionary. Defaults to aruco.DICT_6X6_50.
        :param marker_length_in_m: The length of an ArUco marker in meters. Defaults to 0.1.
        """
        self.camera_matrix = camera_matrix
        self.fisheye_distortion = fisheye_distortion

        self.aruco_config: int = aruco_config

        self.marker_size_in_m: float = marker_length_in_m

        self.aruco_dict: Optional[int] = None
        self.aruco_params: Optional[aruco.DetectorParameters] = None
        self.aruco_detector: Optional[aruco.ArucoDetector] = None

    def setup(self):
        """
        Sets up the ArUco marker detector and parameters.
        """
        self.aruco_dict = aruco.getPredefinedDictionary(self.aruco_config)
        self.aruco_params = aruco.DetectorParameters()
        self.aruco_detector = aruco.ArucoDetector(self.aruco_dict, self.aruco_params)

    def process(self, data: np.ndarray) -> Optional[ArUcoCameraPose]:
        """
        Processes the input image or video frame to detect ArUco markers and estimate camera pose.

        :param data: The input image or video frame.

        :return: The estimated camera pose if an ArUco marker is detected, otherwise None.
        """
        # find ArUco markers
        (corners, ids, rejected) = self.aruco_detector.detectMarkers(data)

        if len(corners) == 0:
            return None

        # select first marker
        ids = ids.flatten()
        marker_corner, marker_id = list(zip(corners, ids))[0]

        # top-left, top-right, bottom-right, and bottom-left order
        corners = marker_corner.reshape((4, 2))
        (topLeft, topRight, bottomRight, bottomLeft) = corners

        marker = ArUcoMarkerDetection(marker_id,
                                      vector.obj(x=topLeft[0], y=topLeft[1]),
                                      vector.obj(x=topRight[0], y=topRight[1]),
                                      vector.obj(x=bottomRight[0], y=bottomRight[1]),
                                      vector.obj(x=bottomLeft[0], y=bottomLeft[1]))

        # estimate pose
        rotation_vector, translation_vector, _ = aruco.estimatePoseSingleMarkers([marker_corner],
                                                                                 self.marker_size_in_m,
                                                                                 self.camera_matrix,
                                                                                 self.fisheye_distortion)

        cv2.drawFrameAxes(data, self.camera_matrix, self.fisheye_distortion, rotation_vector, translation_vector, 0.1)

        #
        return ArUcoCameraPose(position=vector.obj(x=translation_vector[0, 0, 0],
                                                   y=translation_vector[0, 0, 1],
                                                   z=translation_vector[0, 0, 2]),
                               rotation=vector.obj(x=rotation_vector[0, 0, 0],
                                                   y=rotation_vector[0, 0, 1],
                                                   z=rotation_vector[0, 0, 2]),
                               marker=marker)

    def release(self):
        """
        Releases any system resources used by the estimator.
        """
        pass

    def configure(self, args: Namespace):
        """
        Configures the estimator based on the provided command-line arguments.

        :param args: The parsed command-line arguments.
        """
        pass

    @staticmethod
    def add_params(parser: ArgumentParser):
        """
        Adds parameters to the parser for configuration.

        :param parser: The parser to add parameters to.
        """
        pass
