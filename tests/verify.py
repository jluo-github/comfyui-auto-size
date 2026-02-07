import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.presets import resolve_resolution


def test_resolve():
    print("Testing resolve_resolution...")

    # Case 1: Standard Preset
    w, h = resolve_resolution("Qwen - 1:1 (1328x1328)", 0, "1:1", "qwen-image")
    print(f"Case 1 (Preset 1328x1328): {w}x{h}")
    assert w == 1328 and h == 1328

    # Case 2: Custom Override (Qwen uses 28)
    w, h = resolve_resolution("Qwen - 1:1 (1328x1328)", 1200, "1:1", "qwen-image")
    # 1200 / 28 = 42.85 -> 43 * 28 = 1204
    print(f"Case 2 (Custom 1200, 1:1): {w}x{h}")
    assert w == 1204 and h == 1204

    # Case 3: Custom Ratio
    w, h = resolve_resolution("Qwen - 1:1 (1328x1328)", 1000, "16:9", "qwen-image")
    # 16:9 -> w=1000, h=562.5
    # 1000/28 = 35.7 -> 36 * 28 = 1008
    # 562.5/28 = 20.08 -> 20 * 28 = 560
    print(f"Case 3 (Custom 1000, 16:9): {w}x{h}")
    assert w == 1008 and h == 560

    # Case 4: Zero Custom Size (Should use Preset)
    w, h = resolve_resolution("Qwen - 1:1 (1328x1328)", 0, "16:9", "qwen-image")
    print(f"Case 4 (Custom 0 -> Preset 1328x1328): {w}x{h}")
    assert w == 1328 and h == 1328

    print("All tests passed!")


if __name__ == "__main__":
    test_resolve()
