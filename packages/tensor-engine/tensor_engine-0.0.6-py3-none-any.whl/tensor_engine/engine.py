from .window import Display
from .object import Object


class Scene:
    def __init__(self, name: str, display: Display):
        self.name = name
        self.display = display
        self.objects = []
    
    def add_object(self, obj: Object):
        self.objects.append(obj)
    
    def remove_object(self, obj: Object):
        if obj in self.objects:
            self.objects.remove(obj)

    def run(self):
        for obj in self.objects:
            self.display.draw(obj)
        self.display.update()


class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.active_scene: Scene = None
    
    def add_scene(self, scene: Scene):
        self.scenes[scene.name] = scene
    
    def set_scene(self, scene_name: str):
        if scene_name in self.scenes:
            try:
                self.active_scene.display.active = False
                self.active_scene.display.clear()
            except:
                pass
            self.active_scene = self.scenes[scene_name]
            self.active_scene.display.active = True
        else:
            raise ValueError(f'Scene "{scene_name}" not found.')
    
    def run(self):
        self.active_scene.run()