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
def make_mat(name, r, g, b, rough):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n.inputs['Base Color'].default_value = (r, g, b, 1.0)
            n.inputs['Roughness'].default_value = rough
            break
    return mat

def make_tex_mat(name, tex_filename, rough):
    """Create material with an image texture."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Find nodes
    bsdf = output_node = None
    for n in nodes:
        if n.type == 'BSDF_PRINCIPLED':
            bsdf = n
        elif n.type == 'OUTPUT_MATERIAL':
            output_node = n

    bsdf.inputs['Roughness'].default_value = rough

    # Add texture node
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)

    img_node = nodes.new('ShaderNodeTexImage')
    img_node.location = (-400, 0)

    tex_path = os.path.join(tex_dir, tex_filename)
    if os.path.exists(tex_path):
        img_node.image = bpy.data.images.load(tex_path)

    links.new(tex_coord.outputs['UV'], img_node.inputs['Vector'])
    links.new(img_node.outputs['Color'], bsdf.inputs['Base Color'])

    return mat

mat_tip     = make_mat("CueTip", 0.88, 0.82, 0.70, 0.55)
mat_ferrule = make_mat("CueFerrule", 0.94, 0.94, 0.94, 0.18)
mat_shaft   = make_tex_mat("CueShaft", "cue_shaft_color.png", 0.32)
mat_joint   = make_mat("CueJoint", 0.28, 0.28, 0.28, 0.10)
mat_butt    = make_tex_mat("CueButt", "cue_butt_color.png", 0.28)
mat_wrap    = make_tex_mat("CueWrap", "cue_wrap_color.png", 0.75)
mat_bumper  = make_mat("CueBumper", 0.04, 0.04, 0.04, 0.50)

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
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=length, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = (math.radians(-90), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    obj.location = (0, y_center, 0)
    obj.data.materials.append(mat)
    obj.parent = cue_empty
    bpy.ops.object.shade_smooth()

# ============================================================
# 4. Taper the shaft
# ============================================================
shaft = bpy.data.objects.get("CueShaft")
if shaft:
    bpy.context.view_layer.objects.active = shaft
    bpy.ops.object.mode_set(mode='EDIT')

    import bmesh
    bm = bmesh.from_edit_mesh(shaft.data)
    bm.verts.ensure_lookup_table()

    top_y = max(v.co.y for v in bm.verts)
    bottom_y = min(v.co.y for v in bm.verts)
    tip_r, butt_r = 0.0065, 0.010
    length = top_y - bottom_y

    for v in bm.verts:
        t = (v.co.y - bottom_y) / length
        target_r = butt_r + (tip_r - butt_r) * t
        current_r = (v.co.x**2 + v.co.z**2)**0.5
        if current_r > 0.0001:
            scale = target_r / current_r
            v.co.x *= scale
            v.co.z *= scale

    bmesh.update_edit_mesh(shaft.data)
    bpy.ops.object.mode_set(mode='OBJECT')

# ============================================================
# 5. Scale and position
# ============================================================
cue_empty.scale = (CUE_LENGTH_SCALE, CUE_LENGTH_SCALE, CUE_LENGTH_SCALE)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Position behind cue ball (Ball_00)
cue_ball = bpy.data.objects.get("Ball_00")
if cue_ball:
    bx, by, bz = cue_ball.location
    cue_empty.location = (bx, by - 24.6, bz)
else:
    cue_empty.location = (0, -32.6, 1.0)

print("Cue stick created successfully!")
print(f"  Parts: {len(cue_empty.children)}")
print(f"  Location: {cue_empty.location}")
