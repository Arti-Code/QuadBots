import os
from statistics import mean
import sys
import math
import random
from time import time, monotonic
import pygame
from pygame import Surface, Rect, image, Color, Vector2
from pygame.time import Clock
from pygame.event import Event
from pygame.draw import line
import pymunk
from pymunk import Space, Vec2d
import pymunk.pygame_util
from lib.agent import Agent
from lib.utils import random_world_position
from lib.config import cfg
from lib.camera import Camera
from lib.bot import Bot


TITLE: str="EVOBOTS v0.0.5dev"
world: tuple=(2400, 1350)
run: bool=True
screen: Surface=None
dT: float=0.033
space: Space=None
clock: Clock=None
agents = []
bots = []
draw_debug: bool=False
options = None
physics_time: list=[]
draw_time: list=[]
draw_t: float=0.0
physics_t: float=0.0
camera: Camera=None


def set_win_pos(x: int = 20, y: int = 20):
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)

def set_icon(icon_name):
    icon = pygame.Surface((32, 32))
    icon.set_colorkey((0, 0, 0))
    rawicon: Surface = image.load(icon_name).convert()
    size: tuple=rawicon.get_size()
    sx: float = size[0]/32
    sy: float = size[1]/32
    for i in range(0, 32):
        for j in range(0, 32):
            icon.set_at((i, j), rawicon.get_at((int(i*sx), int(j*sy))))
    pygame.display.set_icon(icon)

def set_collisions_calls():
    agents_collisions = space.add_collision_handler(2, 2)
    agents_collisions.pre_solve = process_agents_collisions

    agent_visual_detection = space.add_collision_handler(5, 2)
    agent_visual_detection.pre_solve = process_agents_seeing

def process_agents_collisions(arbiter, space, data):
    agent1 = arbiter.shapes[0].body
    agent2 = arbiter.shapes[1].body
    agent1.position -= arbiter.normal*agent1.speed*20
    agent2.position += arbiter.normal*agent2.speed*20
    agent1.collision_normal = arbiter.normal
    agent1.normal_time = 5.0
    #print(f'COLLISION: [{agent1.id}] >>> [{agent2.id}]')
    return False

def process_agents_seeing(arbiter, space, data):
    agent1 = arbiter.shapes[0].body
    agent2 = arbiter.shapes[1].body
    #agent1.vision.set_detection_color(detection=True)
    v = agent2.position - agent1.position
    f = agent1.rotation_vector
    n = v.normalized()
    angle = f.get_angle_between(n)
    dist = agent2.position.get_distance(agent1.position)
    agent1.vision.add_detection(angle=angle, dist=int(dist), target=agent2)
    return False

def main():
    init_display()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
    init_spacetime()
    set_collisions_calls()
    create_enviroment(17)
    while run:
        events()
        update()
        draw()
        physics()
        calc_timings()
        ticking()

def init_display():
    global screen, camera, draw_debug, options, cfg
    set_win_pos(100, 50)
    cfg.set_world(world)
    cfg.set_window((1600, 900))
    flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    screen = pygame.display.set_mode(size=cfg.window, flags=flags, vsync=1)
    options = pymunk.pygame_util.DrawOptions(screen)
    screen.set_alpha(0)
    screen.set_colorkey(Color(0, 0, 0))
    options.shape_outline_color = (175, 0, 175, 50)
    options.collision_point_color = (255, 0, 0, 50)
    set_icon('asset/img/app32.png')
    pymunk.pygame_util.positive_y_is_up = False
    camera = Camera(center=Vector2(int(cfg.window[0]/2), int(cfg.window[1]/2)), size=Vector2(cfg.window))

def init_spacetime():
    global space, clock, draw_debug, options, cfg
    space = Space(threaded=True)
    space.threads = 2
    space.gravity = (0, 0)
    #space.debug_draw(options)
    clock = Clock()

def create_enviroment(agents_num: int):
    global agents, screen, space, bots
    for i in range(agents_num):
        #new_bot()
        new_agent()

def new_agent():
    global agents, screen, space
    pos = random_world_position(5)
    agent = Agent(space=space, collision_tag=2, position=pos)
    agents.append(agent)

