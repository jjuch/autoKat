from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Ellipse
from shapely import LineString, LinearRing, MultiLineString, Point, Polygon, line_merge
from shapely.affinity import rotate
from kivy.metrics import dp

class PongPaddle(Widget):
    score = NumericProperty(0)
    can_bounce = BooleanProperty(True)

    def bounce_ball(self, ball):
        if self.collide_widget(ball) and self.can_bounce:
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset
            self.can_bounce = False
        elif not self.collide_widget(ball) and not self.can_bounce:
            self.can_bounce = True


class PongPillar(Widget):
    pass

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

def segments(curve):
    return list(map(LineString, zip(curve.coords[:-1], curve.coords[1:])))

class PongGame(Widget):
    ball = ObjectProperty(None)
    pillar = ObjectProperty(None)
    light_red = ObjectProperty(None)
    light_green = ObjectProperty(None)
    cone_red = ObjectProperty([0,0,0,0,0,0])
    cone_green = ObjectProperty([0,0,0,0,0,0])
    # red_shadow: 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._boundary_shape = LinearRing([
            (0, 0),
            (0, self.height),
            (self.width, self.height),
            (self.width, 0),
            # (0, 0)
        ])
        self.shapely_red_intersection = None
        self.shapely_green_intersection = None

    def serve_ball(self, vel=(dp(4), 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):
        self.ball.move()
        ball_size = self.ball.size[0]
        ball_point = Point(self.ball.center)
        ball_circle = ball_point.buffer(ball_size / 2)

        bounced = False
        for intersection in self.shapely_red_intersection, self.shapely_green_intersection:
            if not intersection:
                continue
            for paddle_segment in segments(intersection):
                if ball_circle.intersects(paddle_segment):
                    print("paddle", paddle_segment)
                    print("ball", ball_point)
                    rotation_ratio = paddle_segment.line_locate_point(ball_point, normalized=True) - .5
                    norm = rotate(paddle_segment, -90)
                    norm_vec = Vector(norm.coords[1][0] - norm.coords[0][0], norm.coords[1][1] - norm.coords[0][1]).normalize()
                    print("norm vec", norm_vec)
                    print("original velocity", self.ball.velocity)
                    self.ball.velocity = Vector(self.ball.velocity) - 2 * norm_vec.dot(self.ball.velocity) * norm_vec
                    print("rotation ratio   ", rotation_ratio)
                    self.ball.velocity = Vector(self.ball.velocity).rotate(rotation_ratio * 45) * 1.1
                    print("new velocity     ", self.ball.velocity)
                    bounced = True
        if bounced:
            return
        
        if not ball_circle.within(self._boundary_shape.convex_hull):
            print("AAAA")
            self.serve_ball()

        # if ball_circle.intersects(self._boundary_shape):
        #     self.serve_ball()

    def on_touch_move(self, touch):
        light_vector = Vector(touch.x, touch.y)
        if cone_and_intersection := self._calculate_cone_and_intersection(light_vector):
            shapely_cone, shapely_intersection = cone_and_intersection
            if touch.button == 'left':
                self.shapely_red_intersection = shapely_intersection
                self.light_red.center = light_vector
                self.cone_red = [c for cs in shapely_cone.exterior.coords for c in cs]
            elif touch.button == 'right':
                self.shapely_green_intersection = shapely_intersection
                self.light_green.center = light_vector
                self.cone_green = [c for cs in shapely_cone.exterior.coords for c in cs]

    def _calculate_cone_and_intersection(self, light_vector):
        if not (1 < light_vector.x <= self.width - 2):
            return None
        if not (1 < light_vector.y <= self.height - 2):
            return None
        pillar_vector = Vector(self.pillar.center_x, self.pillar.center_y)
        diff_vector = light_vector - pillar_vector
        perp_left = Vector(diff_vector.y, -diff_vector.x).normalize() * self.pillar.size / 2
        perp_right = Vector(-diff_vector.y, diff_vector.x).normalize() * self.pillar.size / 2
        tangent_left = light_vector + (diff_vector + perp_left) * -1000
        tangent_right = light_vector + (diff_vector + perp_right) * -1000
        shapely_cone = Polygon([light_vector, tangent_left, tangent_right, light_vector])
        shapely_intersection = shapely_cone.intersection(self._boundary_shape)
        if isinstance(shapely_intersection, MultiLineString):
            shapely_intersection = line_merge(shapely_intersection)
        return shapely_cone, shapely_intersection
        


class PongLight(Widget):
    pass


class PongDebugOverlay(Widget):
    pass


class PongApp(App):
    def build(self):
        game = PongGame()
        # Window.bind(on_motion=game.on_motion)
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)

        return game


if __name__ == '__main__':
    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Window.size = dp(1024), dp(768)
    Window.borderless = True
    Window.resizable = False
    # Window.size = 1024, 768
    PongApp().run()