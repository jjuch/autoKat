from collections.abc import Iterable
import dataclasses
import datetime
from functools import cached_property, lru_cache
import math
from typing import Literal, Protocol
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mppatch
import time

from shapely import LineString, LinearRing, Point, Polygon

from autokat.animals import Flock, Dog, Sheep
from autokat.multitrack import Detection, DummyMultiLaserTracker, MultiLaserTracker, Vec

@dataclasses.dataclass(kw_only=True)
class Pillar:
    position: Vec
    radius: float
    forbidden_radius: float

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "radius": self.radius,
            "forbidden_radius": self.forbidden_radius,
        }

@dataclasses.dataclass(kw_only=True)
class Ball:
    position: Vec
    velocity: Vec
    radius: float

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "velocity": self.velocity,
            "radius": self.radius,
        }
    
    def moved(self, dt: datetime.timedelta) -> 'Ball':
        return dataclasses.replace(
            self,
            position=self.position + self.velocity * dt.total_seconds()
        )
    
    def bounced(self, normal: Vec, distance_from_center: float) -> 'Ball':
        new_velocity = self.velocity.reflect(normal)
        added_angle = -math.pi / 4 * distance_from_center
        if new_velocity.rotate(added_angle).dot(normal) < 0:
            new_velocity = new_velocity.rotate(added_angle)
        return dataclasses.replace(
            self,
            velocity=new_velocity
        )

    @property
    def shape(self):
        return Point(self.position).buffer(self.radius)


DEFAULT_SIZE = Vec(1024, 768)

def segments(curve):
    return list(map(LineString, zip(curve.coords[:-1], curve.coords[1:])))


@dataclasses.dataclass
class Playing:
    size: Vec = DEFAULT_SIZE
    lives: int = 3
    score: int = 0
    red_light: Vec = Vec(size[0] / 2 - 200, size[1] / 2)
    green_light: Vec = Vec(size[0] / 2 + 200, size[1] / 2)
    light_speed: float = 800
    pillar: Pillar = dataclasses.field(
        default_factory=lambda: Pillar(
            position=Vec(DEFAULT_SIZE[0] / 2, DEFAULT_SIZE[1] / 2),
            radius=25,
            forbidden_radius=100,
        )
    )
    ball: Ball | None = dataclasses.field(
        default_factory=lambda: Ball(
            position=Vec(DEFAULT_SIZE[0] / 2, DEFAULT_SIZE[1] / 2),
            velocity=Vec.normalized_random() * 150,
            radius=10,
        )
    )
    red_cone: Polygon = dataclasses.field(init=False)
    green_cone: Polygon = dataclasses.field(init=False)

    def __post_init__(self):
        self.red_cone = self._cone(self.red_light)
        self.green_cone = self._cone(self.green_light)
   
    @cached_property
    def boundary_shape(self) -> LinearRing:
        w, h = self.size
        return LinearRing([(0, 0), (0, h), (w, h), (w, 0)])

    @cached_property
    def play_field_shape(self) -> Polygon:
        return self.boundary_shape.convex_hull

    def _cone(self, light_position: Vec) -> Polygon:
        diff_vector = light_position - self.pillar.position
        # print(diff_vector)
        perp_left = diff_vector.rotate(math.pi / 2).norm() * self.pillar.radius
        perp_right = diff_vector.rotate(-math.pi / 2).norm() * self.pillar.radius
        tangent_left = light_position + (diff_vector + perp_left) * -1000
        tangent_right = light_position + (diff_vector + perp_right) * -1000
        return Polygon([light_position, tangent_left, tangent_right, light_position])


    def _update_light(self, light_position: Vec, pointer_position: Vec, dt: datetime.timedelta) -> tuple[Vec, Polygon]:
        max_d = self.light_speed * dt.total_seconds()
        # print(max_d, self.light_speed)
        new_light_position =  light_position + (pointer_position - light_position).truncate(max_d)
        pillar_diff = new_light_position - self.pillar.position
        # prevent division by zero if the light is on the pillar somehow
        if pillar_diff.magnitude < 1:
            pillar_diff = Vec(1, 0)
        # push the light out of the forbidden area
        if pillar_diff.magnitude < self.pillar.forbidden_radius:
            new_light_position = self.pillar.position + pillar_diff.norm() * self.pillar.forbidden_radius
        return new_light_position, self._cone(new_light_position)

    def tick(
        self,
        pointer_detections: dict[str, Detection],
        total_dt: datetime.timedelta,
        dt: datetime.timedelta,
        time_since_last_detection: datetime.timedelta,
    ):
        self.red_light, self.red_cone = self._update_light(self.red_light, pointer_detections['red'].screen_position, dt)
        self.green_light, self.green_cone = self._update_light(self.green_light, pointer_detections['green'].screen_position, dt)
       
        if self.ball is None:
            return self

        moved_ball = self.ball.moved(dt)
        ball_trace_shape = LineString([self.ball.position, moved_ball.position]).buffer(self.ball.radius)

        for wall in segments(self.boundary_shape):
            wall_intersection = wall.intersection(ball_trace_shape)
            if not wall_intersection.is_empty:
                for cone in self.red_cone, self.green_cone:
                    if cone.contains(wall_intersection):
                        intersection_point = wall_intersection.centroid
                        cone_wall_intersection = wall.intersection(cone)
                        relative_intersection_location = cone_wall_intersection.line_locate_point(intersection_point, normalized=True)
                        normal = (Vec(*wall.coords[1]) - Vec(*wall.coords[0])).norm().rotate(math.pi / 2)
                        moved_ball = moved_ball.bounced(normal, distance_from_center=1 - 2 * relative_intersection_location)
                        if (x_overshoot := moved_ball.position.x + moved_ball.radius - self.size.x) > 0:
                            moved_ball.position = moved_ball.position - Vec(2 * x_overshoot, 0)
                        if (y_overshoot := moved_ball.position.y + moved_ball.radius - self.size.y) > 0:
                            moved_ball.position = moved_ball.position - Vec(0, 2 * y_overshoot)
                        if (x_undershoot := moved_ball.position.x - moved_ball.radius) < 0:
                            moved_ball.position = moved_ball.position - Vec(2 * x_undershoot, 0)
                        if (y_undershoot := moved_ball.position.y - moved_ball.radius) < 0:
                            moved_ball.position = moved_ball.position - Vec(0, 2 * y_undershoot)
                        self.score += 1
                        moved_ball.velocity = moved_ball.velocity + moved_ball.velocity.norm() * 50
                        break
                else:
                    self.ball = None
                    return Countdown(
                        start_at=total_dt + datetime.timedelta(seconds=5),
                        playing_state=self,
                    )
        self.ball = moved_ball
        return self

    
    def to_dict(self) -> dict:
        return {
            "name": "playing",
            "red_light": self.red_light,
            "green_light": self.green_light,
            "ball": self.ball,
            "red_cone": list(self.red_cone.boundary.coords),
            "green_cone": list(self.green_cone.boundary.coords),
            "pillar": self.pillar,
        }


