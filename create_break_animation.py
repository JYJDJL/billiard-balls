"""
Create a break shot animation in Blender: cue strikes cue ball,
cue ball hits the rack apex, balls scatter. Keyframe animation.

Run in Blender's Scripting workspace after:
  1. 16 balls (Ball_00 to Ball_15) exist and are racked
  2. Cue stick (Cue empty + 8 children parts) exists

No external dependencies.
"""
import bpy
import math

scene = bpy.context.scene
ball_radius = 1.0
cue_base_y = -32.55   # cue empty Y so tip is at Y=-9.15 (behind cue ball back at -9.0)

# ============================================================
# 1. Clean old animation
# ============================================================
print("Clearing old animation...")
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

# ============================================================
# 2. Reset all positions
# ============================================================
print("Resetting positions...")
rack_layout = {
    1: (0, 0),   2: (-1, 2),  3: (1, 2),
    4: (-2, 4),  8: (0, 4),   5: (2, 4),
    6: (-3, 6),  7: (-1, 6),  9: (1, 6),  10: (3, 6),
    11: (-4, 8), 12: (-2, 8), 13: (0, 8), 14: (2, 8), 15: (4, 8),
}

for i, (col, row) in rack_layout.items():
    ball = bpy.data.objects.get(f"Ball_{i:02d}")
    if ball:
        ball.location = (col * ball_radius, row * ball_radius, 1.0)
        ball.rotation_euler = (0, 0, 0)

cue_ball = bpy.data.objects.get("Ball_00")
cue = bpy.data.objects.get("Cue")

if not cue_ball or not cue:
    raise RuntimeError("Ball_00 or Cue not found. Run create_cue_in_blender.py first.")

cue_ball.location = (0, -8, 1.0)
cue_ball.rotation_euler = (0, 0, 0)

cue.location = (0, cue_base_y, 1.0)
cue.rotation_euler = (0, 0, 0)
cue.scale = (30, 30, 30)

# ============================================================
# 3. Scene setup
# ============================================================
scene.frame_start = 0
scene.frame_end = 120
scene.render.fps = 24

# ============================================================
# 4. Cue stick animation
# ============================================================
print("Animating cue stick...")
cue.keyframe_insert(data_path="location", frame=0)
cue.keyframe_insert(data_path="rotation_euler", frame=0)

# Backswing: 0-12
cue.location.y = cue_base_y - 0.8
cue.keyframe_insert(data_path="location", frame=12)

# Strike: 12-20, tip contacts ball back at Y=-9.0
cue.location.y = -32.4   # tip at -32.4 + 30*0.78 = -9.0
cue.keyframe_insert(data_path="location", frame=20)

# Push through: 20-25
cue.location.y = -31.9   # tip at -8.5
cue.keyframe_insert(data_path="location", frame=25)

# Hold briefly: 25-30
cue.keyframe_insert(data_path="location", frame=30)

# Retract: 30-90
cue.location.y = cue_base_y - 4.0
cue.keyframe_insert(data_path="location", frame=90)
cue.keyframe_insert(data_path="location", frame=120)

# ============================================================
# 5. Cue ball (Ball_00) animation
# ============================================================
print("Animating cue ball...")
cue_ball.keyframe_insert(data_path="location", frame=0)
cue_ball.keyframe_insert(data_path="rotation_euler", frame=0)
cue_ball.keyframe_insert(data_path="location", frame=20)  # hold until struck

# Accelerate after strike
cue_ball.location.y = -7.0
cue_ball.keyframe_insert(data_path="location", frame=24)
cue_ball.location.y = -4.5
cue_ball.keyframe_insert(data_path="location", frame=32)

# Contact with ball 1: centers exactly 2.0 apart
cue_ball.location.y = -2.0
cue_ball.keyframe_insert(data_path="location", frame=44)

# Push phase
cue_ball.location.y = -0.5
cue_ball.keyframe_insert(data_path="location", frame=50)

# Deflect to the left
cue_ball.location.y = 2.0
cue_ball.location.x = -2.5
cue_ball.keyframe_insert(data_path="location", frame=62)
cue_ball.location.y = 5.0
cue_ball.location.x = -5.0
cue_ball.keyframe_insert(data_path="location", frame=80)
cue_ball.location.y = 8.0
cue_ball.location.x = -8.0
cue_ball.keyframe_insert(data_path="location", frame=105)
cue_ball.location.y = 10.0
cue_ball.location.x = -10.0
cue_ball.keyframe_insert(data_path="location", frame=120)

# Rotation: rolling proportional to travel
for frame in range(20, 121, 10):
    scene.frame_set(frame)
    travel = cue_ball.location.y - (-8.0)
    rotations = travel / (2 * math.pi * ball_radius)
    cue_ball.rotation_euler.x = rotations * 2 * math.pi
    if frame > 50:
        cue_ball.rotation_euler.z = (abs(cue_ball.location.x) / 10.0) * 2 * math.pi
    cue_ball.keyframe_insert(data_path="rotation_euler", frame=frame)

# ============================================================
# 6. Ball 1 (apex) animation — deflects to avoid Ball 8 & 13
# ============================================================
print("Animating ball 1 (apex)...")
ball1 = bpy.data.objects.get("Ball_01")
ball1.location = (0, 0, 1.0)
ball1.rotation_euler = (0, 0, 0)
ball1.keyframe_insert(data_path="location", frame=0)
ball1.keyframe_insert(data_path="rotation_euler", frame=0)
ball1.keyframe_insert(data_path="location", frame=44)  # hold until contact

