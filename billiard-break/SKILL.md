# Billiard Break Shot Animation

在 Blender 中创建台球开球动画：球杆击打母球，母球撞击球堆，彩球四散。手写关键帧动画（非刚体模拟）。

## Rules

1. **使用中文回答** — 所有回复、说明、错误信息均使用中文。
2. **结果不需要渲染** — 用户可以直接在 Blender 中查看结果，不需要截图或渲染预览。完成操作后直接告知用户结果即可。

## 前提条件

- 16 个台球模型已创建（Ball_00 到 Ball_15）
- 球杆模型已创建（Cue 空物体 + 8 个子部件）
- 台球按标准 8 球规则摆放完毕

## 动画时间线（120 帧 / 24fps / 5 秒）

| 阶段 | 帧范围 | 内容 |
|------|--------|------|
| 后拉蓄力 | 0-12 | 球杆向后拉 0.8 单位 |
| 前冲击球 | 12-20 | 球杆前冲，杆头在第 20 帧精确接触母球背面 |
| 母球加速 | 20-44 | 母球加速冲向球堆 |
| 母球撞顶点球 | 44 | 母球与 1 号球精确接触（球心距 = 2.0 = 半径之和） |
| 能量传递 | 44-54 | 母球偏转向左，1 号球被推前冲 |
| 1 号球偏转 | 50-58 | 1 号球向 -X 方向偏转，避开身后 8 号和 13 号 |
| 彩球散射 | 55-120 | 所有彩球四散滚动 |

## 关键参数

```
CUE_BASE_Y = -32.55   # 球杆空物体 Y 坐标（scale=30，杆头局部 Y=0.78，杆头世界 Y = -32.55 + 30×0.78 = -9.15）
BALL_RADIUS = 1.0      # 台球半径
CONTACT_DISTANCE = 2.0  # 球心接触距离（半径之和）
FPS = 24
```

## 球堆布局（标准 8 球规则）

```
行1（顶点）: 1 号球            Y=0
行2:        9, 2               Y=2
行3:       10, 8, 3            Y=4  （8 号球居中）
行4:       11, 4, 12, 5        Y=6
行5:       6, 13, 14, 7, 15    Y=8
母球（0 号）:                  Y=-8
```

行间距 = √3 × 球半径 ≈ 1.732

## 动画脚本结构

以下脚本在 Blender Scripting 工作区执行：

### 1. 清理旧动画

```python
for name in ["Cue"] + [f"Ball_{i:02d}" for i in range(16)]:
    obj = bpy.data.objects.get(name)
    if obj and obj.animation_data:
        obj.animation_data_clear()
    if name == "Cue" and obj:
        for child in obj.children:
            if child.animation_data:
                child.animation_data_clear()
for action in list(bpy.data.actions):
    bpy.data.actions.remove(action)
```

### 2. 重置所有位置

```python
# 球堆布局
rack_layout = {
    1: (0, 0),   2: (-1, 2),  3: (1, 2),
    4: (-2, 4),  8: (0, 4),   5: (2, 4),
    6: (-3, 6),  7: (-1, 6),  9: (1, 6),  10: (3, 6),
    11: (-4, 8), 12: (-2, 8), 13: (0, 8), 14: (2, 8), 15: (4, 8),
}
for i, (col, row) in rack_layout.items():
    ball = bpy.data.objects.get(f"Ball_{i:02d}")
    ball.location = (col * ball_radius, row * ball_radius, 1.0)
    ball.rotation_euler = (0, 0, 0)

# 母球
cue_ball = bpy.data.objects.get("Ball_00")
cue_ball.location = (0, -8, 1.0)

# 球杆
cue_base_y = -32.55
cue.location = (0, cue_base_y, 1.0)
cue.scale = (30, 30, 30)
```

### 3. 球杆动画

```python
# 0 帧：初始位置
cue.keyframe_insert(data_path="location", frame=0)
# 12 帧：后拉结束
cue.location.y = cue_base_y - 0.8
cue.keyframe_insert(data_path="location", frame=12)
# 20 帧：杆头接触母球背面（杆头世界 Y = cue.y + 30*0.78 = -32.4 + 23.4 = -9.0）
cue.location.y = -32.4
cue.keyframe_insert(data_path="location", frame=20)
# 25 帧：推击
cue.location.y = -31.9
cue.keyframe_insert(data_path="location", frame=25)
# 30 帧：短暂停顿
cue.keyframe_insert(data_path="location", frame=30)
# 90 帧：回撤
cue.location.y = cue_base_y - 4.0
cue.keyframe_insert(data_path="location", frame=90)
```

