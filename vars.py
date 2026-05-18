"""Color constants for zone display and drone rendering."""

import arcade

# Available color names accepted in map file metadata.
AVB_COLORS: list[str] = [
    "black",
    "blue",
    "brown",
    "crimson",
    "cyan",
    "darkred",
    "gold",
    "green",
    "lime",
    "magenta",
    "maroon",
    "orange",
    "purple",
    "rainbow",
    "red",
    "violet",
    "yellow",
]

# Mapping from color name strings to arcade Color objects.
ARC_COLORS: dict[str, tuple[int, int, int, int]] = {
    "black": arcade.color.BLACK,
    "blue": arcade.color.BLUEBONNET,
    "brown": arcade.color.BROWN,
    "crimson": arcade.color.CRIMSON,
    "cyan": arcade.color.CYAN,
    "darkred": arcade.color.DARK_RED,
    "gold": arcade.color.GOLD,
    "green": arcade.color.GREEN,
    "lime": arcade.color.LIME,
    "magenta": arcade.color.MAGENTA,
    "maroon": arcade.color.MAROON,
    "orange": arcade.color.ORANGE,
    "purple": arcade.color.PURPLE,
    "rainbow": arcade.color.ALLOY_ORANGE,
    "red": arcade.color.RED,
    "violet": arcade.color.VIOLET,
    "yellow": arcade.color.YELLOW,
}

DRN_COLORS: list[tuple[int, int, int, int]] = [
    arcade.color.CYBER_YELLOW,
    arcade.color.ARCADE_GREEN,
    arcade.color.RED_VIOLET,
    arcade.color.VIOLET_BLUE,
    arcade.color.GIANTS_ORANGE
]