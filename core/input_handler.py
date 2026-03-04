from enum import Enum, auto

import pygame


class Action(Enum):
    ACCELERATE = auto()
    BRAKE = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    PAUSE = auto()
    HORN = auto()


_KEY_MAP = {
    pygame.K_UP: Action.ACCELERATE,
    pygame.K_w: Action.ACCELERATE,
    pygame.K_DOWN: Action.BRAKE,
    pygame.K_s: Action.BRAKE,
    pygame.K_LEFT: Action.MOVE_LEFT,
    pygame.K_a: Action.MOVE_LEFT,
    pygame.K_RIGHT: Action.MOVE_RIGHT,
    pygame.K_d: Action.MOVE_RIGHT,
    pygame.K_ESCAPE: Action.PAUSE,
    pygame.K_SPACE: Action.HORN,
}


class InputHandler:
    def get_actions(self) -> set:
        pressed = pygame.key.get_pressed()
        return {action for key, action in _KEY_MAP.items() if pressed[key]}
