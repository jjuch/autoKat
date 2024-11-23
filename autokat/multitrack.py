from __future__ import annotations
from dataclasses import dataclass
import dataclasses
import datetime
import json
import math
import os
import random
import sys
from typing import Any, NamedTuple
from typing_extensions import Self
import cv2
import numpy

from autokat.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from autokat.vec import Vec

class Calibration(NamedTuple):
    top_left: Vec
    top_right: Vec
    bottom_left: Vec
    bottom_right: Vec

    def transform(self, coords: Vec) -> Vec:
        tl, tr, bl, br = self
        y_offset_top = (tl.y + tr.y) / 2
        delta_y =  (bl.y + br.y) / 2 - y_offset_top
        y_scale = (SCREEN_HEIGHT - 1) / delta_y
        x, y = coords
        ty = (y - y_offset_top) * y_scale
        
        t = ty / (SCREEN_HEIGHT - 1)
        x_offset_left = tl[0] * (1 - t) + bl[0] * t
        x_offset_right = tr[0] * (1 - t) + br[0] * t
        x_width = x_offset_right - x_offset_left
        x_scale = x_width / (SCREEN_WIDTH - 1)
        tx = (x - x_offset_left) / x_scale
        return Vec(tx,ty)
    
    @classmethod
    def from_dict(cls, data: dict[str, list[float]]) -> Self:
        return cls(**{k: Vec(*v) for k, v in data.items()})

    def to_dict(self) -> dict[str, list[float, float]]:
        return {k: list(v) for k, v in self._asdict().items()}

class DummyTracker:
    position = (300, 300)
    calibration = Calibration(
        top_left=(0, 0),
        top_right=(SCREEN_WIDTH - 1, 0),
        bottom_left=(0, SCREEN_HEIGHT - 1),
        bottom_right=(SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1)
    )
    time_since_last_detection = datetime.timedelta(seconds=0.1)

    def run(self):
        pass

    def update_calibration(
        self,
        **kwargs: Vec,
    ) -> None:
        self.calibration = self.calibration._replace(**kwargs)


@dataclass
class LaserConfig:
    hue_min: int
    hue_max: int


@dataclass
class ProcessingConfig:
    val_min: int = 80
    val_max: int = 255
    laser_configs: dict[str, LaserConfig] = dataclasses.field(default_factory=lambda: {
        "red": LaserConfig(137, 217),
        "green": LaserConfig(60, 124),
    })

    @classmethod
    def load_from_file(cls, file_path: str) -> Self:
        try:
            with open(file_path) as f:
                raw_json = json.load(f)
        except IOError:
            print(f"Couldn't open file {file_path}")
            return cls()
        return cls(**{**raw_json, "laser_configs": {k: LaserConfig(**v) for k, v in raw_json["laser_configs"].items()}})

    def save_to_file(self, file_path: str) -> None:
        with open(file_path, 'w') as f:
            json.dump({**dataclasses.asdict(self), "laser_configs": {name: dataclasses.asdict(lc) for name, lc in self.laser_configs.items()}}, f)


class ProcessingConfigEditor:

    def __init__(self, processing_config: ProcessingConfig):
        self._processing_config = processing_config

    def run(self):
        import tkinter as tk
        from tkinter import ttk

        # root window
        root = tk.Tk()
        root.tk.call('tk', 'scaling', 2.0)
        root.geometry('800x400')
        root.resizable(False, False)
        root.title('Processing config')

        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=3)

        fields = ['val_min', 'val_max']
        for name, laser_config in self._processing_config.laser_configs.items():
            fields.extend([
                (name, 'hue_min'),
                (name, 'hue_max'),
            ])
        
        def _get_field_value(field):
            match field:
                case [laser_name, field_name]:
                    return getattr(self._processing_config.laser_configs[laser_name], field_name)
                case field_name:
                    return getattr(self._processing_config, field_name)

        def _set_field_value(field, value):
            match field:
                case [laser_name, field_name]:
                    setattr(self._processing_config.laser_configs[laser_name], field_name, value)
                case field_name:
                    setattr(self._processing_config, field_name, value)
            self._processing_config.save_to_file('processing_config.json')

        def slider_changed(field, current_value):
            def _(value):
                _set_field_value(field, int(float(value)))
                current_value.set(int(float(value)))
            return _
    
        for i, field in enumerate(fields):
            label = ttk.Label(
                root,
                text=f'{field}:'
            )
            label.grid(
                column=0,
                row=i,
                sticky='w'
            )
            # slider current value
            current_value = tk.IntVar(value=_get_field_value(field))
            current_int_value = tk.IntVar(value=current_value.get())
            slider = ttk.Scale(
                root,
                from_=0,
                to=255,
                orient='horizontal',
                command=slider_changed(field, current_int_value),
                variable=current_value
            )
            slider.grid(
                column=1,
                row=i,
                sticky='we'
            )
            value_label = ttk.Label(
                root,
                textvariable=current_int_value
            )
            value_label.grid(
                column=2,
                row=i,
                sticky='w'
            )

        root.mainloop()

    def run_thread(self):
        import threading
        threading.Thread(target=self.run).start()


