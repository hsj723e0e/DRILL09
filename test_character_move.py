"""PRD 동작과 프로그램의 입력 및 종료 흐름을 검증한다."""
import math
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import character_move as game


class CharacterTests(unittest.TestCase):
    def setUp(self):
        self.character = game.Character()

    def test_starts_idle_at_center(self):
        c = self.character
        c.update(0.5)
        self.assertEqual((c.x, c.y), (640, 512))
        self.assertFalse(c.moving)
        self.assertEqual(c.frame, 0)

    def test_each_arrow_moves_in_its_direction(self):
        for key, expected in [("right", (665, 512)), ("left", (615, 512)),
                              ("up", (640, 537)), ("down", (640, 487))]:
            with self.subTest(key=key):
                c = game.Character()
                c.press(key)
                c.update(0.1)
                self.assertEqual((c.x, c.y), expected)
                self.assertTrue(c.moving)

    def test_release_stops_and_idle_stays_frozen(self):
        c = self.character
        c.press("right")
        c.update(0.1)
        self.assertNotEqual(c.frame, 0)
        c.release("right")
        position = (c.x, c.y)
        for _ in range(20):
            c.update(0.1)
            self.assertEqual((c.x, c.y), position)
            self.assertEqual(c.frame, 0)
            self.assertFalse(c.moving)

    def test_vertical_movement_preserves_both_facings(self):
        for facing in ("left", "right"):
            for vertical in ("up", "down"):
                with self.subTest(facing=facing, vertical=vertical):
                    c = game.Character()
                    c.press(facing)
                    c.update(0.1)
                    c.release(facing)
                    c.press(vertical)
                    c.update(0.1)
                    self.assertEqual(c.facing, facing)

    def test_repeated_keydown_does_not_accumulate_speed(self):
        c = self.character
        for _ in range(10):
            c.press("right")
        c.update(0.1)
        self.assertEqual(c.x, 665)
        c.release("right")
        c.update(0.1)
        self.assertEqual(c.x, 665)

    def test_opposing_keys_cancel_on_each_axis(self):
        for pair in [("left", "right"), ("up", "down")]:
            with self.subTest(pair=pair):
                c = game.Character()
                for key in pair:
                    c.press(key)
                c.update(0.1)
                self.assertEqual((c.x, c.y), (640, 512))
                self.assertFalse(c.moving)

    def test_releasing_opposite_key_restores_remaining_direction(self):
        c = self.character
        c.press("right")
        c.press("left")
        c.update(0.1)
        c.release("left")
        c.update(0.1)
        self.assertEqual(c.x, 665)
        self.assertEqual(c.facing, "right")

    def test_unrelated_input_does_not_move_character(self):
        c = self.character
        c.press("space")
        c.release("up")
        c.update(0.1)
        self.assertEqual((c.x, c.y), (640, 512))

    def test_diagonal_speed_matches_straight_speed(self):
        c = self.character
        c.press("right")
        c.press("up")
        c.update(0.1)
        self.assertAlmostEqual(math.hypot(c.x - 640, c.y - 512), 25)

    def test_all_edges_keep_entire_sprite_inside_canvas(self):
        for key, expected in [("left", (50, 512)), ("right", (1230, 512)),
                              ("down", (640, 50)), ("up", (640, 974))]:
            with self.subTest(key=key):
                c = game.Character()
                c.press(key)
                c.update(100)
                self.assertEqual((c.x, c.y), expected)
                c.update(0.1)
                self.assertFalse(c.moving)
                self.assertEqual(c.frame, 0)

    def test_can_move_along_edge_and_return_inward(self):
        c = self.character
        c.x = 1230
        c.press("right")
        c.press("up")
        c.update(0.1)
        self.assertEqual(c.x, 1230)
        self.assertGreater(c.y, 512)
        self.assertTrue(c.moving)
        c.release("right")
        c.release("up")
        c.press("left")
        c.update(0.1)
        self.assertEqual(c.x, 1205)

    def test_move_and_animation_are_independent_of_update_frequency(self):
        slow, fast = game.Character(), game.Character()
        for c in (slow, fast):
            c.press("right")
        slow.update(0.25)
        for _ in range(5):
            fast.update(0.05)
        self.assertAlmostEqual(slow.x, fast.x)
        self.assertEqual(slow.frame, fast.frame)
        slow.update(0.5)
        self.assertEqual(slow.frame, 1)  # 0.75초 = 9프레임, 8프레임 순환

    def test_draw_uses_correct_idle_and_running_rows(self):
        for facing, idle_row, run_row in [("right", 300, 100), ("left", 200, 0)]:
            with self.subTest(facing=facing):
                c = game.Character()
                sprite = Mock()
                c.press(facing)
                c.update(0.1)
                c.draw(sprite)
                self.assertEqual(sprite.clip_draw.call_args.args[:4], (100, run_row, 100, 100))
                c.release(facing)
                c.update(0.1)
                c.draw(sprite)
                self.assertEqual(sprite.clip_draw.call_args.args[:4], (0, idle_row, 100, 100))


class ApplicationTests(unittest.TestCase):
    def make_pico(self, batches):
        p = SimpleNamespace(SDL_QUIT=1, SDL_KEYDOWN=2, SDL_KEYUP=3,
                            SDLK_RIGHT=4, SDLK_LEFT=5, SDLK_UP=6,
                            SDLK_DOWN=7, SDLK_ESCAPE=8)
        for name in ("open_canvas", "close_canvas", "clear_canvas", "update_canvas", "delay"):
            setattr(p, name, Mock())
        p.load_image = Mock(return_value=Mock())
        p.get_events = Mock(side_effect=batches)
        return p

    def test_key_events_reach_character_and_escape_closes_canvas(self):
        batches = [[SimpleNamespace(type=2, key=4)],
                   [SimpleNamespace(type=3, key=4)],
                   [SimpleNamespace(type=2, key=8)]]
        p = self.make_pico(batches)
        c = game.Character()
        with patch.dict("sys.modules", {"pico2d": p}), \
                patch.object(game, "Character", return_value=c), \
                patch.object(game, "perf_counter", side_effect=[0, 0.1, 0.2]):
            game.main()
        self.assertEqual(c.x, 665)
        self.assertFalse(c.moving)
        p.open_canvas.assert_called_once_with(1280, 1024)
        p.close_canvas.assert_called_once()
        self.assertEqual(p.update_canvas.call_count, 2)
        for call in p.load_image.call_args_list:
            self.assertTrue(game.Path(call.args[0]).is_absolute())

    def test_window_close_exits_without_drawing(self):
        p = self.make_pico([[SimpleNamespace(type=1)]])
        with patch.dict("sys.modules", {"pico2d": p}):
            game.main()
        p.close_canvas.assert_called_once()
        p.update_canvas.assert_not_called()

    def test_canvas_is_closed_when_resource_loading_fails(self):
        p = self.make_pico([])
        p.load_image.side_effect = OSError("이미지 로드 실패")
        with patch.dict("sys.modules", {"pico2d": p}):
            with self.assertRaises(OSError):
                game.main()
        p.close_canvas.assert_called_once()


if __name__ == "__main__":
    unittest.main()
