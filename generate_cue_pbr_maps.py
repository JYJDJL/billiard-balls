"""
Generate PBR roughness and normal maps for cue stick textures.
Uses existing base color textures (shaft/butt/wrap) to derive
roughness variation and normal (height) maps.

Run after generate_cue_textures.py.
Requires: pip install Pillow numpy
"""
from PIL import Image, ImageFilter
import numpy as np
import os
import math

tex_dir = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# PBR parameters
# ============================================================
# Roughness values (0-1 mapped to 0-255)
ROUGHBASE_SHAFT = 0.30    # maple: moderate roughness
ROUGHGRAIN_SHAFT = 0.22   # grain lines slightly smoother
ROUGHNOISE_SHAFT = 0.04   # subtle noise amplitude

ROUGHBASE_BUTT = 0.22     # ebony: smoother, polished
ROUGHGRAIN_BUTT = 0.15    # grain lines even smoother
ROUGHNOISE_BUTT = 0.03

ROUGHBASE_WRAP = 0.70     # leather: quite rough
ROUGHGRAIN_WRAP = 0.55    # grain depressions slightly smoother
ROUGHNOISE_WRAP = 0.10    # significant noise

# Normal/height parameters
HEIGHT_GRAIN_SHAFT = 0.008
HEIGHT_GRAIN_BUTT = 0.006
HEIGHT_LEATHER = 0.015      # leather grain bump height
NORMAL_STRENGTH = 1.5
BEVEL_SIGMA = 2.0


def load_texture(filename):
    """Load a texture file, return as float32 RGB array [0,1]."""
    path = os.path.join(tex_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found. Run generate_cue_textures.py first.")
    img = Image.open(path).convert('RGB')
    return np.array(img).astype(np.float32) / 255.0


def gaussian_blur(arr, sigma):
    """Blur a 2D array using Pillow."""
    img = Image.fromarray((arr * 255).clip(0, 255).astype(np.uint8), mode='L')
    img = img.filter(ImageFilter.GaussianBlur(radius=sigma))
    return np.array(img).astype(np.float32) / 255.0


def height_to_normal(height_map, w, strength=1.0):
    """Convert height map to tangent-space normal map.

    The texture wraps around cylinder: U-axis (width) is 360 degrees,
    V-axis (height) is along the cylinder length.
    """
    hm = height_map
    h, actual_w = hm.shape

    gx = np.zeros_like(hm)
    gy = np.zeros_like(hm)

    # Sobel gradients with U-axis wrapping
    for y in range(1, h - 1):
        for x in range(actual_w):
            xm1 = (x - 1) % actual_w
            xp1 = (x + 1) % actual_w
            gx[y, x] = (hm[y, xp1] - hm[y, xm1]) * 0.5
            gy[y, x] = (hm[y + 1, x] - hm[y - 1, x]) * 0.5

    # Scale: circumference = width pixels, but object radius depends on part
    # Use a fixed scale for visual quality
    scale = strength * (w / (2 * math.pi * 50)) * 10
    gx *= scale
    gy *= scale

    gz = np.ones_like(gx)
    length = np.sqrt(gx * gx + gy * gy + gz * gz)
    length = np.maximum(length, 1e-8)
    gx /= length
    gy_ = gy / length
    gz_ = gz / length

    nx = ((gx + 1.0) * 127.5).clip(0, 255).astype(np.uint8)
    ny = ((gy_ + 1.0) * 127.5).clip(0, 255).astype(np.uint8)
    nz = ((gz_ + 1.0) * 127.5).clip(0, 255).astype(np.uint8)

    return np.stack([nx, ny, nz], axis=2)


def generate_wood_roughness(rgb, base_rough, grain_rough, noise_amp):
    """Generate roughness map from wood grain texture.

    Darker grain lines → slightly different roughness.
    Use luminance to detect grain.
    """
    h, w = rgb.shape[:2]
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]

    # Grain regions are darker than average
    avg_lum = np.mean(lum)
    grain_mask = np.clip((avg_lum - lum) / max(avg_lum, 0.01), 0, 1)

    # Interpolate roughness between base and grain values
    rough = base_rough + (grain_rough - base_rough) * grain_mask

    # Add subtle noise
    np.random.seed(42)
    noise = np.random.rand(h, w).astype(np.float32) * noise_amp * 2 - noise_amp
    rough = np.clip(rough + noise, 0.05, 0.95)

    return rough


def generate_wood_height(rgb, grain_height):
    """Generate height map from wood grain.

    Darker grain = slightly recessed (lower height).
    """
    h, w = rgb.shape[:2]
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]

    avg_lum = np.mean(lum)
    grain_mask = np.clip((avg_lum - lum) / max(avg_lum, 0.01), 0, 1)

    height = -grain_mask * grain_height  # negative = recessed
    height = gaussian_blur(height, BEVEL_SIGMA)

    return height


