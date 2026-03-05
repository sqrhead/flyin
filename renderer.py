import arcade

# Window Configrations
WINDOW_W = 600
WINDOW_H = 400
WINDOW_T = 'Fly In'
BACKGROUND_COLOR = arcade.color.WARM_BLACK

# Path Node Colors
COLOR_GOAL = arcade.color.GREEN
COLOR_DEADEND = arcade.color.RED
COLOR_NORMAL = arcade.color.BLUE


class Renderer(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_W, WINDOW_H, WINDOW_T)
        self.background_color = BACKGROUND_COLOR
        self.text = arcade.Text('Fly In', 1, WINDOW_H - 14, arcade.color.GREEN, 14)
        self.default_rect = arcade.Rect(50, 50, 80, 80, 20, 20, 50, 50)
        self.drone_rect = arcade.Rect(30,30, 50, 50, 14, 14, 50, 50)

        # Find way to move, cpy
        self.cpy_rect = self.default_rect
        self.cpy_rect.resize(102, 32)
        self.cpy_rect.move(0, 0)

    def setup(self) -> None:
        ...

    def on_draw(self) -> None:
        self.clear()
        self.text.draw()
        arcade.draw_line(0, WINDOW_H - 20, WINDOW_W, WINDOW_H - 20, arcade.color.TEA_GREEN, 3)
        arcade.draw_rect_filled(self.default_rect, arcade.color.RED)
        arcade.draw_rect_filled(self.drone_rect, arcade.color.WHITE)
        arcade.draw_rect_filled(self.cpy_rect, arcade.color.GREEN)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
        if symbol == arcade.key.SPACE:
            self.drone_rect.move(120, self.drone_rect.y)

    def on_update(self, delta_time):
        self.text.x += delta_time * 120
        if self.text.x > WINDOW_W:
            self.text.x = -120
        return super().on_update(delta_time)

    def run(self, view = None):
        return super().run(view)
