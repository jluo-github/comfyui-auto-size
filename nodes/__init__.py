from __future__ import annotations

from .auto_size import AutoSize
from .auto_size_latent import AutoSizeLatent

NODE_CLASS_MAPPINGS = {
    "AutoSize": AutoSize,
    "AutoSizeLatent": AutoSizeLatent,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AutoSize": "📐 Auto Size",
    "AutoSizeLatent": "📐 Auto Size Latent",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
