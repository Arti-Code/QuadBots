from random import random, randint, choice
from math import log, sin, cos, radians, degrees, floor, ceil, pi as PI, sqrt
from pygame.draw import polygon, aaline
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect, Vector2
from pymunk import Vec2d, Body, Circle, Segment, Space, Poly, Transform
from lib.utils import random_world_position, flipy, clamp
from lib.parts import Corpus, Vision, Yaw, Limb
from lib.config import cfg
from lib.camera import Camera
from lib.chassis import TriChassis, QuadChassis


class Bot(Body):

    def __init__(self, space: Space, collision_tag: int, position: tuple, genome: dict=None):
        super().__init__(body_type=Body.KINEMATIC)
        self.init_properties(position=position)
        self.chassis = QuadChassis(self, self.size, int(self.size/4), int(self.size/2))
        self.vision = Vision(self, self.vision_radius, PI*0.75, (0.0, 0.0))
        self.yaw = Yaw(self, int(self.size/2+1), (int(self.size/2), 0))
        space.add(self)
        space.add(self.chassis)
        space.add(self.vision)
        space.add(self.yaw)

    def init_properties(self, position: tuple=None):
        self.id = randint(1000, 9999)
        self.size = randint(15, 30)
        self.max_eng = pow(self.size, 2) * 100
        self.eng = self.max_eng
        self.health = 100
        self.angle = random()*2*PI
        self.speed = 0.05
        self.turn = 0.005
        self.acts = {
            'go'    : 0,
            'turn'  : 0,
            'bite'  : 0
        }
        self.time: float = 0.0
        if position is not None:
            self.position = Vec2d(position[0], position[1])
        else:
            x = random_world_position(5)
            y = random_world_position(5)
            self.position = Vec2d(x, y)
        self.rect: Rect=self.get_rect()
        self.vision_radius = 400

    def update(self, dT: float)->bool:
        if not self.update_params(dT):
            return False
        self.analize()
        self.yaw.update(dT)
        self.move(self.acts['go'], self.acts['turn'], dT)
        self.rect = self.get_rect()
        return True

    def get_rect(self) -> Rect:
        return Rect(int(self.position[0]-self.size), int(self.position[1]-self.size), 2*self.size, 2*self.size)

    def update_params(self, dT: float) -> bool:
        self.time += dT*0.002
        self.eng -= dT/5
        if self.eng < 0:
            self.eng = 0
        if self.eng < self.max_eng/4:
            self.health -= dT/500
        if self.health <= 0:
            return False
        if self.acts['bite'] > 0:
            self.acts['bite'] -= dT/3
        if self.acts['bite'] < 0:
            self.acts['bite'] ==0
        return True

    def move(self, ahead: int, turn: float, dT: float):
        if turn != 0:
            self.angle += (turn*dT)
            self.angle = self.angle%(2*PI)
        if ahead != 0:
            self.position += (ahead*dT)*self.rotation_vector
            x = clamp(self.position[0], 0, cfg.world[0])
            y = clamp(self.position[1], 0, cfg.world[1])
            self.position = Vec2d(x, y)

    def draw(self, screen: Surface, camera: Camera) -> tuple:
        rel_pos: Vector2=camera.rel_pos(position=self.position)
        bite = False
        if self.acts['bite'] > 0:
            bite = True
        self.yaw.draw(screen=screen, rel_position=rel_pos, size=self.size, bite=bite)
        self.vision.draw(screen=screen, camera=camera, rel_position=rel_pos)
        self.chassis.draw(screen, rel_pos)
        x0 = int(rel_pos.x - self.size); x1 = int(rel_pos.x + self.size)
        y = int(rel_pos.y + self.size*2)
        dx = x1 - x0
        eng = self.eng/self.max_eng
        x2 = floor(x0 + (dx*eng))
        x3 = floor(x0 + (self.health/100) * dx)
        gfxdraw.hline(screen, x0, x1, y+2, Color('red'))
        gfxdraw.hline(screen, x0, x2, y+2, Color('green'))
        gfxdraw.hline(screen, x0, x1, y-2, Color('yellow'))
        gfxdraw.hline(screen, x0, x3, y-2, Color('blue'))

    def analize(self):
        #self.acts = {
        #    'go'    : 0,
        #    'turn'  : 0,
        #    'bite'  : 0
        #}
        self.acts['go'] = 0
        self.acts['turn'] = 0
        rnd = randint(0, 9)
        if rnd == 0:
            self.acts['turn'] = choice([self.turn, -self.turn])
        else:
            self.acts['go'] = self.speed*random()
        rnd = randint(0, 100)
        if rnd == 0:
            self.yaw.go_bite()

    def kill(self, space: Space):
        space.remove(self.vision)
        space.remove(self.yaw)
        space.remove(self.chassis)
        space.remove(self)