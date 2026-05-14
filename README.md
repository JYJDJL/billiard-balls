# Billiard Balls

PBR billiard/pool ball generation toolkit. Produces game-ready GLB models (0-15) with base color, roughness, and normal maps, plus Clear Coat coating.

## Quick Start

```bash
# 1. Install dependencies
pip install Pillow numpy

# 2. Generate all 16 ball textures (1024x512 equirectangular PNGs)
python generate_all_balls.py

# 3. Generate PBR maps (roughness + normal)
python generate_pbr_maps.py
```

Then open Blender with the `billiard-ball` skill, or manually run the material setup and GLB export scripts.

## What You Get

| Output | Description |
|--------|-------------|
| `ball_00.png` ~ `ball_15.png` | BaseColor equirectangular textures |
| `ball_00_roughness.png` ~ `ball_15_roughness.png` | Roughness maps |
| `ball_00_normal.png` ~ `ball_15_normal.png` | Tangent-space normal maps |
| `billiard_balls_clearcoat.glb` | 16 balls, PBR + Clear Coat, ready for Unity/Three.js |

## Ball Colors

| Ball | Type | Body | Ball | Type | Stripe |
|------|------|------|------|------|--------|
| 0 | Cue | White | — | — | — |
| 1 | Solid | Yellow | 9 | Stripe | Yellow |
| 2 | Solid | Blue | 10 | Stripe | Blue |
| 3 | Solid | Red | 11 | Stripe | Red |
| 4 | Solid | Purple | 12 | Stripe | Purple |
| 5 | Solid | Orange | 13 | Stripe | Orange |
| 6 | Solid | Green | 14 | Stripe | Green |
| 7 | Solid | Maroon | 15 | Stripe | Maroon |
| 8 | Solid | Black | — | — | — |

## Engine Compatibility

- **Unity HDRP**: Drag & drop GLB, all PBR channels + Clear Coat auto-mapped
- **Three.js r131+**: `GLTFLoader` auto-converts to `MeshPhysicalMaterial` with `clearcoat`
- **Unreal**: Import GLB, assign material instances

## File Structure

```
billiard-balls/
├── generate_all_balls.py       # Generate 16 base color textures
├── generate_pbr_maps.py        # Generate roughness + normal maps
├── generate_8ball_texture.py   # Single 8-ball texture (quick test)
├── billiard-ball.skill         # Cowork skill (shareable, one-click install)
├── .gitignore                  # Excludes generated *.png and *.glb
└── README.md
```

Generated textures and GLB files are excluded from Git — reprodruce them by running the scripts.

## Sharing the Skill

Send `billiard-ball.skill` to any Cowork user. They click once to install the full billiard ball generation workflow.