class Detection(NamedTuple):
    camera_position: Vec
    screen_position: Vec
    time: datetime.datetime

class MultiLaserTracker:
    def __init__(
        self,
        cam_width=800,
        cam_height=600,
        processing_config: ProcessingConfig|None = None,
        calibration_file_path: str = 'calibration.json',
    ):
        self.cam_width = cam_width
        self.cam_height = cam_height
        self.processing_config = processing_config
        if self.processing_config is None:
            # self._processing_config = GuiProcessingConfig()
            self.processing_config = ProcessingConfig.load_from_file('processing_config.json')

        self.capture = None  # camera capture device

        self.calibration_file_path = calibration_file_path
        self.calibration = Calibration(
            top_left=Vec(0, 0),
            top_right=Vec(SCREEN_WIDTH - 1, 0),
            bottom_left=Vec(0, SCREEN_HEIGHT - 1),
            bottom_right=Vec(SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1)
        )
        try:
            with open(calibration_file_path) as f:
                self.calibration = Calibration.from_dict(json.load(f))
            print(f"Using calibration from file {calibration_file_path}: {self.calibration}")
        except IOError:
            print(f"Couldn't open calibration file, using default {self.calibration}")
        
        self.last_detections = {
            laser_name: Detection(
                camera_position=Vec(self.cam_width / 2, self.cam_height / 2),
                screen_position=Vec(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2),
                time=datetime.datetime.now(),
            )
            for laser_name in self.processing_config.laser_configs.keys()
        }

    def update_calibration(
        self,
        **kwargs: Vec,
    ) -> None:
        self.calibration = self.calibration._replace(**kwargs)
        with open(self.calibration_file_path, 'w') as f:
            json.dump(self.calibration.to_dict(), f)

    @property
    def time_since_last_detection(self) -> datetime.timedelta:
        return max(d.time for d in self.last_detections.values()) - datetime.datetime.now()

    def create_and_position_window(self, name, xpos, ypos):
        """Creates a named widow placing it on the screen at (xpos, ypos)."""
        # Create a window
        cv2.namedWindow(name)
        # Resize it to the size of the camera image
        cv2.resizeWindow(name, self.cam_width, self.cam_height)
        # Move to (xpos,ypos) on the screen
        cv2.moveWindow(name, xpos, ypos)

    def setup_camera_capture(self, device_num=os.environ.get('CAMERA') or 0):
        """Perform camera setup for the device number (default device = 0).
        Returns a reference to the camera Capture object.

        """
        try:
            device = int(device_num)
            sys.stdout.write("Using Camera Device: {0}\n".format(device))
        except (IndexError, ValueError):
            # assume we want the 1st device
            device = 0
            sys.stderr.write("Invalid Device. Using default device 0\n")

        # Try to start capturing frames
        self.capture = cv2.VideoCapture(device)
        if not self.capture.isOpened():
            sys.stderr.write("Failed to Open Capture device. Quitting.\n")
            sys.exit(1)

        # self.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3) # auto mode
        # self.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) # manual mode
        # self.capture.set(cv2.CAP_PROP_EXPOSURE, 12)
        # set the wanted image size from the camera
        self.capture.set(
            cv2.cv.CV_CAP_PROP_FRAME_WIDTH
            if cv2.__version__.startswith("2")
            else cv2.CAP_PROP_FRAME_WIDTH,
            self.cam_width,
        )
        self.capture.set(
            cv2.cv.CV_CAP_PROP_FRAME_HEIGHT
            if cv2.__version__.startswith("2")
            else cv2.CAP_PROP_FRAME_HEIGHT,
            self.cam_height,
        )
        return self.capture

    def handle_quit(self, delay=10):
        """Quit the program if the user presses "Esc" or "q"."""
        key = cv2.waitKey(delay)
        c = chr(key & 255)
        if c in ["c", "C"]:
            self.trail = numpy.zeros((self.cam_height, self.cam_width, 3), numpy.uint8)
        if c in ["q", "Q", chr(27)]:
            sys.exit(0)


    def threshold(self, img, min_val, max_val):
        """Threshold the image to only include values between min_val and max_val."""
        (t, tmp) = cv2.threshold(
            img,  # src
            max_val,  # threshold value
            0,  # we dont care because of the selected type
            cv2.THRESH_TOZERO_INV,  # t type
        )

        (t, img) = cv2.threshold(
            tmp,  # src
            min_val,  # threshold value
            255,  # maxvalue
            cv2.THRESH_BINARY,  # type
        )
        return img


    def run(self):
        # Set up window positions
        # self.setup_windows()
        # Set up the camera capture
        self.setup_camera_capture()

        while True:
            # 1. capture the current image
            success, frame = self.capture.read()
            if not success:  # no image captured... end the processing
                sys.stderr.write("Could not read camera frame. Quitting\n")
                sys.exit(1)

            hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hue, saturation, value = cv2.split(hsv_image)
            hue = cv2.medianBlur(hue, 3)
            value_t = self.threshold(value, self.processing_config.val_min, self.processing_config.val_max)

            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(value_t, 4, cv2.CV_32S)

            # loop over all detected blobs
            # the first blob is the background, so we skip it
            candidates: dict[str, list[tuple[Vec, float, float, Any]]] = {}
            unknowns: list[tuple[Vec, float, float, Any]] = []
            for i in range(1, num_labels):
                x, y = centroids[i]
                # get the average hue value of the blob
                mean_mask = (labels == i).astype(numpy.uint8)
                mean_hue = cv2.mean(hue, mask=mean_mask)[0]
                area = stats[i, cv2.CC_STAT_AREA]

                # convert the mean hue value to BGR to color the circle around the detected blob
                hsv_pixel = numpy.array([[[int(mean_hue), 255, 128]]], numpy.uint8)
                bgr_pixel = cv2.cvtColor(hsv_pixel, cv2.COLOR_HSV2BGR)

                debug_color = bgr_pixel[0][0].tolist()

                for laser_name, laser_config in self.processing_config.laser_configs.items():
                    if laser_config.hue_min <= mean_hue <= laser_config.hue_max:
                        candidates.setdefault(laser_name, []).append((Vec(x, y), area, mean_hue, debug_color))
                    else:
                        unknowns.append((Vec(x, y), area, mean_hue, debug_color))
                        # self.last_detections[laser_name] = Detection(
                        #     camera_position=Vec(x, y),
                        #     screen_position=self.calibration.transform(Vec(x, y)),
                        #     time=datetime.datetime.now(),
                        # )
                        # cv2.putText(frame, f"{laser_name} {mean_hue}", (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, debug_color, 2)
                        # break
                # else:
                #     cv2.putText(frame, f"??? {mean_hue}", (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, debug_color, 2)

            for laser_name, laser_candidates in candidates.items():
                camera_position, area, mean_hue, debug_color = max(laser_candidates, key=lambda x: x[1])
                self.last_detections[laser_name] = Detection(
                    camera_position=camera_position,
                    screen_position=self.calibration.transform(camera_position),
                    time=datetime.datetime.now(),
                )
                cv2.putText(frame, f"{laser_name} {int(mean_hue)}", (int(camera_position.x), int(camera_position.y)), cv2.FONT_HERSHEY_SIMPLEX, 1, debug_color, 2)

            for camera_position, area, mean_hue, debug_color in unknowns:
                cv2.putText(frame, f"??? {int(mean_hue)}", (int(camera_position.x), int(camera_position.y)), cv2.FONT_HERSHEY_SIMPLEX, 1, debug_color, 2)
                # cv2.circle(frame, (int(x), int(y)), 10, debug_color, 2)
                
            
            # cv2.imshow("Hue", hue)
            # cv2.imshow("Saturation", saturation)
            # cv2.imshow("Value", value)
            # cv2.imshow("Value Thresholded", value_t)
            cv2.imshow("RGB", frame)
            self.handle_quit()


