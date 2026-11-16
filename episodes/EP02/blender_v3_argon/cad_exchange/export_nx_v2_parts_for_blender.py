"""NXOpen NX 12 read-only exporter: Tessellate V2 native .prt parts into high-res sub-part Binary STL meshes for Blender V3."""

import argparse
import json
import os
import struct
import sys
import time
import traceback
from pathlib import Path

import NXOpen


def close_all_safely(session):
    try:
        session.Parts.CloseAll(NXOpen.BasePart.CloseModified.CloseModified, None)
    except NXOpen.NXException:
        pass


def open_readonly(session, path: Path):
    for existing in list(session.Parts):
        if existing.Leaf.lower() == path.stem.lower():
            try:
                existing.Close(
                    NXOpen.BasePart.CloseWholeTree.TrueValue,
                    NXOpen.BasePart.CloseModified.CloseModified,
                    None,
                )
            except NXOpen.NXException:
                pass
    part, status = session.Parts.OpenBaseDisplay(str(path))
    if status is not None:
        status.Dispose()
    return part


def parse_binary_stl_stats(stl_path: Path):
    data = stl_path.read_bytes()
    if len(data) < 84:
        raise RuntimeError(f"STL too small: {stl_path}")
    tri_count = struct.unpack("<I", data[80:84])[0]
    expected_len = 84 + tri_count * 50
    if len(data) != expected_len:
        raise RuntimeError(f"STL size mismatch ({len(data)} vs {expected_len}) for {stl_path}")
    xs, ys, zs = [], [], []
    offset = 84
    # stride unpack vertices quickly
    step = 50
    for i in range(tri_count):
        base = offset + i * step + 12
        v = struct.unpack_from("<9f", data, base)
        xs.extend((v[0], v[3], v[6]))
        ys.extend((v[1], v[4], v[7]))
        zs.extend((v[2], v[5], v[8]))
    bbox = {
        "min_mm": [round(min(xs), 4), round(min(ys), 4), round(min(zs), 4)],
        "max_mm": [round(max(xs), 4), round(max(ys), 4), round(max(zs), 4)],
    }
    return {"triangles": tri_count, "size_bytes": len(data), "bbox": bbox}


def export_stl_bodies(session, bodies, target: Path, chordal=0.08, adj=0.025):
    if target.exists():
        target.unlink()
    mesh = session.DexManager.CreateStlCreator()
    try:
        mesh.OutputFile = str(target)
        mesh.OutputType = NXOpen.STLCreator.OutputTypeEnum.Binary
        mesh.ChordalTol = float(chordal)
        mesh.AdjacencyTol = float(adj)
        mesh.AutoNormalGen = True
        for b in bodies:
            mesh.ExportSelectionBlock.Add(b)
        mesh.Commit()
    finally:
        mesh.Destroy()

    deadline = time.monotonic() + 20.0
    while time.monotonic() < deadline:
        if target.is_file() and target.stat().st_size >= 84:
            return parse_binary_stl_stats(target)
        time.sleep(0.1)
    raise RuntimeError(f"STL export timed out or empty: {target}")


def classify_bodies(part):
    """Map every solid body in a part to its generating feature name."""
    all_solids = [b for b in part.Bodies if b.IsSolidBody]
    tag_to_name = {}
    for feat in part.Features:
        fname = (feat.Name or feat.JournalIdentifier or "").strip()
        try:
            fbodies = feat.GetBodies()
        except Exception:
            fbodies = ()
        for b in fbodies:
            if b.IsSolidBody:
                tag_to_name[b.Tag] = fname
    mapped = [(b, tag_to_name.get(b.Tag, f"UNMAPPED_{b.Tag}")) for b in all_solids]
    return all_solids, mapped


