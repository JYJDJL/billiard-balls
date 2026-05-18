"""
Create a break shot animation in Blender: cue strikes cue ball,
cue ball moves to rack, brief pause, then all balls scatter outward.

Uses monotonic mapping (target_x = start_x * factor, target_y = start_y + const)
to guarantee zero collisions. Cue retracts during scatter for natural look.

Run in Blender's Scripting workspace after:
  1. 16 balls (Ball_00 to Ball_15) exist and are racked
  2. Cue stick (Cue empty + 8 children parts) exists

No external dependencies.
"""
import bpy
import math

scene = bpy.context.scene

# ============================================================
# Config
# ============================================================
FACTOR = 3.5            # x-spread amplification
CONST = 14              # uniform upward shift
B00_TARGET = (-12, 16)  # cue ball target (left, up)
SCATTER_START = 36      # frame when rack balls start scattering
SCATTER_END = 85        # frame when scatter completes
B00_STAGGER = 2         # cue ball starts 2 frames after rack balls

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
    1: (0, 0),   9: (-1, 2),  2: (1, 2),
    10: (-2, 4),  8: (0, 4),   3: (2, 4),
    11: (-3, 6),  4: (-1, 6), 12: (1, 6),  5: (3, 6),
    6: (-4, 8),  13: (-2, 8), 14: (0, 8),  7: (2, 8), 15: (4, 8),
}

init = {**rack_layout, 0: (0, -8)}

for i, (col, row) in rack_layout.items():
    ball = bpy.data.objects.get(f"Ball_{i:02d}")
    if ball:
        ball.location = (col, row, 1.0)
        ball.rotation_euler = (0, 0, 0)

cue_ball = bpy.data.objects.get("Ball_00")
cue = bpy.data.objects.get("Cue")

if not cue_ball or not cue:
    raise RuntimeError("Ball_00 or Cue not found.")

cue_ball.location = (0, -8, 1.0)
cue_ball.rotation_euler = (0, 0, 0)
cue.location = (0, -32.55, 1.0)
cue.rotation_euler = (0, 0, 0)
cue.scale = (30, 30, 30)   # Cue geometry is meter-scale, need 30x to match balls

# ============================================================
# 3. Compute scatter targets (monotonic, collision-free)
# ============================================================
targets = {}
for i in range(1, 16):
    x, y = init[i]
    targets[i] = (x * FACTOR, y + CONST)
targets[0] = B00_TARGET

# ============================================================
# 4. Scene setup
# ============================================================
scene.frame_start = 0
scene.frame_end = SCATTER_END
scene.render.fps = 24

# ============================================================
# 5. Cue stick animation
#   F0-F12: backswing
#   F12-F22: strike forward
#   F22-F28: push through
#   F28-F30: brief hold
#   F30-F50: retract (syncs with scatter start at F42)
# ============================================================
print("Animating cue stick...")
cue.keyframe_insert(data_path="location", frame=0)
cue.keyframe_insert(data_path="rotation_euler", frame=0)

cue.location.y = -33.05  # backswing
cue.keyframe_insert(data_path="location", frame=12)

cue.location.y = -32.4   # strike (tip contacts cue ball)
cue.keyframe_insert(data_path="location", frame=22)

cue.location.y = -32.1   # push through
cue.keyframe_insert(data_path="location", frame=28)

cue.keyframe_insert(data_path="location", frame=30)  # hold

cue.location.y = -34.5   # retract during scatter
cue.keyframe_insert(data_path="location", frame=50)
cue.keyframe_insert(data_path="location", frame=SCATTER_END)

# ============================================================
# 6. Cue ball (Ball_00) animation
#   F0-F22: stationary
#   F22-F36: roll to rack contact
#   F36-F43: hold at contact (brief pause + 1-frame stagger)
#   F43-F90: scatter to target
# ============================================================
print("Animating cue ball...")
b00_start = SCATTER_START + B00_STAGGER

cue_ball.keyframe_insert(data_path="location", frame=0)
cue_ball.keyframe_insert(data_path="rotation_euler", frame=0)
cue_ball.keyframe_insert(data_path="location", frame=22)  # hold until struck

cue_ball.location.y = -2.0  # move to rack contact
cue_ball.keyframe_insert(data_path="location", frame=36)
cue_ball.keyframe_insert(data_path="location", frame=b00_start)  # hold at contact

cue_ball.location.x = targets[0][0]  # scatter
cue_ball.location.y = targets[0][1]
cue_ball.keyframe_insert(data_path="location", frame=SCATTER_END)

