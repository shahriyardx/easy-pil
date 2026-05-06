"""Tests for all effects."""

import unittest
from unittest.mock import patch

from PIL import Image as PilImage

from easy_pil import Canvas, Editor, Font
from easy_pil.effect import (
    Bloom,
    Blur,
    Cartoon,
    ChromaticAberration,
    ColorOverlay,
    Contour,
    Dither,
    DropShadow,
    Duotone,
    EdgeEnhance,
    EdgeGlow,
    Emboss,
    Glitch,
    Glow,
    Gradient,
    Grayscale,
    Halftone,
    Invert,
    Kaleidoscope,
    Neon,
    Noise,
    OilPaint,
    Pixelate,
    PixelateRegion,
    PixelSort,
    Posterize,
    Ripple,
    Scanlines,
    Sepia,
    Sharpen,
    Sketch,
    Smooth,
    Solarize,
    Thermal,
    Threshold,
    TiltShift,
    Vignette,
    Vortex,
)


class TestEffects(unittest.TestCase):
    """Test all effect classes via editor.effect()."""

    @classmethod
    def setUpClass(cls) -> None:
        canvas = Canvas((64, 64), color="white")
        cls.img = Editor(canvas)
        # draw something so effects have content
        cls.img.rectangle((10, 10), 44, 44, color="red")
        cls.img.text((32, 32), "A", color="black", font=Font.poppins(size=20))

    def _apply(self, effect) -> Editor:
        result = Editor(self.img.image).effect(effect)
        self.assertIsInstance(result, Editor)
        self.assertEqual(result.image.size, (64, 64))
        return result

    def test_vignette(self) -> None:
        self._apply(Vignette())

    def test_vignette_custom(self) -> None:
        self._apply(Vignette(radius=50, color=(255, 0, 0), feather=10))

    def test_vignette_string_color(self) -> None:
        self._apply(Vignette(color="red"))

    def test_color_overlay(self) -> None:
        self._apply(ColorOverlay(color=(255, 0, 0), alpha=0.5))

    def test_color_overlay_string(self) -> None:
        self._apply(ColorOverlay(color="red"))

    def test_drop_shadow(self) -> None:
        self._apply(DropShadow())

    def test_drop_shadow_custom(self) -> None:
        self._apply(DropShadow(offset=(3, 3), blur_radius=5, alpha=0.8))

    def test_glow(self) -> None:
        self._apply(Glow())

    def test_glow_custom(self) -> None:
        self._apply(Glow(radius=5, color="cyan", alpha=0.3))

    def test_gradient(self) -> None:
        self._apply(Gradient(colors=["red", "blue"]))

    def test_gradient_vertical(self) -> None:
        self._apply(Gradient(colors=["red", "green", "blue"], direction="vertical"))

    def test_gradient_diagonal(self) -> None:
        self._apply(Gradient(colors=["black", "white"], direction="diagonal"))

    def test_gradient_invalid(self) -> None:
        with self.assertRaises(ValueError):
            Gradient(colors=["red"])

    def test_pixelate_region(self) -> None:
        self._apply(PixelateRegion(box=(10, 10, 30, 30), pixel_size=4))

    def test_noise(self) -> None:
        self._apply(Noise())

    def test_noise_color(self) -> None:
        self._apply(Noise(intensity=0.5, monochrome=False))

    def test_posterize(self) -> None:
        self._apply(Posterize(bits=3))

    def test_posterize_clamp(self) -> None:
        self._apply(Posterize(bits=10))  # clamped to 8

    def test_solarize(self) -> None:
        self._apply(Solarize(threshold=100))

    def test_threshold(self) -> None:
        self._apply(Threshold(cutoff=128))

    def test_oil_paint(self) -> None:
        self._apply(OilPaint(radius=2))

    def test_tilt_shift(self) -> None:
        self._apply(TiltShift(blur_strength=3, focus_width=0.5))

    def test_duotone(self) -> None:
        self._apply(Duotone(dark_color=(10, 10, 50), light_color=(255, 240, 200)))

    def test_bloom(self) -> None:
        self._apply(Bloom())

    def test_chromatic_aberration(self) -> None:
        self._apply(ChromaticAberration(offset=2))

    def test_edge_glow(self) -> None:
        self._apply(EdgeGlow(color="cyan", intensity=0.5))

    def test_halftone(self) -> None:
        self._apply(Halftone(dot_size=8))

    def test_kaleidoscope(self) -> None:
        self._apply(Kaleidoscope(segments=4))

    def test_ripple(self) -> None:
        self._apply(Ripple(amplitude=3, period=20))

    def test_blur_gaussian(self) -> None:
        self._apply(Blur(amount=2))

    def test_blur_box(self) -> None:
        self._apply(Blur(amount=2, mode="box"))

    def test_contour(self) -> None:
        self._apply(Contour())

    def test_emboss(self) -> None:
        self._apply(Emboss())

    def test_edge_enhance(self) -> None:
        self._apply(EdgeEnhance(amount=2))

    def test_sharpen(self) -> None:
        self._apply(Sharpen(amount=2))

    def test_smooth(self) -> None:
        self._apply(Smooth(amount=2))

    def test_grayscale(self) -> None:
        self._apply(Grayscale())

    def test_sepia(self) -> None:
        self._apply(Sepia())

    def test_invert(self) -> None:
        self._apply(Invert())

    def test_pixelate(self) -> None:
        self._apply(Pixelate(pixel_size=8))

    def test_glitch(self) -> None:
        self._apply(Glitch(amount=0.5))

    def test_glitch_zero(self) -> None:
        self._apply(Glitch(amount=0))

    def test_sketch(self) -> None:
        self._apply(Sketch(blur=3))

    def test_cartoon(self) -> None:
        self._apply(Cartoon(colors=4))

    def test_thermal(self) -> None:
        self._apply(Thermal())

    def test_dither(self) -> None:
        self._apply(Dither())

    def test_scanlines(self) -> None:
        self._apply(Scanlines())

    def test_vortex(self) -> None:
        self._apply(Vortex(strength=2.0))

    def test_neon(self) -> None:
        self._apply(Neon(color="cyan"))

    def test_pixel_sort_horizontal(self) -> None:
        self._apply(PixelSort(direction="horizontal"))

    def test_pixel_sort_vertical(self) -> None:
        self._apply(PixelSort(direction="vertical"))

    def test_effect_chained(self) -> None:
        """Chaining multiple effects."""
        result = Editor(self.img.image)
        result.effect(Grayscale()).effect(Invert()).effect(Blur(amount=1))
        self.assertIsInstance(result, Editor)

    def test_effect_on_black(self) -> None:
        """Test effects on a completely black image."""
        black = Editor(Canvas((32, 32), color="black"))
        black.effect(Glow(radius=5))
        self.assertEqual(black.image.size, (32, 32))

    # --- color variant branches ---

    def test_vignette_rgba_tuple(self) -> None:
        self._apply(Vignette(color=(255, 0, 0, 128)))

    def test_vignette_invalid_tuple(self) -> None:
        self._apply(Vignette(color=(1, 2, 3, 4, 5)))

    def test_vignette_int_color(self) -> None:
        self._apply(Vignette(color=0xFF0000))

    def test_color_overlay_rgba(self) -> None:
        self._apply(ColorOverlay(color=(255, 0, 0, 128), alpha=0.5))

    def test_color_overlay_int(self) -> None:
        self._apply(ColorOverlay(color=0xFF0000, alpha=0.5))

    def test_drop_shadow_int_color(self) -> None:
        self._apply(DropShadow(color=0))

    def test_drop_shadow_rgba(self) -> None:
        self._apply(DropShadow(color=(0, 0, 0, 128)))

    def test_drop_shadow_invalid_tuple(self) -> None:
        self._apply(DropShadow(color=(1, 2, 3, 4, 5)))

    def test_glow_tuple_color(self) -> None:
        self._apply(Glow(color=(0, 255, 255)))

    def test_glow_rgba_color(self) -> None:
        self._apply(Glow(color=(0, 255, 255, 128)))

    def test_glow_invalid_tuple(self) -> None:
        self._apply(Glow(color=(1, 2, 3, 4, 5)))

    def test_glow_int_color(self) -> None:
        self._apply(Glow(color=0x00FFFF))

    def test_gradient_int_colors(self) -> None:
        self._apply(Gradient(colors=[0xFF0000, 0x0000FF]))

    def test_gradient_tuple_colors(self) -> None:
        self._apply(Gradient(colors=[(255, 0, 0), (0, 0, 255)]))

    def test_duotone_string_colors(self) -> None:
        self._apply(Duotone(dark_color="black", light_color="white"))

    def test_duotone_int_colors(self) -> None:
        self._apply(Duotone(dark_color=0x000000, light_color=0xFFFFFF))

    def test_edge_glow_int_color(self) -> None:
        self._apply(EdgeGlow(color=0x00FFFF))

    def test_edge_glow_tuple_color(self) -> None:
        self._apply(EdgeGlow(color=(0, 255, 255)))

    # --- load() returns None defensive branches ---

    def test_ripple_load_none(self) -> None:
        img = Editor(Canvas((64, 64))).image
        with patch.object(PilImage.Image, "load", return_value=None):
            result = Ripple().apply(img)
        self.assertIsInstance(result, PilImage.Image)

    def test_sketch_load_none(self) -> None:
        img = Editor(Canvas((64, 64))).image
        with patch.object(PilImage.Image, "load", return_value=None):
            result = Sketch().apply(img)
        self.assertIsInstance(result, PilImage.Image)

    def test_dither_load_none(self) -> None:
        img = Editor(Canvas((64, 64))).image
        with patch.object(PilImage.Image, "load", return_value=None):
            result = Dither().apply(img)
        self.assertIsInstance(result, PilImage.Image)

    def test_vortex_load_none(self) -> None:
        img = Editor(Canvas((64, 64))).image
        with patch.object(PilImage.Image, "load", return_value=None):
            result = Vortex().apply(img)
        self.assertIsInstance(result, PilImage.Image)

    def test_pixel_sort_load_none(self) -> None:
        img = Editor(Canvas((64, 64))).image
        with patch.object(PilImage.Image, "load", return_value=None):
            result = PixelSort().apply(img)
        self.assertIsInstance(result, PilImage.Image)

    def test_vortex_high_strength(self) -> None:
        """Vortex pushes pixels out of bounds (line 1185)."""
        img = Editor(Canvas((16, 16))).image
        result = Vortex(strength=8.0, radius=100).apply(img)
        self.assertIsInstance(result, PilImage.Image)

    def test_ripple_second_load_none(self) -> None:
        """Ripple: out.load() returns None (line 771)."""
        img = Editor(Canvas((64, 64))).image
        calls: list[int] = []
        orig = PilImage.Image.load

        def _load(self_obj: object) -> object:
            calls.append(1)
            if len(calls) == 1:
                return orig(self_obj)
            return None

        with patch.object(PilImage.Image, "load", _load):
            result = Ripple().apply(img)
        self.assertIsInstance(result, PilImage.Image)

    def test_sketch_second_load_none(self) -> None:
        """Sketch: o_p.load() returns None (line 996)."""
        img = Editor(Canvas((64, 64))).image
        calls: list[int] = []
        orig = PilImage.Image.load

        def _load(self_obj: object) -> object:
            calls.append(1)
            if len(calls) <= 2:
                return orig(self_obj)
            return None

        with patch.object(PilImage.Image, "load", _load):
            result = Sketch().apply(img)
        self.assertIsInstance(result, PilImage.Image)

    def test_dither_second_load_none(self) -> None:
        """Dither: op.load() returns None (line 1107)."""
        img = Editor(Canvas((64, 64))).image
        calls: list[int] = []
        orig = PilImage.Image.load

        def _load(self_obj: object) -> object:
            calls.append(1)
            if len(calls) == 1:
                return orig(self_obj)
            return None

        with patch.object(PilImage.Image, "load", _load):
            result = Dither().apply(img)
        self.assertIsInstance(result, PilImage.Image)

    def test_vortex_second_load_none(self) -> None:
        """Vortex: op.load() returns None (line 1172)."""
        img = Editor(Canvas((64, 64))).image
        calls: list[int] = []
        orig = PilImage.Image.load

        def _load(self_obj: object) -> object:
            calls.append(1)
            if len(calls) == 1:
                return orig(self_obj)
            return None

        with patch.object(PilImage.Image, "load", _load):
            result = Vortex().apply(img)
        self.assertIsInstance(result, PilImage.Image)


if __name__ == "__main__":
    unittest.main()
