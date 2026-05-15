# Billiard Balls / 台球生成工具

PBR billiard/pool ball generation toolkit. Produces game-ready GLB models (0-15) with base color, roughness, normal maps, and Clear Coat. Includes cue stick model, wood grain textures, and break shot animation.

PBR 台球生成工具。产出可直接用于游戏的 GLB 模型（0-15 号球），包含基础色、粗糙度、法线贴图和 Clear Coat 涂层。附带台球杆模型、木纹贴图和开球动画。

## Quick Start / 快速开始

```bash
# 1. 安装依赖 / Install dependencies
pip install Pillow numpy

# 2. 生成全部 16 个球的纹理 / Generate all 16 ball textures
python generate_all_balls.py

# 3. 生成 PBR 贴图 / Generate PBR maps
python generate_pbr_maps.py

# 4. 生成球杆纹理 / Generate cue textures
python generate_cue_textures.py

# 5. 生成球杆 PBR 贴图 / Generate cue PBR maps
python generate_cue_pbr_maps.py
```

然后在 Blender 中加载对应的 Cowork skill 或手动运行脚本。

Then load the matching Cowork skill in Blender, or run the scripts manually.

## Output / 产出文件

| 文件 / File | 说明 / Description |
|-------------|-------------------|
| `ball_00.png` ~ `ball_15.png` | 基础色贴图 / BaseColor textures |
| `ball_00_roughness.png` ~ `ball_15_roughness.png` | 粗糙度贴图 / Roughness maps |
| `ball_00_normal.png` ~ `ball_15_normal.png` | 切线空间法线贴图 / Normal maps |
| `cue_shaft_color.png` | 枫木杆身贴图 / Maple shaft texture |
| `cue_shaft_roughness.png` | 杆身粗糙度贴图 / Shaft roughness |
| `cue_shaft_normal.png` | 杆身法线贴图 / Shaft normal |
| `cue_butt_color.png` | 乌木后把贴图 / Ebony butt texture |
| `cue_butt_roughness.png` | 后把粗糙度贴图 / Butt roughness |
| `cue_butt_normal.png` | 后把法线贴图 / Butt normal |
| `cue_wrap_color.png` | 皮革握把贴图 / Leather wrap texture |
| `cue_wrap_roughness.png` | 握把粗糙度贴图 / Wrap roughness |
| `cue_wrap_normal.png` | 握把法线贴图 / Wrap normal |
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

## Cue Stick / 台球杆

8 部件结构，从杆头到杆尾：

| 部件 | 半径 | 长度 | 材质 |
|------|------|------|------|
| Tip 杆头 | 6.5mm | 12mm | 皮革 |
| Ferrule 先角 | 6.5mm | 25mm | 白色塑料 |
| Shaft 杆身 | 6.5→10mm | 730mm | 枫木（锥形渐粗） |
| Joint 接环 | 11mm | 20mm | 深色金属 |
| ButtUpper 后把上 | 14mm | 200mm | 乌木 |
| Wrap 握把 | 14mm | 180mm | 皮革 |
| ButtLower 后把下 | 15mm | 200mm | 乌木 |
| Bumper 缓冲垫 | 15mm | 25mm | 黑色橡胶 |

比例系数 30x，匹配台球尺寸（球半径 = 1.0）。

球杆使用完整 PBR 材质：枫木/乌木/皮革部件有 BaseColor + Roughness + Normal 三通道贴图，Joint 有 Metallic 金属度。

## Break Shot Animation / 开球动画

120 帧 / 24fps / 5 秒，手写关键帧动画：

| 阶段 | 帧范围 | 说明 |
|------|--------|------|
| 后拉蓄力 | 0-12 | 球杆后拉 |
| 前冲击球 | 12-20 | 杆头精确接触母球背面 |
| 母球加速 | 20-44 | 母球冲向球堆 |
| 撞顶点球 | 44 | 母球与 1 号球精确接触（球心距=2.0） |
| 能量传递 | 44-54 | 母球偏转，1 号球前冲 |
| 1 号偏转 | 50-58 | 1 号球绕开 8 号和 13 号 |
| 彩球散射 | 55-120 | 全部彩球四散 |

## Engine Compatibility / 引擎兼容

- **Unity HDRP**：拖入 GLB 即可，全部 PBR 通道 + Clear Coat 自动映射。
- **Three.js r131+**：GLTFLoader 自动转换为 MeshPhysicalMaterial，clearcoat 自动设置。
- **Unreal**：导入 GLB，手动指定材质实例。

## File Structure / 文件结构

```
billiard-balls/
├── generate_all_balls.py         # 16 个台球 BaseColor 贴图
├── generate_pbr_maps.py          # Roughness + Normal 贴图
├── generate_8ball_texture.py     # 单球快速测试
├── generate_cue_textures.py      # 球杆木纹 + 皮革贴图
├── generate_cue_pbr_maps.py      # 球杆 Roughness + Normal 贴图
├── create_balls_in_blender.py    # Blender 台球 3D 模型 + PBR + Clear Coat
├── create_cue_in_blender.py      # Blender 球杆 3D 模型 + PBR
├── create_break_animation.py     # Blender 开球动画
├── billiard-ball.skill           # Cowork skill — 台球生成
├── billiard-cue.skill            # Cowork skill — 球杆建模
├── billiard-break.skill          # Cowork skill — 开球动画
├── .gitignore                    # 忽略 *.png 和 *.glb
└── README.md
```

贴图、GLB 和 CLAUDE.md 不纳入版本控制——运行脚本即可重现。

## Sharing / 分享

将 `.skill` 文件发给任何 Cowork 用户，点击一下即可安装完整工作流。

| Skill | 用途 |
|-------|------|
| `billiard-ball.skill` | 台球 PBR 纹理 + Blender 材质 + GLB 导出 |
| `billiard-cue.skill` | 球杆纹理 + 8 部件 3D 模型 + PBR 材质 |
| `billiard-break.skill` | 开球动画（球杆→母球→球堆散射） |
