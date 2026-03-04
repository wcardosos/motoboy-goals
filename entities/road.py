import pygame

from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, ROAD_SPRITE_PATH


class Road:
    def __init__(self):
        raw = pygame.image.load(ROAD_SPRITE_PATH).convert()
        self.image = pygame.transform.scale(raw, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.height = SCREEN_HEIGHT
        self.y1 = 0
        self.y2 = -self.height

    def update(self, dt: float, speed: float):
        self.y1 += speed * dt
        self.y2 += speed * dt
        if self.y1 >= self.height:
            self.y1 = self.y2 - self.height
        if self.y2 >= self.height:
            self.y2 = self.y1 - self.height

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, (0, self.y1))
        screen.blit(self.image, (0, self.y2))
