"""Color constants for zone display and drone rendering."""

import arcade

# Mapping from color name strings to arcade Color objects.
ARC_COLORS: dict[str, tuple[int, int, int, int]] = {
    "red": arcade.color.RED,
    "blue": arcade.color.BLUE,
    "green": arcade.color.GREEN,
    "yellow": arcade.color.YELLOW,
    "orange": arcade.color.ORANGE,
    "purple": arcade.color.PURPLE,

    "black": arcade.color.BLACK,
    "white": arcade.color.WHITE,
    "gray": arcade.color.GRAY,
    "silver": arcade.color.SILVER,
    "brown": arcade.color.BROWN,

    "cyan": arcade.color.CYAN,
    "aqua": arcade.color.AQUA,
    "teal": arcade.color.TEAL,
    "navy": arcade.color.NAVY_BLUE,
    "indigo": arcade.color.INDIGO,

    "lime": arcade.color.LIME,
    "olive": arcade.color.OLIVE,

    "magenta": arcade.color.MAGENTA,
    "pink": arcade.color.PINK,
    "violet": arcade.color.VIOLET,
    "plum": arcade.color.PLUM,

    "gold": arcade.color.GOLD,
    "maroon": arcade.color.MAROON,
    "crimson": arcade.color.CRIMSON,
    "coral": arcade.color.CORAL,
    "salmon": arcade.color.SALMON,
    "tomato": arcade.color.TOMATO,
    "sienna": arcade.color.SIENNA,
    "tan": arcade.color.TAN,
    "khaki": arcade.color.KHAKI,
    "wheat": arcade.color.WHEAT,

    "darkred": arcade.color.DARK_RED,
    "darkblue": arcade.color.DARK_BLUE,
    "darkgreen": arcade.color.DARK_GREEN,
    "darkorange": arcade.color.DARK_ORANGE,
    "darkcyan": arcade.color.DARK_CYAN,
    "darkmagenta": arcade.color.DARK_MAGENTA,
    "darkgray": arcade.color.DARK_GRAY,
    "darkkhaki": arcade.color.DARK_KHAKI,
    "darksalmon": arcade.color.DARK_SALMON,
    "darkviolet": arcade.color.DARK_VIOLET,
    "darkorchid": arcade.color.DARK_ORCHID,

    "lightblue": arcade.color.LIGHT_BLUE,
    "lightgreen": arcade.color.LIGHT_GREEN,
    "lightcyan": arcade.color.LIGHT_CYAN,
    "lightpink": arcade.color.LIGHT_PINK,
    "lightyellow": arcade.color.LIGHT_YELLOW,
    "lightgray": arcade.color.LIGHT_GRAY,
    "lightsalmon": arcade.color.LIGHT_SALMON,
    "lightcoral": arcade.color.LIGHT_CORAL,


    "rainbow": arcade.color.BABY_BLUE_EYES
}

DRN_COLORS: list[tuple[int, int, int, int]] = [
    arcade.color.CYBER_YELLOW,
    arcade.color.ARCADE_GREEN,
    arcade.color.RED_VIOLET,
    arcade.color.VIOLET_BLUE,
    arcade.color.GIANTS_ORANGE
]
