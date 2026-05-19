"""Renderer module providing the arcade graphical simulation window."""

from typing import Any

import arcade

from drone import Drone
from graph import Graph
from vars import ARC_COLORS

# Unused legacy constants kept for reference.
WINDOW_W = 600
WINDOW_H = 400
WINDOW_T = "Fly In"
BACKGROUND_COLOR = arcade.color.DARK_CHESTNUT

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
    """Arcade window that visualizes the drone simulation turn by turn."""

    def __init__(self, graph: Graph, drones: list[Drone]) -> None:
        """Initialize the renderer and precompute screen positions.

        Args:
            graph: The zone graph to display.
            drones: List of drones whose paths will be animated.
        """
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        self.current_col: int = 0
        self.color_counter: float = 0.4
        self.drone_rot: float = 0
        self.outer_radius: float = 12
        self.increase_rad: bool = True
        self.color_drones: list[Any] = [
            arcade.color.LIGHT_GOLDENROD_YELLOW,
            arcade.color.LIGHT_DEEP_PINK,
            arcade.color.ORANGE,
        ]
        self.graph: Graph = graph
        self.zones_info: list[
            tuple[arcade.Rect,
                  tuple[int, int, int, int]]] = []
        self.conns_info: list[tuple[float, float, float, float]] = []
        self.drones: list[Drone] = drones
        self.turn_timer: float = 0.0
        self.simulation_speed: float = .8
        self.current_sim_turn: int = 0

        self.text_space: arcade.Text = arcade.Text(
            "Press SPACE to restart",
            10, WINDOW_HEIGHT - 20,
            arcade.color.WHITE, 20
        )

        # Scale zone coordinates to fit the window.
        coords_x = [z.x for z in self.graph.zones]
        coords_y = [z.y for z in self.graph.zones]
        min_x, max_x = min(coords_x), max(coords_x)
        min_y, max_y = min(coords_y), max(coords_y)

        range_x = (max_x - min_x) if max_x != min_x else 1
        range_y = (max_y - min_y) if max_y != min_y else 1

        scale_x = (WINDOW_WIDTH * 0.8) / range_x
        scale_y = (WINDOW_HEIGHT * 0.6) / range_y

        self.pos_map: dict[str, tuple[float, float]] = {}
        for zone in self.graph.zones:
            if isinstance(zone.color, str):
                clr = ARC_COLORS.get(zone.color, arcade.color.GHOST_WHITE)
            else:
                clr = arcade.color.GHOST_WHITE

            screen_x = (zone.x - min_x) * scale_x + (WINDOW_WIDTH * 0.1)
            screen_y = (zone.y - min_y) * scale_y + (WINDOW_HEIGHT * 0.1)

            self.pos_map[zone.name] = (screen_x, screen_y)
            rect = arcade.Rect(
                0, 0, 0, 0,
                ZONE_SIZE, ZONE_SIZE,
                screen_x, screen_y)
            self.zones_info.append((rect, clr))

        for conn in self.graph.connections:
            if conn.zone_a in self.pos_map and conn.zone_b in self.pos_map:
                s = self.pos_map[conn.zone_a]
                e = self.pos_map[conn.zone_b]
                self.conns_info.append((s[0], s[1], e[0], e[1]))

        arcade.set_background_color(BACKGROUND_COLOR)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle key press events.

        Args:
            symbol: The key symbol pressed.
            modifiers: Any active modifier keys.
        """
        if symbol == arcade.key.SPACE:
            self.current_sim_turn = 0

    def on_draw(self) -> None:
        """Render the current simulation frame."""
        self.clear()

        self.text_space.draw()

        for sx, sy, ex, ey in self.conns_info:
            arcade.draw_line(
                sx, sy, ex, ey,
                arcade.color.GHOST_WHITE,
                LINE_WIDTH)
        for zone in self.zones_info:
            arcade.draw_rect_filled(zone[0], zone[1])

        for drone in self.drones:
            current_step: Any = next(
                (
                    item
                    for item, turn in drone.path
                    if turn == self.current_sim_turn
                ),
                None,
            )
            if current_step is None:
                continue
            if hasattr(current_step, "name"):
                if current_step.name in self.pos_map:
                    screen_x, screen_y = self.pos_map[current_step.name]
                    self.draw_drone(screen_x, screen_y, drone.color)
            elif isinstance(current_step, str):
                # In-transit on a restricted link "ZoneA-ZoneB": draw midpoint.
                parts = current_step.split("-")
                if len(parts) == 2:
                    start_name, end_name = parts[0], parts[1]
                    if (start_name in self.pos_map
                            and end_name in self.pos_map):
                        p1 = self.pos_map[start_name]
                        p2 = self.pos_map[end_name]
                        mid_x = (p1[0] + p2[0]) / 2
                        mid_y = (p1[1] + p2[1]) / 2
                        self.draw_drone(mid_x, mid_y, drone.color)

    def on_update(self, delta_time: float) -> None:
        """Update animation state and advance the simulation turn timer.

        Args:
            delta_time: Seconds elapsed since the last frame.
        """
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

        super().on_update(delta_time)

    def draw_drone(self, x: float, y: float, color: Any) -> None:
        """Draw a single drone at the given screen coordinates.

        Args:
            x: Screen X position.
            y: Screen Y position.
            color: Arcade color for the drone's accent ring and center dot.
        """
        arcade.draw_circle_filled(
            x, y,
            self.outer_radius * 0.6,
            arcade.color.WHITE)
        arcade.draw_circle_outline(
            x, y,
            self.outer_radius,
            color, 6, self.drone_rot, 6)
        arcade.draw_circle_filled(x, y, 5, color)
