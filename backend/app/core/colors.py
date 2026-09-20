import re
from functools import lru_cache

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

PALETTE: dict[str, str] = {
    "Білий": "#FFFFFF",
    "Світло-сірий": "#C8C8C8",
    "Сірий": "#808080",
    "Темно-сірий": "#404040",
    "Чорний": "#000000",
    "Бежевий": "#DCC9A6",
    "Пісочний": "#C2B280",
    "Коричневий": "#6B4226",
    "Червоний": "#E03131",
    "Бордовий": "#7B1E2B",
    "Кораловий": "#FF7F6B",
    "Рожевий": "#F4A6C0",
    "Помаранчевий": "#F28C28",
    "Жовтий": "#F6D935",
    "Гірчичний": "#C99A1F",
    "Зелений": "#2E8B3E",
    "Оливковий": "#6B7A2A",
    "Блакитний": "#8FC3E8",
    "Джинсовий": "#4F6D8F",
    "Синій": "#2456C8",
    "Темно-синій": "#14224F",
    "Фіолетовий": "#7B4BB7",
}

COLOR_NAMES: list[str] = list(PALETTE)


def _srgb_to_lab(hex_color: str) -> tuple[float, float, float]:
    r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5))

    def linear(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = linear(r), linear(g), linear(b)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


_PALETTE_LAB = {name: _srgb_to_lab(hex_color) for name, hex_color in PALETTE.items()}


@lru_cache(maxsize=1024)
def color_name(hex_color: str | None) -> str | None:
    if not hex_color or not HEX_RE.match(hex_color):
        return None

    lab = _srgb_to_lab(hex_color)
    return min(
        _PALETTE_LAB,
        key=lambda name: sum((a - b) ** 2 for a, b in zip(lab, _PALETTE_LAB[name])),
    )
