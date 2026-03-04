from core.game import Game
from scenes.gameplay_scene import GameplayScene

if __name__ == "__main__":
    game = Game()
    game.scene_manager.set_scene(GameplayScene(game.screen))
    game.run()