def new_bot():
    global agents, screen, space, bots
    pos = random_world_position(5)
    bot = Bot(space=space, collision_tag=2, position=pos)
    bots.append(bot)

def update():
    to_kill = []
    for agent in agents:
        if not agent.update(dT):
            to_kill.append(agent)
    for agent in to_kill:
        agent.kill(space)
        agents.remove(agent)
    if len(agents) < 15:
        new_agent()

#def update():
#    to_kill = []
#    for bot in bots:
#        if not bot.update(dT):
#            to_kill.append(bot)
#    for bot in to_kill:
#        bot.kill(space)
#        bots.remove(bot)
#    if len(bots) < 15:
#        new_bot()

def events():
    global run
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            key_event(event)
        elif event.type == pygame.QUIT:
            run = False

def key_event(event: Event):
    global run
    if event.key == pygame.K_ESCAPE:
        run = False
    elif event.key == pygame.K_LEFT:
        camera.update(move=Vector2(-25, 0))
    elif event.key == pygame.K_RIGHT:
        camera.update(move=Vector2(25, 0))
    elif event.key == pygame.K_UP:
        camera.update(move=Vector2(0, -25))
    elif event.key == pygame.K_DOWN:
        camera.update(move=Vector2(0, 25))
    
def draw():
    time = monotonic()
    global screen, space, camera, draw_time
    screen.fill(Color('black'))
    draw_edges()
    draw_agents(screen=screen, camera=camera)
    #draw_bots(screen=screen, camera=camera)
    if draw_debug:
        space.debug_draw(options)
    time = monotonic() - time
    draw_time.append(time)

def physics():
    global physics_time, space
    time = monotonic()
    space.step(0.033)
    time = monotonic() - time
    physics_time.append(time)

def ticking():
    global dT
    pygame.display.flip()
    dT = clock.tick(30)
    pygame.display.set_caption(f"{TITLE}     \t[dT:{round(dT, 2)}]     \t[draw:{round(draw_t, 5)}]     \t[physics:{round(physics_t, 5)}]")

def draw_agents(screen: Surface, camera: Camera):
    for agent in agents:
        if camera.rect_on_screen(agent.rect):
            agent.draw(screen=screen, camera=camera)

def draw_bots(screen: Surface, camera: Camera):
    for bot in bots:
        if camera.rect_on_screen(bot.rect):
            bot.draw(screen=screen, camera=camera)

def draw_edges():
    global screen
    rect = Rect(Vector2(0, 0).x, Vector2(0, 0).y, cfg.world[0], cfg.world[1])
    #rect = Rect(camera.rel_pos(Vector2(0, 0)).x, camera.rel_pos(Vector2(0, 0)).y, cfg.world[0], cfg.world[1])
    if not camera.rect_on_screen(rect):
        return
    x0 = 1; y0 = 1; x1 = cfg.world[0]-1; y1 = cfg.world[1]-1
    p0 = Vector2(x0, y0); p1 = Vector2(x1, y0); p2 = Vector2(x1, y1); p3 = Vector2(x0, y1);
    pts = [camera.rel_pos(p0), camera.rel_pos(p1), camera.rel_pos(p2), camera.rel_pos(p3), camera.rel_pos(p0)]
    for p in range(4):
        v1 = pts[p]
        v2 = pts[p+1]
        #rect = Rect((min([v1[0], v2[0]]))-1, (min([v1[1], v2[1]]))-1, (max([v1[0], v2[0]])-min([v1[0], v2[0]]))+1, (max([v1[1], v2[1]])-min([v1[1], v2[1]]))+1)
        line(screen, Color(255,255,255), v1, v2, 1)

def calc_timings():
    global draw_t, draw_time, physics_time, physics_t
    if len(draw_time) > 120:
        #draw_time.pop(0)
        draw_t = mean(draw_time)
        draw_time = []
    if len(physics_time) > 120:
        #physics_time.pop(0)
        physics_t = mean(physics_time)
        physics_time = []


if __name__ == "__main__":
    sys.exit(main())