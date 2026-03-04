import pygame

from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_TITLE
from core.scene import SceneManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.scene_manager = SceneManager()
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.scene_manager.current:
                    self.scene_manager.current.handle_event(event)

            if self.scene_manager.current:
                self.scene_manager.current.update(dt)
                self.scene_manager.current.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
