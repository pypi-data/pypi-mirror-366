import logging
from argparse import ArgumentParser, Namespace
from typing import Optional

import cv2
import numpy as np
import pyk4a
from pyk4a import PyK4A, PyK4ACapture, Config, PyK4ARecord, PyK4APlayback, ImageFormat, CalibrationType

from visiongraph.input.BaseDepthCamera import BaseDepthCamera
from visiongraph.model.CameraStreamType import CameraStreamType
from visiongraph.util import CommonArgs
from visiongraph.util.ArgUtils import add_enum_choice_argument
from visiongraph.util.CollectionUtils import default_value_dict
from visiongraph.util.TimeUtils import current_millis


class AzureKinectInput(BaseDepthCamera):
    """
    Azure Kinect DK1 input device based on pyk4a library.
    """
    _HeightToResolutionMapping = default_value_dict(pyk4a.ColorResolution.RES_720P,
                                                    {
                                                        720: pyk4a.ColorResolution.RES_720P,
                                                        1080: pyk4a.ColorResolution.RES_1080P,
                                                        1440: pyk4a.ColorResolution.RES_1440P,
                                                        1536: pyk4a.ColorResolution.RES_1536P,
                                                        2160: pyk4a.ColorResolution.RES_2160P,
                                                        3072: pyk4a.ColorResolution.RES_3072P,
                                                    })

    _FPSToK4AFPSMapping = default_value_dict(pyk4a.FPS.FPS_30,
                                             {
                                                 5: pyk4a.FPS.FPS_5,
                                                 15: pyk4a.FPS.FPS_15,
                                                 30: pyk4a.FPS.FPS_30,
                                             })

    def __init__(self, device_id: int = 0):
        """
        Initializes the Azure Kinect input stream with specified device ID.

        :param device_id: The ID of the Azure Kinect device to use. Default is 0.
        """
        super().__init__()
        self.sync_frames: bool = True
        self.align_frames_to_color: bool = False
        self.align_frames_to_depth: bool = False

        self.depth_min_clipping: Optional[int] = 0
        self.depth_max_clipping: Optional[int] = 5000
        self.depth_color_map: Optional[int] = cv2.COLORMAP_JET

        self.ir_min_clipping: Optional[int] = 0
        self.ir_max_clipping: Optional[int] = 5000
        self.ir_color_map: Optional[int] = None
        self.passive_ir: bool = False

        self.device: Optional[PyK4A] = None
        self.capture: Optional[PyK4ACapture] = None

        self.wired_sync_mode: Optional[pyk4a.WiredSyncMode] = None
        self.subordinate_delay_off_master_usec = 0

        self.device_id: int = device_id
        self.color_resolution: Optional[pyk4a.ColorResolution] = None
        self.color_format: pyk4a.ImageFormat = pyk4a.ImageFormat.COLOR_BGRA32
        self.depth_mode: pyk4a.DepthMode = pyk4a.DepthMode.NFOV_UNBINNED

        self.config: Optional[Config] = None

        # recording / playback
        self.input_mkv_file: Optional[str] = None
        self.output_mkv_file: Optional[str] = None

        self._record: Optional[PyK4ARecord] = None
        self._playback: Optional[PyK4APlayback] = None

        self.loop: bool = True

        self._last_color_frame: Optional[np.ndarray] = None
        self._last_ir_frame: Optional[np.ndarray] = None
        self._last_depth_frame: Optional[np.ndarray] = None

    def setup(self, config: Optional[Config] = None):
        """
        Sets up the Azure Kinect device by initializing it and configuring settings.

        :param config: Optional configuration object for initializing the device.
        """
        if self.input_mkv_file is not None:
            logging.info(f"Playing mkv file from {self.input_mkv_file}")
            self._playback = PyK4APlayback(self.input_mkv_file)
            self._playback.open()
            self.color_format = self._playback.configuration["color_format"]
            return

        if self.device_count == 0:
            raise Exception("No Azure Kinect device found!")

        if config is not None:
            self.device = PyK4A(config=config, device_id=self.device_id)
            self.device.start()
        else:
            config = Config()

            if self.color_resolution is None:
                config.color_resolution = AzureKinectInput._HeightToResolutionMapping[self.height]
            else:
                config.color_resolution = self.color_resolution

            config.color_format = self.color_format
            config.camera_fps = AzureKinectInput._FPSToK4AFPSMapping[int(self.fps)]
            config.depth_mode = pyk4a.DepthMode.OFF
            config.synchronized_images_only = False

            if self.use_infrared:
                if self.passive_ir:
                    config.depth_mode = pyk4a.DepthMode.PASSIVE_IR
                else:
                    config.depth_mode = self.depth_mode
                config.synchronized_images_only = self.sync_frames

            if self.enable_depth:
                config.depth_mode = self.depth_mode
                config.synchronized_images_only = self.sync_frames

            if self.wired_sync_mode is not None:
                config.wired_sync_mode = self.wired_sync_mode
            config.subordinate_delay_off_master_usec = self.subordinate_delay_off_master_usec

            self.config = config
            self.device = PyK4A(config=config, device_id=self.device_id)
            self.device.start()

        # set options
        self._apply_initial_settings()

        # recording
        if self.output_mkv_file is not None:
            logging.info(f"Starting recording to {self.output_mkv_file}")
            self._record = PyK4ARecord(device=self.device, config=config, path=self.output_mkv_file)
            self._record.create()

    def read(self) -> (int, Optional[np.ndarray]):
        """
        Reads the next frame from the Azure Kinect device.

        :return: A timestamp and the captured image or None if not available.
        """
        self._read_next_capture()
        time_stamp = current_millis()

        if self._record is not None:
            self._record.write_capture(self.capture)

        if self.enable_depth and self.use_depth_as_input:
            depth = self.capture.depth
            image = self._colorize(depth, (self.depth_min_clipping, self.depth_max_clipping), self.depth_color_map)
            self._last_depth_frame = image
        else:
            if self.use_infrared:
                ir_frame = self.capture.transformed_ir if self.align_frames_to_color else self.capture.ir
                image = self._colorize(ir_frame, (self.ir_min_clipping, self.ir_max_clipping), self.ir_color_map)
                self._last_ir_frame = image
            else:
                image = self.capture.transformed_color if self.align_frames_to_depth else self.capture.color
                if image is not None:
                    image = self._convert_to_bgra_if_required(self.color_format, image)
                    image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
                self._last_color_frame = image

        if image is None:
            logging.warning("could not read frame.")
            return self._post_process(time_stamp, None)

        return self._post_process(time_stamp, image)

    def release(self):
        """
        Releases the Azure Kinect device resources and stops recording or playback.
        """
        if self._record is not None:
            self._record.flush()
            self._record.close()
            logging.info(f"Recording has been written to {self.output_mkv_file}")

        if self._playback is not None:
            self._playback.close()
        else:
            self.device.stop()

    def distance(self, x: float, y: float) -> float:
        """
        Calculates the distance from the camera to a point in the depth frame.

        :param x: The x-coordinate in the depth frame.
        :param y: The y-coordinate in the depth frame.

        :return: The distance in meters to the specified coordinates.
        """
        depth_frame = self.capture.depth
        h, w = depth_frame.shape[:2]

        ix, iy = self._calculate_depth_coordinates(x, y, w, h)

        # convert mm into m
        return float(depth_frame[iy, ix] / 1000)

    def _read_next_capture(self):
        if self._playback is None:
            self.capture = self.device.get_capture()
            return

        try:
            self.capture = self._playback.get_next_capture()
        except EOFError as error:
            if self.loop:
                self._playback.seek(0)
                self.capture = self._playback.get_next_capture()
                return
            raise error

    @staticmethod
    def _convert_to_bgra_if_required(color_format: ImageFormat, color_image):
        """
        Converts the color image to BGRA format if required based on the specified image format.

        :param color_format: The format of the input color image.
        :param color_image: The color image to convert.

        """
        if color_format == ImageFormat.COLOR_BGRA32:
            return color_image

        # examples for all possible pyk4a.ColorFormats
        if color_format == ImageFormat.COLOR_MJPG:
            color_image = cv2.imdecode(color_image, cv2.IMREAD_COLOR)
        elif color_format == ImageFormat.COLOR_NV12:
            color_image = cv2.cvtColor(color_image, cv2.COLOR_YUV2BGRA_NV12)
            # this also works and it explains how the COLOR_NV12 color color_format is stored in memory
            # h, w = color_image.shape[0:2]
            # h = h // 3 * 2
            # luminance = color_image[:h]
            # chroma = color_image[h:, :w//2]
            # color_image = cv2.cvtColorTwoPlane(luminance, chroma, cv2.COLOR_YUV2BGRA_NV12)
        elif color_format == ImageFormat.COLOR_YUY2:
            color_image = cv2.cvtColor(color_image, cv2.COLOR_YUV2BGRA_YUY2)
        return color_image

    @property
    def depth_map(self) -> np.ndarray:
        """
        Gets the colorized depth map of the current frame based on clipping values and color map.

        :return: The colorized depth map.
        """
        return self._colorize(self.depth_buffer, (self.depth_min_clipping, self.depth_max_clipping),
                              self.depth_color_map)

    @property
    def depth_buffer(self) -> np.ndarray:
        """
        Retrieves the current depth buffer array based on frame alignment settings.

        :return: The raw depth buffer.
        """
        if self.align_frames_to_color:
            return self.capture.transformed_depth
        return self.capture.depth

    @property
    def device_count(self) -> int:
        """
        Gets the number of connected Azure Kinect devices.

        :return: The count of connected devices.
        """
        return pyk4a.connected_device_count()

    def configure(self, args: Namespace):
        """
        Configures the Azure Kinect input using command line arguments.

        :param args: The command line arguments to configure the input.
        """
        super().configure(args)

        if args.source is not None:
            args.k4a_play_mkv = args.source

        self.align_frames_to_color = args.k4a_align_to_color
        self.align_frames_to_depth = args.k4a_align_to_depth

        self.device_id = args.k4a_device

        self.output_mkv_file = args.k4a_record_mkv
        self.input_mkv_file = args.k4a_play_mkv

        self.depth_mode = args.k4a_depth_mode
        self.color_resolution = args.k4a_color_resolution
        self.color_format = args.k4a_color_format

        self.depth_min_clipping, self.depth_max_clipping = args.k4a_depth_clipping
        self.ir_min_clipping, self.ir_max_clipping = args.k4a_ir_clipping

        self.passive_ir = args.k4a_passive_ir

        self.wired_sync_mode = args.k4a_wired_sync_mode
        self.subordinate_delay_off_master_usec = args.k4a_subordinate_delay_off_master_usec

    @staticmethod
    def add_params(parser: ArgumentParser):
        """
        Adds the Azure Kinect input parameters to the argument parser.

        :param parser: The argument parser to add parameters to.
        """
        super(AzureKinectInput, AzureKinectInput).add_params(parser)
        CommonArgs.add_source_argument(parser)

        parser.add_argument("--k4a-align-to-color", action="store_true",
                            help="Align azure frames to color frame.")
        parser.add_argument("--k4a-align-to-depth", action="store_true",
                            help="Align azure frames to depth frame.")
        parser.add_argument("--k4a-device", type=int, default=0, help="Azure device id.")

        parser.add_argument("--k4a-depth-clipping", default=[0, 5000], type=int, nargs=2,
                            metavar=("min", "max"), help="Depth input clipping.")
        parser.add_argument("--k4a-ir-clipping", default=[0, 5000], type=int, nargs=2,
                            metavar=("min", "max"), help="Infrared input clipping.")

        parser.add_argument("--k4a-play-mkv", type=str, default=None,
                            help="Path to a pre-recorded bag file for playback.")
        parser.add_argument("--k4a-record-mkv", type=str, default=None,
                            help="Path to a mkv file to store the current recording.")

        add_enum_choice_argument(parser, pyk4a.DepthMode, "--k4a-depth-mode", default=pyk4a.DepthMode.NFOV_UNBINNED,
                                 help="Azure depth mode")
        parser.add_argument("--k4a-passive-ir", action="store_true",
                            help="Use passive IR input.")
        add_enum_choice_argument(parser, pyk4a.ColorResolution, "--k4a-color-resolution",
                                 default=pyk4a.ColorResolution.RES_720P,
                                 help="Azure color resolution (overwrites input-size)")
        add_enum_choice_argument(parser, pyk4a.ImageFormat, "--k4a-color-format",
                                 default=pyk4a.ImageFormat.COLOR_BGRA32,
                                 help="Azure color image format")

        add_enum_choice_argument(parser, pyk4a.WiredSyncMode, "--k4a-wired-sync-mode", default=None,
                                 help="Synchronization mode when connecting two or more devices together")
        parser.add_argument("--k4a-subordinate-delay-off-master-usec", type=int, default=0,
                            help="The external synchronization timing.")

    @property
    def gain(self) -> int:
        """
        Gets the current gain setting for the device.

        :return: The current gain setting.
        """
        return self.device.gain

    @gain.setter
    def gain(self, value: int):
        """
        Sets the gain for the device.

        :param value: The gain value to set.
        """
        self.device.gain = value

    @property
    def exposure(self) -> int:
        """
        Gets the current exposure setting for the device.

        :return: The current exposure setting.
        """
        return self.device.exposure

    @exposure.setter
    def exposure(self, value: int):
        """
        Sets the exposure for the device.

        :param value: The exposure value to set.
        """
        self.device.exposure = value

    @property
    def enable_auto_exposure(self) -> bool:
        """
        Checks if auto exposure is enabled.

        :return: True if auto exposure is enabled, False otherwise.
        """
        return self.device.exposure_mode_auto

    @enable_auto_exposure.setter
    def enable_auto_exposure(self, value: bool):
        """
        Enables or disables auto exposure.

        :param value: Flag to enable or disable auto exposure.
        """
        self.device.exposure_mode_auto = value

    @property
    def enable_auto_white_balance(self) -> bool:
        """
        Checks if auto white balance is enabled.

        :return: True if auto white balance is enabled, False otherwise.
        """
        return self.device.whitebalance_mode_auto

    @enable_auto_white_balance.setter
    def enable_auto_white_balance(self, value: bool):
        """
        Enables or disables auto white balance.

        :param value: Flag to enable or disable auto white balance.
        """
        self.device.whitebalance_mode_auto = value

    @property
    def white_balance(self) -> int:
        """
        Gets the current white balance setting for the device.

        :return: The current white balance setting.
        """
        return self.device.whitebalance

    @white_balance.setter
    def white_balance(self, value: int):
        """
        Sets the white balance for the device.

        :param value: The white balance value to set.
        """
        value = value // 10 * 10
        self.device.whitebalance = value

    @staticmethod
    def _to_k4a_calibration_type(stream: CameraStreamType) -> CalibrationType:
        """
        Converts CameraStreamType to PyK4A calibration type.

        :param stream: The camera stream type.

        :return: The corresponding calibration type.

        :raises Exception: If the stream type is not recognized.
        """
        if stream == CameraStreamType.Color:
            return CalibrationType.COLOR
        elif stream == CameraStreamType.Depth:
            return CalibrationType.DEPTH
        elif stream == CameraStreamType.Infrared:
            return CalibrationType.DEPTH

        raise Exception(f"Azure Kinect calibration type {stream} not available.")

    def get_camera_matrix(self, stream_type: CameraStreamType = CameraStreamType.Color) -> np.ndarray:
        """
        Retrieves the camera matrix for a specified stream type.

        :param stream_type: The type of camera stream (Color, Depth, or Infrared).

        :return: The camera matrix for the specified stream type.
        """
        calibration = self.playback.calibration if self.is_playback else self.device.calibration
        return calibration.get_camera_matrix(self._to_k4a_calibration_type(stream_type))

    def get_fisheye_distortion(self, stream_type: CameraStreamType = CameraStreamType.Color) -> np.ndarray:
        """
        Retrieves the fisheye distortion coefficients for a specified stream type.

        :param stream_type: The type of camera stream (Color, Depth, or Infrared).

        :return: The fisheye distortion coefficients for the specified stream type.
        """
        calibration = self.playback.calibration if self.is_playback else self.device.calibration
        return calibration.get_distortion_coefficients(self._to_k4a_calibration_type(stream_type))

    def pre_process_image(self, image: np.ndarray,
                          stream_type: CameraStreamType = CameraStreamType.Color) -> Optional[np.ndarray]:
        """
        Pre-processes the input image based on the stream type.

        :param image: The image to process.
        :param stream_type: The type of camera stream (Color, Depth, or Infrared).

        :return: The processed image after applying colorization if applicable.
        """
        if stream_type == CameraStreamType.Depth:
            return self._colorize(image, (self.depth_min_clipping, self.depth_max_clipping), self.depth_color_map)
        elif stream_type == CameraStreamType.Infrared:
            return self._colorize(image, (self.ir_min_clipping, self.ir_max_clipping), self.ir_color_map)

        return image

    def get_raw_image(self, stream_type: CameraStreamType = CameraStreamType.Color) -> Optional[np.ndarray]:
        """
        Retrieves the raw image from the specified stream type.

        :param stream_type: The type of camera stream (Color, Depth, or Infrared).

        :return: The raw image for the specified stream type, or None if unavailable.
        """
        if stream_type == CameraStreamType.Depth:
            if self.align_frames_to_color:
                return self.transformed_depth
            else:
                return self.depth
        elif stream_type == CameraStreamType.Infrared:
            if self.align_frames_to_color:
                return self.transformed_infrared
            else:
                return self.infrared
        elif stream_type == CameraStreamType.Color:
            if self.align_frames_to_depth:
                return self.transformed_color
            else:
                return self.color

        return None

    @property
    def serial(self) -> str:
        """
        Gets the serial number of the connected Azure Kinect device.

        :return: The serial number of the device.
        """
        return self.device.serial

    @property
    def color(self) -> np.ndarray:
        """
        Retrieves the color image from the current capture.

        :return: The color image.
        """
        if self._playback is None:
            return self.capture.color

        color = self._convert_to_bgra_if_required(self._playback.configuration["color_format"], self.capture.color)
        return color

    @property
    def transformed_color(self) -> np.ndarray:
        """
        Retrieves the transformed color image.

        :return: The transformed color image aligned with depth frame.
        """
        if self._playback is None:
            return self.capture.transformed_color

        color = self._convert_to_bgra_if_required(self._playback.configuration["color_format"], self.capture.color)
        color = cv2.cvtColor(color, cv2.COLOR_RGB2RGBA)
        depth = self.capture.depth
        transformed = pyk4a.color_image_to_depth_camera(color, depth,
                                                        self._playback.calibration, self._playback.thread_safe)
        transformed = transformed[:, :, :3]
        return transformed

    @property
    def infrared(self) -> np.ndarray:
        """
        Retrieves the infrared image from the current capture.

        :return: The infrared image.
        """
        return self.capture.ir

    @property
    def transformed_infrared(self) -> np.ndarray:
        """
        Retrieves the transformed infrared image.

        :return: The transformed infrared image aligned with depth frame.
        """
        return self.capture.transformed_ir

    @property
    def depth(self) -> np.ndarray:
        """
        Retrieves the depth image from the current capture.

        :return: The depth image.
        """
        return self.capture.depth

    @property
    def transformed_depth(self) -> np.ndarray:
        """
        Retrieves the transformed depth image.

        :return: The transformed depth image aligned with color frame.
        """
        return self.capture.transformed_depth

    @property
    def is_playback(self):
        """
        Checks if the input is currently in playback mode.

        :return: True if in playback mode, False otherwise.
        """
        return self._playback is not None

    @property
    def playback(self) -> Optional[PyK4APlayback]:
        """
        Gets the playback object if available.

        :return: The playback object.
        """
        return self._playback

    @property
    def record_length_ms(self) -> float:
        """
        Gets the length of the recording in milliseconds.

        :return: The length of the recording, or -1 if not in playback mode.
        """
        if self._playback is None:
            logging.warning("Azure Kinect is not a playback device.")
            return -1

        return self._playback.length / 1000

    def seek(self, time_ms: float):
        """
        Seeks to a specific time in playback.

        :param time_ms: The time in milliseconds to seek to.
        """
        if self._playback is None:
            logging.warning("Azure Kinect is not a playback device.")
            return

        self._playback.seek(int(time_ms * 1000))
