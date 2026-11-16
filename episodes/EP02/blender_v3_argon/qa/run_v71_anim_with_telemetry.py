"""Run Blender V7.1 540-frame GPU animation render while logging nvidia-smi telemetry every 2 seconds."""

import json
import subprocess
import time
from pathlib import Path

WS_ROOT = Path(__file__).resolve().parents[1]
BLENDER_EXE = Path(r"C:\Program Files\Blender Foundation\Blender 5.3\blender.exe")
BUILD_SCRIPT = WS_ROOT / "blender_project" / "build_ep02_v7_1_cinematic.py"
FRAMES_DIR = WS_ROOT / "renders" / "frames_v7_1"
REPORT_JSON = WS_ROOT / "qa" / "gpu_vram_thermal_report_v7_1.json"
RENDER_LOG = WS_ROOT / "qa" / "blender_v71_anim_render.log"

NVIDIA_SMI = r"nvidia-smi"
QUERY_ARGS = [
    NVIDIA_SMI,
    "--query-gpu=name,utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw,clocks.current.sm",
    "--format=csv,noheader,nounits",
]


def sample_gpu():
    proc = subprocess.run(QUERY_ARGS, capture_output=True, text=True, check=False)
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    parts = [p.strip() for p in proc.stdout.strip().splitlines()[0].split(",")]
    if len(parts) < 8:
        return None
    return {
        "t_s": round(time.monotonic(), 2),
        "gpu_name": parts[0],
        "gpu_util_pct": float(parts[1]),
        "mem_ctrl_util_pct": float(parts[2]),
        "vram_used_mib": float(parts[3]),
        "vram_total_mib": float(parts[4]),
        "temp_c": float(parts[5]),
        "power_w": float(parts[6]),
        "sm_clock_mhz": float(parts[7]),
    }


def main():
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    for old_png in FRAMES_DIR.glob("ep02_v71_*.png"):
        old_png.unlink()

    baseline = sample_gpu()
    cmd = [
        str(BLENDER_EXE),
        "--background",
        "--python",
        str(BUILD_SCRIPT),
        "--",
        "--mode",
        "animate",
        "--anim-engine",
        "BLENDER_EEVEE",
        "--anim-samples",
        "32",
    ]
    t0 = time.monotonic()
    samples = []
    with RENDER_LOG.open("w", encoding="utf-8") as logf:
        proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT)
        while proc.poll() is None:
            s = sample_gpu()
            if s is not None:
                s["elapsed_s"] = round(time.monotonic() - t0, 2)
                s["frames_done"] = len(list(FRAMES_DIR.glob("ep02_v71_*.png")))
                samples.append(s)
            time.sleep(2.0)
        rc = proc.returncode

    total_wall_s = round(time.monotonic() - t0, 2)
    post = sample_gpu()
    frames_count = len(list(FRAMES_DIR.glob("ep02_v71_*.png")))

    def agg(key):
        vals = [s[key] for s in samples] or ([baseline[key]] if baseline else [0.0])
        return {"min": round(min(vals), 2), "avg": round(sum(vals) / len(vals), 2), "max": round(max(vals), 2)}

    # Separate active rendering phase (after first frame starts appearing)
    active = [s for s in samples if s.get("frames_done", 0) >= 1]
    def agg_active(key):
        vals = [s[key] for s in active] or [s[key] for s in samples] or [0.0]
        return {"min": round(min(vals), 2), "avg": round(sum(vals) / len(vals), 2), "max": round(max(vals), 2)}

    report = {
        "engine": "BLENDER_EEVEE (Raytracing + AO + DOF + Compositor Fog Glow)",
        "taa_samples": 32,
        "resolution": "1920x1080 @ 30fps",
        "exit_code": rc,
        "frames_rendered": frames_count,
        "total_wall_time_s": total_wall_s,
        "baseline_idle": baseline,
        "post_render": post,
        "samples_count": len(samples),
        "active_render_samples_count": len(active),
        "overall_stats": {
            "gpu_util_pct": agg("gpu_util_pct"),
            "vram_used_mib": agg("vram_used_mib"),
            "temp_c": agg("temp_c"),
            "power_w": agg("power_w"),
            "sm_clock_mhz": agg("sm_clock_mhz"),
        },
        "active_render_stats": {
            "gpu_util_pct": agg_active("gpu_util_pct"),
            "vram_used_mib": agg_active("vram_used_mib"),
            "temp_c": agg_active("temp_c"),
            "power_w": agg_active("power_w"),
            "sm_clock_mhz": agg_active("sm_clock_mhz"),
        },
        "samples": samples,
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("exit_code", "frames_rendered", "total_wall_time_s", "active_render_stats")}, indent=2))
    if rc != 0 or frames_count != 540:
        raise SystemExit(f"Render incomplete: rc={rc}, frames={frames_count}")


if __name__ == "__main__":
    main()