@dataclass
class DummyMultiLaserTracker:
    last_detections: dict[str, Detection] = dataclasses.field(default_factory=lambda: {
        "red": Detection(
            camera_position=Vec(300, 300),
            screen_position=Vec(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2),
            time=datetime.datetime.now(),
        ),
        "green": Detection(
            camera_position=Vec(500, 500),
            screen_position=Vec(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2),
            time=datetime.datetime.now(),
        ),
    })
    calibration: Calibration = Calibration(
        top_left=Vec(0, 0),
        top_right=Vec(SCREEN_WIDTH - 1, 0),
        bottom_left=Vec(0, SCREEN_HEIGHT - 1),
        bottom_right=Vec(SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1)
    )

    @property
    def time_since_last_detection(self) -> datetime.timedelta:
        return max(d.time for d in self.last_detections.values()) - datetime.datetime.now()
    
    def detect(self, color: str, coords: Vec):
        self.last_detections[color] = Detection(
            camera_position=coords,
            screen_position=coords,
            time=datetime.datetime.now(),
        )
    
    def update_calibration(
        self,
        **kwargs: Vec,
    ) -> None:
        pass

    def run(self):
        pass

if __name__ == "__main__":

    tracker = MultiLaserTracker()
    editor = ProcessingConfigEditor(tracker.processing_config)
    editor.run_thread()
    tracker.run()
