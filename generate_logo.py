import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Canvas setup
size = 512
img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 1. Base Squircle Shape (Rounded Rectangle)
margin = 24
r = 110
# Outer glow
for i in range(12, 0, -2):
    alpha = int(35 * (1 - i / 12))
    glow_box = [margin - i, margin - i, size - margin + i, size - margin + i]
    draw.rounded_rectangle(glow_box, radius=r + i, fill=(217, 107, 30, alpha))

# Dark Obsidian/Carbon Hearth Background
bg_box = [margin, margin, size - margin, size - margin]
draw.rounded_rectangle(bg_box, radius=r, fill=(18, 12, 8, 255), outline=(180, 75, 15, 230), width=6)

# Inner warm gradient overlay
inner_box = [margin + 6, margin + 6, size - margin - 6, size - margin - 6]
overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
ov_draw = ImageDraw.Draw(overlay)
for y in range(margin + 6, size - margin - 6):
    pct = (y - margin) / (size - 2 * margin)
    # Warm radial/gradient from top dark to bottom molten hearth
    r_val = int(24 + 70 * (pct ** 1.8))
    g_val = int(14 + 35 * (pct ** 2.2))
    b_val = int(10 + 10 * (pct ** 3))
    ov_draw.line([(margin + 6, y), (size - margin - 6, y)], fill=(r_val, g_val, b_val, 255))

# Mask overlay to squircle
mask = Image.new("L", (size, size), 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.rounded_rectangle(inner_box, radius=r - 6, fill=255)
img.paste(overlay, (0, 0), mask)

draw = ImageDraw.Draw(img)

# 2. Refractory Furnace Hearth Shell Arc (Crucible)
crucible_w = 340
crucible_h = 160
crucible_top = 260
cx = size // 2

# Molten Bath Radiant Core
bath_poly = [
    (cx - 150, crucible_top + 40),
    (cx - 110, crucible_top + 130),
    (cx + 110, crucible_top + 130),
    (cx + 150, crucible_top + 40),
]
# Draw crucible refractory wall
wall_poly = [
    (cx - 165, crucible_top + 30),
    (cx - 125, crucible_top + 145),
    (cx + 125, crucible_top + 145),
    (cx + 165, crucible_top + 30),
]
draw.polygon(wall_poly, fill=(45, 30, 22, 255), outline=(190, 80, 20, 240))

# Molten glowing liquid silicon metal
# Outer hot glow
for i in range(16, 0, -2):
    draw.ellipse([cx - 130 - i, crucible_top + 20 - i, cx + 130 + i, crucible_top + 90 + i], fill=(230, 81, 0, int(40 * (1 - i / 16))))

# Core liquid silicon pool
draw.ellipse([cx - 130, crucible_top + 25, cx + 130, crucible_top + 75], fill=(245, 124, 0, 255), outline=(255, 214, 0, 255), width=3)
draw.ellipse([cx - 95, crucible_top + 35, cx + 95, crucible_top + 65], fill=(255, 235, 59, 255))
draw.ellipse([cx - 60, crucible_top + 42, cx + 60, crucible_top + 58], fill=(255, 255, 255, 240))

# 3. 3-Phase Soderberg Carbon Electrodes
electrode_xs = [cx - 75, cx, cx + 75]
electrode_w = 38
electrode_top = 100
electrode_bottoms = [crucible_top + 22, crucible_top + 16, crucible_top + 22]

for idx, ex in enumerate(electrode_xs):
    ebot = electrode_bottoms[idx]
    # Electrode Carbon Column
    draw.rectangle([ex - electrode_w//2, electrode_top, ex + electrode_w//2, ebot], fill=(55, 58, 64, 255), outline=(120, 125, 135, 255), width=2)
    # Highlight rib
    draw.line([(ex - 5, electrode_top + 4), (ex - 5, ebot - 4)], fill=(160, 165, 175, 200), width=3)
    # Copper Terminal Clamp at Top
    draw.rectangle([ex - electrode_w//2 - 4, electrode_top - 6, ex + electrode_w//2 + 4, electrode_top + 16], fill=(184, 93, 25, 255), outline=(230, 138, 34, 255), width=2)
    # Hot Glowing Tip
    draw.rectangle([ex - electrode_w//2 + 2, ebot - 12, ex + electrode_w//2 - 2, ebot], fill=(255, 109, 0, 255))

    # Electric Arc Plasma Discharge beneath electrode
    arc_points = [
        (ex - 6, ebot),
        (ex + 8, ebot + 8),
        (ex - 7, ebot + 16),
        (ex + 4, ebot + 24),
    ]
    draw.line(arc_points, fill=(255, 255, 230, 255), width=3)
    draw.ellipse([ex - 12, ebot + 10, ex + 12, ebot + 34], fill=(255, 230, 80, 160))

# 4. Stylized Energy / AI Flame Crest
flame_cx = cx
flame_cy = 135
# Small flame spark
draw.polygon([(flame_cx, flame_cy - 48), (flame_cx + 14, flame_cy - 20), (flame_cx, flame_cy - 8), (flame_cx - 14, flame_cy - 20)], fill=(255, 215, 64, 255))
draw.polygon([(flame_cx, flame_cy - 38), (flame_cx + 7, flame_cy - 20), (flame_cx, flame_cy - 12), (flame_cx - 7, flame_cy - 20)], fill=(255, 255, 255, 255))

# 5. Bottom Typography / Badge
# "SILICAFORGE RL"
badge_y = size - margin - 56
draw.rounded_rectangle([cx - 165, badge_y - 20, cx + 165, badge_y + 24], radius=16, fill=(12, 8, 5, 245), outline=(217, 107, 30, 220), width=2)

try:
    font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 15)
except:
    font_bold = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Text SILICAFORGE
text1 = "SILICAFORGE"
bbox1 = draw.textbbox((0, 0), text1, font=font_bold)
w1 = bbox1[2] - bbox1[0]
draw.text((cx - 80, badge_y - 12), text1, font=font_bold, fill=(255, 248, 235, 255))

# Badge RL
draw.rounded_rectangle([cx + 95, badge_y - 11, cx + 145, badge_y + 14], radius=6, fill=(217, 107, 30, 255))
draw.text((cx + 106, badge_y - 10), "RL", font=font_small, fill=(255, 255, 255, 255))

# Subtitle under crucible
subtext = "28.5 MW SUBMERGED ARC FURNACE TWIN"
try:
    font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
except:
    font_tiny = ImageFont.load_default()
bbox_sub = draw.textbbox((0, 0), subtext, font=font_tiny)
w_sub = bbox_sub[2] - bbox_sub[0]
draw.text((cx - w_sub//2, crucible_top + 155), subtext, font=font_tiny, fill=(217, 140, 60, 230))

img.save("silicaforge_logo.png", "PNG")
print("Successfully generated silicaforge_logo.png (512x512)")
