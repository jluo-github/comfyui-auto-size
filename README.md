# ComfyUI Auto Size Plugin

[![GitHub](https://img.shields.io/github/license/jluo-github/comfyui-auto-size)](LICENSE)
[![GitHub](https://img.shields.io/github/stars/jluo-github/comfyui-auto-size)](https://github.com/jluo-github/comfyui-auto-size)

A powerful ComfyUI extension for handling image resolutions. It provides smart, model-aware resolution presets and robust resizing tools, designed for "engineering-grade" automation.

## 🌟 Features

*   **Dynamic Dropdowns**: The `size` dropdown smartly filters to show only relevant presets for your selected `model` (e.g., selecting "Flux" hides "Qwen" sizes).
*   **Model-Aware Resolution**: Automatically snaps resolutions to specific multiples required by different architectures:
    *   **Flux / Z-Image / Illustrious**: Multiples of 32
    *   **Qwen-Image**: Multiples of 28
*   **Smart Custom Logic**: Seamlessly switch between presets and custom sizes without fighting the UI.
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
    *   `custom_longer_size`: Target pixel size for the longer side. **Set to 0 to use the `size` dropdown.**
    *   `custom_ratio`: Target aspect ratio (used only when `custom_longer_size > 0`).
    *   `batch_size`: Number of latents to generate.
*   **Outputs**: `latent`, `width`, `height`, `size` (string).

### 2. Auto Size (Image/Mask)
**Category**: `image/AutoSize`

Resizes an existing image and/or mask to target dimensions. Perfect for image-to-image workflows.

*   **Inputs**: Same as above, plus:
    *   `crop_method`: Strategy if aspect ratios don't match (Crop vs Fit vs Stretch).
    *   `scale_method`: Interpolation (Lanczos, Bicubic, Nearest, etc.).
    *   `image` (Optional): Input image to resize.
    *   `mask` (Optional): Input mask to resize.
*   **Outputs**: Resized `image`, resized `mask`, and dimension info.

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
    *   *Note: If the dynamic dropdowns don't appear immediately, try reloading the browser page.*

## ⚙️ How It Works (The Logic)

The nodes use a **Priority System** to determine the final resolution:

1.  **Custom Override (`custom_longer_size > 0`)**:
    *   If you set `custom_longer_size` to any value greater than 0, the node **ignores the Size dropdown**.
    *   It calculates the resolution using `custom_longer_size` + `custom_ratio`.
    *   It strictly aligns the result to the selected `model`'s required multiple (e.g., rounding to nearest 32px or 28px).

2.  **Preset Mode (`custom_longer_size = 0`)**:
    *   If `custom_longer_size` is 0 (default), the node uses the resolution from the **Size** dropdown (e.g., `Flux - 16:9`).

## 💻 Development

The project is structured for maintainability and pure Python logic where possible.

*   `nodes/`: ComfyUI node definitions.
*   `utils/`: Core logic (presets, math, resizing) decoupled from ComfyUI.
*   `js/`: Frontend extensions for dynamic UI behavior.

### Running Tests
To verify the math and resize logic:
```bash
python -m unittest discover -s tests
```

## License

[MIT License](LICENSE)

---

Made with ❤️ for the ComfyUI community