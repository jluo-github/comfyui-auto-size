"""
ComfyUI node class definitions for the Auto Size plugin.

This implementation is pure Python and has no JavaScript dependency.
"""

from __future__ import annotations


import torch

try:
    from ..utils.presets import (
        CROP_METHODS,
        MODEL_LIST,
        RATIO_LIST,
        SCALE_METHODS,
        SIZE_LIST,
        DEFAULT_MODEL,
        resolve_resolution,
    )
    from ..utils.resize import resize_image, resize_mask
except ImportError:
    # Fallback for when running directly or in compatible envs
    from utils.presets import (
        CROP_METHODS,
        MODEL_LIST,
        RATIO_LIST,
        SCALE_METHODS,
        SIZE_LIST,
        DEFAULT_MODEL,
        resolve_resolution,
    )
    from utils.resize import resize_image, resize_mask


class AutoSize:
    """
    ComfyUI node that resizes an optional image and mask to a model‑aligned resolution.
    """

    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, tuple]]:
        return {
            "required": {
                "model": (MODEL_LIST, {"default": DEFAULT_MODEL}),
                # Pure Python list – updates in presets.py will appear immediately.
                "size": (SIZE_LIST, {"default": SIZE_LIST[0]}),
                "custom_longer_size": (
                    "INT",
                    {"default": 0, "min": 0, "max": 8192, "step": 16},
                ),
                "custom_ratio": (RATIO_LIST, {"default": "1:1"}),
                "crop_method": (CROP_METHODS, {"default": "Center Crop"}),
                "scale_method": (SCALE_METHODS, {"default": "lanczos"}),
            },
            "optional": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT", "STRING")
    RETURN_NAMES = ("image", "mask", "width", "height", "size")
    FUNCTION = "process"
    CATEGORY = "image/AutoSize"
    OUTPUT_NODE = True

    def process(
        self,
        model: str,
        size: str,
        custom_longer_size: int,
        custom_ratio: str,
        crop_method: str,
        scale_method: str,
        image: torch.Tensor | None = None,
        mask: torch.Tensor | None = None,
    ) -> dict[str, object]:
        """
        Process the image and mask resizing.

        Args:
            model: The target model architecture (affects resizing multiples).
            size: The target resolution string (e.g. "1024x1024").
            custom_longer_size: The longer side size for custom resolution.
            custom_ratio: The aspect ratio for custom resolution.
            crop_method: The method to use for cropping (e.g. "Center Crop").
            scale_method: The interpolation method (e.g. "lanczos").
            image: Optional input image tensor in [B, H, W, C] format.
            mask: Optional input mask tensor in [B, H, W] format.

        Returns:
            Mapping containing ComfyUI UI feedback and result tuple:
            (output_image, output_mask, width, height, size_string).
        """

        target_width, target_height = resolve_resolution(
            size, custom_longer_size, custom_ratio, model
        )

        # Resolution string
        res_string = f"{target_width}x{target_height}"

        # Process image
        if image is not None:
            output_image = resize_image(
                image, target_width, target_height, crop_method, scale_method
            )
        else:
            output_image = torch.zeros((1, target_height, target_width, 3))

        # Process mask
        if mask is not None:
            output_mask = resize_mask(
                mask, target_width, target_height, crop_method, scale_method
            )
        else:
            output_mask = torch.zeros((1, target_height, target_width))

        # RETURN DICTIONARY for UI feedback
        # The "ui" key tells ComfyUI to show this text in the interface history
        return {
            "ui": {"text": [res_string]},
            "result": (
                output_image,
                output_mask,
                target_width,
                target_height,
                res_string,
            ),
        }
