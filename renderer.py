import arcade

WINDOW_W = 600
WINDOW_H = 400
WINDOW_T = 'Fly In'
BACKGROUND_COLOR = arcade.color.WARM_BLACK

class Renderer(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_W, WINDOW_H, WINDOW_T)
        self.background_color = BACKGROUND_COLOR
        self.text = arcade.Text('Fly In', 1, WINDOW_H - 14, arcade.color.GREEN, 14)

    def setup(self) -> None:
        ...

    def on_draw(self) -> None:
        self.clear()
        self.text.draw()
        arcade.draw_line(0, WINDOW_H - 20, WINDOW_W, WINDOW_H - 20, arcade.color.TEA_GREEN, 3)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            raise SystemExit('exit')

    def on_update(self, delta_time):
        self.text.x += delta_time * 120
        if self.text.x > WINDOW_W:
            self.text.x = -120
        return super().on_update(delta_time)

    def run(self, view = None):
        return super().run(view)
