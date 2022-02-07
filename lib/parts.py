from random import random, randint, choice
from math import log, sin, cos, radians, degrees, floor, ceil, pi as PI, sqrt
import pygame.gfxdraw as gfxdraw
from pygame.draw import polygon, aaline
from pygame import Surface, Color, Rect, Vector2, draw
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.utils import random_world_position, flipy, clamp
from lib.config import cfg
from lib.camera import Camera


class Corpus(Circle):

    def __init__(self, body: Body, radius: int):
        super().__init__(body, radius)

    def draw(self, screen: Surface, rel_position: Vector2):
        x0 = int(rel_position.x); y0 = int(rel_position.y)
        r = int(self.radius)
        t = int((abs(sin(self.body.time%(2*PI))))*r/4)+1
        v = self.body.rotation_vector * r
        x1 = int(x0 + v.x); y1 = int(y0 + v.y)
        gfxdraw.aacircle(screen, x0, y0, r+1, Color(0, 150, 0))
        gfxdraw.aacircle(screen, x0, y0, r-int(r/6+1), Color(0, 150, 0))
        #gfxdraw.aacircle(screen, x0, y0, r, Color('yellowgreen'))
        gfxdraw.filled_circle(screen, x0, y0, r, Color('yellow'))
        draw.circle(screen, Color(0, 150, 0), (x0, y0), r+1, int(r/6+1))
        gfxdraw.aacircle(screen, x0, y0, t, Color('red'))
        gfxdraw.filled_circle(screen, x0, y0, t, Color('red'))
        #gfxdraw.filled_circle(screen, x1, y1, ceil(r/5), Color(0, 0, 0))
        aaline(screen, Color('blue'), (x0, y0), (x1, y1), blend=1)


class Vision(Circle):

    def __init__(self, body: Body, radius: int, wide: float, offset: float):
        super().__init__(body, radius)
        self.offset2 = offset
        self.wide = wide
        self.collision_type = 5
        self.sensor = True
        self.base_color = Color(255, 255, 255, 30)
        self.seeing_color = Color(255, 0, 0, 100)
        self.active_color = self.base_color
        self.reset_detection()

    def reset_detection(self):
        self.detection = {
            'ang': 0,
            'dist': 500,
            'target': None
        }

    def add_detection(self, angle: float, dist: float, target: Body):
        if self.detection['dist'] > dist and self.wide/2 >= abs(angle):
            self.detection = {
                'ang': angle,
                'dist': dist,
                'target': target
            }

    def set_detection_color(self, detection: bool):
        if detection:
            self.active_color = self.seeing_color
        else:
            self.active_color = self.base_color

    def draw(self, screen: Surface, camera: Camera, rel_position: Vector2):
        if self.detection['target'] != None:
            self.set_detection_color(detection=True)
        r = int(self.radius)
        w1 = (int(cos(self.body.angle-self.wide/2)*(r+r*self.offset2[0])), int(sin(self.body.angle-self.wide/2)*(r+r*self.offset2[1])))
        w2 = (int(cos(self.body.angle+self.wide/2)*(r+r*self.offset2[0])), int(sin(self.body.angle+self.wide/2)*(r+r*self.offset2[1])))
        x0 = int(rel_position.x); y0 = int(rel_position.y)
        v = self.body.rotation_vector * r
        x = x0 + v.x; y = y0 + v.y
        s = self.body.size
        v2 = (cos(self.body.angle+1)*s, sin(self.body.angle+1)*s)
        v3 = (cos(self.body.angle-1)*s, sin(self.body.angle-1)*s)
        #gfxdraw.aacircle(screen, int(x0), int(y0), r, self.active_color)
        #gfxdraw.circle(screen, int(x0), int(y0), r, self.active_color)
        #arc_rect = Rect(x0-r, y0-r, 2*r, 2*r)
        #draw.arc(screen, self.active_color, arc_rect, (self.body.angle+self.wide/2), (self.body.angle-self.wide/2), 5)
        gfxdraw.arc(screen, x0, y0, r, int(degrees(self.body.angle-self.wide/2)), int(degrees(self.body.angle+self.wide/2)), self.active_color)
        gfxdraw.line(screen, x0, y0, x0+w1[0], y0+w1[1], self.active_color)
        gfxdraw.line(screen, x0, y0, x0+w2[0], y0+w2[1], self.active_color)
        gfxdraw.aacircle(screen, x0+int(v2[0]), y0+int(v2[1]), int(s/7+1), Color('blue'))
        gfxdraw.filled_circle(screen, x0+int(v2[0]), y0+int(v2[1]), int(s/7+1), Color('blue'))
        gfxdraw.aacircle(screen, x0+int(v3[0]), y0+int(v3[1]), int(s/7+1), Color('blue'))
        gfxdraw.filled_circle(screen, x0+int(v3[0]), y0+int(v3[1]), int(s/7+1), Color('blue'))
        if self.detection['target'] != None:
            target = self.detection['target']
            rel_target_pos = camera.rel_pos(target.position)
            xt = int(rel_target_pos.x); yt = int(rel_target_pos.y)
            gfxdraw.line(screen, x0+int(v2[0]), y0+int(v2[1]), xt, yt, Color(56, 255, 245, 75))
            gfxdraw.line(screen, x0+int(v3[0]), y0+int(v3[1]), xt, yt, Color(56, 255, 245, 75))
        self.set_detection_color(detection=False)
        self.reset_detection()


