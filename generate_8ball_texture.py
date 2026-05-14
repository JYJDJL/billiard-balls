"""
Generate an equirectangular 8-ball texture.
Fixes: seam wrapping for U=0 circle, supersampling anti-aliasing.
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Target dimensions
W, H = 1024, 512
SCALE = 4  # supersampling factor for anti-aliasing

RADIUS = 58 * SCALE  # circle radius at supersampled resolution

# --- Create high-res canvas ---
sw, sh = W * SCALE, H * SCALE
img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# --- Black background ---
bg = (5, 5, 5, 255)
draw.rectangle([(0, 0), (sw, sh)], fill=bg)

# --- Load font ---
font = None
font_paths = [
    "C:\\Windows\\Fonts\\Arialbd.ttf",
    "C:\\Windows\\Fonts\\Arial.ttf",
    "C:\\Windows\\Fonts\\segoeuib.ttf",
    "C:\\Windows\\Fonts\\calibrib.ttf",
    "C:\\Windows\\Fonts\\DejaVuSans-Bold.ttf",
]

for fp in font_paths:
    if os.path.exists(fp):
        try:
            font = ImageFont.truetype(fp, size=80 * SCALE)
            print(f"Using font: {fp}")
            break
        except Exception as e:
            print(f"  Failed {fp}: {e}")
            continue

if font is None:
    print("No bold font found, using default")
    font = ImageFont.load_default()

# --- White circles and numbers ---
center_y = sh // 2
white = (255, 255, 255, 255)
black = (0, 0, 0, 255)
text = "8"

# Helper to draw circle + text centered at (cx, cy)
def draw_circle_and_text(cx, cy):
    draw.ellipse(
        [(cx - RADIUS, cy - RADIUS), (cx + RADIUS, cy + RADIUS)],
        fill=white,
    )
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = cx - tw // 2 - bbox[0]
    ty = cy - th // 2 - bbox[1]
    draw.text((tx, ty), text, fill=black, font=font)

# Circle at U=0 (left edge) — draw at x=0 AND x=sw for seamless wrapping
draw_circle_and_text(0, center_y)
draw_circle_and_text(sw, center_y)

# Circle at U=0.5 (center)
draw_circle_and_text(sw // 2, center_y)

# --- Downscale with anti-aliasing ---
img = img.resize((W, H), Image.LANCZOS)

# --- Save ---
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "8ball_texture.png")
img.save(out_path)
print(f"Saved: {out_path}")
print(f"Final size: {W}x{H}")
print(f"Supersampling: {SCALE}x")
