"""방향키로 소년 캐릭터를 이동하는 pico2d 프로그램."""

WIDTH, HEIGHT = 1280, 1024
FRAME_WIDTH, FRAME_HEIGHT = 100, 100


class Character:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.pressed = set()
        self.facing = "right"
        self.moving = False

    def press(self, key):
        if key not in ("right", "left", "up", "down"):
            return
        self.pressed.add(key)
        if key in ("right", "left"):
            self.facing = key

    def release(self, key):
        self.pressed.discard(key)

    def movement(self):
        dx = int("right" in self.pressed) - int("left" in self.pressed)
        dy = int("up" in self.pressed) - int("down" in self.pressed)
        return dx, dy

    def update(self):
        dx, dy = self.movement()
        self.moving = bool(dx or dy)
        if dx:
            self.facing = "right" if dx > 0 else "left"
        self.x += dx * 5
        self.y += dy * 5

    def draw(self, sprite):
        if self.moving:
            row = 100 if self.facing == "right" else 0
        else:
            row = 300 if self.facing == "right" else 200
        sprite.clip_draw(0, row, FRAME_WIDTH, FRAME_HEIGHT, self.x, self.y)


def main():
    import pico2d as p

    p.open_canvas(WIDTH, HEIGHT)
    try:
        character = Character()
        sprite = p.load_image("animation_sheet.png")
        ground = p.load_image("TUK_GROUND.png")
        keys = {p.SDLK_RIGHT: "right", p.SDLK_LEFT: "left", p.SDLK_UP: "up", p.SDLK_DOWN: "down"}
        running = True
        while running:
            for event in p.get_events():
                if event.type == p.SDL_QUIT:
                    running = False
                elif event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE:
                    running = False
                elif event.type == p.SDL_KEYDOWN and event.key in keys:
                    character.press(keys[event.key])
                elif event.type == p.SDL_KEYUP and event.key in keys:
                    character.release(keys[event.key])
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
