"""Generate 1920x1080 storyboard timeline PNGs for GitHub PR #15 / web-agent review."""

import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WS_ROOT = Path(__file__).resolve().parents[1]
RENDERS_DIR = WS_ROOT / "renders"
FRAMES_V71_DIR = RENDERS_DIR / "frames_v7_1"
V70_MP4 = RENDERS_DIR / "v7_0_baseline" / "EP02_V7_ARGON_CINEMATIC_DEMO_18s.mp4"
FFMPEG_EXE = Path(r"D:\Creativity_CAPY_BK_EP01_Assets_For_Codex\.capy-tools\python\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe")


def load_fonts():
    try:
        return (
            ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 30),
            ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 21),
            ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 19),
            ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 16),
        )
    except OSError:
        f = ImageFont.load_default()
        return f, f, f, f


def build_v71_3x3_storyboard(fonts):
    f_hdr, f_sub, f_tag, f_cap = fonts
    canvas = Image.new("RGB", (1920, 1080), (14, 18, 24))
    draw = ImageDraw.Draw(canvas)

    draw.text((36, 20), "EP02 V7.1 — 18s CINEMATIC ANIMATION STORYBOARD (30 FPS / 540 FRAMES)", fill=(242, 178, 36), font=f_hdr)
    draw.text((36, 60), "Siemens NX V2 -> MATLAB R2026b (< 0.004 mm QA PASS) -> Blender 5.3 EEVEE Raytracing (RTX A3000 GPU, 808.52s)", fill=(195, 208, 222), font=f_sub)

    milestones = [
        (1,   "F001 (0.0s) · LOW Hero + I-Beam Plinth"),
        (60,  "F060 (2.0s) · Lifting & Soil Clods Drop"),
        (120, "F120 (4.0s) · End Establishing -> Push-In"),
        (185, "F185 (6.1s) · Close-Up Chrome, Bolts & Hoses"),
        (260, "F260 (8.6s) · Cutaway Reveal Open + Reticles"),
        (331, "F331 (11.0s) · Fluid Pulse Waves + Live HUD"),
        (400, "F400 (13.3s) · Powered Lift Cutaway Progression"),
        (480, "F480 (16.0s) · Cutaway Sealed + Wide Pull-Back"),
        (540, "F540 (18.0s) · HIGH Completion Hold"),
    ]

    tile_w, tile_h = 592, 294  # ~16:9 slightly cropped or padded cleanly; actually exact 16:9 at 520x292: 520*3=1560 or 544x306!
    # Check 3 rows of 276px + gap = 828px + header 100px = 928px -> 496 x 279 (exact 16:9!)
    tile_w, tile_h = 544, 306  # wait: 3*306 = 918 + 2*20 gaps + 100 header = 1058 -> fits inside 1080 cleanly!
    gap_x = 34
    gap_y = 18
    x_start = (1920 - (3 * tile_w + 2 * gap_x)) // 2  # (1920 - 1700)/2 = 110
    y_start = 104

    for idx, (fnum, caption) in enumerate(milestones):
        row, col = divmod(idx, 3)
        x = x_start + col * (tile_w + gap_x)
        y = y_start + row * (tile_h + gap_y)
        fpath = FRAMES_V71_DIR / f"ep02_v71_{fnum:04d}.png"
        im = Image.open(fpath).convert("RGB").resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        canvas.paste(im, (x, y))
        draw.rectangle([x - 1, y - 1, x + tile_w + 1, y + tile_h + 1], outline=(85, 98, 118), width=2)
        draw.rectangle([x + 6, y + tile_h - 32, x + tile_w - 6, y + tile_h - 4], fill=(12, 16, 22))
        draw.text((x + 14, y + tile_h - 28), caption, fill=(242, 200, 100), font=f_cap)

    out_path = RENDERS_DIR / "STORYBOARD_V7_1_18S_TIMELINE.png"
    canvas.save(out_path, optimize=True)
    print("SAVED_STORYBOARD:", out_path)


def extract_v70_frame(timestamp_s: float, dst_png: Path):
    cmd = [
        str(FFMPEG_EXE), "-y", "-v", "error",
        "-ss", f"{timestamp_s:.3f}", "-i", str(V70_MP4),
        "-frames:v", "1", str(dst_png),
    ]
    subprocess.run(cmd, check=True)