### 4. 母球动画

```python
# 0-20 帧：静止
cue_ball.keyframe_insert(data_path="location", frame=0)
cue_ball.keyframe_insert(data_path="location", frame=20)
# 24 帧：被推击移动
cue_ball.location.y = -7.0
cue_ball.keyframe_insert(data_path="location", frame=24)
# 32 帧：加速中
cue_ball.location.y = -4.5
cue_ball.keyframe_insert(data_path="location", frame=32)
# 44 帧：精确接触 1 号球（母球球心 Y=-2，1 号球心 Y=0，距离=2.0）
cue_ball.location.y = -2.0
cue_ball.keyframe_insert(data_path="location", frame=44)
# 50 帧：推挤中
cue_ball.location.y = -0.5
cue_ball.keyframe_insert(data_path="location", frame=50)
# 之后母球偏转向左 -X
```

### 5. 1 号球（顶点）动画 — 防穿模偏转

```python
# 0-44 帧：静止
ball1.keyframe_insert(data_path="location", frame=44)
# 50 帧：前冲至 Y=1.5（安全距离，距 8 号球 Y=4 仍有 2.5 单位）
ball1.location.y = 1.5
ball1.keyframe_insert(data_path="location", frame=50)
# 58 帧：快速向 -X 偏转，避开 X=0 线
ball1.location.y = 3.5
ball1.location.x = -3.5
ball1.keyframe_insert(data_path="location", frame=58)
# 继续偏转远离
ball1.location.y = 6.0; ball1.location.x = -6.5   # F70
ball1.location.y = 9.5; ball1.location.x = -10.0  # F90
ball1.location.y = 13.5; ball1.location.x = -14.0 # F120
```

### 6. 彩球散射

每个球从初始位置向四周散射，起始帧和速度各不相同，模拟从内向外扩散的物理效果。

```python
scatter_def = {
    2: (-3.5, 10, 48, 90),   3: (3.5, 12, 50, 92),
    4: (-7, 13, 52, 95),     8: (0, 18, 55, 100),
    5: (6, 10, 52, 93),      6: (-8, 18, 56, 100),
    7: (-3, 22, 58, 100),    9: (3, 20, 58, 100),
    10: (8, 20, 60, 100),    11: (-10, 24, 62, 105),
    12: (-5, 28, 64, 108),   13: (0, 30, 66, 110),
    14: (5, 26, 64, 108),    15: (10, 22, 62, 105),
}
# 格式: (target_x, target_y, start_frame, end_frame)
```

### 7. 设置插值 + 旋转

```python
# 线性插值
for obj in bpy.data.objects:
    if obj.animation_data and obj.animation_data.action:
        for layer in action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    for fcurve in cb.fcurves:
                        for kf in fcurve.keyframe_points:
                            kf.interpolation = 'LINEAR'

# 滚动旋转：旋转角度 = 位移 / (2πr)
# r = 1.0, 一圈 = 2π ≈ 6.283 单位距离
```

## 穿模预防要点

手写关键帧动画的核心难点是避免穿模。必须遵守：

1. **球心距 ≥ 2.0**（两个半径之和）——逐帧验证
2. **同轨避让**：X=0 线上有 1 号(0,0)、8 号(0,4)、13 号(0,8)，1 号必须在到达 Y=4 之前离开 X=0
3. **时间差**：后面的球等前面的球过去后再启动
4. **逐帧验证**：对所有球对的最近距离做遍历检查

## 与刚体模拟的对比

| 方面 | 手写关键帧 | 刚体模拟 |
|------|-----------|---------|
| 穿模 | 需要手动避免 | 物理引擎自动防止 |
| 轨迹 | 完全可控 | 不可预测 |
| 复杂度 | O(球数) 手写 | O(球数²) 自动碰撞 |
| 二次碰撞 | 不支持 | 自动处理 |
| 调试 | 逐帧检查 | 参数调优 |

当前项目因 Blender 5.1 会话中刚体模拟不工作（ptcache.bake_all 执行后球不动），故采用手写关键帧方案。

## 播放方式

在 Blender 时间轴中按空格键播放。帧范围：0-120，帧率：24fps。