# Push forward (limited: Y=1.5 is safe from Ball 8 at Y=4)
ball1.location.y = 1.5
ball1.location.x = 0
ball1.keyframe_insert(data_path="location", frame=50)

# Deflect left, clearing X=0 before reaching Y=4
ball1.location.y = 3.5
ball1.location.x = -3.5
ball1.keyframe_insert(data_path="location", frame=58)

ball1.location.y = 6.0
ball1.location.x = -6.5
ball1.keyframe_insert(data_path="location", frame=70)

ball1.location.y = 9.5
ball1.location.x = -10.0
ball1.keyframe_insert(data_path="location", frame=90)

ball1.location.y = 13.5
ball1.location.x = -14.0
ball1.keyframe_insert(data_path="location", frame=120)

# Rotation
for frame in [44, 50, 58, 70, 90, 120]:
    scene.frame_set(frame)
    travel = math.sqrt(ball1.location.x**2 + (ball1.location.y - 0)**2)
    rotations = travel / (2 * math.pi * ball_radius)
    ball1.rotation_euler.x = rotations * 2 * math.pi * 0.8
    if travel > 0.01:
        ball1.rotation_euler.z = (ball1.location.x / travel) * rotations * 2 * math.pi * 0.5
    ball1.keyframe_insert(data_path="rotation_euler", frame=frame)

# ============================================================
# 7. Rack balls (2-15) scatter
# ============================================================
print("Animating rack balls...")
scatter_def = {
    2:  (-3.5, 10, 48, 90),
    3:  (3.5, 12, 50, 92),
    4:  (-7, 13, 52, 95),
    8:  (0, 18, 55, 100),
    5:  (6, 10, 52, 93),
    6:  (-8, 18, 56, 100),
    7:  (-3, 22, 58, 100),
    9:  (3, 20, 58, 100),
    10: (8, 20, 60, 100),
    11: (-10, 24, 62, 105),
    12: (-5, 28, 64, 108),
    13: (0, 30, 66, 110),
    14: (5, 26, 64, 108),
    15: (10, 22, 62, 105),
}

for ball_num, (tx, ty, start_f, end_f) in scatter_def.items():
    ball = bpy.data.objects.get(f"Ball_{ball_num:02d}")
    if not ball:
        continue

    ix, iy = ball.location.x, ball.location.y

    ball.keyframe_insert(data_path="location", frame=0)
    ball.keyframe_insert(data_path="rotation_euler", frame=0)
    ball.keyframe_insert(data_path="location", frame=start_f - 1)

    ball.location.x = tx
    ball.location.y = ty
    ball.keyframe_insert(data_path="location", frame=end_f)
    ball.keyframe_insert(data_path="location", frame=120)

    # Rotation: proportional to travel
    dx, dy = tx - ix, ty - iy
    dist = math.sqrt(dx*dx + dy*dy)
    total_rot = dist / (2 * math.pi * ball_radius)

    for frame in range(start_f, min(end_f + 1, 121), 10):
        scene.frame_set(frame)
        frac = (frame - start_f) / max(end_f - start_f, 1)
        ball.rotation_euler.x = total_rot * 2 * math.pi * frac
        ball.rotation_euler.z = (dx / max(dist, 0.01)) * total_rot * 2 * math.pi * frac * 0.3
        ball.keyframe_insert(data_path="rotation_euler", frame=frame)

# ============================================================
# 8. Set LINEAR interpolation
# ============================================================
print("Setting interpolation...")
count = 0
for obj in bpy.data.objects:
    if not (obj.animation_data and obj.animation_data.action):
        continue
    action = obj.animation_data.action
    for layer in action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fcurve in cb.fcurves:
                    for kf in fcurve.keyframe_points:
                        kf.interpolation = 'LINEAR'
                        count += 1

print(f"  {count} keyframes set to LINEAR")

# ============================================================
# 9. Verify no clipping
# ============================================================
print("\nVerifying collisions...")
ball8 = bpy.data.objects.get("Ball_08")
ball13 = bpy.data.objects.get("Ball_13")
min_d8, min_d13 = 999, 999

for frame in range(44, 121):
    scene.frame_set(frame)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    b1 = ball1.evaluated_get(depsgraph).matrix_world.translation
    b8 = ball8.evaluated_get(depsgraph).matrix_world.translation
    b13 = ball13.evaluated_get(depsgraph).matrix_world.translation

    d8 = math.sqrt((b1.x - b8.x)**2 + (b1.y - b8.y)**2)
    d13 = math.sqrt((b1.x - b13.x)**2 + (b1.y - b13.y)**2)

    if d8 < min_d8:
        min_d8 = d8
    if d13 < min_d13:
        min_d13 = d13

ok = min(min_d8, min_d13) >= 1.99
print(f"  Ball 1 vs Ball 8:  min distance {min_d8:.2f} {'OK' if min_d8 >= 1.99 else 'CLIPPING!'}")
print(f"  Ball 1 vs Ball 13: min distance {min_d13:.2f} {'OK' if min_d13 >= 1.99 else 'CLIPPING!'}")
print(f"\n{'All clear!' if ok else 'CLIPPING DETECTED — adjust trajectory.'}")

# Reset to frame 0
scene.frame_set(0)

print(f"""
Break shot animation created!
  Frames: 0-120, FPS: 24, Duration: {120/24:.1f}s
  Cue ball: {cue_ball.location}
  Ball 1: {ball1.location}
  Press SPACE to play.
""")
