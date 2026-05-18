"""
Create a billiard cue stick in Blender with textured materials.
Run in Blender's Scripting workspace after textures are generated.

Requirements: generate_cue_textures.py must be run first.
"""
import bpy
import math
import os

# ============================================================
# Config
# ============================================================
tex_dir = os.path.dirname(os.path.abspath(__file__))
SCALE = 30.0

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
# 2. Material factories
# ============================================================
def make_solid_mat(name, r, g, b, rough, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n.inputs['Base Color'].default_value = (r, g, b, 1.0)
            n.inputs['Roughness'].default_value = rough
            n.inputs['Metallic'].default_value = metallic
            break
    return mat

def make_pbr_mat(name, color_file, rough_file, normal_file, fallback_rough=0.3):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial'); output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location = (300, 0)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = fallback_rough
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    tc = nodes.new('ShaderNodeTexCoord'); tc.location = (-600, 200)

    ct = nodes.new('ShaderNodeTexImage'); ct.location = (-400, 200)
    cp = os.path.join(tex_dir, color_file)
    if os.path.exists(cp): ct.image = bpy.data.images.load(cp)
    links.new(tc.outputs['UV'], ct.inputs['Vector'])
    links.new(ct.outputs['Color'], bsdf.inputs['Base Color'])

    rp = os.path.join(tex_dir, rough_file)
    if os.path.exists(rp):
        rt = nodes.new('ShaderNodeTexImage'); rt.location = (-400, -100)
        rt.image = bpy.data.images.load(rp)
        rt.image.colorspace_settings.name = 'Non-Color'
        links.new(tc.outputs['UV'], rt.inputs['Vector'])
        links.new(rt.outputs['Color'], bsdf.inputs['Roughness'])

    np = os.path.join(tex_dir, normal_file)
    if os.path.exists(np):
        nt = nodes.new('ShaderNodeTexImage'); nt.location = (-400, -400)
        nt.image = bpy.data.images.load(np)
        nt.image.colorspace_settings.name = 'Non-Color'
        nm = nodes.new('ShaderNodeNormalMap'); nm.location = (-100, -400)
        links.new(tc.outputs['UV'], nt.inputs['Vector'])
        links.new(nt.outputs['Color'], nm.inputs['Color'])
        links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

# ============================================================
# 3. Create materials
# ============================================================
mat_tip     = make_solid_mat("CueTip", 0.88, 0.82, 0.70, 0.55)
mat_ferrule = make_solid_mat("CueFerrule", 0.94, 0.94, 0.94, 0.18)
mat_joint   = make_solid_mat("CueJoint", 0.28, 0.28, 0.28, 0.10, metallic=0.9)
mat_bumper  = make_solid_mat("CueBumper", 0.04, 0.04, 0.04, 0.50)
mat_shaft   = make_pbr_mat("CueShaft", "cue_shaft_color.png", "cue_shaft_roughness.png", "cue_shaft_normal.png", 0.30)
mat_butt    = make_pbr_mat("CueButt", "cue_butt_color.png", "cue_butt_roughness.png", "cue_butt_normal.png", 0.22)
mat_wrap    = make_pbr_mat("CueWrap", "cue_wrap_color.png", "cue_wrap_roughness.png", "cue_wrap_normal.png", 0.70)

# ============================================================
# 4. Create cue parts
# ============================================================
cue_empty = bpy.data.objects.new("Cue", None)
bpy.context.scene.collection.objects.link(cue_empty)

parts_def = [
    # (name, radius_m, length_m, y_center_m, material, tapered)
    ("CueTip",       0.0065, 0.012,  0.780, mat_tip,     False),
    ("CueFerrule",   0.0065, 0.025,  0.761, mat_ferrule, False),
    ("CueShaft",     0.010,  0.730,  0.384, mat_shaft,   True),
    ("CueJoint",     0.011,  0.020,  0.009, mat_joint,   False),
    ("CueButtUpper", 0.014,  0.200, -0.101, mat_butt,    False),
    ("CueWrap",      0.014,  0.180, -0.291, mat_wrap,    False),
    ("CueButtLower", 0.015,  0.200, -0.481, mat_butt,    False),
    ("CueBumper",    0.015,  0.025, -0.593, mat_bumper,  False),
]

for name, radius, length, y_center, mat, tapered in parts_def:
    segments = 32 if not tapered else 64
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=segments, radius=radius * SCALE, depth=length * SCALE,
        location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name

    # Rotate -90 around X to lie along Y
    obj.rotation_euler.x = -math.pi / 2
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    # Position along Y
    obj.location.y = y_center * SCALE
    obj.location.z = 1.0

    # Taper shaft
    if tapered:
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        y_top = (y_center + length/2) * SCALE
        y_bottom = (y_center - length/2) * SCALE
        tip_radius = 0.0065 * SCALE
        joint_radius = radius * SCALE

        for v in bm.verts:
            wy = obj.matrix_world @ v.co
            t = (wy.y - y_bottom) / (y_top - y_bottom) if y_top != y_bottom else 0.5
            t = max(0, min(1, t))
            r = joint_radius + (tip_radius - joint_radius) * t
            if v.co.z != 0 or v.co.x != 0:
                factor = r / (radius * SCALE)
                v.co.x *= factor
                v.co.z *= factor

        bm.to_mesh(obj.data)
        bm.free()

    obj.data.materials.append(mat)
    obj.parent = cue_empty

# ============================================================
# 5. Position behind cue ball
# ============================================================
cue_ball = bpy.data.objects.get("Ball_00")
if cue_ball:
    cue_empty.location = (0, -32.55, 1.0)

print(f"Cue stick created: {len(cue_empty.children)} parts")
