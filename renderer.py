import arcade

# Window Configrations
WINDOW_W = 600
WINDOW_H = 400
WINDOW_T = 'Fly In'
BACKGROUND_COLOR = arcade.color.ORANGE_PEEL

# Path Node Colors
COLOR_GOAL = arcade.color.GREEN
COLOR_DEADEND = arcade.color.RED
COLOR_NORMAL = arcade.color.BLUE

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500
WINDOW_TITLE = "Fly In"

class Renderer(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        self.grid: list[list[int]] = []
        for y in range(5):
            self.grid[y].append([])
            for x in range(5):
                self.grid[y][x].append(x - y)


    def setup(self) -> None:
        arcade.set_background_color(arcade.color.BLACK)
        ...
    def on_draw(self) -> None:
        self.clear()
        arcade.draw_circle_filled(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, 24, arcade.color.RED)
        for y in len(self.grid):
            for x in len(self.grid[0]):
                if self.grid[y][x] < 0:
                    arcade.draw_rect_filled(arcade.Rect(0,0,0,0, 16,16, x * 16, y * 16), arcade.color.RED)
                else:
                    arcade.draw_rect_filled(arcade.Rect(0,0,0,0, 16,16, x * 16, y * 16), arcade.color.GREEN)
