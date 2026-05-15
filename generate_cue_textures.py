"""
Generate wood grain and leather textures for the billiard cue stick.
Uses Pillow + numpy for noise-based wood grain patterns.
Usage: pip install Pillow numpy && python generate_cue_textures.py
"""
from PIL import Image, ImageFilter
import numpy as np
import os
import math
import random

out_dir = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# Config — texture dimensions (V=length, U=circumference)
# ============================================================
SHAFT_W, SHAFT_H = 256, 2048    # maple shaft: long and thin
BUTT_W,  BUTT_H  = 256, 1024    # ebony butt sections
WRAP_W,  WRAP_H  = 256, 512     # leather wrap

# ============================================================
# Wood grain generator
# ============================================================
def generate_wood_grain(w, h, base_color, grain_color, grain_count=40, noise_scale=0.02):
    """Generate wood grain texture running along V (h).

    Wood grain = base color + darker grain lines along V,
    with slight sinusoidal warping for natural look.
    """
    random.seed(42)
    np.random.seed(42)

    # Base layer
    img = np.full((h, w, 3), base_color, dtype=np.float32)

    # Grain lines along V (vertical in the texture)
    # Each grain line has a random U position, with warping
    for i in range(grain_count):
        # Random U center for this grain line
        u_center = random.uniform(0, w)

        # Random width of grain line
        grain_width = random.uniform(0.5, 3.0)

        # Random opacity
        opacity = random.uniform(0.3, 0.9)

        # Generate warped grain line
        for y in range(h):
            # Sinusoidal warp
            warp = math.sin(y * noise_scale * 10 + i * 1.7) * w * noise_scale * 8
            u = int((u_center + warp) % w)

            # Gaussian falloff
            for du in range(-int(grain_width * 3), int(grain_width * 3) + 1):
                x = (u + du) % w
                dist = abs(du) / grain_width
                if dist < 3:
                    falloff = math.exp(-dist * dist)
                    blend = opacity * falloff * 0.4
                    img[y, x] = img[y, x] * (1 - blend) + grain_color * blend

    # Add subtle noise for wood texture
    noise = np.random.rand(h, w).astype(np.float32) * 0.04 - 0.02
    for c in range(3):
        img[:, :, c] = np.clip(img[:, :, c] + noise, 0, 1)

    img = (img * 255).clip(0, 255).astype(np.uint8)
    return Image.fromarray(img, mode='RGB')


def generate_leather(w, h):
    """Generate dark leather texture with subtle grain."""
    np.random.seed(99)

    # Base dark gray
    img = np.full((h, w, 3), [0.12, 0.12, 0.12], dtype=np.float32)

    # Add fine noise grain
    noise = np.random.rand(h, w).astype(np.float32) * 0.08 - 0.04
    for c in range(3):
        img[:, :, c] = np.clip(img[:, :, c] + noise, 0, 1)

    # Blur slightly for leather texture
    img_pil = Image.fromarray((img * 255).astype(np.uint8), mode='RGB')
    img_pil = img_pil.filter(ImageFilter.GaussianBlur(radius=0.5))

    return img_pil


# ============================================================
# Generate textures
# ============================================================

# Maple shaft: light warm wood
print("Generating shaft wood grain (maple)...")
maple_base = np.array([0.85, 0.72, 0.52], dtype=np.float32)   # warm maple
maple_grain = np.array([0.55, 0.42, 0.25], dtype=np.float32)   # darker grain
shaft_tex = generate_wood_grain(SHAFT_W, SHAFT_H, maple_base, maple_grain,
                                 grain_count=50, noise_scale=0.015)
shaft_tex.save(os.path.join(out_dir, "cue_shaft_color.png"))

# Ebony butt: very dark wood with subtle grain
print("Generating butt wood grain (ebony)...")
ebony_base = np.array([0.18, 0.10, 0.04], dtype=np.float32)    # dark ebony
ebony_grain = np.array([0.08, 0.04, 0.02], dtype=np.float32)    # even darker grain
butt_tex = generate_wood_grain(BUTT_W, BUTT_H, ebony_base, ebony_grain,
                                grain_count=30, noise_scale=0.02)
butt_tex.save(os.path.join(out_dir, "cue_butt_color.png"))

# Leather wrap
print("Generating leather wrap...")
wrap_tex = generate_leather(WRAP_W, WRAP_H)
wrap_tex.save(os.path.join(out_dir, "cue_wrap_color.png"))

print("\nAll cue textures generated:")
for f in ["cue_shaft_color.png", "cue_butt_color.png", "cue_wrap_color.png"]:
    path = os.path.join(out_dir, f)
    size_kb = os.path.getsize(path) / 1024
    print(f"  {f} ({size_kb:.0f} KB)")

print("\nDone!")
