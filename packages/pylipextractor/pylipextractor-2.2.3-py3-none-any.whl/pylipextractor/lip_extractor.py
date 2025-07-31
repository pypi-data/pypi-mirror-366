# pylipextractor/pylipextractor/lip_extractor.py

import os
import cv2
import numpy as np
import mediapipe as mp
import av
from pathlib import Path
import warnings
import math
import subprocess
import time
import cProfile
import pstats
from typing import Tuple, Optional, List, Union
import logging

def _histogram_matching(src, ref):
    """
    Matches the histogram of a source image to a reference image.
    """
    # Convert the images to YCrCb color space
    src_ycrcb = cv2.cvtColor(src, cv2.COLOR_RGB2YCrCb)
    ref_ycrcb = cv2.cvtColor(ref, cv2.COLOR_RGB2YCrCb)

    # Split the images into their components
    src_y, src_cr, src_cb = cv2.split(src_ycrcb)
    ref_y, _, _ = cv2.split(ref_ycrcb)

    # Compute the histograms of the Y channels
    src_hist, _ = np.histogram(src_y.flatten(), 256, [0, 256])
    ref_hist, _ = np.histogram(ref_y.flatten(), 256, [0, 256])

    # Compute the cumulative distribution functions (CDFs)
    src_cdf = src_hist.cumsum()
    ref_cdf = ref_hist.cumsum()

    # Normalize the CDFs
    src_cdf_normalized = src_cdf * ref_hist.max() / src_hist.max()

    # Create a lookup table
    lookup_table = np.zeros(256, dtype=np.uint8)
    for i in range(256):
        j = 255
        while j >= 0 and src_cdf_normalized[i] < ref_cdf[j]:
            j -= 1
        lookup_table[i] = j

    # Apply the lookup table to the Y channel of the source image
    src_y_matched = cv2.LUT(src_y, lookup_table)

    # Merge the matched Y channel back with the original Cr and Cb channels
    src_ycrcb_matched = cv2.merge([src_y_matched, src_cr, src_cb])

    # Convert the matched YCrCb image back to RGB color space
    src_matched = cv2.cvtColor(src_ycrcb_matched, cv2.COLOR_YCrCb2RGB)

    return src_matched


# --- Setup for logging ---
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# --- Suppress specific MediaPipe warnings and GLOG messages ---
warnings.filterwarnings("ignore", category=UserWarning, module="mediapipe")
os.environ['GLOG_minloglevel'] = '2' # Suppress all GLOG messages below WARNING level.

# Access the pre-defined lip connections from MediaPipe
_LIP_CONNECTIONS = mp.solutions.face_mesh.FACEMESH_LIPS

# Extract all unique landmark indices involved in these connections
LIPS_MESH_LANDMARKS_INDICES = sorted(list(set([
    idx for connection in _LIP_CONNECTIONS for idx in connection
])))

# Additional landmarks for expanded bounding box
NOSE_BOTTOM_LANDMARK_INDEX = 2
CHIN_BOTTOM_LANDMARK_INDEX = 200
# LEFT_CHEEK_LANDMARK_INDEX = 58
# RIGHT_CHEEK_LANDMARK_INDEX = 288

# Import MainConfig here so LipExtractor can manage it as a class-level attribute
from pylipextractor.config import MainConfig, LipExtractionConfig 


