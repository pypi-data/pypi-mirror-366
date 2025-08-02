from engine import Scene, Display, Object, SceneManager

sceneManager = SceneManager()

menu = Scene('Menu', Display((10, 10), fr=2))
Game = Scene('Game', Display((20, 20), fr=2))

bird = Object((2, 2), (1, 5), ch='$')

Game.add_object(bird)

sceneManager.add_scene(menu)
sceneManager.add_scene(Game)

sceneManager.set_scene('Menu')


while True:
    if Game.display.check_key('w'):
        bird.y -= 1
    if Game.display.check_key('s'):
        bird.y += 1
    if menu.display.check_key('e'):
        sceneManager.set_scene('Game')
    if Game.display.check_key('d'):
        sceneManager.set_scene('Menu')
    

    sceneManager.run()