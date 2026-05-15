"""
Create all 16 billiard balls in Blender with PBR materials + Clear Coat.
Run in Blender's Scripting workspace after textures are generated.

Requirements: generate_all_balls.py + generate_pbr_maps.py must be run first.
"""
import bpy
import os
import math

tex_dir = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# Config
# ============================================================
SEGMENTS = 128
RING_COUNT = 64
BALL_RADIUS = 1.0
CLEARCOAT_WEIGHT = 0.6
CLEARCOAT_ROUGHNESS = 0.03
CLEARCOAT_IOR = 1.55

# ============================================================
# 1. Clean up old balls
# ============================================================
print("Cleaning up old objects...")
for i in range(16):
    obj = bpy.data.objects.get(f"Ball_{i:02d}")
    if obj:
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh and mesh.users == 0:
            bpy.data.meshes.remove(mesh)

for i in range(16):
    mat = bpy.data.materials.get(f"BallMat_{i:02d}")
    if mat:
        bpy.data.materials.remove(mat)

# Also clean template sphere
template = bpy.data.objects.get("Ball_Template")
if template:
    mesh = template.data
    bpy.data.objects.remove(template, do_unlink=True)
    if mesh and mesh.users == 0:
        bpy.data.meshes.remove(mesh)

# ============================================================
# 2. Create template UV sphere
# ============================================================
print("Creating template sphere...")
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=SEGMENTS,
    ring_count=RING_COUNT,
    radius=BALL_RADIUS,
    location=(0, 0, 0)
)
template = bpy.context.active_object
template.name = "Ball_Template"
bpy.ops.object.shade_smooth()

# ============================================================
# 3. Create PBR material for each ball
# ============================================================
def create_pbr_material(ball_num):
    """Create a PBR material with BaseColor, Roughness, Normal + Clear Coat."""
    mat = bpy.data.materials.new(name=f"BallMat_{ball_num:02d}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # --- Output ---
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)

    # --- BSDF ---
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Specular IOR Level'].default_value = 0.5

    # Clear Coat
    bsdf.inputs['Coat Weight'].default_value = CLEARCOAT_WEIGHT
    bsdf.inputs['Coat Roughness'].default_value = CLEARCOAT_ROUGHNESS
    bsdf.inputs['Coat IOR'].default_value = CLEARCOAT_IOR

    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # --- TexCoord ---
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, 200)

    # --- BaseColor texture ---
    color_tex = nodes.new('ShaderNodeTexImage')
    color_tex.location = (-400, 200)
    color_path = os.path.join(tex_dir, f"ball_{ball_num:02d}.png")
    if os.path.exists(color_path):
        color_tex.image = bpy.data.images.load(color_path)

    links.new(tex_coord.outputs['UV'], color_tex.inputs['Vector'])
    links.new(color_tex.outputs['Color'], bsdf.inputs['Base Color'])

    # --- Roughness texture (Non-Color) ---
    rough_tex = nodes.new('ShaderNodeTexImage')
    rough_tex.location = (-400, -100)
    rough_path = os.path.join(tex_dir, f"ball_{ball_num:02d}_roughness.png")
    if os.path.exists(rough_path):
        rough_tex.image = bpy.data.images.load(rough_path)
        rough_tex.image.colorspace_settings.name = 'Non-Color'

    links.new(tex_coord.outputs['UV'], rough_tex.inputs['Vector'])
    links.new(rough_tex.outputs['Color'], bsdf.inputs['Roughness'])

    # --- Normal texture (Non-Color) ---
    normal_tex = nodes.new('ShaderNodeTexImage')
    normal_tex.location = (-400, -400)
    normal_path = os.path.join(tex_dir, f"ball_{ball_num:02d}_normal.png")
    if os.path.exists(normal_path):
        normal_tex.image = bpy.data.images.load(normal_path)
        normal_tex.image.colorspace_settings.name = 'Non-Color'

    normal_map = nodes.new('ShaderNodeNormalMap')
    normal_map.location = (-100, -400)

    links.new(tex_coord.outputs['UV'], normal_tex.inputs['Vector'])
    links.new(normal_tex.outputs['Color'], normal_map.inputs['Color'])
    links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

# ============================================================
# 4. Create all 16 balls
# ============================================================
print("Creating 16 balls...")
for i in range(16):
    # Duplicate template mesh (independent copy — no material slot sharing)
    bpy.context.view_layer.objects.active = template
    template.select_set(True)
    bpy.ops.object.duplicate()
    ball = bpy.context.active_object
    ball.name = f"Ball_{i:02d}"

    # Assign mesh copy
    mesh = template.data.copy()
    ball.data = mesh

    # Create material
    mat = create_pbr_material(i)
    ball.data.materials.clear()
    ball.data.materials.append(mat)

    print(f"  Ball_{i:02d} created")

# Delete template
bpy.data.objects.remove(template, do_unlink=True)
if template.data.users == 0:
    print("  Template mesh cleaned up")

# ============================================================
# 5. Rack positioning (standard 8-ball)
# ============================================================
print("Positioning balls in rack...")
row_spacing = math.sqrt(3) * BALL_RADIUS

rack_layout = {
    1:  (0, 0),
    9:  (-1, 2),
    2:  (1, 2),
    10: (-2, 4),
    8:  (0, 4),
    3:  (2, 4),
    11: (-3, 6),
    4:  (-1, 6),
    12: (1, 6),
    5:  (3, 6),
    6:  (-4, 8),
    13: (-2, 8),
    14: (0, 8),
    7:  (2, 8),
    15: (4, 8),
}

for ball_num, (col, row) in rack_layout.items():
    ball = bpy.data.objects.get(f"Ball_{ball_num:02d}")
    if ball:
        ball.location = (col * BALL_RADIUS, row * BALL_RADIUS, BALL_RADIUS)

# Cue ball behind the rack
cue_ball = bpy.data.objects.get("Ball_00")
if cue_ball:
    cue_ball.location = (0, -8, BALL_RADIUS)

# ============================================================
# Done
# ============================================================
print(f"""
All 16 balls created with PBR + Clear Coat!
  Segments: {SEGMENTS}, Rings: {RING_COUNT}
  Clear Coat: Weight={CLEARCOAT_WEIGHT}, Roughness={CLEARCOAT_ROUGHNESS}, IOR={CLEARCOAT_IOR}
  Textures from: {tex_dir}
""")