class LipExtractor:
    """
    A class for extracting lip frames from videos using MediaPipe Face Mesh.
    This class crops and resizes lip frames, returning them as a NumPy array.
    It also provides utilities for loading previously saved NPY files.
    """
    # Class-level attribute to hold MediaPipe model instance, initialized once for all objects
    _mp_face_mesh_instance = None 

    # Class-level attribute to hold the configuration.
    # Users can access and modify this directly: LipExtractor.config.IMG_H = ...
    config: LipExtractionConfig = MainConfig().lip_extraction 

    def __init__(self):
        """
        Initializes the LipExtractor.
        Configuration is managed by the class-level attribute `LipExtractor.config`.
        """
        # Ensure MediaPipe model is loaded/initialized for this process
        self._initialize_mediapipe_if_not_set()
        # Assign the class-level MediaPipe instance to the object for convenient access
        self.mp_face_mesh = LipExtractor._mp_face_mesh_instance

        # --- Changes for EMA Smoothing ---
        self.ema_smoothed_bbox = None # To store the last smoothed bounding box for EMA
        # --- End Changes for EMA Smoothing ---

    @classmethod
    def _initialize_mediapipe_if_not_set(cls):
        """
        Initializes the MediaPipe Face Mesh model if it hasn't been initialized yet.
        This ensures the model is loaded only once across all instances and processes.
        """
        if cls._mp_face_mesh_instance is None:
            cls._mp_face_mesh_instance = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,  # Assume one dominant face in the video
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                refine_landmarks=cls.config.REFINE_LANDMARKS
            )
            logger.debug(f"MediaPipe Face Mesh model loaded for process {os.getpid()}.")

    @staticmethod
    def _is_black_frame(frame_np: np.ndarray) -> bool:
        """
        Checks if a frame is completely black (all pixel values are zero).
        
        Args:
            frame_np (np.ndarray): NumPy array representing the image frame.
            
        Returns:
            bool: `True` if the frame is black or `None`/empty, otherwise `False`.
        """
        if frame_np is None or frame_np.size == 0:
            return True
        return np.sum(frame_np) == 0

    def _debug_frame_processing(self, frame, frame_idx, debug_type, current_lip_bbox_val=None, mp_face_landmarks=None):
        """
        Saves debug frames at various stages of processing for visual inspection.
        
        Args:
            frame (np.array): Image frame (assumed RGB format).
            frame_idx (int): Current frame index.
            debug_type (str): Type of debug frame ('original', 'landmarks', 'clahe_applied', 'black_generated').
            current_lip_bbox_val (tuple or np.ndarray, optional): The bounding box value (x1, y1, x2, y2).
                                                                  Can be None if no valid bbox.
            mp_face_landmarks (mp.solution.face_mesh.NormalizedLandmarkList, optional): Raw MediaPipe landmarks.
        """
        if not self.config.SAVE_DEBUG_FRAMES or frame_idx >= self.config.MAX_DEBUG_FRAMES:
            return

        debug_dir = self.config.DEBUG_OUTPUT_DIR
        debug_dir.mkdir(parents=True, exist_ok=True)

        display_frame = frame.copy()
        # Ensure frame is 3-channel for text overlay if it's grayscale
        if len(display_frame.shape) == 2: # If grayscale, convert to BGR for text overlay and saving
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_GRAY2BGR)
        
        cv2.putText(display_frame, f"{debug_type.capitalize()} Frame {frame_idx}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if debug_type == 'landmarks' and mp_face_landmarks is not None:
            # Draw all detected face mesh landmarks (for general debug)
            for lm_idx_all, lm in enumerate(mp_face_landmarks.landmark):
                x, y = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
                color = (0, 255, 0) # Default green for all landmarks
                if lm_idx_all in LIPS_MESH_LANDMARKS_INDICES or lm_idx_all in [NOSE_BOTTOM_LANDMARK_INDEX, CHIN_BOTTOM_LANDMARK_INDEX]:
                    color = (255, 0, 0) # Red for actual lip landmarks to highlight them
                cv2.circle(display_frame, (x, y), 1, color, -1)
            # Draw the calculated bounding box for the lip
            if current_lip_bbox_val is not None and len(current_lip_bbox_val) == 4: # Ensure it's a valid bbox (tuple or list)
                # Convert to int if it's a numpy array to avoid potential float issues with cv2.rectangle
                x1, y1, x2, y2 = [int(val) for val in current_lip_bbox_val]
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 0, 255), 2) # Red rectangle for lip bbox
        
        # Convert to BGR for OpenCV saving
        if len(display_frame.shape) == 3 and display_frame.shape[2] == 3: # Only convert if it's already RGB
            display_frame_bgr = cv2.cvtColor(display_frame, cv2.COLOR_RGB2BGR)
        else: # Otherwise, it might already be BGR or grayscale, keep as is
            display_frame_bgr = display_frame
            
        cv2.imwrite(str(debug_dir / f"{debug_type}_{frame_idx:04d}.png"), display_frame_bgr)


    @staticmethod
    def _is_hw_encoder_available(encoder: str) -> bool:
        """
        Checks if a specific hardware encoder is available in FFmpeg.
        """
        try:
            result = subprocess.run(['ffmpeg', '-encoders'], capture_output=True, text=True, check=True)
            return encoder in result.stdout
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def _apply_ema_smoothing(self, current_bbox: Optional[np.ndarray]) -> np.ndarray:
        """
        Applies Exponential Moving Average (EMA) to bounding box coordinates.
        The `ema_smoothed_bbox` attribute is used to maintain state across frames.
        
        Args:
            current_bbox (np.ndarray, optional): Bounding box (x1, y1, x2, y2) for the current frame
                                                 as a NumPy array. `None` if no face/lip detected.
        Returns:
            np.ndarray: The smoothed bounding box (x1, y1, x2, y2) as a NumPy array.
        """
        # If no current bbox is detected, and we have a previous smoothed value, use that
        # Otherwise, if no history and no current detection, use a default black frame bbox.
        if current_bbox is None:
            if self.ema_smoothed_bbox is not None:
                # If current detection failed, but we have a previous smoothed state, repeat it
                # This helps in maintaining continuity during brief detection drops.
                logger.debug(f"EMA: current_bbox is None, using previous smoothed_bbox: {self.ema_smoothed_bbox}")
                return self.ema_smoothed_bbox
            else:
                # If no detection and no history, return a default "black frame" bbox
                default_bbox = np.array([0, 0, self.config.IMG_W, self.config.IMG_H], dtype=np.int32)
                logger.debug(f"EMA: current_bbox is None and no previous smoothed_bbox, returning default black frame bbox: {default_bbox}")
                return default_bbox
        
        # Ensure current_bbox is a NumPy array for calculations
        current_bbox_np = np.array(current_bbox, dtype=np.float32)
        logger.debug(f"EMA: current_bbox_np: {current_bbox_np}")

        if self.ema_smoothed_bbox is None:
            # Initialize EMA with the first valid detection
            self.ema_smoothed_bbox = current_bbox_np
            logger.debug(f"EMA: Initializing smoothed_bbox with current_bbox_np: {self.ema_smoothed_bbox}")
        else:
            # Apply EMA formula: new_smoothed = alpha * current_value + (1 - alpha) * old_smoothed
            self.ema_smoothed_bbox = (self.config.EMA_ALPHA * current_bbox_np +
                                      (1 - self.config.EMA_ALPHA) * self.ema_smoothed_bbox)
            logger.debug(f"EMA: Applying smoothing. Old: {self.ema_smoothed_bbox}, New (before round): {self.ema_smoothed_bbox}")
        
        return self.ema_smoothed_bbox.astype(np.int32)


    # REMOVED @staticmethod decorator
    def _convert_video_to_mp4(self, input_filepath: Path, output_directory: Path) -> Optional[Path]:
        """
        Converts a video file to MP4 format using FFmpeg.
        
        Args:
            input_filepath (Path): Path to the input video file.
            output_directory (Path): Directory where the MP4 output file will be saved.
                                     This directory will be created if it does not exist.
                                     
        Returns:
            Optional[Path]: Path to the converted MP4 file, or `None` if conversion fails.
        """
        output_directory.mkdir(parents=True, exist_ok=True)
        filename_without_ext = input_filepath.stem
        output_filepath = output_directory / f"{filename_without_ext}.mp4"

        # Determine the encoder based on the configuration
        device = self.config.HW_ACCELERATION_DEVICE.lower() # Normalize to lowercase
        encoder = 'libx264'
        preset = 'veryfast'

        if device == 'cuda' or (device == 'auto' and self._is_hw_encoder_available('h264_nvenc')):
            if self._is_hw_encoder_available('h264_nvenc'):
                encoder = 'h264_nvenc'
                preset = 'p6'
                logger.info("Using NVIDIA GPU (h264_nvenc) for hardware-accelerated video conversion.")
            else:
                logger.warning("NVIDIA GPU (h264_nvenc) not available. Falling back to CPU (libx264).")
                encoder = 'libx264'
                preset = 'veryfast'
        else:
            logger.info("Using CPU (libx264) for video conversion.")

        # FFmpeg command for converting to MP4 with H.264 video and AAC audio
        ffmpeg_command = (
            f"ffmpeg -i \"{input_filepath}\" -c:v {encoder} -preset {preset} "
            f"-crf 0 -an -y -loglevel quiet \"{output_filepath}\""
        )

        logger.info(f"Attempting to convert '{input_filepath.name}' to MP4...")
        try:
            subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True, shell=True)
            logger.info(f"Conversion successful: '{output_filepath.name}'.") 
            return output_filepath
        except FileNotFoundError:
            logger.error("FFmpeg not found. Please ensure FFmpeg is installed and added to your system's PATH to use video conversion. Skipping conversion.") 
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"Error converting '{input_filepath.name}' with FFmpeg: {e}") 
            logger.error(f"FFmpeg stdout: {e.stdout}") 
            logger.error(f"FFmpeg stderr: {e.stderr}") 
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during FFmpeg conversion of '{input_filepath.name}': {e}") 
            return None
        
    def extract_lip_frames(self, video_path: Union[str, Path], output_npy_path: Optional[Union[str, Path]] = None) -> Tuple[Optional[np.ndarray], Optional[float]]:
        """
        Extracts and processes lip frames from a video.
        Uses PyAV for efficient video reading and MediaPipe for accurate facial landmark detection.
        
        Args:
            video_path (Union[str, Path]): Path to the input video file (e.g., MP4, MPG).
            output_npy_path (Union[str, Path], optional): Path to the .npy file where the extracted
                                                          lip frames will be saved. If `None`,
                                                          frames are only returned, not saved.
            
        Returns:
            Tuple[Optional[np.ndarray], Optional[float]]: A tuple containing:
                                                            - NumPy array of processed lip frames in RGB format
                                                              (shape: NUM_FRAMES x IMG_H x IMG_W x 3), or `None`.
                                                            - The calculated Real-Time Factor (RTF) as a float, or `None`.
                                                          Returns `None, None` if an error occurs during processing or
                                                          if the extracted clip is deemed invalid (e.g., too many problematic frames).
        """
        original_video_path = Path(video_path) 
        current_video_path = original_video_path 
        rtf = None # Initialize rtf to None for all paths

        # --- NEW: Optional MP4 Conversion ---
        converted_temp_mp4_path = None
        if self.config.CONVERT_TO_MP4_IF_NEEDED and original_video_path.suffix.lower() not in ['.mp4', '.mov']: 
            logger.info(f"'{original_video_path.name}' is not in MP4/MOV format. Attempting conversion...") 
            converted_temp_mp4_path = self._convert_video_to_mp4(original_video_path, self.config.MP4_TEMP_DIR)
            if converted_temp_mp4_path:
                current_video_path = converted_temp_mp4_path
            else:
                logger.warning(f"MP4 conversion failed for '{original_video_path.name}'. Attempting to process original file.") 
                current_video_path = original_video_path 

        if self.config.PROFILE_CODE:
            profiler = cProfile.Profile()
            profiler.enable()

        if not current_video_path.exists():
            logger.error(f"Video file not found at '{current_video_path}'. Processing stopped.")
            return None, None # Changed: return None, None

        # --- RTF Calculation Initialization ---
        if self.config.CALCULATE_RTF:
            start_time = time.time()
            video_duration_seconds = 0.0

        processed_frames_temp_list = []
        # --- Reset EMA state for each new video ---
        self.ema_smoothed_bbox = None

        try:
            container = av.open(str(current_video_path))
            if self.config.CALCULATE_RTF:
                video_duration_seconds = container.duration / 1000000  # Duration in seconds
        except AVError as e: # Changed: Used imported AVError
            logger.error(f"Error opening video '{current_video_path.name}' with PyAV: {e}. Processing stopped.")
            return None, None # Changed: return None, None
        except Exception as e: # Added: Catch other potential exceptions during container opening
            logger.error(f"An unexpected error occurred while opening video '{current_video_path.name}': {e}. Processing stopped.")
            return None, None # Changed: return None, None


        if not container.streams.video:
            logger.error(f"No video stream found in '{current_video_path.name}'. Processing stopped.") 
            container.close()
            return None, None # Changed: return None, None
            
        video_stream = container.streams.video[0]

        # Determine the total number of frames to process
        total_frames_to_process = self.config.MAX_FRAMES
        if total_frames_to_process is None:
            try:
                frames_from_av = video_stream.frames
                if frames_from_av is not None and frames_from_av > 0:
                    total_frames_to_process = frames_from_av
                else:
                    total_frames_to_process = float('inf') 
            except Exception:
                total_frames_to_process = float('inf') 

        logger.info(f"Processing video: '{current_video_path.name}' ({total_frames_to_process if total_frames_to_process != float('inf') else 'all available'} frames)...") 

        # --- Get reference frame for histogram matching ---
        ref_frame = None
        if self.config.APPLY_HISTOGRAM_MATCHING:
            try:
                container.seek(int(container.duration / 2))
                ref_frame_av = next(container.decode(video=0))
                ref_frame = ref_frame_av.to_rgb().to_ndarray()
                container.seek(0)
            except (StopIteration, AVError): # Changed: Used imported AVError
                logger.warning("Could not get reference frame for histogram matching. Histogram matching will be disabled.")
                self.config.APPLY_HISTOGRAM_MATCHING = False

        num_problematic_frames = 0 
        black_frame = np.zeros((self.config.IMG_H, self.config.IMG_W, 3), dtype=np.uint8) # Define black frame once

        try:
            for frame_idx, frame_av in enumerate(container.decode(video=0)):
                if total_frames_to_process != float('inf') and frame_idx >= total_frames_to_process:
                    logger.debug(f"Max frames limit ({total_frames_to_process}) reached. Stopping video processing.") 
                    break 

                current_frame_is_problematic = False
                processed_lip_frame = black_frame.copy() # Initialize with a black frame, will be overwritten if successful

                try:
                    image_rgb = frame_av.to_rgb().to_ndarray()
                    original_frame_height, original_frame_width, _ = image_rgb.shape

                    if self.config.SAVE_DEBUG_FRAMES:
                        self._debug_frame_processing(image_rgb, frame_idx, 'original')
                    
                    results = self.mp_face_mesh.process(image_rgb) 
                    
                    raw_lip_bbox: Optional[np.ndarray] = None 
                    mp_face_landmarks = None 
                    
                    if results.multi_face_landmarks:
                        mp_face_landmarks = results.multi_face_landmarks[0]
                        landmarks = mp_face_landmarks.landmark

                        lip_x_coords = []
                        lip_y_coords = []
                        for idx in LIPS_MESH_LANDMARKS_INDICES:
                            if idx < len(landmarks): 
                                lip_x_coords.append(landmarks[idx].x * original_frame_width)
                                lip_y_coords.append(landmarks[idx].y * original_frame_height)

                        if lip_x_coords and lip_y_coords:
                            min_y_tight = landmarks[NOSE_BOTTOM_LANDMARK_INDEX].y * original_frame_height
                            max_y_tight = landmarks[CHIN_BOTTOM_LANDMARK_INDEX].y * original_frame_height
                            min_x_tight = np.min(lip_x_coords)
                            max_x_tight = np.max(lip_x_coords)

                            # Calculate the centroid of the tight lip region
                            lip_centroid_x = (min_x_tight + max_x_tight) / 2
                            lip_centroid_y = (min_y_tight + max_y_tight) / 2

                            # Calculate desired bounding box dimensions based on proportional margins and fixed padding
                            initial_tight_width = max_x_tight - min_x_tight
                            initial_tight_height = max_y_tight - min_y_tight

                            # Determine the target size of the bounding box including margins and padding
                            target_bbox_width = initial_tight_width * (1 + 2 * self.config.LIP_PROPORTIONAL_MARGIN_X) + \
                                                self.config.LIP_PADDING_LEFT_PX + self.config.LIP_PADDING_RIGHT_PX
                            target_bbox_height = initial_tight_height * (1 + 2 * self.config.LIP_PROPORTIONAL_MARGIN_Y) + \
                                                 self.config.LIP_PADDING_TOP_PX + self.config.LIP_PADDING_BOTTOM_PX

                            # Adjust target_bbox_width/height to maintain the target aspect ratio (IMG_W / IMG_H)
                            # This ensures the cropped region has the correct aspect ratio *before* resizing to IMG_W x IMG_H
                            target_aspect_ratio = self.config.IMG_W / self.config.IMG_H

                            current_bbox_aspect_ratio = target_bbox_width / target_bbox_height

                            if current_bbox_aspect_ratio > target_aspect_ratio:
                                # Bounding box is wider than target aspect ratio, increase height
                                target_bbox_height = target_bbox_width / target_aspect_ratio
                            else:
                                # Bounding box is taller or equal, increase width
                                target_bbox_width = target_bbox_height * target_aspect_ratio

                            # Calculate proposed bounding box coordinates centered around the lip centroid
                            x1_proposed = lip_centroid_x - target_bbox_width / 2
                            y1_proposed = lip_centroid_y - target_bbox_height / 2
                            x2_proposed = lip_centroid_x + target_bbox_width / 2
                            y2_proposed = lip_centroid_y + target_bbox_height / 2

                            # Clamp coordinates to frame boundaries and adjust to maintain size if possible
                            x1_final = int(x1_proposed)
                            y1_final = int(y1_proposed)
                            x2_final = int(x2_proposed)
                            y2_final = int(y2_proposed)

                            # Shift box if it goes out of bounds
                            if x1_final < 0:
                                x2_final += abs(x1_final)
                                x1_final = 0
                            if y1_final < 0:
                                y2_final += abs(y1_final)
                                y1_final = 0
                            if x2_final > original_frame_width:
                                x1_final -= (x2_final - original_frame_width)
                                x2_final = original_frame_width
                            if y2_final > original_frame_height:
                                y1_final -= (y2_final - original_frame_height)
                                y2_final = original_frame_height

                            # Final clamping (important after shifts to ensure values are within limits)
                            x1_final = max(0, min(original_frame_width, x1_final))
                            y1_final = max(0, min(original_frame_height, y1_final))
                            x2_final = max(0, min(original_frame_width, x2_final))
                            y2_final = max(0, min(original_frame_height, y2_final))

                            # Ensure the final box has positive dimensions
                            if (x2_final - x1_final) > 0 and (y2_final - y1_final) > 0:
                                raw_lip_bbox = np.array([x1_final, y1_final, x2_final, y2_final], dtype=np.int32)
                            else:
                                logger.warning(f"Frame {frame_idx}: Calculated final bounding box has zero or negative dimensions after centering/adjustment. Marking as problematic.") 
                                current_frame_is_problematic = True
                        else:
                            logger.warning(f"Frame {frame_idx}: No lip coordinates found. Marking as problematic.") 
                            current_frame_is_problematic = True
                    else:
                        logger.warning(f"Frame {frame_idx}: No face detected. Marking as problematic.") 
                        current_frame_is_problematic = True

                    # --- Apply temporal smoothing using EMA if enabled ---
                    smoothed_lip_bbox_np = None
                    if self.config.APPLY_EMA_SMOOTHING:
                        smoothed_lip_bbox_np = self._apply_ema_smoothing(raw_lip_bbox)
                    else:
                        smoothed_lip_bbox_np = raw_lip_bbox # Use raw if EMA is off

                    # Save debug frames if enabled
                    if self.config.SAVE_DEBUG_FRAMES:
                        self._debug_frame_processing(image_rgb, frame_idx, 'landmarks', raw_lip_bbox.tolist() if raw_lip_bbox is not None else None, mp_face_landmarks)
                        if self.config.APPLY_EMA_SMOOTHING:
                            self._debug_frame_processing(image_rgb, frame_idx, 'smoothed_bbox', smoothed_lip_bbox_np.tolist() if smoothed_lip_bbox_np is not None else None, mp_face_landmarks)

                    # Crop and resize the frame using the smoothed bounding box
                    if not current_frame_is_problematic and smoothed_lip_bbox_np is not None and \
                       (smoothed_lip_bbox_np[2] > smoothed_lip_bbox_np[0]) and \
                       (smoothed_lip_bbox_np[3] > smoothed_lip_bbox_np[1]):
                        
                        x1_smoothed, y1_smoothed, x2_smoothed, y2_smoothed = smoothed_lip_bbox_np.tolist()
                        
                        # Ensure coordinates are within original frame bounds before cropping
                        x1_smoothed = max(0, min(original_frame_width, x1_smoothed))
                        y1_smoothed = max(0, min(original_frame_height, y1_smoothed))
                        x2_smoothed = max(0, min(original_frame_width, x2_smoothed))
                        y2_smoothed = max(0, min(original_frame_height, y2_smoothed))

                        # Re-check dimensions after clamping
                        if (x2_smoothed - x1_smoothed) <= 0 or (y2_smoothed - y1_smoothed) <= 0:
                            logger.warning(f"Frame {frame_idx}: Smoothed bounding box became invalid after clamping. Marking as problematic.")
                            current_frame_is_problematic = True
                        else:
                            lip_cropped_frame = image_rgb[y1_smoothed:y2_smoothed, x1_smoothed:x2_smoothed]
                            
                            current_crop_width = lip_cropped_frame.shape[1]
                            current_crop_height = lip_cropped_frame.shape[0]

                            if current_crop_width > self.config.IMG_W or current_crop_height > self.config.IMG_H:
                                interpolation_method = cv2.INTER_AREA
                            else:
                                interpolation_method = cv2.INTER_LANCZOS4 
                            
                            final_resized_lip = cv2.resize(lip_cropped_frame, (self.config.IMG_W, self.config.IMG_H), interpolation=interpolation_method)
                            
                            processed_lip_frame = final_resized_lip.copy()

                            if self.config.APPLY_HISTOGRAM_MATCHING and ref_frame is not None:
                                processed_lip_frame = _histogram_matching(processed_lip_frame, ref_frame)
                            
                                    
                            if self.config.INCLUDE_LANDMARKS_ON_FINAL_OUTPUT and mp_face_landmarks and smoothed_lip_bbox_np is not None:
                                x_offset_for_mapping = smoothed_lip_bbox_np[0] 
                                y_offset_for_mapping = smoothed_lip_bbox_np[1]
                                
                                width_cropped_for_mapping = smoothed_lip_bbox_np[2] - smoothed_lip_bbox_np[0]
                                height_cropped_for_mapping = smoothed_lip_bbox_np[3] - smoothed_lip_bbox_np[1]

                                if width_cropped_for_mapping > 0 and height_cropped_for_mapping > 0:
                                    scale_x_to_output = self.config.IMG_W / width_cropped_for_mapping
                                    scale_y_to_output = self.config.IMG_H / height_cropped_for_mapping

                                    for lm_idx in LIPS_MESH_LANDMARKS_INDICES:
                                        if lm_idx < len(mp_face_landmarks.landmark):
                                            orig_x_px = mp_face_landmarks.landmark[lm_idx].x * original_frame_width
                                            orig_y_px = mp_face_landmarks.landmark[lm_idx].y * original_frame_height
                                            
                                            relative_x_px = orig_x_px - x_offset_for_mapping
                                            relative_y_px = orig_y_px - y_offset_for_mapping

                                            final_x_lm = int(relative_x_px * scale_x_to_output)
                                            final_y_lm = int(relative_y_px * scale_y_to_output)
                                            
                                            final_x_lm = max(0, min(self.config.IMG_W - 1, final_x_lm))
                                            final_y_lm = max(0, min(self.config.IMG_H - 1, final_y_lm))
                                            
                                            cv2.circle(processed_lip_frame, (final_x_lm, final_y_lm), 1, (0, 255, 0), -1) 
                                else:
                                    logger.warning(f"Frame {frame_idx}: Cropped dimensions for landmark mapping are invalid. Skipping landmark drawing.")
                            
                    else: # This block is for when current_frame_is_problematic is True or smoothed_lip_bbox_np is invalid.
                        logger.warning(f"Frame {frame_idx}: Problematic frame (face/lip detection failed or invalid bounding box). Appending black frame.")
                        current_frame_is_problematic = True # Ensure it's marked problematic

                except Exception as e:
                    logger.warning(f"Unexpected error processing frame {frame_idx} from '{current_video_path.name}': {e}. Appending black frame.") 
                    current_frame_is_problematic = True 
                    if self.config.APPLY_EMA_SMOOTHING:
                        self._apply_ema_smoothing(None) # Pass None to EMA to maintain continuity or drift

                if current_frame_is_problematic:
                    processed_frames_temp_list.append(black_frame.copy())
                    num_problematic_frames += 1 
                    if self.config.SAVE_DEBUG_FRAMES:
                        self._debug_frame_processing(black_frame, frame_idx, 'black_generated')
                else:
                    processed_frames_temp_list.append(processed_lip_frame)


        finally:
            container.close()
            # --- NEW: Cleanup temporary MP4 file if it was created ---
            if converted_temp_mp4_path and converted_temp_mp4_path.exists():
                try:
                    os.remove(str(converted_temp_mp4_path))
                    logger.info(f"Cleaned up temporary MP4 file: '{converted_temp_mp4_path.name}'.") 
                except Exception as e:
                    logger.warning(f"Could not remove temporary MP4 file '{converted_temp_mp4_path.name}': {e}") 

        if not processed_frames_temp_list:
            logger.warning(f"No frames could be processed from video '{current_video_path.name}'. Returning `None, None`.") 
            return None, None # Changed: return None, None

        final_processed_np_frames = np.array(processed_frames_temp_list, dtype=np.uint8)

        # Apply MAX_FRAMES limit if specified
        if self.config.MAX_FRAMES is not None:
            if final_processed_np_frames.shape[0] > self.config.MAX_FRAMES:
                # If we processed more frames than MAX_FRAMES, truncate
                final_processed_np_frames = final_processed_np_frames[:self.config.MAX_FRAMES]
                logger.info(f"Video truncated to {self.config.MAX_FRAMES} frames as per configuration.") 
            elif final_processed_np_frames.shape[0] < self.config.MAX_FRAMES:
                # If we processed fewer frames, pad with black frames
                padding_needed = self.config.MAX_FRAMES - final_processed_np_frames.shape[0]
                black_padding = np.zeros((padding_needed, self.config.IMG_H, self.config.IMG_W, 3), dtype=np.uint8)
                final_processed_np_frames = np.concatenate((final_processed_np_frames, black_padding), axis=0)
                num_problematic_frames += padding_needed # Account for padded black frames as problematic
                logger.info(f"Video padded with {padding_needed} black frames to reach {self.config.MAX_FRAMES} frames as per configuration.") 


        total_output_frames = final_processed_np_frames.shape[0]
        
        # Final check on problematic frames percentage
        if total_output_frames == 0 or (total_output_frames > 0 and (num_problematic_frames / total_output_frames) * 100 > self.config.MAX_PROBLEMATIC_FRAMES_PERCENTAGE): 
            percentage_problematic_frames = (num_problematic_frames / total_output_frames) * 100 if total_output_frames > 0 else 100
            logger.error(f"Clip '{original_video_path.name}' rejected: {percentage_problematic_frames:.2f}% problematic frames (exceeds {self.config.MAX_PROBLEMATIC_FRAMES_PERCENTAGE}% allowed). Returning None, None.") 
            return None, None # Changed: return None, None
        elif num_problematic_frames > 0:
            percentage_problematic_frames = (num_problematic_frames / total_output_frames) * 100
            logger.info(f"Clip '{original_video_path.name}': {percentage_problematic_frames:.2f}% problematic frames found. Clip retained.") 
        
        # Save to .npy file if a path is provided
        if output_npy_path:
            output_npy_path = Path(output_npy_path)
            output_npy_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(output_npy_path, final_processed_np_frames)
            logger.info(f"Extracted frames saved to '{output_npy_path}'.")

        # --- RTF Calculation ---
        if self.config.CALCULATE_RTF:
            end_time = time.time()
            processing_time = end_time - start_time
            if video_duration_seconds > 0:
                rtf = processing_time / video_duration_seconds
                logger.info(f"RTF Calculation: Video Duration: {video_duration_seconds:.2f}s, Processing Time: {processing_time:.2f}s, RTF: {rtf:.4f}")
            else:
                logger.warning("RTF Calculation: Could not determine video duration. RTF cannot be calculated.")
                rtf = None
        else:
            rtf = None    

        if self.config.PROFILE_CODE:
            profiler.disable()
            stats = pstats.Stats(profiler).sort_stats('cumulative')
            stats.dump_stats('lip_extraction.prof')
            logger.info("Profiling results saved to 'lip_extraction.prof'")

        return final_processed_np_frames, rtf # Changed: return both frames and rtf

    @staticmethod
    def extract_npy(npy_path: Union[str, Path]) -> Optional[np.ndarray]:
        """
        Loads a NumPy array from a .npy file.

        Args:
            npy_path (Union[str, Path]): Path to the .npy file.

        Returns:
            Optional[np.ndarray]: The loaded NumPy array, or `None` if the file is not found or an error occurs.
        """
        npy_path = Path(npy_path)
        if not npy_path.exists():
            logger.error(f"NPY file not found at '{npy_path}'.") 
            return None
        
        try:
            data = np.load(npy_path)
            logger.info(f"Successfully loaded NPY file from '{npy_path}'. Shape: {data.shape}") 
            return data
        except Exception as e:
            logger.error(f"Error loading NPY file '{npy_path}': {e}") 
            return None
