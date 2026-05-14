"""
Generate equirectangular textures for all 16 billiard balls (0-15).
Pure Python + Pillow, 4x supersampling for anti-aliasing.
"""
from PIL import Image, ImageDraw, ImageFont
import os

# --- Config ---
W, H = 1024, 512
SCALE = 4
RADIUS = 58 * SCALE
FONT_SIZE = 80 * SCALE

# Stripe band: middle third of V range
STRIPE_TOP = int(512 * SCALE * 0.30)
STRIPE_BOTTOM = int(512 * SCALE * 0.65)

# --- Font ---
font = None
font_paths = [
    "C:\\Windows\\Fonts\\Arialbd.ttf",
    "C:\\Windows\\Fonts\\Arial.ttf",
    "C:\\Windows\\Fonts\\segoeuib.ttf",
    "C:\\Windows\\Fonts\\calibrib.ttf",
]

for fp in font_paths:
    if os.path.exists(fp):
        font = ImageFont.truetype(fp, size=FONT_SIZE)
        print(f"Font: {fp}")
        break

if font is None:
    raise RuntimeError("No font found")

# --- Draw helpers ---
def draw_circle_and_text(draw, cx, center_y, text):
    """White circle with black number centered at (cx, center_y)."""
    white = (255, 255, 255, 255)
    black = (0, 0, 0, 255)
    draw.ellipse(
        [(cx - RADIUS, center_y - RADIUS), (cx + RADIUS, center_y + RADIUS)],
        fill=white,
    )
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = cx - tw // 2 - bbox[0]
    ty = center_y - th // 2 - bbox[1]
    draw.text((tx, ty), text, fill=black, font=font)


def place_circles(draw, center_y, text):
    """Place circles at U=0 (both edges) and U=0.5 (center)."""
    sw = W * SCALE
    for cx in [0, sw, sw // 2]:
        draw_circle_and_text(draw, cx, center_y, text)


# --- Ball definitions ---
SOLIDS = {
    0:  (255, 255, 255),   # cue
    1:  (255, 206, 0),     # yellow
    2:  (0, 38, 255),      # blue
    3:  (226, 0, 0),       # red
    4:  (102, 0, 153),     # purple
    5:  (255, 102, 0),     # orange
    6:  (0, 102, 0),       # green
    7:  (102, 0, 0),       # maroon
    8:  (5, 5, 5),         # black
}

STRIPES = {
    9:  (255, 206, 0),     # yellow stripe
    10: (0, 38, 255),      # blue stripe
    11: (226, 0, 0),       # red stripe
    12: (102, 0, 153),     # purple stripe
    13: (255, 102, 0),     # orange stripe
    14: (0, 102, 0),       # green stripe
    15: (102, 0, 0),       # maroon stripe
}

out_dir = os.path.dirname(os.path.abspath(__file__))
sw, sh = W * SCALE, H * SCALE
center_y = sh // 2

# === Solid balls (0-8) ===
for num, (br, bg, bb) in SOLIDS.items():
    img = Image.new("RGBA", (sw, sh))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (sw, sh)], fill=(br, bg, bb, 255))

    if num != 0:
        place_circles(draw, center_y, str(num))

    img = img.resize((W, H), Image.LANCZOS)
    path = os.path.join(out_dir, f"ball_{num:02d}.png")
    img.save(path)
    print(f"  Solid {num}: {path}")

# === Stripe balls (9-15) ===
for num, (sr, sg, sb) in STRIPES.items():
    img = Image.new("RGBA", (sw, sh))
    draw = ImageDraw.Draw(img)

    # White body
    draw.rectangle([(0, 0), (sw, sh)], fill=(255, 255, 255, 255))
    # Colored stripe band
    draw.rectangle(
        [(0, STRIPE_TOP), (sw, STRIPE_BOTTOM)],
        fill=(sr, sg, sb, 255)
    )

    place_circles(draw, center_y, str(num))

    img = img.resize((W, H), Image.LANCZOS)
    path = os.path.join(out_dir, f"ball_{num:02d}.png")
    img.save(path)
    print(f"  Stripe {num}: {path}")

print("\nDone! All 16 balls generated.")
