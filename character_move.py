"""방향키로 소년 캐릭터를 이동하는 pico2d 프로그램."""

WIDTH, HEIGHT = 1280, 1024


def main():
    import pico2d as p

    p.open_canvas(WIDTH, HEIGHT)
    try:
        running = True
        while running:
            for event in p.get_events():
                if event.type == p.SDL_QUIT:
                    running = False
                elif event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE:
                    running = False
            if not running:
                break
            p.clear_canvas()
            p.update_canvas()
            p.delay(0.01)
    finally:
        p.close_canvas()


if __name__ == "__main__":
    main()