def split_groups_for_part(part_stem: str, mapped_bodies):
    s = part_stem.lower()
    groups = {}

    if s == "boom":
        groups["boom_structure"] = [b for b, fn in mapped_bodies if "boss" not in fn.lower() and "bulkhead" not in fn.lower()]
        groups["boom_bosses"] = [b for b, fn in mapped_bodies if "boss" in fn.lower() or "bulkhead" in fn.lower()]
    elif s == "stick":
        groups["stick_structure"] = [b for b, fn in mapped_bodies if "boss" not in fn.lower() and "bulkhead" not in fn.lower()]
        groups["stick_bosses"] = [b for b, fn in mapped_bodies if "boss" in fn.lower() or "bulkhead" in fn.lower()]
    elif s == "bucket":
        groups["bucket_teeth"] = [b for b, fn in mapped_bodies if "replaceable_tooth" in fn.lower()]
        groups["bucket_wear_edges"] = [
            b for b, fn in mapped_bodies
            if any(k in fn.lower() for k in ("cutting_edge", "side_cutter", "heel_wear_shroud"))
        ]
        used_tags = {b.Tag for gname in ("bucket_teeth", "bucket_wear_edges") for b in groups[gname]}
        groups["bucket_shell"] = [b for b, _ in mapped_bodies if b.Tag not in used_tags]
    elif s.endswith("_cylinder_barrel"):
        prefix = s
        groups[prefix + "_body"] = [
            b for b, fn in mapped_bodies
            if any(k in fn.lower() for k in ("annular_tube", "closed_head", "clevis_eye"))
        ]
        groups[prefix + "_gland"] = [
            b for b, fn in mapped_bodies
            if any(k in fn.lower() for k in ("gland", "wiper_retainer"))
        ]
        groups[prefix + "_ports"] = [
            b for b, fn in mapped_bodies
            if any(k in fn.lower() for k in ("port_boss", "feed_pipe"))
        ]
    elif s.endswith("_rod"):
        prefix = s
        groups[prefix + "_chrome"] = [b for b, fn in mapped_bodies if "chrome_rigid_piston_rod" in fn.lower()]
        groups[prefix + "_piston"] = [
            b for b, fn in mapped_bodies
            if fn.lower().startswith("piston_")
        ]
        groups[prefix + "_eye"] = [b for b, fn in mapped_bodies if "rod_end" in fn.lower() or "grease_boss" in fn.lower()]
    elif s == "h_link":
        groups["h_link_body"] = [b for b, fn in mapped_bodies if "boss" not in fn.lower()]
        groups["h_link_bosses"] = [b for b, fn in mapped_bodies if "boss" in fn.lower()]
    elif s == "side_link":
        groups["side_link_body"] = [b for b, fn in mapped_bodies if "boss" not in fn.lower()]
        groups["side_link_bosses"] = [b for b, fn in mapped_bodies if "boss" in fn.lower()]
    else:
        groups[s] = [b for b, _ in mapped_bodies]

    # Verify strict 1-to-1 partition of all solid bodies
    total_in = len(mapped_bodies)
    flat_tags = [b.Tag for blist in groups.values() for b in blist]
    if len(flat_tags) != total_in or len(set(flat_tags)) != total_in:
        raise RuntimeError(f"Partition mismatch in {part_stem}: {len(flat_tags)} vs {total_in}")
    return groups


def resolve_ws_and_v2():
    ws_root = Path(__file__).resolve().parents[1]
    v2_dir = ws_root.parent / "CAPY_BK_EP02_NX_CODEX_PILOT" / "NX_NATIVE_V2_ARGON_20261116"
    return ws_root, v2_dir


