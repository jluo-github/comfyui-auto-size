import unittest
from utils.presets import resolve_resolution


class TestPresets(unittest.TestCase):

    def test_preset_parsing(self):
        # "Qwen - 1:1 (1024x1024)"
        w, h = resolve_resolution("Qwen - 1:1 (1024x1024)", 0, "1:1", "qwen-image")
        self.assertEqual(w, 1024)
        self.assertEqual(h, 1024)

    def test_custom_calc_1_to_1(self):
        # 1024, 1:1 -> 1024x1024 (multiple 32)
        w, h = resolve_resolution("Full Custom", 1024, "1:1", "flux")
        self.assertEqual(w, 1024)
        self.assertEqual(h, 1024)

    def test_custom_calc_16_to_9(self):
        # 1024 longer side, 16:9 ratio
        # w=1024, h=1024/(16/9) = 576
        w, h = resolve_resolution("Full Custom", 1024, "16:9", "flux")
        self.assertEqual(w, 1024)
        self.assertEqual(h, 576)

    def test_resolution_rounding_flux(self):
        # Flux needs multiple of 32
        # 1000 -> rounds to 992 or 1024. 1000/32 = 31.25 -> 31*32=992
        w, h = resolve_resolution("Full Custom", 1000, "1:1", "flux")
        self.assertEqual(w, 992)
        self.assertEqual(h, 992)

    def test_resolution_rounding_qwen(self):
        # Qwen needs multiple of 28
        # 1000/28 = 35.71 -> 36*28 = 1008
        w, h = resolve_resolution("Full Custom", 1000, "1:1", "qwen-image")
        self.assertEqual(w, 1008)
        self.assertEqual(h, 1008)


if __name__ == "__main__":
    unittest.main()
