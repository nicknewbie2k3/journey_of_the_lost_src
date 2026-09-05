import pyray as rl

from core.scenes.loading import LoadingScene

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450


def main():
    rl.set_config_flags(rl.FLAG_WINDOW_RESIZABLE)
    rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Hestie")
    rl.init_audio_device()
    rl.set_target_fps(60)

    current_scene = LoadingScene()

    while not rl.window_should_close():
        current_scene.update()

        rl.begin_drawing()
        rl.clear_background(rl.BLACK)
        current_scene.draw()
        rl.end_drawing()

        if current_scene.is_done():
            if hasattr(current_scene, "cleanup"):
                current_scene.cleanup()
            current_scene = current_scene.next_scene
            if current_scene is None:
                break

    rl.close_audio_device()
    rl.close_window()


if __name__ == "__main__":
    main()