def main():
    ws_root, default_v2 = resolve_ws_and_v2()
    v2_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else default_v2
    stl_out = ws_root / "cad_exchange" / "stl"
    stl_out.mkdir(parents=True, exist_ok=True)

    part_stems = [
        "carrier_mount_reference",
        "boom",
        "stick",
        "bucket",
        "boom_cylinder_barrel",
        "boom_rod",
        "arm_cylinder_barrel",
        "arm_rod",
        "bucket_cylinder_barrel",
        "bucket_rod",
        "side_link",
        "h_link",
        "pivot_pin",
        "pin_R64_L710",
        "pin_R60_L496",
        "pin_R54_L476",
        "pin_R44_L344",
        "pin_R44_L256",
        "pin_R42_L184",
        "pin_R42_L170",
        "pin_R40_L204",
        "pin_R38_L470",
        "pin_R38_L320",
        "pin_R38_L264",
    ]

    session = NXOpen.Session.GetSession()
    close_all_safely(session)

    manifest = {
        "nx_version": session.GetEnvironmentVariableValue("UGII_FULL_VERSION"),
        "source_dir": str(v2_dir),
        "stl_settings": {"chordal_tol_mm": 0.08, "adjacency_tol_mm": 0.025, "units": "mm", "binary": True},
        "parts": {},
        "total_stl_files": 0,
        "total_triangles": 0,
    }

    try:
        for stem in part_stems:
            prt_path = v2_dir / f"{stem}.prt"
            if not prt_path.is_file():
                raise FileNotFoundError(f"Missing V2 part: {prt_path}")
            part = open_readonly(session, prt_path)
            all_solids, mapped = classify_bodies(part)
            groups = split_groups_for_part(stem, mapped)

            part_info = {
                "source_prt": prt_path.name,
                "solid_bodies_total": len(all_solids),
                "datums": {
                    p.Name: [round(p.Coordinates.X, 4), round(p.Coordinates.Y, 4), round(p.Coordinates.Z, 4)]
                    for p in part.Points if p.Name
                },
                "sub_meshes": {},
                "whole_part_stl": None,
            }

            # Export each separated sub-mesh group
            for gname, blist in groups.items():
                if not blist:
                    continue
                out_stl = stl_out / f"{gname}.stl"
                stats = export_stl_bodies(session, blist, out_stl, chordal=0.08, adj=0.025)
                stats["body_count"] = len(blist)
                part_info["sub_meshes"][out_stl.name] = stats
                manifest["total_stl_files"] += 1
                manifest["total_triangles"] += stats["triangles"]

            # Also export full part STL if split into multiple sub-meshes (useful for QA / quick comparison)
            if len(groups) > 1 or list(groups.keys())[0] != stem.lower():
                whole_stl = stl_out / f"{stem}.stl"
                wstats = export_stl_bodies(session, all_solids, whole_stl, chordal=0.08, adj=0.025)
                wstats["body_count"] = len(all_solids)
                part_info["whole_part_stl"] = {"file": whole_stl.name, **wstats}
                manifest["total_stl_files"] += 1

            manifest["parts"][stem] = part_info
            print(
                f"EXPORT_OK {stem}: {len(all_solids)} bodies -> "
                f"{list(part_info['sub_meshes'].keys())}"
            )
            part.Close(NXOpen.BasePart.CloseWholeTree.FalseValue, NXOpen.BasePart.CloseModified.CloseModified, None)

        # Verify assembly file opens cleanly read-only too
        assy_path = v2_dir / "PC2008_WORK_EQUIPMENT_CONCEPT_ASSY.prt"
        assy = open_readonly(session, assy_path)
        manifest["assembly_verified"] = {
            "file": assy_path.name,
            "components": len(assy.ComponentAssembly.RootComponent.GetChildren()),
            "constraints": len(list(assy.ComponentAssembly.Positioner.Constraints)),
            "persistent_points": len(list(assy.Points)),
        }
        assy.Close(NXOpen.BasePart.CloseWholeTree.TrueValue, NXOpen.BasePart.CloseModified.CloseModified, None)

        out_manifest = ws_root / "cad_exchange" / "cad_exchange_manifest.json"
        out_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(
            f"CAD_EXCHANGE_DONE | files={manifest['total_stl_files']} | "
            f"submesh_triangles={manifest['total_triangles']}"
        )
    except Exception:
        print(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