def build_v70_vs_v71_timeline(fonts):
    f_hdr, f_sub, f_tag, f_cap = fonts
    canvas = Image.new("RGB", (1920, 1080), (14, 18, 24))
    draw = ImageDraw.Draw(canvas)

    draw.text((36, 22), "EP02 V7.0 vs V7.1 ANIMATION TIMELINE COMPARISON (2.0s -> 6.1s -> 11.0s -> 16.0s)", fill=(242, 178, 36), font=f_hdr)
    draw.text((36, 62), "Top Row: V7.0 Baseline  |  Bottom Row: V7.1 Polish (AO + I-Beam + Bezier Hoses + Soil Clods + Fluid Wave + Dynamic HUD)", fill=(195, 208, 222), font=f_sub)

    slots = [
        (60,  2.00, "t = 2.0s (F060) · Lifting + Soil Clods"),
        (185, 6.13, "t = 6.1s (F185) · Cylinder Close-Up"),
        (331, 11.00, "t = 11.0s (F331) · Cutaway Reveal"),
        (480, 15.97, "t = 16.0s (F480) · Wide Pull-Back"),
    ]

    tile_w, tile_h = 448, 252  # exact 16:9; 4*448 + 3*20 = 1852 -> x_start = 34
    gap_x = 20
    x_start = 34
    y_top_lbl = 128
    y_row0 = 168
    y_bot_lbl = 480
    y_row1 = 520

    draw.rectangle([34, y_top_lbl, 340, y_top_lbl + 32], fill=(42, 48, 58))
    draw.text((46, y_top_lbl + 4), "BEFORE · V7.0 BASELINE", fill=(220, 228, 238), font=f_tag)

    draw.rectangle([34, y_bot_lbl, 380, y_bot_lbl + 32], fill=(242, 178, 36))
    draw.text((46, y_bot_lbl + 4), "AFTER · V7.1 CINEMATIC POLISH", fill=(16, 20, 26), font=f_tag)

    with tempfile.TemporaryDirectory() as tmpd:
        tmp_dir = Path(tmpd)
        for col, (fnum, ts, label) in enumerate(slots):
            x = x_start + col * (tile_w + gap_x)
            # Column header pill above Row 0
            draw.text((x + 6, y_row0 + tile_h + 10), label, fill=(210, 220, 232), font=f_tag)

            v70_png = tmp_dir / f"v70_{fnum}.png"
            extract_v70_frame(ts, v70_png)
            im0 = Image.open(v70_png).convert("RGB").resize((tile_w, tile_h), Image.Resampling.LANCZOS)
            canvas.paste(im0, (x, y_row0))
            draw.rectangle([x - 1, y_row0 - 1, x + tile_w + 1, y_row0 + tile_h + 1], outline=(105, 118, 138), width=2)

            v71_png = FRAMES_V71_DIR / f"ep02_v71_{fnum:04d}.png"
            im1 = Image.open(v71_png).convert("RGB").resize((tile_w, tile_h), Image.Resampling.LANCZOS)
            canvas.paste(im1, (x, y_row1))
            draw.rectangle([x - 1, y_row1 - 1, x + tile_w + 1, y_row1 + tile_h + 1], outline=(242, 178, 36), width=3)

    draw.text((36, 840), "Ghi chu kiem duyet nhanh:", fill=(242, 178, 36), font=f_tag)
    draw.text((36, 874), "- F060 (2.0s): Bo sung be dam chu I + 8 bu-long neo M36, 4 duong ong thep lung can, 6 ong mem Bezier cung 14 vien dat roi tu gau.", fill=(205, 215, 225), font=f_sub)
    draw.text((36, 908), "- F185 (6.1s): AO + Pointiness tao bong tiep xuc quanh co bit & vong 6 bu-long M20; hai ty chrome khong bien dang (zero_metal_scaling = True).", fill=(205, 215, 225), font=f_sub)
    draw.text((36, 942), "- F331 (11.0s): Mat cat lo ro 2 dai dong + phot PTFE, xung song dau do/xanh, reticle A/B, thanh tien trinh & thong so HUD nhay dong theo khung.", fill=(205, 215, 225), font=f_sub)
    draw.text((36, 976), "- F480 (16.0s): Vo xi lanh khep kin dung nhip 14.0s, camera lui ra toan canh quay Depth of Field + Compositor Fog Glow.", fill=(205, 215, 225), font=f_sub)

    out_path = RENDERS_DIR / "STORYBOARD_V7_0_VS_V7_1_TIMELINE.png"
    canvas.save(out_path, optimize=True)
    print("SAVED_TIMELINE_CMP:", out_path)


def main():
    fonts = load_fonts()
    build_v71_3x3_storyboard(fonts)
    build_v70_vs_v71_timeline(fonts)


if __name__ == "__main__":
    main()
