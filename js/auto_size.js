import { app } from "../../scripts/app.js";

const PREFIX_MAP = {
	"qwen-image": "Qwen",
	"illustrious": "Illustrious",
	"z-image": "Z-Image",
	"flux": "Flux",
};

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
					const model = modelWidget.value ? modelWidget.value.trim() : "";
					const prefix = PREFIX_MAP[model];

					let filteredSizes = originalSizeOptions.filter((option) => {
						// Always keep "Full Custom" and "Fav"
						if (option.startsWith("Full Custom") || option.startsWith("Fav")) {
							return true;
						}

						if (prefix) {
							return option.startsWith(prefix);
						}

						// If no valid prefix found (unknown model), default to showing everything
						// or maybe just "Full Custom" + "Fav"?
						// Current behavior: Show everything if no match found (safest fallthrough)
						return true;
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

				// Hook into configure() — fires AFTER saved widget values are restored
				const originalConfigure = node.configure;
				node.configure = function (info) {
					if (originalConfigure) {
						originalConfigure.apply(this, arguments);
					}
					// Values are now restored from the saved workflow, re-sync dropdown
					updateSizeOptions();
				};

				// Initial update + deferred safety net for edge cases
				updateSizeOptions();
				requestAnimationFrame(() => updateSizeOptions());
			}
		}
	},
});
