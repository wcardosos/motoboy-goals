class Scene:
    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass


class SceneManager:
    def __init__(self):
        self._current = None

    def set_scene(self, scene: Scene):
        self._current = scene

    @property
    def current(self) -> Scene:
        return self._current
