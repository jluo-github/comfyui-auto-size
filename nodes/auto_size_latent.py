"""
ComfyUI node class definitions for the Auto Size plugin.

This implementation is pure Python and has no JavaScript dependency.
"""

from __future__ import annotations

from typing import Dict, Mapping, MutableMapping

import torch

try:
    from ..utils.presets import (
        MODEL_LIST,
        RATIO_LIST,
        SIZE_LIST,
        DEFAULT_MODEL,
        resolve_resolution,
    )
except ImportError:
    from utils.presets import (
        MODEL_LIST,
        RATIO_LIST,
        SIZE_LIST,
        DEFAULT_MODEL,
        resolve_resolution,
    )


# ============================================================================
# Node 2: AutoSizeLatent
# ============================================================================


class AutoSizeLatent:
    """
    ComfyUI node that produces an empty latent tensor at a model‑aligned resolution.
    """

    def __init__(self) -> None:
        return

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Mapping[str, tuple]]:
        return {
            "required": {
                "model": (MODEL_LIST, {"default": DEFAULT_MODEL}),
                "size": (SIZE_LIST, {"default": SIZE_LIST[0]}),
                "custom_longer_size": (
                    "INT",
                    {"default": 1024, "min": 256, "max": 8192, "step": 16},
                ),
                "custom_ratio": (RATIO_LIST, {"default": "1:1"}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096}),
            }
        }

    RETURN_TYPES = ("LATENT", "INT", "INT", "STRING")
    RETURN_NAMES = ("latent", "width", "height", "size")
    FUNCTION = "generate"
    CATEGORY = "latent/AutoSize"
    OUTPUT_NODE = True

    def generate(
        self,
        model: str,
        size: str,
        custom_longer_size: int,
        custom_ratio: str,
        batch_size: int = 1,
    ) -> MutableMapping[str, object]:
        """
        Generate an empty latent tensor for downstream processing.

        Args:
            model: The target model architecture.
            size: The target resolution string.
            custom_longer_size: The longer side size for custom resolution.
            custom_ratio: The aspect ratio for custom resolution.
            batch_size: The number of latents to generate.

        Returns:
            Mapping containing ComfyUI UI feedback and result tuple:
            ({"samples": latent}, width, height, size_string).
        """

        target_width, target_height = resolve_resolution(
            size, custom_longer_size, custom_ratio, model
        )

        res_string = f"{target_width}x{target_height}"

        # Latent space is 1/8 of pixel dimensions
        latent_width = target_width // 8
        latent_height = target_height // 8

        latent = torch.zeros([batch_size, 4, latent_height, latent_width])

        return {
            "ui": {"text": [res_string]},
            "result": ({"samples": latent}, target_width, target_height, res_string),
        }
