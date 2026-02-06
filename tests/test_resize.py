import unittest
import torch
from utils.resize import resize_image, resize_mask


class TestResize(unittest.TestCase):

    def setUp(self):
        # Create a simple 100x100 red image
        self.image = torch.zeros((1, 100, 100, 3))
        self.image[:, :, :, 0] = 1.0  # Red

        # Create a 100x100 mask
        self.mask = torch.zeros((1, 100, 100))

    def test_resize_image_stretch(self):
        # 100x100 -> 200x50
        resized = resize_image(self.image, 200, 50, "Stretch to Fill", "nearest")
        self.assertEqual(resized.shape, (1, 50, 200, 3))

    def test_resize_image_crop(self):
        # 100x100 -> 50x50 center crop
        resized = resize_image(self.image, 50, 50, "Center Crop", "nearest")
        self.assertEqual(resized.shape, (1, 50, 50, 3))

    def test_resize_image_fit(self):
        # 100x100 -> 200x200 fit (should just scale up)
        resized = resize_image(self.image, 200, 200, "Scale to Fit", "nearest")
        self.assertEqual(resized.shape, (1, 200, 200, 3))

    def test_resize_image_fit_letterbox(self):
        # 100x100 input -> fit into 200x100 target
        # Should scale to 100x100 (fit height), then pad width?
        # Wait, 100x100 source fitting into 200x100 target.
        # Scale factor: min(200/100, 100/100) = 1.0.
        # New dims: 100x100.
        # Pad: (200-100)/2 = 50 pixels left/right.
        resized = resize_image(self.image, 200, 100, "Scale to Fit", "nearest")
        self.assertEqual(resized.shape, (1, 100, 200, 3))

        # Check center is red (the image)
        self.assertEqual(resized[0, 50, 100, 0], 1.0)
        # Check padding is black
        self.assertEqual(resized[0, 50, 10, 0], 0.0)

    def test_resize_mask(self):
        resized = resize_mask(self.mask, 200, 50, "Stretch to Fill", "nearest")
        self.assertEqual(resized.shape, (1, 50, 200))


if __name__ == "__main__":
    unittest.main()