def generate_leather_roughness(rgb, base_rough, grain_rough, noise_amp):
    """Generate leather roughness with fine grain pattern."""
    h, w = rgb.shape[:2]
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]

    # Leather has fine grain: use local variance as roughness variation
    np.random.seed(99)
    fine_noise = np.random.rand(h, w).astype(np.float32) * noise_amp * 2 - noise_amp

    # Small darker spots = slightly smoother (worn spots)
    avg_lum = np.mean(lum)
    dark_spots = np.clip((avg_lum - lum) / max(avg_lum, 0.01), 0, 1)

    rough = base_rough + (grain_rough - base_rough) * dark_spots + fine_noise
    rough = np.clip(rough, 0.10, 0.95)

    return rough


def generate_leather_height(rgb, bump_height):
    """Generate leather grain height map."""
    h, w = rgb.shape[:2]
    np.random.seed(99)

    # Fine random bumps for leather grain
    fine = np.random.rand(h, w).astype(np.float32) * bump_height

    # Slightly larger grain patterns
    coarse = np.random.rand(h // 4, w // 4).astype(np.float32) * bump_height * 2
    coarse_img = Image.fromarray((coarse * 255).astype(np.uint8), mode='L')
    coarse_img = coarse_img.resize((w, h), Image.BILINEAR)
    coarse = np.array(coarse_img).astype(np.float32) / 255.0 * bump_height * 2

    height = fine * 0.7 + coarse * 0.3
    height = gaussian_blur(height, 1.0)

    return height - bump_height * 0.5  # center around 0


# ============================================================
# Process each texture
# ============================================================

# --- Shaft (maple wood) ---
print("Generating cue shaft PBR maps...")
shaft = load_texture("cue_shaft_color.png")
h, w = shaft.shape[:2]

shaft_rough = generate_wood_roughness(shaft, ROUGHBASE_SHAFT, ROUGHGRAIN_SHAFT, ROUGHNOISE_SHAFT)
Image.fromarray((shaft_rough * 255).astype(np.uint8), mode='L').save(
    os.path.join(tex_dir, "cue_shaft_roughness.png"))

shaft_height = generate_wood_height(shaft, HEIGHT_GRAIN_SHAFT)
shaft_normal = height_to_normal(shaft_height, w, NORMAL_STRENGTH)
Image.fromarray(shaft_normal, mode='RGB').save(
    os.path.join(tex_dir, "cue_shaft_normal.png"))

print(f"  shaft: {h}x{w}")

# --- Butt (ebony wood) ---
print("Generating cue butt PBR maps...")
butt = load_texture("cue_butt_color.png")
h, w = butt.shape[:2]

butt_rough = generate_wood_roughness(butt, ROUGHBASE_BUTT, ROUGHGRAIN_BUTT, ROUGHNOISE_BUTT)
Image.fromarray((butt_rough * 255).astype(np.uint8), mode='L').save(
    os.path.join(tex_dir, "cue_butt_roughness.png"))

butt_height = generate_wood_height(butt, HEIGHT_GRAIN_BUTT)
butt_normal = height_to_normal(butt_height, w, NORMAL_STRENGTH)
Image.fromarray(butt_normal, mode='RGB').save(
    os.path.join(tex_dir, "cue_butt_normal.png"))

print(f"  butt: {h}x{w}")

# --- Wrap (leather) ---
print("Generating cue wrap PBR maps...")
wrap = load_texture("cue_wrap_color.png")
h, w = wrap.shape[:2]

wrap_rough = generate_leather_roughness(wrap, ROUGHBASE_WRAP, ROUGHGRAIN_WRAP, ROUGHNOISE_WRAP)
Image.fromarray((wrap_rough * 255).astype(np.uint8), mode='L').save(
    os.path.join(tex_dir, "cue_wrap_roughness.png"))

wrap_height = generate_leather_height(wrap, HEIGHT_LEATHER)
wrap_normal = height_to_normal(wrap_height, w, NORMAL_STRENGTH * 1.5)
Image.fromarray(wrap_normal, mode='RGB').save(
    os.path.join(tex_dir, "cue_wrap_normal.png"))

print(f"  wrap: {h}x{w}")

# ============================================================
# Summary
# ============================================================
print("\nCue PBR maps generated:")
for f in ["cue_shaft_roughness.png", "cue_shaft_normal.png",
          "cue_butt_roughness.png", "cue_butt_normal.png",
          "cue_wrap_roughness.png", "cue_wrap_normal.png"]:
    path = os.path.join(tex_dir, f)
    size_kb = os.path.getsize(path) / 1024
    print(f"  {f} ({size_kb:.0f} KB)")

print("""
PBR roughness values:
  Shaft (maple):  base=0.30, grain=0.22
  Butt (ebony):   base=0.22, grain=0.15
  Wrap (leather): base=0.70, grain=0.55

Solid part roughness (set directly in Blender):
  Tip (leather):     0.55
  Ferrule (plastic): 0.18
  Joint (metal):     0.10
  Bumper (rubber):   0.50

Next: run create_cue_in_blender.py in Blender (updated to use PBR maps).
""")
