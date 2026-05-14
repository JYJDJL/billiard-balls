# Billiard Balls / 台球生成工具

PBR billiard/pool ball generation toolkit. Produces game-ready GLB models (0-15) with base color, roughness, and normal maps, plus Clear Coat coating.

PBR 台球生成工具。产出可直接用于游戏的 GLB 模型（0-15 号球），包含基础色、粗糙度、法线贴图和 Clear Coat 透明涂层。

## Quick Start / 快速开始

```bash
# 1. 安装依赖 / Install dependencies
pip install Pillow numpy

# 2. 生成全部 16 个球的纹理（1024x512 equirectangular PNG）
#    Generate all 16 ball textures
python generate_all_balls.py

# 3. 生成 PBR 贴图（粗糙度 + 法线）
#    Generate PBR maps (roughness + normal)
python generate_pbr_maps.py
```

然后在 Blender 中使用 `billiard-ball` skill 完成材质节点搭建和 GLB 导出，或手动执行对应脚本。

Then use the `billiard-ball` skill in Blender to set up materials and export GLB, or run the scripts manually.

## Output / 产出文件

| 文件 / File | 说明 / Description |
|-------------|-------------------|
| `ball_00.png` ~ `ball_15.png` | 基础色贴图 / BaseColor textures |
| `ball_00_roughness.png` ~ `ball_15_roughness.png` | 粗糙度贴图 / Roughness maps |
| `ball_00_normal.png` ~ `ball_15_normal.png` | 切线空间法线贴图 / Normal maps |
| `billiard_balls_clearcoat.glb` | 16 球 PBR + Clear Coat 模型 |

## Ball Colors / 球色表

| 球号 | 类型 | 底色 | 球号 | 类型 | 条纹色 |
|------|------|------|------|------|--------|
| 0 | 母球 Cue | 白 White | — | — | — |
| 1 | 实色 Solid | 黄 Yellow | 9 | 花色 Stripe | 黄 Yellow |
| 2 | 实色 Solid | 蓝 Blue | 10 | 花色 Stripe | 蓝 Blue |
| 3 | 实色 Solid | 红 Red | 11 | 花色 Stripe | 红 Red |
| 4 | 实色 Solid | 紫 Purple | 12 | 花色 Stripe | 紫 Purple |
| 5 | 实色 Solid | 橙 Orange | 13 | 花色 Stripe | 橙 Orange |
| 6 | 实色 Solid | 绿 Green | 14 | 花色 Stripe | 绿 Green |
| 7 | 实色 Solid | 棕 Maroon | 15 | 花色 Stripe | 棕 Maroon |
| 8 | 实色 Solid | 黑 Black | — | — | — |

## Engine Compatibility / 引擎兼容

- **Unity HDRP**：拖入 GLB 即可，全部 PBR 通道 + Clear Coat 自动映射。Drag and drop, auto-mapped.
- **Three.js r131+**：`GLTFLoader` 自动转换为 `MeshPhysicalMaterial`，`clearcoat` 自动设置。Auto-converts with clearcoat.
- **Unreal**：导入 GLB，手动指定材质实例。Import GLB, assign material instances.

## File Structure / 文件结构

```
billiard-balls/
├── generate_all_balls.py       # 生成 16 个基础色贴图 / Generate base color textures
├── generate_pbr_maps.py        # 生成粗糙度 + 法线贴图 / Generate roughness + normal maps
├── generate_8ball_texture.py   # 单球快速测试 / Quick single-ball test
├── billiard-ball.skill         # Cowork skill 安装包（分享即装）/ Shareable one-click install
├── .gitignore                  # 忽略生成的 *.png 和 *.glb
└── README.md
```

贴图和 GLB 文件不纳入版本控制——运行脚本即可重现。

Generated textures and GLB files are gitignored — reproducible by running the scripts.

## Sharing / 分享

将 `billiard-ball.skill` 发给任何 Cowork 用户，点击一下即可安装完整的台球生成工作流。

Send `billiard-ball.skill` to any Cowork user. One click installs the full billiard ball generation workflow.
