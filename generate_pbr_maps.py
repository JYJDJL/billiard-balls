"""
Generate PBR texture maps for all 16 billiard balls:
- Roughness map: subtle variations (body 0.15, circle 0.10, number 0.25)
- Normal map: embossed numbers and circle edges (tangent-space)

Dependencies: pip install Pillow numpy
"""
from PIL import Image, ImageFilter
import numpy as np
import os
import math

W, H = 1024, 512
tex_dir = os.path.dirname(os.path.abspath(__file__))

ROUGHNESS_BODY   = int(0.15 * 255)   # 38
ROUGHNESS_CIRCLE = int(0.10 * 255)   # 25
ROUGHNESS_NUMBER = int(0.22 * 255)   # 56

HEIGHT_BODY   = 0.0
HEIGHT_CIRCLE = 0.012
HEIGHT_NUMBER = 0.030
BEVEL_SIGMA = 3.0
NORMAL_STRENGTH = 2.5
RADIUS_PX = 58


def gaussian_blur(arr, sigma):
    img = Image.fromarray((arr * 255).clip(0, 255).astype(np.uint8), mode='L')
    img = img.filter(ImageFilter.GaussianBlur(radius=sigma))
    return np.array(img).astype(np.float32) / 255.0


def get_masks(rgb):
    """Detect circle and number regions.
    Number detection is constrained to within circle areas to handle black balls.
    """
    if rgb.shape[2] == 4:
        rgb = rgb[:, :, :3]

    # White circle: high luminance
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    circle_mask = (lum > 0.75).astype(np.float32)

    # Number: dark pixels WITHIN the circle area
    # First find dark pixels, then intersect with circle area
    dark = (lum < 0.15).astype(np.float32)
    number_mask = dark * circle_mask  # only dark pixels inside white circles

    return circle_mask, number_mask


def height_to_normal(height_map, strength=1.0):
    """Convert height map to tangent-space normal map."""
    hm = height_map
    h, w = hm.shape

    gx = np.zeros_like(hm)
    gy = np.zeros_like(hm)

    # Sobel gradients with U-axis wrapping
    for y in range(1, h - 1):
        for x in range(w):
            xm1 = (x - 1) % w
            xp1 = (x + 1) % w
            gx[y, x] = (hm[y, xp1] - hm[y, xm1]) * 0.5
            gy[y, x] = (hm[y + 1, x] - hm[y - 1, x]) * 0.5

    scale = strength * (W / (2 * math.pi * RADIUS_PX)) * 10
    gx *= scale
    gy *= scale

    gz = np.ones_like(gx)
    length = np.sqrt(gx * gx + gy * gy + gz * gz)
    gx /= length
    gy_ = gy / length
    gz_ = gz / length

    nx = ((gx + 1.0) * 127.5).clip(0, 255).astype(np.uint8)
    ny = ((gy_ + 1.0) * 127.5).clip(0, 255).astype(np.uint8)
    nz = ((gz_ + 1.0) * 127.5).clip(0, 255).astype(np.uint8)

    return np.stack([nx, ny, nz], axis=2)


# === Process all balls ===
for n in range(16):
    base_path = os.path.join(tex_dir, f"ball_{n:02d}.png")
    if not os.path.exists(base_path):
        print(f"  Skip ball {n:02d}: not found")
        continue

    print(f"Ball {n:02d}...", end=" ")
    img = Image.open(base_path)
    rgb = np.array(img).astype(np.float32) / 255.0

    circle_mask, number_mask = get_masks(rgb)

    # --- Height map ---
    height = np.full((H, W), HEIGHT_BODY, dtype=np.float32)
    height += circle_mask * HEIGHT_CIRCLE
    height += number_mask * HEIGHT_NUMBER
    height = gaussian_blur(height, BEVEL_SIGMA)

    # --- Normal map ---
    normal_rgb = height_to_normal(height, NORMAL_STRENGTH)
    Image.fromarray(normal_rgb, mode='RGB').save(
        os.path.join(tex_dir, f"ball_{n:02d}_normal.png"))

    # --- Roughness map ---
    rough = np.full((H, W), ROUGHNESS_BODY / 255.0, dtype=np.float32)
    rough = np.where(circle_mask > 0.5, ROUGHNESS_CIRCLE / 255.0, rough)
    rough = np.where(number_mask > 0.5, ROUGHNESS_NUMBER / 255.0, rough)
    rough = gaussian_blur(rough, 1.5)

    Image.fromarray((rough * 255).astype(np.uint8), mode='L').save(
        os.path.join(tex_dir, f"ball_{n:02d}_roughness.png"))

    print("done")

print(f"\nAll PBR maps saved to: {tex_dir}")
