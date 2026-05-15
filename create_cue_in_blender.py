"""
Create a billiard cue stick in Blender with textured materials.
Run in Blender's Scripting workspace after textures are generated.

Requirements: generate_cue_textures.py must be run first.
"""
import bpy
import math
import os

# ============================================================
# Config — adjust paths as needed
# ============================================================
tex_dir = os.path.dirname(os.path.abspath(__file__))
CUE_LENGTH_SCALE = 30  # scale factor to match billiard ball proportions

# ============================================================
# 1. Clean up old cue
# ============================================================
for obj_name in ["CueTip", "CueFerrule", "CueShaft", "CueJoint",
                  "CueButtUpper", "CueWrap", "CueButtLower", "CueBumper", "Cue"]:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        mesh = obj.data if obj.type == 'MESH' else None
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh and mesh.users == 0:
            bpy.data.meshes.remove(mesh)

for mat_name in ["CueTip", "CueFerrule", "CueShaft", "CueJoint",
                 "CueButt", "CueWrap", "CueBumper"]:
    mat = bpy.data.materials.get(mat_name)
    if mat:
        bpy.data.materials.remove(mat)

# ============================================================
# 2. Create materials
# ============================================================
def make_mat(name, r, g, b, rough, metallic=0.0):
    """Create a simple solid-color material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n.inputs['Base Color'].default_value = (r, g, b, 1.0)
            n.inputs['Roughness'].default_value = rough
            n.inputs['Metallic'].default_value = metallic
            break
    return mat

def make_pbr_mat(name, color_filename, roughness_filename, normal_filename, fallback_rough=0.3):
    """Create a full PBR material with BaseColor, Roughness, and Normal maps."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear defaults
    nodes.clear()

    # --- Output ---
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)

    # --- BSDF ---
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = fallback_rough

    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # --- TexCoord ---
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, 200)

    # --- BaseColor texture ---
    color_tex = nodes.new('ShaderNodeTexImage')
    color_tex.location = (-400, 200)
    color_path = os.path.join(tex_dir, color_filename)
    if os.path.exists(color_path):
        color_tex.image = bpy.data.images.load(color_path)

    links.new(tex_coord.outputs['UV'], color_tex.inputs['Vector'])
    links.new(color_tex.outputs['Color'], bsdf.inputs['Base Color'])

    # --- Roughness texture (Non-Color) ---
    rough_path = os.path.join(tex_dir, roughness_filename)
    if os.path.exists(rough_path):
        rough_tex = nodes.new('ShaderNodeTexImage')
        rough_tex.location = (-400, -100)
        rough_tex.image = bpy.data.images.load(rough_path)
        rough_tex.image.colorspace_settings.name = 'Non-Color'
        links.new(tex_coord.outputs['UV'], rough_tex.inputs['Vector'])
        links.new(rough_tex.outputs['Color'], bsdf.inputs['Roughness'])

    # --- Normal texture (Non-Color) ---
    normal_path = os.path.join(tex_dir, normal_filename)
    if os.path.exists(normal_path):
        normal_tex = nodes.new('ShaderNodeTexImage')
        normal_tex.location = (-400, -400)
        normal_tex.image = bpy.data.images.load(normal_path)
        normal_tex.image.colorspace_settings.name = 'Non-Color'

        normal_map = nodes.new('ShaderNodeNormalMap')
        normal_map.location = (-100, -400)

        links.new(tex_coord.outputs['UV'], normal_tex.inputs['Vector'])
        links.new(normal_tex.outputs['Color'], normal_map.inputs['Color'])
        links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

# Solid parts (colors + roughness values)
mat_tip     = make_mat("CueTip", 0.88, 0.82, 0.70, 0.55)      # leather
mat_ferrule = make_mat("CueFerrule", 0.94, 0.94, 0.94, 0.18)   # polished plastic
mat_joint   = make_mat("CueJoint", 0.28, 0.28, 0.28, 0.10, metallic=0.9)  # dark metal
mat_bumper  = make_mat("CueBumper", 0.04, 0.04, 0.04, 0.50)     # rubber

# Textured parts (full PBR: BaseColor + Roughness + Normal)
mat_shaft = make_pbr_mat("CueShaft",
    "cue_shaft_color.png", "cue_shaft_roughness.png", "cue_shaft_normal.png",
    fallback_rough=0.30)
mat_butt = make_pbr_mat("CueButt",
    "cue_butt_color.png", "cue_butt_roughness.png", "cue_butt_normal.png",
    fallback_rough=0.22)
mat_wrap = make_pbr_mat("CueWrap",
    "cue_wrap_color.png", "cue_wrap_roughness.png", "cue_wrap_normal.png",
    fallback_rough=0.70)

# ============================================================
# 3. Create cue parts (cylinders, rotated -90 X to lie along Y)
# ============================================================
cue_empty = bpy.data.objects.new("Cue", None)
bpy.context.scene.collection.objects.link(cue_empty)

parts_def = [
    # (name, radius, length, y_center, material)
    ("CueTip",       0.0065, 0.012,  0.780, mat_tip),
    ("CueFerrule",   0.0065, 0.025,  0.761, mat_ferrule),
    ("CueShaft",     0.010,  0.730,  0.384, mat_shaft),
    ("CueJoint",     0.011,  0.020,  0.009, mat_joint),
    ("CueButtUpper", 0.014,  0.200, -0.101, mat_butt),
    ("CueWrap",      0.014,  0.180, -0.291, mat_wrap),
    ("CueButtLower", 0.015,  0.200, -0.481, mat_butt),
    ("CueBumper",    0.015,  0.025, -0.593, mat_bumper),
]

for name, radius, length, y_center, mat in parts_def:
    bp