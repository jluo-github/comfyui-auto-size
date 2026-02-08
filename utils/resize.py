"""
Image and mask resize utilities for the ComfyUI Auto Size plugin.

Provides unified resize logic with support for various crop and scale methods.
"""

from __future__ import annotations


import torch
import torch.nn.functional as F

try:
    from .presets import INTERPOLATION_MODES
except ImportError:
    from utils.presets import INTERPOLATION_MODES

# ============================================================================
# Core Resize Logic
# ============================================================================


def _calculate_scaled_dimensions(
    src_w: int, src_h: int, target_w: int, target_h: int, cover: bool
) -> tuple[int, int]:
    """
    Calculate new dimensions for scaling.

    Args:
        src_w: Source width.
        src_h: Source height.
        target_w: Target width.
        target_h: Target height.
        cover: If True, scale to cover target (for cropping);
            if False, scale to fit within target (for letterboxing).

    Returns:
        (new_width, new_height) for the scaled image.
    """
    src_ratio = src_w / src_h
    tgt_ratio = target_w / target_h

    # For cover: use the dimension that gives larger result (to ensure full coverage)
    # For fit: use the dimension that gives smaller result (to ensure it fits inside)
    use_width_as_ref = (src_ratio > tgt_ratio) != cover

    if use_width_as_ref:
        new_w = target_w
        new_h = int(target_w / src_ratio)
    else:
        new_h = target_h
        new_w = int(target_h * src_ratio)

    return new_w, new_h


def _get_crop_offset(
    crop_method: str, new_w: int, new_h: int, target_w: int, target_h: int
) -> tuple[int, int]:
    """
    Calculate crop offset based on crop method.

    Args:
        crop_method: One of "Center Crop", "Top-Left Crop", "Bottom-Right Crop".
        new_w: Scaled width before cropping.
        new_h: Scaled height before cropping.
        target_w: Target width.
        target_h: Target height.

    Returns:
        (top, left) offset for cropping.
    """
    if crop_method == "Top-Left Crop":
        return 0, 0
    if crop_method == "Bottom-Right Crop":
        return new_h - target_h, new_w - target_w

    # Center crop (default)
    return (new_h - target_h) // 2, (new_w - target_w) // 2


def _resize_tensor(
    tensor: torch.Tensor,
    target_width: int,
    target_height: int,
    crop_method: str,
    scale_method: str,
) -> torch.Tensor:
    """
    Core resize function for tensors in [B, C, H, W] format.

    Args:
        tensor: Input tensor in [B, C, H, W] format.
        target_width: Target width in pixels.
        target_height: Target height in pixels.
        crop_method: Resize strategy (crop, fit, or stretch).
        scale_method: Interpolation method name.

    Returns:
        Resized tensor in [B, C, H, W] format.
    """
    batch, channels, src_h, src_w = tensor.shape

    # Get interpolation mode
    mode = INTERPOLATION_MODES.get(scale_method, "bicubic")
    align_corners = None if mode == "nearest" else False

    if crop_method == "Stretch to Fill":
        # Direct resize to target dimensions
        return F.interpolate(
            tensor,
            size=(target_height, target_width),
            mode=mode,
            align_corners=align_corners,
        )

    if crop_method == "Scale to Fit":
        # Scale proportionally, pad with black (letterbox)
        new_w, new_h = _calculate_scaled_dimensions(
            src_w, src_h, target_width, target_height, cover=False
        )

        resized = F.interpolate(
            tensor,
            size=(new_h, new_w),
            mode=mode,
            align_corners=align_corners,
        )

        # Create black canvas and center the image
        result = torch.zeros(
            (batch, channels, target_height, target_width),
            dtype=tensor.dtype,
            device=tensor.device,
        )
        pad_top = (target_height - new_h) // 2
        pad_left = (target_width - new_w) // 2
        result[:, :, pad_top : pad_top + new_h, pad_left : pad_left + new_w] = resized
        return result

    # Crop modes: scale to cover, then crop
    new_w, new_h = _calculate_scaled_dimensions(
        src_w, src_h, target_width, target_height, cover=True
    )

    resized = F.interpolate(
        tensor,
        size=(new_h, new_w),
        mode=mode,
        align_corners=align_corners,
    )

    # Crop to target size
    top, left = _get_crop_offset(crop_method, new_w, new_h, target_width, target_height)
    return resized[:, :, top : top + target_height, left : left + target_width]


# ============================================================================
# Public API
# ============================================================================


def resize_image(
    image_tensor: torch.Tensor,
    target_width: int,
    target_height: int,
    crop_method: str,
    scale_method: str,
) -> torch.Tensor:
    """
    Resize an image tensor.

    Args:
        image_tensor: Input tensor in [B, H, W, C] format.
        target_width: Target width in pixels.
        target_height: Target height in pixels.
        crop_method: Resize strategy.
        scale_method: Interpolation method.

    Returns:
        Resized tensor in [B, H, W, C] format.
    """
    # Convert [B, H, W, C] -> [B, C, H, W]
    img = image_tensor.permute(0, 3, 1, 2)
    resized = _resize_tensor(
        img,
        target_width,
        target_height,
        crop_method,
        scale_method,
    )
    # Convert back [B, C, H, W] -> [B, H, W, C]
    return resized.permute(0, 2, 3, 1)


def resize_mask(
    mask_tensor: torch.Tensor,
    target_width: int,
    target_height: int,
    crop_method: str,
    scale_method: str,
) -> torch.Tensor:
    """
    Resize a mask tensor.

    Args:
        mask_tensor: Input tensor in [B, H, W] format.
        target_width: Target width in pixels.
        target_height: Target height in pixels.
        crop_method: Resize strategy.
        scale_method: Interpolation method.

    Returns:
        Resized tensor in [B, H, W] format.
    """
    # Add channel dimension [B, H, W] -> [B, 1, H, W]
    mask = mask_tensor.unsqueeze(1)
    resized = _resize_tensor(
        mask,
        target_width,
        target_height,
        crop_method,
        scale_method,
    )
    # Remove channel dimension [B, 1, H, W] -> [B, H, W]
    return resized.squeeze(1)
