import logging
from argparse import ArgumentParser, Namespace
from typing import Optional, Tuple

import cv2
import numpy as np
from cv2 import aruco

from visiongraph.estimator.spatial.camera.BoardCameraCalibrator import BoardCameraCalibrator
from visiongraph.model.CameraIntrinsics import CameraIntrinsics
from visiongraph.result.CameraPoseResult import CameraPoseResult


class ChArUcoCalibrator(BoardCameraCalibrator):
    """
    A class to perform camera calibration using ChArUco boards.
    """

    def __init__(self, columns: int, rows: int,
                 marker_length_in_m: float = 0.23,
                 square_length_in_m: float = 0.3,
                 aruco_config: int = aruco.DICT_4X4_50,
                 max_samples: int = -1):
        """
        Initializes the ChArUcoCalibrator with specified parameters.

        :param columns: Number of columns in the ChArUco board.
        :param rows: Number of rows in the ChArUco board.
        :param marker_length_in_m: Length of the markers in meters.
        :param square_length_in_m: Length of the squares in meters.
        :param aruco_config: Configuration for the ArUco dictionary.
        :param max_samples: Maximum number of samples to collect for calibration.
        """
        super().__init__(rows, columns, max_samples)

        self.marker_length_in_m: float = marker_length_in_m
        self.square_length_in_m = square_length_in_m
        self.aruco_config = aruco_config

        self.board: Optional[aruco.CharucoBoard] = None
        self.detector: Optional[aruco.CharucoDetector] = None
        self.aruco_params: Optional[aruco.CharucoParameters] = None
        self.aruco_dict: Optional[int] = None

        self.corners = []
        self.ids = []

        self.image_size: Optional[Tuple[int, int]] = None

        self.pose_result: Optional[CameraPoseResult] = None

        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.00001)

    def setup(self):
        """
        Sets up the ChArUco board and initializes the detector.
        """
        self.corners = []
        self.ids = []

        self.aruco_dict = aruco.getPredefinedDictionary(self.aruco_config)
        self.aruco_params = aruco.CharucoParameters()
        self.board = aruco.CharucoBoard((self.rows, self.columns),
                                        self.square_length_in_m, self.marker_length_in_m,
                                        self.aruco_dict)
        self.detector = aruco.CharucoDetector(self.board)

    def process(self, data: np.ndarray) -> Optional[CameraPoseResult]:
        """
        Processes the input data to detect ChArUco markers and calibrate the camera.

        :param data: The input image data.

        :return: The result of the camera pose estimation, or None if not available.
        """
        self.board_detected = False

        if self.pose_result is not None:
            return self.pose_result

        gray = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)

        # find markers
        charuco_corners, charuco_ids, marker_corners, marker_ids = self.detector.detectBoard(gray)

        if charuco_corners is not None and len(charuco_corners) > 0:
            self.image_size = gray.shape[::-1]

            if len(charuco_corners) > 3:
                self.corners.append(charuco_corners)
                self.ids.append(charuco_ids)

                aruco.drawDetectedMarkers(data, marker_corners, marker_ids)
                self.board_detected = True

        if 0 < self.max_samples <= self.sample_count:
            return self.calibrate()

        return None

    def calibrate(self) -> Optional[CameraPoseResult]:
        """
        Calibrates the camera using the detected corners and IDs.

        :raises Exception: If calibration is not supported by OpenCV.

        :return: The result of the camera pose estimation, or None if calibration fails.
        """
        raise Exception("Currently not supported! - Waiting for fix by opencv!")

        (ret, camera_matrix, distortion_coefficients,
         rotation_vectors, translation_vectors,
         std_deviations_intrinsics, std_deviations_extrinsics,
         per_view_errors) = cv2.aruco.calibrateCameraCharucoExtended(
            charucoCorners=self.corners,
            charucoIds=self.ids,
            board=self.board,
            imageSize=self.image_size,
            cameraMatrix=None,
            distCoeffs=None,
            criteria=self.criteria)

        if ret:
            intrinsics = CameraIntrinsics(camera_matrix, distortion_coefficients.flatten())
            self.pose_result = CameraPoseResult(intrinsics)

            error = float(sum(per_view_errors) / len(per_view_errors))
            print(f"Error: {error:.4f}")

            return self.pose_result

        logging.warning(f"Could not calibrate camera with {self.sample_count} samples.")
        return None

    def release(self):
        """
        Releases resources associated with the calibrator.
        """
        pass

    def configure(self, args: Namespace):
        """
        Configures the calibrator with command line arguments.

        :param args: The parsed command line arguments.
        """
        self.marker_length_in_m = float(args.marker_length)
        self.square_length_in_m = float(args.square_length)

    @staticmethod
    def add_params(parser: ArgumentParser):
        """
        Adds command line arguments for the calibrator.

        :param parser: The argument parser to which parameters are added.
        """
        parser.add_argument("--marker-length", type=float, required=True, help="Marker length in m.")
        parser.add_argument("--square-length", type=float, required=True, help="Square length in m.")

    @property
    def sample_count(self) -> int:
        """
        Gets the count of samples collected.

        :return: The number of samples collected.
        """
        return len(self.ids)
