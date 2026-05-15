"""
Export the complete billiard scene (balls + cue + animation) as GLB.

在 Blender 的 Scripting 工作区中运行，前提是场景中已有台球和球杆模型。
Run in Blender's Scripting workspace after balls and cue are created.

产出一个自包含的 GLB 文件，包含：
- 16 个台球（PBR 材质 + Clear Coat 涂层）
- 8 部件球杆（PBR 材质：BaseColor + Roughness + Normal）
- 开球动画（120 帧 / 24fps / 5 秒）
"""

import bpy
import os
import struct
import json
import sys

# ============================================================
# Config
# ============================================================
# 输出路径 — 修改为你想要的路径
# Output path — change to wherever you want the GLB saved
OUTPUT_PATH = r"C:\Users\FZ-LT-26\Desktop\claude-desktop-test\billiard_complete_scene.glb"

# 导出选项 / Export options
EXPORT_SELECTED_ONLY = True   # True = 只导出球和球杆；False = 导出场景全部物体
INCLUDE_LIGHTS = False        # 是否包含灯光
INCLUDE_CAMERA = False        # 是否包含摄像机
Y_UP = True                   # glTF 标准 Y-up（关闭则 Z-up）


# ============================================================
# 1. Verify objects exist / 检查场景物体
# ============================================================
print("=" * 50)
print("Billiard Scene GLB Exporter")
print("=" * 50)

required = [f"Ball_{i:02d}" for i in range(16)] + ["Cue"]
missing = [name for name in required if bpy.data.objects.get(name) is None]

if missing:
    print(f"\n缺少以下物体 / Missing objects: {missing}")
    print("请先运行:")
    print("  - create_balls_in_blender.py  (生成台球)")
    print("  - create_cue_in_blender.py    (生成球杆)")
    sys.exit(1)

print(f"\n场景验证通过 / Scene OK: {len(required)} 个物体就绪")


# ============================================================
# 2. Triangulate cue cylinders for proper tangent export
# ============================================================
print("\n三角化球杆部件 / Triangulating cue parts...")
triangulated = 0
for obj in bpy.data.objects:
    if obj.name.startswith("Cue") and obj.type == 'MESH':
        # Skip if already triangulated
        already_tri = True
        for poly in obj.data.polygons:
            if len(poly.vertices) > 3:
                already_tri = False
                break
        if already_tri:
            continue
        bpy.context.view_layer.objects.active = obj
        mod = obj.modifiers.new(name="Triangulate_Export", type='TRIANGULATE')
        mod.quad_method = 'BEAUTY'
        bpy.ops.object.modifier_apply(modifier=mod.name)
        triangulated += 1

print(f"  三角化了 {triangulated} 个部件 / Triangulated {triangulated} parts")


# ============================================================
# 3. Select objects to export
# ============================================================
bpy.ops.object.select_all(action='DESELECT')
export_names = []
for obj in bpy.data.objects:
    if obj.name.startswith("Ball_") or obj.name.startswith("Cue"):
        obj.select_set(True)
        export_names.append(obj.name)

print(f"\n选中导出物体 / Selected for export: {len(export_names)}")


# ============================================================
# 4. Export as GLB
# ============================================================
print(f"\n导出中 / Exporting to: {OUTPUT_PATH}")

bpy.ops.export_scene.gltf(
    filepath=OUTPUT_PATH,
    export_format='GLB',
    use_selection=EXPORT_SELECTED_ONLY,
    export_apply=True,
    export_animations=True,
    export_frame_range=True,
    export_frame_step=1,
    export_skins=False,
    export_morph=False,
    export_lights=INCLUDE_LIGHTS,
    export_cameras=INCLUDE_CAMERA,
    export_extras=True,
    export_yup=Y_UP,
    export_image_format='AUTO',
    export_texcoords=True,
    export_normals=True,
    export_tangents=True,
    export_materials='EXPORT',
)

if not os.path.exists(OUTPUT_PATH):
    print("导出失败 / Export failed!")
    sys.exit(1)

size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)


# ============================================================
# 5. Verify GLB content
# ============================================================
print("验证 GLB 内容 / Verifying GLB contents...")

with open(OUTPUT_PATH, 'rb') as f:
    header = f.read(12)
    magic = struct.unpack('<I', header[:4])[0]
    version = struct.unpack('<I', header[4:8])[0]
    total_len = struct.unpack('<I', header[8:12])[0]

    chunk_len = struct.unpack('<I', f.read(4))[0]
    chunk_type = struct.unpack('<I', f.read(4))[0]
    gltf = json.loads(f.read(chunk_len))

nodes = len(gltf.get('nodes', []))
meshes = len(gltf.get('meshes', []))
mats = len(gltf.get('materials', []))
anims = len(gltf.get('animations', []))
exts = gltf.get('extensionsUsed', [])

anim_channels = sum(len(a.get('channels', [])) for a in gltf.get('animations', []))

# ============================================================
# Summary
# ============================================================
print(f"""
{'=' * 50}
导出完成 / Export complete
{'=' * 50}
文件 / File:      {OUTPUT_PATH}
大小 / Size:      {size_mb:.1f} MB
GLB 版本:         {version}
{'=' * 50}
节点 / Nodes:     {nodes}
网格 / Meshes:    {meshes}
材质 / Materials: {mats}
动画 / Animations:{anims} 条轨道（{anim_channels} 个通道）
{'=' * 50}
扩展 / Extensions: {', '.join(exts)}
Clear Coat:       {'KHR_materials_clearcoat' in exts}
{'=' * 50}

如何使用 / How to use:
  Unity HDRP: 拖入 GLB 即可，PBR + Clear Coat 自动映射
  Three.js:   GLTFLoader 加载，clearcoat 自动设置
  Unreal:     导入 GLB，手动指定材质实例
  网页预览:   https://gltf-viewer.donmccurdy.com/
""")
