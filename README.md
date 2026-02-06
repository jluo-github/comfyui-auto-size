# ComfyUI Auto Size Plugin

A **Pure Python** suite of nodes for ComfyUI that automates resolution handling. It allows you to "set and forget" your image dimensions, ensuring they are always aligned with your target model's requirements (e.g., multiples of 32 for Flux, 28 for Qwen, etc.).

[![GitHub](https://img.shields.io/github/license/jluo-github/comfyui-auto-size)](LICENSE)
[![GitHub](https://img.shields.io/github/stars/jluo-github/comfyui-auto-size)](https://github.com/jluo-github/comfyui-auto-size)

## 🌟 Features

*   **Model-Aware Resolution**: Automatically snaps resolutions to specific multiples required by different architectures:
    *   **Flux / Z-Image / Illustrious**: Multiples of 32
    *   **Qwen-Image**: Multiples of 28
*   **Smart Presets**: Curated lists of popular aspect ratios (`1:1`, `16:9`, `21:9`) and "Favourite" sizes.
*   **Pure Python**: Zero JavaScript distractions. No browser caching issues, no complex build steps.
*   **Robust Resizing**: Includes an advanced `AutoSize` node for images/masks with multiple modes:
    *   `Center Crop` / `Edge Crop`
    *   `Scale to Fit` (Letterboxing)
    *   `Stretch to Fill`

## 📦 Provided Nodes

### 1. Auto Size Latent
**Category**: `latent/AutoSize`

Generates an empty latent tensor for starting a workflow.

*   **Inputs**:
    *   `model`: Select standard (Flux, Qwen, etc.) or specific architectures.
    *   `size`: Choose a preset (e.g., `Flux - 16:9`) or `Full Custom`.
    *   `custom_longer_size`: (Only used in Full Custom) Target pixel size for the longer side.
    *   `custom_ratio`: (Only used in Full Custom) Target aspect ratio.
    *   `batch_size`: Number of latents to generate.
*   **Outputs**:
    *   `latent`: The requested empty latent.
    *   `width`: Final pixel width.
    *   `height`: Final pixel height.
    *   `size`: String representation (e.g., `"1024x1024"`).

### 2. Auto Size (Image/Mask)
**Category**: `image/AutoSize`

Resizes an existing image and/or mask to target dimensions. Perfect for image-to-image workflows.

*   **Inputs**: Same as above, plus:
    *   `crop_method`: Strategy if aspect ratios don't match (Crop vs Fit vs Stretch).
    *   `scale_method`: Interpolation (Lanczos, Bicubic, Nearest, etc.).
    *   `image` (Optional): Input image to resize.
    *   `mask` (Optional): Input mask to resize.
*   **Outputs**: Resized image, resized mask, and dimension info.

## 🛠️ Installation

1.  Navigate to your ComfyUI custom nodes directory:
    ```bash
    cd ComfyUI/custom_nodes
    ```
2.  Clone this repository:
    ```bash
    git clone https://github.com/jluo-github/comfyui-auto-size.git
    ```
3.  Restart ComfyUI.

## ⚙️ How It Works (The Logic)

The node follows a strict priority system to determine resolution:

1.  **Preset Mode**: If you select a preset in the `size` dropdown (e.g., `Flux - 16:9`), the node **strictly uses that preset's resolution**.
    *   *The `custom_longer_size` and `custom_ratio` widgets are IGNORED in this mode.*
2.  **Custom Mode**: If you select `Full Custom (Use Inputs Below)`, the node calculates resolution based on your manual inputs:
    *   It takes your `custom_longer_size`.
    *   It applies the `custom_ratio`.
    *   It aligns the result to the `model`'s required multiple (e.g. rounding to the nearest 32 pixels).


## 💻 Development

The project is structured for maintainability:

*   `nodes/`: Contains the ComfyUI node class definitions.
    *   `auto_size.py`: Image resizing node.
    *   `auto_size_latent.py`: Latent generation node.
*   `utils/`: Core logic decoupled from ComfyUI.
    *   `presets.py`: Resolution dictionaries and calculation math.
    *   `resize.py`: PyTorch tensor resizing and cropping logic.

### Running Tests
To verify the math and resize logic:
```bash
python -m unittest discover -s tests
```

## License

[MIT License](LICENSE)

---

Made with ❤️ for the ComfyUI community