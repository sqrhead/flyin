import sys

import arcade

from drone import Drone
from graph import Graph
from vars import ARC_COLORS

# Window Configrations
WINDOW_W = 600
WINDOW_H = 400
WINDOW_T = "Fly In"
BACKGROUND_COLOR = arcade.color.ORANGE_PEEL

# Path Node Colors
COLOR_GOAL = arcade.color.GREEN
COLOR_DEADEND = arcade.color.RED
COLOR_NORMAL = arcade.color.BLUE

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Fly In"

ZONE_SIZE = 24
PADDING = 40
TOP_PADDING = 8
LINE_WIDTH = 6


class Renderer(arcade.Window):
    def __init__(self, graph: Graph, drones: list[Drone]):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        self.current_col = 0
        self.color_counter: float = 0.4
        self.drone_rot: float = 0
        self.outer_radius: float = 12
        self.increase_rad: bool = True
        self.color_drones = [
            arcade.color.LIGHT_GOLDENROD_YELLOW,
            arcade.color.LIGHT_DEEP_PINK,
            arcade.color.ORANGE,
        ]
        self.graph = graph
        self.zones_info: list[tuple[arcade.Rect, tuple[int, int, int]]] = []
        self.conns_info: list[tuple[int, int, int, int]] = []
        self.drones = drones
        self.turn_timer = 0.0
        self.simulation_speed = 2
        self.current_sim_turn = 0

        self.text_space: arcade.Text = arcade.Text(
            "Press SPACE to restart", 10, WINDOW_HEIGHT - 20, arcade.color.WHITE, 20
        )
        self.text_turn: arcade.Text = arcade.Text(
            "OK", 10, WINDOW_HEIGHT - 42, arcade.color.WHITE, 20
        )

        # COORDS AND PADDING FOR THE ZONES BASED ON WINDOW SIZE
        coords_x = [z.x for z in self.graph.zones]
        coords_y = [z.y for z in self.graph.zones]
        min_x, max_x = min(coords_x), max(coords_x)
        min_y, max_y = min(coords_y), max(coords_y)

        range_x = (max_x - min_x) if max_x != min_x else 1
        range_y = (max_y - min_y) if max_y != min_y else 1

        scale_x = (WINDOW_WIDTH * 0.8) / range_x
        scale_y = (WINDOW_HEIGHT * 0.4) / range_y

        self.pos_map = {}
        for zone in self.graph.zones:
            clr = ARC_COLORS.get(zone.color, arcade.color.GHOST_WHITE)
            screen_x = (zone.x - min_x) * scale_x + (WINDOW_WIDTH * 0.1)
            screen_y = (zone.y - min_y) * scale_y + (WINDOW_HEIGHT * 0.1)

            self.pos_map[zone.name] = (screen_x, screen_y)
            rect = arcade.Rect(0, 0, 0, 0, ZONE_SIZE, ZONE_SIZE, screen_x, screen_y)
            self.zones_info.append((rect, clr))

        for conn in self.graph.connections:
            if conn.zone_a in self.pos_map and conn.zone_b in self.pos_map:
                start = self.pos_map[conn.zone_a]
                end = self.pos_map[conn.zone_b]

                self.conns_info.append((start[0], start[1], end[0], end[1]))

        arcade.set_background_color(arcade.color.BLACK)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            self.current_sim_turn = 0

    def on_draw(self) -> None:
        self.clear()

        self.text_space.draw()
        self.text_turn.text = f"Turn number = {self.current_sim_turn}"
        self.text_turn.draw()

        for sx, sy, ex, ey in self.conns_info:
            arcade.draw_line(sx, sy, ex, ey, arcade.color.GHOST_WHITE, LINE_WIDTH)
        for zone in self.zones_info:
            arcade.draw_rect_filled(zone[0], zone[1])

        # Draw Drones
        for drone in self.drones:
            current_step = next(
                (item for item, turn in drone.path if turn == self.current_sim_turn),
                None,
            )
            if current_step:
                if hasattr(current_step, "name"):
                    # 1. Use the name to get the calculated screen position
                    if current_step.name in self.pos_map:
                        screen_x, screen_y = self.pos_map[current_step.name]
                        self.draw_drone(screen_x, screen_y, drone.color)

                elif isinstance(current_step, str):
                    # 2. Handle the restricted link "ZoneA-ZoneB"
                    start_name, end_name = current_step.split("-")
                    if start_name in self.pos_map and end_name in self.pos_map:
                        p1 = self.pos_map[start_name]
                        p2 = self.pos_map[end_name]

                        # Calculate midpoint using screen coordinates
                        mid_x = (p1[0] + p2[0]) / 2
                        mid_y = (p1[1] + p2[1]) / 2
                        self.draw_drone(mid_x, mid_y, drone.color)
            # prev_pos = None
            # curr_pos = None
            # is_done = self.current_sim_turn > drone.path[-1][1]

            # for item, turn in drone.path:
            #     if turn <= self.current_sim_turn:
            #         prev_pos = curr_pos
            #         if hasattr(item, "name"):
            #             # it's a Zone
            #             if item.name in self.pos_map:
            #                 curr_pos = self.pos_map[item.name]
            #         else:
            #             # it's a connection string like "gate3-restricted_tunnel1"
            #             parts = item.split("-", 1)
            #             if parts[0] in self.pos_map and parts[1] in self.pos_map:
            #                 ax, ay = self.pos_map[parts[0]]
            #                 bx, by = self.pos_map[parts[1]]
            #                 # drone is halfway along the connection
            #                 curr_pos = ((ax + bx) / 2, (ay + by) / 2)

            # if curr_pos:
            #     if prev_pos and not is_done:
            #         t = self.turn_timer / self.simulation_speed
            #         sx = prev_pos[0] + (curr_pos[0] - prev_pos[0]) * t
            #         sy = prev_pos[1] + (curr_pos[1] - prev_pos[1]) * t
            #     else:
            #         sx, sy = curr_pos
            #     self.draw_drone(sx, sy)

    def on_update(self, delta_time):
        self.color_counter -= delta_time
        if self.color_counter <= 0:
            self.color_counter = 0.2
            self.current_col += 1
            if self.current_col > 2:
                self.current_col = 0
        self.drone_rot += delta_time * 120
        if self.drone_rot > 360:
            self.drone_rot = 0

        if self.outer_radius >= 24:
            self.increase_rad = False

        if self.increase_rad:
            self.outer_radius += delta_time * 26
        else:
            self.outer_radius -= delta_time * 32
            if self.outer_radius <= 12:
                self.increase_rad = True

        self.turn_timer += delta_time
        if self.turn_timer >= self.simulation_speed:
            self.current_sim_turn += 1
            self.turn_timer = 0

        return super().on_update(delta_time)

    def draw_drone(self, x: float, y: float, color) -> None:
        # 1. Draw a white background circle slightly larger than the drone
        # This acts as a 'stroke' so the drone never disappears into a zone
        arcade.draw_circle_filled(x, y, self.outer_radius * 0.6, arcade.color.WHITE)

        # 2. Draw your existing animated outline using the drone's unique color
        arcade.draw_circle_outline(x, y, self.outer_radius, color, 6, self.drone_rot, 6)

        # 3. Draw the center dot
        arcade.draw_circle_filled(x, y, 5, color)
