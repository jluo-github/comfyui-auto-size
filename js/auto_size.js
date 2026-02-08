import { app } from "../../scripts/app.js";

app.registerExtension({
	name: "ComfyUI.AutoSizeLatent",
	async nodeCreated(node, app) {
		if (node.comfyClass === "AutoSizeLatent" || node.comfyClass === "AutoSize") {
			const modelWidget = node.widgets.find((w) => w.name === "model");
			const sizeWidget = node.widgets.find((w) => w.name === "size");

			if (modelWidget && sizeWidget) {
				// Store original options
				const originalSizeOptions = [...sizeWidget.options.values];

				const updateSizeOptions = () => {
					const model = modelWidget.value;
					let filteredSizes = originalSizeOptions.filter((option) => {
						// Always keep "Full Custom" and "Fav"
						if (option.startsWith("Full Custom") || option.startsWith("Fav")) {
							return true;
						}
						// Map model values to prefix matching
						// Model values: "qwen-image", "flux", "z-image", "illustrious"
						// Preset prefixes: "Qwen", "Flux", "Z-Image", "Illustrious"
						let prefix = "";
						if (model === "qwen-image") prefix = "Qwen";
						else if (model === "z-image") prefix = "Z-Image";
						else if (model === "flux") prefix = "Flux";
						else if (model === "illustrious") prefix = "Illustrious";

						return option.startsWith(prefix);
					});

					// Update the widget options
					sizeWidget.options.values = filteredSizes;

					// If current value is invalid, reset to first available
					if (!filteredSizes.includes(sizeWidget.value)) {
						sizeWidget.value = filteredSizes[0];
					}
				};

				// Add callback to model widget
				const originalCallback = modelWidget.callback;
				modelWidget.callback = function () {
					updateSizeOptions();
					if (originalCallback) {
						originalCallback.apply(this, arguments);
					}
				};

				// Initial update
				updateSizeOptions();
			}
		}
	},
});
