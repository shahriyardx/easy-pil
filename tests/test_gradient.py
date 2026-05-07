"""Tests for gradient fill module (LinearGradient, RadialGradient)."""

from easy_pil.gradient import LinearGradient, RadialGradient


class TestLinearGradient:
    def test_horizontal(self) -> None:
        g = LinearGradient(["red", "blue"])
        img = g.render(100, 50)
        assert img.size == (100, 50)
        assert img.mode == "RGBA"
        # left edge should be red-ish
        left = img.getpixel((0, 25))
        assert left == (255, 0, 0, 255), f"Expected red-ish, got {left}"
        # right edge should be blue-ish
        right = img.getpixel((99, 25))
        assert right == (0, 0, 255, 255), f"Expected blue-ish, got {right}"
        # center should be purple-ish
        center = img.getpixel((49, 25))
        assert center[0] > 0 and center[2] > 0, f"Expected purple-ish, got {center}"

    def test_vertical(self) -> None:
        g = LinearGradient(["white", "black"], direction="vertical")
        img = g.render(50, 100)
        top = img.getpixel((25, 0))
        bottom = img.getpixel((25, 99))
        assert top == (255, 255, 255, 255), f"Expected white, got {top}"
        assert bottom == (0, 0, 0, 255), f"Expected black, got {bottom}"

    def test_diagonal(self) -> None:
        g = LinearGradient(["red", "blue"], direction="diagonal")
        img = g.render(100, 100)
        assert img.size == (100, 100)

    def test_solid_to_transparent(self) -> None:
        g = LinearGradient(["red", (255, 0, 0, 0)])
        img = g.render(100, 10)
        left = img.getpixel((0, 5))
        right = img.getpixel((99, 5))
        assert left == (255, 0, 0, 255), f"Expected opaque red, got {left}"
        assert right[3] == 0, f"Expected transparent, got alpha={right[3]}"

    def test_three_colors(self) -> None:
        g = LinearGradient(["red", "green", "blue"])
        img = g.render(100, 10)
        mid = img.getpixel((49, 5))
        assert mid[1] > 0, f"Expected green influence, got {mid}"

    def test_1x1(self) -> None:
        g = LinearGradient(["red", "blue"])
        img = g.render(1, 1)
        assert img.getpixel((0, 0)) == (255, 0, 0, 255)

    def test_invalid_direction_defaults_to_horizontal(self) -> None:
        g = LinearGradient(["red", "blue"], direction="unknown")
        img = g.render(100, 10)
        assert img is not None


class TestRadialGradient:
    def test_default_center(self) -> None:
        g = RadialGradient(["white", "black"])
        img = g.render(100, 100)
        assert img.size == (100, 100)
        assert img.mode == "RGBA"
        # center should be white
        center = img.getpixel((50, 50))
        assert center == (255, 255, 255, 255), f"Expected white, got {center}"
        # corner should be black
        corner = img.getpixel((0, 0))
        assert corner == (0, 0, 0, 255), f"Expected black, got {corner}"

    def test_offset_center(self) -> None:
        g = RadialGradient(["white", "black"], center=(0.2, 0.5))
        img = g.render(100, 100)
        # center at 20%, 50% should be white
        cx, cy = 20, 50
        assert img.getpixel((cx, cy)) == (255, 255, 255, 255)

    def test_solid_to_transparent(self) -> None:
        g = RadialGradient(["red", (255, 0, 0, 0)])
        img = g.render(50, 50)
        center = img.getpixel((25, 25))
        assert center[3] == 255, f"Expected opaque center, got alpha={center[3]}"
        corner = img.getpixel((0, 0))
        assert corner[3] == 0, f"Expected transparent corner, got alpha={corner[3]}"

    def test_three_colors(self) -> None:
        g = RadialGradient(["red", "green", "blue"])
        img = g.render(50, 50)
        assert img is not None

    def test_1x1(self) -> None:
        g = RadialGradient(["red", "blue"])
        img = g.render(1, 1)
        assert img.getpixel((0, 0)) == (255, 0, 0, 255)