@dataclasses.dataclass
class Countdown: 
    start_at: datetime.timedelta
    playing_state: Playing

    def tick(
        self,
        pointer_detections: dict[str, Detection],
        total_dt: datetime.timedelta,
        dt: datetime.timedelta,
        time_since_last_detection: datetime.timedelta,
    ):
        self.playing_state = self.playing_state.tick(
            pointer_detections=pointer_detections,
            total_dt=total_dt,
            dt=dt,
            time_since_last_detection=time_since_last_detection,
        )
        if total_dt > self.start_at:
            return Playing(
                size=self.playing_state.size,
                lives=self.playing_state.lives - 1,
                red_light=self.playing_state.red_light,
                green_light=self.playing_state.green_light,
            )
        return self
    
    def to_dict(self) -> dict:
        return {
            "name": "countdown",
            "start_at": self.start_at,
            "playing_state": self.playing_state
        }


DEFAULT_LIGHT_SPEED = 150


@dataclasses.dataclass
class Intro:
    playing_state: Playing = dataclasses.field(default_factory=lambda: Playing(size=DEFAULT_SIZE, light_speed=DEFAULT_LIGHT_SPEED))
    pointer_detections: dict[str, Detection] = dataclasses.field(default_factory=lambda: {
        "red": Detection(
            screen_position=Vec(1024 / 2 - 300, 768 / 2),
            camera_position=Vec(1024 / 2 - 300, 768 / 2),
            time=datetime.timedelta(0)
        ),
        "green": Detection(
            screen_position=Vec(1024 / 2 + 300, 768 / 2),
            camera_position=Vec(1024 / 2 + 300, 768 / 2),
            time=datetime.timedelta(0)
        ),
    })
    light_speed: float = DEFAULT_LIGHT_SPEED

    def tick(
        self,
        pointer_detections: dict[str, Detection],
        total_dt: datetime.timedelta,
        dt: datetime.timedelta,
        time_since_last_detection: datetime.timedelta,
    ):
        for wall in segments(self.playing_state.boundary_shape):
            velocity_line = LineString([self.playing_state.ball.position, self.playing_state.ball.position + self.playing_state.ball.velocity * 10_000])
            intersection = wall.intersection(velocity_line)
            if not intersection.is_empty:
                pillar_diff = Vec(intersection.x, intersection.y) - self.playing_state.pillar.position
                target_position = self.playing_state.pillar.position + pillar_diff.norm() * -1.5 * self.playing_state.pillar.forbidden_radius
                color, _ = min(
                    self.pointer_detections.items(),
                    key=lambda item: item[1].screen_position.distance_to(target_position)
                )
                self.pointer_detections[color] = Detection(screen_position=target_position, camera_position=target_position, time=total_dt)

        self.playing_state = self.playing_state.tick(
            pointer_detections=self.pointer_detections,
            total_dt=total_dt,
            dt=dt,
            time_since_last_detection=0,
        )
        if not isinstance(self.playing_state, Playing):
            self.playing_state = Playing(light_speed=self.light_speed)


        return self

    def to_dict(self) -> dict:
        return {
            "name": "intro",
            "playing_state": self.playing_state,
        }
class Game:
    state: Playing | Countdown | Intro
    victory_time: datetime.timedelta | None
    def __init__(self, *, laser_tracker: MultiLaserTracker | DummyMultiLaserTracker, size=Vec(1024, 768)):
        self.size = size
        self.laser_tracker = laser_tracker
        self.state = Playing(size=size)
        # self.state = Intro()

    def tick(self, total_dt: datetime.timedelta, dt: datetime.timedelta) -> Iterable[dict]:
        self.state = self.state.tick(
            pointer_detections=self.laser_tracker.last_detections,
            total_dt=total_dt,
            dt=dt,
            time_since_last_detection=self.laser_tracker.time_since_last_detection,
        )
        yield {
            "type": "state",
            "state": self.state,
            "calibration": self.laser_tracker.calibration,
            "debug": {
                "red_position": self.laser_tracker.last_detections["red"].screen_position,
                "green_position": self.laser_tracker.last_detections["green"].screen_position,
            },
            "time": total_dt,
        }



if __name__ == '__main__':
    game = Game()
    game.simulate()