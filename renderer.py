import arcade

# Window Configrations
WINDOW_W = 600
WINDOW_H = 400
WINDOW_T = 'Fly In'
BACKGROUND_COLOR = arcade.color.ZAFFRE

# Path Node Colors
COLOR_GOAL = arcade.color.GREEN
COLOR_DEADEND = arcade.color.RED
COLOR_NORMAL = arcade.color.BLUE


class Renderer(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_W, WINDOW_H, WINDOW_T)
        self.background_color = BACKGROUND_COLOR
        self.top_text: list[arcade.Text] = [
            arcade.Text('Fly In', 1, WINDOW_H - 16, arcade.color.WHITE, 14),
            arcade.Text('Fly In', 96, WINDOW_H - 16, arcade.color.WHITE, 14),
            arcade.Text('Fly In', 96 * 2, WINDOW_H - 16, arcade.color.WHITE, 14),
            arcade.Text('Fly In', 96 * 3, WINDOW_H - 16, arcade.color.WHITE_SMOKE, 14),
            arcade.Text('Fly In', 96 * 4, WINDOW_H - 16, arcade.color.WHITE_SMOKE, 14),
            arcade.Text('Fly In', 96 * 5, WINDOW_H - 16, arcade.color.WHITE_SMOKE, 14)
        ]
        self.animation_speed: int = 100


    def setup(self) -> None:
        ...

    def on_draw(self) -> None:
        self.clear()
        # Animation
        for txt in self.top_text:
            txt.draw()
        arcade.draw_line(0, WINDOW_H - 32, WINDOW_W, WINDOW_H - 32, arcade.color.WHITE, 2)
        #

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
        if symbol == arcade.key.SPACE:
            self.animation_speed += 20
            if self.animation_speed > 200:
                self.animation_speed = 100


    def on_update(self, delta_time):
        for txt in self.top_text:
            txt.x += delta_time * self.animation_speed
            if txt.x > WINDOW_W:
                txt.x = -120
        return super().on_update(delta_time)

    def run(self, view = None):
        return super().run(view)