class Limb(Segment):

    def __init__(self, body: Body, angle: float, radius: int, length: int, speed: float, deviation: int):
        r = body.size
        f = Vec2d(1, 0)
        v = f.rotated_degrees(angle)
        self.length = length
        self.speed = speed
        self.deviation = deviation
        v0 = v * r
        v1 = v * length * r
        self.angle = angle
        self.angle2 = self.angle
        self.side = angle/abs(angle) 
        super().__init__(body, (v0.x, v0.y), (v1.x, v1.y), radius)
        self.cycle = 0.0

    def draw(self, screen: Surface, rel_position: Vector2):
        v0 = rel_position
        f = self.body.rotation_vector.rotated_degrees(self.angle+self.side*(self.deviation*sin(self.cycle)))
        #f1 = self.body.rotation_vector.rotated_degrees(self.angle+5*self.side)
        #f2 = self.body.rotation_vector.rotated_degrees(self.angle-5*self.side)
        #f3 = self.body.rotation_vector.rotated_degrees(self.angle+5*self.side)
        #f4 = self.body.rotation_vector.rotated_degrees(self.angle-2*self.side)
        #curve = []
        #curve.append(v0 + f*self.body.size)
        #curve.append(v0 + f1*self.body.size*1.5)
        #curve.append(v0 + f2*self.body.size*2)
        #curve.append(v0 + f3*self.body.size*2.4)
        #curve.append(v0 + f4*self.body.size*2.8)
        #a = v0 + f*self.body.size
        #b = v0 + f*self.body.size*1.5
        #v1 = a
        #v2 = b
        p1 = v0 + f*self.body.size
        p2 = v0 + f*self.body.size*self.length
        r = self.radius
        #gfxdraw.bezier(screen, curve, 5, Color('skyblue'))
        draw.line(screen, Color(100, 100, 150), (int(p1.x), int(p1.y)), (int(p2.x), int(p2.y)), int(r))

    def update(self, dT: float):
        self.cycle += dT/200*self.speed
        self.cycle = (self.cycle)%(2*PI)


class Yaw(Circle):

    def __init__(self, body: Body, radius: int, offset: tuple=(0, 0)):
        super().__init__(body, radius, offset)
        self.b_color = Color(150, 150, 150, 255)
        self.collision_type = 7
        self.open = 0.0
        self.bite = False
        self.bite_time = 0.0

    def draw(self, screen:Surface, rel_position: Vector2, size: int, bite: bool):
        x0 = rel_position.x; y0 = rel_position.y
        a = self.body.angle
        r = int(self.radius/2)
        s = size
        f = self.body.rotation_vector
        vc = f*s + f*r*0.4
        vf = f*s + f*r
        xc = x0 + vc.x; yc = y0 + vc.y;
        xf = x0 + vf.x; yf = y0 + vf.y;
        o = cos(self.open)
        draw.circle(screen, self.b_color, (xc, yc), r, int(r/2+1))
        if o == 1.0:
            draw.circle(screen, Color(0, 0, 0), (xf, yf), int(r*0.7), r)
        else:
            draw.circle(screen, self.b_color, (xc, yc), int(r*0.7), r)
        #gfxdraw.filled_circle(screen, int(xc), int(yc), r, self.b_color)
        #gfxdraw.filled_circle(screen, int(xf), int(yf), int(r*0.7), Color(0, 0, 0))
        #rect = Rect(x0+v.x-r*f.x, y0+v.y-r*f.y, 2*r*f.x, 2*r*f.y)
        #v1 = f.rotated_degrees(-20*o)*s; v2 = f.rotated_degrees(20*o)*s;
        #xl = int(x0+v1.x); yl = int(y0+v1.y);
        #xr = int(x0+v2.x); yr = int(y0+v2.y);
        #xl2 = int(x0+v1.x*1.4); yl2 = int(y0+v1.y*1.4);
        #xr2 = int(x0+v2.x*1.4); yr2 = int(y0+v2.y*1.4);
        #xl3 = int(x0+v1.x*1); yl3 = int(y0+v1.y*1);
        #xr3 = int(x0+v2.x*1); yr3 = int(y0+v2.y*1);
        #gfxdraw.filled_circle(screen, xl, yl, r, self.b_color)
        #gfxdraw.filled_circle(screen, xr, yr, r, self.b_color)
        #draw.line(screen, self.b_color, (xl, yl), (xl2, yl2), int(s/4+1))
        #draw.line(screen, self.b_color, (xr, yr), (xr2, yr2), int(s/4+1))
        #draw.arc(screen, self.b_color, rect, a+radians(30), a-radians(30), 3)

    def go_bite(self):
        if not self.bite:
            self.bite = True

    def update(self, dT: float):
        dT = dT/1000
        if self.bite:
            self.open = (self.open + dT)%PI
            self.bite_time += dT
            if self.bite_time > 2.0:
                self.bite = False
                self.open = 0.0
                self.bite_time = 0.0