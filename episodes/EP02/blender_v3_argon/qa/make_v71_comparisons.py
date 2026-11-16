"""Create crisp side-by-side Before (V7.0) vs After (V7.1) 1920x1080 comparison sheets."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def make_comparison_image(v70_path: Path, v71_path: Path, out_path: Path, label: str):
    im0 = Image.open(v70_path).convert("RGB").resize((940, 529), Image.Resampling.LANCZOS)
    im1 = Image.open(v71_path).convert("RGB").resize((940, 529), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (1920, 1080), (16, 20, 26))
    draw = ImageDraw.Draw(canvas)

    # Load clean Windows TrueType font or default fallback
    try:
        font_hdr = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 34)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 24)
        font_tag = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 22)
    except OSError:
        font_hdr = font_sub = font_tag = ImageFont.load_default()

    draw.text((40, 32), f"EP02 V7 vs V7.1 CINEMATIC UPGRADE  |  {label}", fill=(242, 178, 36), font=font_hdr)
    draw.text((40, 82), "Siemens NX V2 Geometry + MATLAB R2026b Kinematics (< 0.004 mm)  |  Blender 5.3 Cycles OPTIX",
              fill=(195, 208, 222), font=font_sub)

    y_img = 210
    canvas.paste(im0, (16, y_img))
    canvas.paste(im1, (964, y_img))

    # Crisp borders & labels
    draw.rectangle([14, y_img - 2, 958, y_img + 531], outline=(110, 125, 145), width=2)
    draw.rectangle([962, y_img - 2, 1906, y_img + 531], outline=(242, 178, 36), width=3)

    draw.rectangle([16, y_img - 44, 340, y_img - 6], fill=(42, 48, 58))
    draw.text((28, y_img - 37), "BEFORE · V7.0 BASELINE", fill=(215, 225, 235), font=font_tag)

    draw.rectangle([964, y_img - 44, 1340, y_img - 6], fill=(242, 178, 36))
    draw.text((976, y_img - 37), "AFTER · V7.1 CINEMATIC POLISH", fill=(18, 22, 28), font=font_tag)

    notes = [
        ("V7.0", "Pointiness (không chạy trong EEVEE), bệ hộp đơn giản, không chốt bu-lông, dầu tĩnh không xung dòng, không DOF.", (180, 192, 208)),
        ("V7.1", "Ambient Occlusion + Pointiness (EEVEE & Cycles), bệ dầm chữ I + bu-lông M20/M36, 4 ống thép cần,", (245, 212, 120)),
        ("    ", "6 ống mềm Bezier võng thực + đất rơi, mặt cắt có xung dòng dầu + reticle + HUD động, DOF + Glare.", (245, 212, 120)),
    ]
    y_n = 790
    for tag, txt, col in notes:
        prefix = f"[{tag}] " if tag.strip() else "       "
        draw.text((40, y_n), f"{prefix}{txt}", fill=col, font=font_sub)
        y_n += 40

    canvas.save(out_path, optimize=True)
    print(f"SAVED_COMPARE: {out_path.name}")


def main():
    ws_root = Path(__file__).resolve().parents[1]
    base = ws_root / "renders" / "v7_0_baseline"
    ren = ws_root / "renders"
    pairs = (
        ("SHOT_01_HERO_MECHANICAL_ASSEMBLY.png", "SHOT_01_V7_1.png", "COMPARE_SHOT_01_V7_0_VS_V7_1.png", "SHOT 01 — HERO 3/4 ASSEMBLY"),
        ("SHOT_02_HYDRAULIC_CYLINDER_CLOSEUP.png", "SHOT_02_V7_1.png", "COMPARE_SHOT_02_V7_0_VS_V7_1.png", "SHOT 02 — CYLINDER & CHROME CLOSE-UP"),
        ("SHOT_03_EXPLODED_ENGINEERING_VIEW.png", "SHOT_03_V7_1.png", "COMPARE_SHOT_03_V7_0_VS_V7_1.png", "SHOT 03 — EXPLODED CYLINDER"),
        ("SHOT_04_CUTAWAY_XRAY.png", "SHOT_04_V7_1.png", "COMPARE_SHOT_04_V7_0_VS_V7_1.png", "SHOT 04 — CUTAWAY HYDRAULIC REVEAL"),
    )
    for f0, f1, fout, lbl in pairs:
        make_comparison_image(base / f0, ren / f1, ren / fout, lbl)


if __name__ == "__main__":
    main()
