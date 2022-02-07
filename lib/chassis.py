from random import random, randint, choice
from math import log, sin, cos, radians, degrees, floor, ceil, pi as PI, sqrt
import pygame.gfxdraw as gfxdraw
from pygame.draw import polygon, aaline
from pygame import Surface, Color, Rect, Vector2, draw
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.utils import random_world_position, flipy, clamp
from lib.config import cfg
from lib.camera import Camera


class TriChassis(Poly):

    def __init__(self, body: Body, length: int, width: int):
        points = []
        points.append((int(length/2), 0))
        points.append((int(-length/2), int(width/2)))
        points.append((int(-length/2), int(-width/2)))
        super().__init__(body, points, None, 1)

    def draw(self, screen: Surface, relative_position: Vec2d):
        pos = relative_position
        verts = self.get_vertices()
        verts2 = []
        for v in verts:
            v2 = v.rotated(self.body.angle)
            verts2.append(pos+v2)

        gfxdraw.polygon(screen, verts2, Color('green'))


class QuadChassis(Poly):

    def __init__(self, body: Body, length: int, front: int, back: int):
        points = []
        points.append((int(length/2), int(-front/2)))
        points.append((int(length/2), int(front/2)))
        points.append((int(-length/2), int(back/2)))
        points.append((int(-length/2), int(-back/2)))
        super().__init__(body, points, None, 1)
        self.collision_type = 2

    def draw(self, screen: Surface, relative_position: Vec2d):
        pos = relative_position
        verts = self.get_vertices()
        verts2 = []
        for v in verts:
            v2 = v.rotated(self.body.angle)
            verts2.append(pos+v2)

        gfxdraw.polygon(screen, verts2, Color('green'))