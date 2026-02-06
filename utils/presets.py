"""
Size preset definitions and calculation logic for the ComfyUI Auto Size plugin.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

# ============================================================================
# Model Specifications
# ============================================================================

MODEL_SPECS: Dict[str, int] = {
    "qwen-image": 28,
    "illustrious": 32,
    "z-image": 32,
    "flux": 32,
}

DEFAULT_MODEL: str = "qwen-image"

# ============================================================================
# Fixed Size Presets
# ============================================================================

QWEN_SIZES: Dict[str, Tuple[int, int]] = {
    "1:1": (1328, 1328),
    "9:16": (928, 1664),
    "16:9": (1664, 928),
    "3:4": (1104, 1472),
    "4:3": (1472, 1104),
    "2:3": (1056, 1584),
    "3:2": (1584, 1056),
}

ILLUSTRIOUS_SIZES: Dict[str, Tuple[int, int]] = {
    "1:1": (1024, 1024),
    "9:16": (768, 1344),
    "16:9": (1344, 768),
    "13:19": (832, 1216),  # Inferred aspect based on resolution
    "19:13": (1216, 832),
    "9:7": (1152, 896),  # Matches Flux/SDXL approx
    "7:9": (896, 1152),
    "12:5": (1536, 640),
    "5:12": (640, 1536),
    "2:3": (1024, 1536),
}

Z_IMAGE_SIZES: Dict[str, Tuple[int, int]] = {
    "1:1": (1280, 1280),
    "16:9": (1600, 896),
    "9:16": (896, 1600),
    "9:7": (1440, 1120),
    "7:9": (1120, 1440),
    "4:3": (1472, 1104),
    "3:4": (1104, 1472),
    "3:2": (1536, 1024),
    "2:3": (1024, 1536),
    "21:9": (1680, 720),
    "9:21": (720, 1680),
}

FLUX_SIZES: Dict[str, Tuple[int, int]] = {
    "1:1": (1024, 1024),
    "16:9": (1280, 720),
    "9:16": (720, 1280),
    "9:7": (1152, 896),
    "7:9": (896, 1152),
    "4:3": (1152, 864),
    "3:4": (864, 1152),
    "3:2": (1248, 832),
    "2:3": (832, 1248),
    "21:9": (1344, 576),
    "9:21": (576, 1344),
}


FAV_SIZES: Dict[str, Tuple[int, int]] = {
    "1:1": (1536, 1536),
    "9:7ish": (1728, 1344),
    "7:9ish": (1344, 1728),
    "3:2ish": (1824, 1248),
    "2:3ish": (1248, 1824),
    "16:9ish": (2016, 1152),
    "9:16ish": (1152, 2016),
}

# Combine for dropdown (labelled with size)
SIZE_LIST: List[str] = ["Full Custom (Use Inputs Below)"]


def add_to_list(prefix: str, sizes: Dict[str, Tuple[int, int]]) -> None:
    """
    Populate the `SIZE_LIST` with human‑readable entries for a given size map.
    """
    for ratio_label, (width, height) in sizes.items():
        SIZE_LIST.append(f"{prefix} - {ratio_label} ({width}x{height})")


add_to_list("Qwen", QWEN_SIZES)
add_to_list("Z-Image", Z_IMAGE_SIZES)
add_to_list("Flux", FLUX_SIZES)
add_to_list("Illustrious", ILLUSTRIOUS_SIZES)
add_to_list("Fav", FAV_SIZES)


# ============================================================================
# Ratios
# ============================================================================

RATIOS: Dict[str, float] = {
    "1:1": 1.0,
    "9:16": 9 / 16,
    "16:9": 16 / 9,
    "4:5": 4 / 5,
    "5:4": 5 / 4,
    "3:4": 3 / 4,
    "4:3": 4 / 3,
    "2:3": 2 / 3,
    "3:2": 3 / 2,
    "5:7": 5 / 7,
    "7:5": 7 / 5,
    "9:21": 9 / 21,
    "21:9": 21 / 9,
    "1:2": 1 / 2,
    "2:1": 2 / 1,
}

# ============================================================================
# Lists for UI
# ============================================================================

MODEL_LIST: List[str] = list(MODEL_SPECS.keys())
RATIO_LIST: List[str] = [
    "1:1",
    "1:2",
    "2:1",
    "2:3",
    "3:2",
    "3:4",
    "4:3",
    "4:5",
    "5:4",
    "5:7",
    "7:5",
    "9:16",
    "16:9",
    "9:21",
    "21:9",
]

# ============================================================================
# Method Constants
# ============================================================================

CROP_METHODS: List[str] = [
    "Center Crop",
    "Top-Left Crop",
    "Bottom-Right Crop",
    "Scale to Fit",
    "Stretch to Fill",
]

SCALE_METHODS: List[str] = ["lanczos", "bilinear", "bicubic", "nearest"]

INTERPOLATION_MODES: Dict[str, str] = {
    "lanczos": "bicubic",
    "bilinear": "bilinear",
    "bicubic": "bicubic",
    "nearest": "nearest",
}

# ============================================================================
# Calculation Logic
# ============================================================================


def resolve_resolution(
    size_selection: str,
    longer_side: int,
    custom_ratio: str,
    model: str,
) -> Tuple[int, int]:
    """
    Resolve final resolution based on priority:

    1. Size selection (if not "Full Custom")
    2. Custom calculation (longer side + ratio)

    Args:
        size_selection: The selected size string from defaults.
        longer_side: The manual long side size.
        custom_ratio: The manual aspect ratio.
        model: The selected model (for strict alignment).

    Returns:
        (width, height) in pixels, snapped to the model's required multiple.
    """

    # 1. Fixed "Size" selection
    if size_selection and "Full Custom" not in size_selection:
        # data format example: "Qwen - 1:1 (1328x1328)"
        try:
            # Extract "1328x1328" from inside parens
            dim_part = size_selection.rsplit("(", 1)[-1].strip(")")
            w_str, h_str = dim_part.split("x")
            return int(w_str), int(h_str)
        except (ValueError, IndexError):
            # Fallback to default if parsing fails
            return 1024, 1024

    # 2. Custom calculation
    target_ratio = RATIOS.get(custom_ratio, 1.0)
    multiple = MODEL_SPECS.get(model, 32)

    if target_ratio > 1.0:
        width = float(longer_side)
        height = width / target_ratio
    elif target_ratio < 1.0:
        height = float(longer_side)
        width = height * target_ratio
    else:
        width = float(longer_side)
        height = float(longer_side)

    final_width = round(width / multiple) * multiple
    final_height = round(height / multiple) * multiple

    final_width = max(final_width, multiple)
    final_height = max(final_height, multiple)

    return int(final_width), int(final_height)
