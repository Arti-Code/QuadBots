
class Config():

    def __init__(self):
        self.world = (800, 600)
        self.window = (800, 600)

    def set_world(self, world_size: tuple):
        self.world = world_size

    def set_window(self, window_size: tuple):
        self.window = window_size

cfg = Config()