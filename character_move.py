"""방향키로 소년 캐릭터를 이동하는 pico2d 프로그램."""

WIDTH, HEIGHT = 1280, 1024
FRAME_WIDTH, FRAME_HEIGHT = 100, 100


class Character:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.direction = None
        self.facing = "right"

    def press(self, key):
        if key == "up":
            self.direction = key
        elif key in ("right", "left"):
            self.direction = key
            self.facing = key

    def update(self):
        if self.direction == "right":
            self.x += 5
        elif self.direction == "left":
            self.x -= 5
        elif self.direction == "up":
            self.y += 5

    def draw(self, sprite):
        row = 300 if self.facing == "right" else 200
        sprite.clip_draw(0, row, FRAME_WIDTH, FRAME_HEIGHT, self.x, self.y)


def main():
    import pico2d as p

    p.open_canvas(WIDTH, HEIGHT)
    try:
        character = Character()
        sprite = p.load_image("animation_sheet.png")
        ground = p.load_image("TUK_GROUND.png")
        keys = {p.SDLK_RIGHT: "right", p.SDLK_LEFT: "left", p.SDLK_UP: "up"}
        running = True
        while running:
            for event in p.get_events():
                if event.type == p.SDL_QUIT:
                    running = False
                elif event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE:
                    running = False
                elif event.type == p.SDL_KEYDOWN and event.key in keys:
                    character.press(keys[event.key])
            if not running:
                break
            character.update()
            p.clear_canvas()
            ground.draw(WIDTH / 2, HEIGHT / 2, WIDTH, HEIGHT)
            character.draw(sprite)
            p.update_canvas()
            p.delay(0.01)
    finally:
        p.close_canvas()


if __name__ == "__main__":
    main()
