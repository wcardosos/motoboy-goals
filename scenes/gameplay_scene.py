import pygame

from config.settings import ROAD_SCROLL_SPEED
from core.scene import Scene
from core.input_handler import InputHandler
from entities.road import Road


class GameplayScene(Scene):
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.road = Road()
        self.input_handler = InputHandler()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pass  # pause — not implemented yet

    def update(self, dt: float):
        self.input_handler.get_actions()
        self.road.update(dt, ROAD_SCROLL_SPEED)

    def draw(self, screen: pygame.Surface):
        self.road.draw(screen)
