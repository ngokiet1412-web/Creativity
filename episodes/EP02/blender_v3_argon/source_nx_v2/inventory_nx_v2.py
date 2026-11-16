"""Inventory and verify Siemens NX V2 Argon assets into EP02_V7_ARGON_BLENDER/source_nx_v2 without modifying originals."""

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_default_v2_dirs(ws_root: Path):
    parent = ws_root.parent
    pilot_dir = parent / "CAPY_BK_EP02_NX_CODEX_PILOT"
    v2_dir = pilot_dir / "NX_NATIVE_V2_ARGON_20261116"
    return pilot_dir, v2_dir


def main():
    ws_root = Path(__file__).resolve().parents[1]
    default_pilot, default_v2 = resolve_default_v2_dirs(ws_root)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nx-v2-dir", type=Path, default=default_v2)
    parser.add_argument("--nx-pilot-dir", type=Path, default=default_pilot)
    args = parser.parse_args()

    v2_dir = args.nx_v2_dir.resolve()
    pilot_dir = args.nx_pilot_dir.resolve()
    if not v2_dir.is_dir():
        raise FileNotFoundError(f"NX V2 directory not found: {v2_dir}")

    zip_candidate = v2_dir.with_suffix(".zip")
    zip_in_parent = ws_root.parent / "NX_NATIVE_V2_ARGON_20261116.zip"

    source_out = ws_root / "source_nx_v2"
    step_out = ws_root / "cad_exchange" / "step"
    source_out.mkdir(parents=True, exist_ok=True)
    step_out.mkdir(parents=True, exist_ok=True)

    categories = {
        "prt_native": [],
        "argon_v2_prefixed_prt": [],
        "step_ap214": [],
        "stl_v2_existing": [],
        "csv_tables": [],
        "logs_and_audit": [],
        "viewports_png": [],
        "other": [],
    }

    total_bytes = 0
    for item in sorted(v2_dir.iterdir()):
        if not item.is_file():
            continue
        stat = item.stat()
        total_bytes += stat.st_size
        entry = {
            "name": item.name,
            "size_bytes": stat.st_size,
            "sha256": sha256_file(item),
            "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        }
        lower = item.name.lower()
        if item.name.startswith("ARGON_V2_") and lower.endswith(".prt"):
            categories["argon_v2_prefixed_prt"].append(entry)
        elif lower.endswith(".prt"):
            categories["prt_native"].append(entry)
        elif lower.endswith(".step") or lower.endswith(".stp"):
            categories["step_ap214"].append(entry)
            shutil.copy2(item, step_out / item.name)
        elif lower.endswith(".stl"):
            categories["stl_v2_existing"].append(entry)
        elif lower.endswith(".csv"):
            categories["csv_tables"].append(entry)
            shutil.copy2(item, source_out / item.name)
        elif lower.endswith(".log") or lower.endswith(".json"):
            categories["logs_and_audit"].append(entry)
            shutil.copy2(item, source_out / item.name)
        elif lower.endswith(".png"):
            categories["viewports_png"].append(entry)
        else:
            categories["other"].append(entry)

    scripts_info = []
    for sname in (
        "geometry_v2_argon.py",
        "nx_pilot_v2_argon.py",
        "nx_review_v2_argon.py",
        "nx_ui_preview_v2_argon.py",
        "render_nx_viewports_v2_argon.py",
        "REPORT_V2_ARGON_TAKEOVER.md",
    ):
        sp = pilot_dir / sname
        if sp.is_file():
            scripts_info.append({
                "name": sp.name,
                "size_bytes": sp.stat().st_size,
                "sha256": sha256_file(sp),
            })

    audit_path = v2_dir / "feature_tree_audit_v2_argon.json"
    audit_data = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.is_file() else {}

    inventory = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_folder_rel": str(v2_dir),
        "zip_package_present": zip_candidate.is_file() or zip_in_parent.is_file(),
        "zip_note": (
            "Found extracted folder NX_NATIVE_V2_ARGON_20261116/ containing all V2 deliverables; "
            "no standalone NX_NATIVE_V2_ARGON_20261116.zip archive present on disk."
            if not (zip_candidate.is_file() or zip_in_parent.is_file())
            else "Found both folder and zip archive."
        ),
        "total_v2_bytes": total_bytes,
        "counts": {k: len(v) for k, v in categories.items()},
        "categories": categories,
        "nxopen_v2_scripts": scripts_info,
        "feature_audit_summary": {
            "assemblies": {
                k: {
                    "component_count": v.get("component_count"),
                    "constraint_count": v.get("constraint_count"),
                    "datum_points": v.get("datum_points"),
                    "max_datum_error_mm": v.get("max_datum_error_mm"),
                }
                for k, v in audit_data.get("assemblies", {}).items()
            },
            "placed_solids": audit_data.get("placed_solids", {}),
            "parts_count": len(audit_data.get("parts", {})),
        },
        "known_gaps_inherited_from_v2": [
            "PC200-8 undercarriage/tracks, revolving upper deck, cabin, engine, pump block, and counterweight are NOT in V2 (only carrier_mount_reference A-frame turret lugs + working attachment).",
            "Cylinder bore/rod diameters (boom 120/85, arm 135/95, bucket 115/80) match brochure/public reference tables; clevis joint coordinates, closed lengths, and external SAE feed ports are V2 assumed/illustrative engineering geometry, NOT OEM Komatsu shop drawings.",
            "Rubber flexible hoses from carrier manifold to boom cylinders and stick cylinder feed were NOT yet modeled in NX V2 (to be added as clearly labeled illustrative routing in Blender V3).",
        ],
    }

    out_json = source_out / "nx_v2_inventory.json"
    out_json.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    print("NX_V2_INVENTORY_OK | counts =", inventory["counts"])
    print("ZIP_PRESENT =", inventory["zip_package_present"])


if __name__ == "__main__":
    main()