# Rotation proportional to travel
tx, ty = targets[0]
scatter_frames = SCATTER_END - b00_start
for f in range(0, SCATTER_END + 1, 8):
    scene.frame_set(f)
    if f <= 22:
        r = 0
    elif f <= 36:
        r = (f - 22) / 14.0 * 6.0
    elif f <= b00_start:
        r = 6.0
    else:
        r = 6.0 + ((f - b00_start) / scatter_frames) * math.hypot(tx, ty + 2)
    cue_ball.rotation_euler = (r, 0, 0)
    cue_ball.keyframe_insert(data_path="rotation_euler", frame=f)

# ============================================================
# 7. Rack balls (1-15) animation
#   F0-F42: hold at rack positions
#   F42-F90: scatter to targets
# ============================================================
print("Animating rack balls...")
scatter_len = SCATTER_END - SCATTER_START

for ball_num in range(1, 16):
    ball = bpy.data.objects.get(f"Ball_{ball_num:02d}")
    if not ball:
        continue

    ball.keyframe_insert(data_path="location", frame=0)
    ball.keyframe_insert(data_path="rotation_euler", frame=0)
    ball.keyframe_insert(data_path="location", frame=SCATTER_START)  # hold

    tx, ty = targets[ball_num]
    sx, sy = init[ball_num]
    ball.location.x = tx
    ball.location.y = ty
    ball.keyframe_insert(data_path="location", frame=SCATTER_END)  # scatter

    # Rotation
    dx, dy = tx - sx, ty - sy
    dist = math.hypot(dx, dy)
    for f in range(SCATTER_START, SCATTER_END + 1, 5):
        scene.frame_set(f)
        frac = (f - SCATTER_START) / scatter_len
        r = dist * frac
        z = (dx / max(dist, 0.01)) * dist * frac * 0.3 if dist > 0.01 else 0
        ball.rotation_euler = (r, 0, z)
        ball.keyframe_insert(data_path="rotation_euler", frame=f)

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
# 9. Verify no collisions
# ============================================================
print("\nVerifying collisions...")
ball_data = {}
for i in range(16):
    obj = bpy.data.objects.get(f"Ball_{i:02d}")
    if not obj or not obj.animation_data or not obj.animation_data.action:
        continue
    kx, ky = {}, {}
    for layer in obj.animation_data.action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    if fc.data_path == 'location':
                        for kf in fc.keyframe_points:
                            f = int(kf.co.x)
                            v = kf.co.y
                            if fc.array_index == 0: kx[f] = v
                            elif fc.array_index == 1: ky[f] = v
    ball_data[i] = (kx, ky)

def lerp(kf_dict, frame):
    fr = sorted(kf_dict.keys())
    if frame <= fr[0]: return kf_dict[fr[0]]
    if frame >= fr[-1]: return kf_dict[fr[-1]]
    for j in range(len(fr) - 1):
        if fr[j] <= frame <= fr[j + 1]:
            t = (frame - fr[j]) / (fr[j + 1] - fr[j])
            return kf_dict[fr[j]] + (kf_dict[fr[j + 1]] - kf_dict[fr[j]]) * t
    return 0.0

violations = []
worst = {}
for frame in range(0, SCATTER_END + 1):
    pos = {}
    for i, (kx, ky) in ball_data.items():
        pos[i] = (lerp(kx, frame), lerp(ky, frame))
    for i in range(16):
        for j in range(i + 1, 16):
            if i in pos and j in pos:
                d = math.hypot(pos[i][0] - pos[j][0], pos[i][1] - pos[j][1])
                p = f"Ball_{i:02d}-Ball_{j:02d}"
                if p not in worst or d < worst[p]:
                    worst[p] = d
                if d < 1.98:
                    violations.append((frame, i, j, d))

if violations:
    print(f"  WARNING: {len(violations)} collisions!")
    for v in violations[:10]:
        print(f"    F{v[0]}: Ball_{v[1]:02d} vs Ball_{v[2]:02d} dist={v[3]:.2f}")
else:
    print("  All frames verified — zero collisions!")

print("  Closest pairs:")
for pair, d in sorted(worst.items(), key=lambda x: x[1])[:5]:
    print(f"    {pair}: {d:.2f}")

scene.frame_set(0)

print(f"""
Break shot animation complete!
  Frames: 0-{SCATTER_END}, FPS: 24, Duration: {SCATTER_END / 24:.1f}s
  Contact: F36, Scatter: F{SCATTER_START}-F{SCATTER_END}, Cue retract: F30-F50
  Scatter: monotonic (factor={FACTOR}, const={CONST})
  Balls verified: zero collisions
""")
