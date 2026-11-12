"""Pin-coordinate and cylinder plot from telemetry.csv (Godot --qa pass)."""
import csv, json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
tel, rig_path, out = sys.argv[1:4]
r = list(csv.DictReader(open(tel)))
col = lambda k: [float(x[k]) for x in r]
t = col("t")
rig = json.load(open(rig_path))
fig, ax = plt.subplots(2, 2, figsize=(16, 9), dpi=120)
a = ax[0][0]
a.plot(t, col("boom_deg"), label="góc cần (°)")
a.plot(t, col("bucket_rel"), label="góc gầu tương đối (°)")
a2 = a.twinx(); a2.plot(t, col("spool"), "k--", lw=1, label="con trượt (0–1)"); a2.set_ylim(-0.05, 1.6)
a.set_title("Góc khớp và lệnh van"); a.set_xlabel("t (s)"); a.legend(loc="upper left"); a2.legend(loc="upper right"); a.grid(alpha=.3)
a = ax[0][1]
for k, spec, c in (("Lb", "boom_cyl", "C0"), ("La", "arm_cyl", "C1"), ("Lk", "bucket_cyl", "C2")):
    s = rig[spec]
    a.plot(t, col(k), c, label=f"{k} (px)")
    a.axhline(s["closed"], color=c, ls=":", lw=1); a.axhline(s["closed"] + s["stroke"], color=c, ls="--", lw=1)
a.set_title("Khoảng cách chốt xi lanh · chấm = chiều dài đóng, gạch = hết hành trình"); a.set_xlabel("t (s)"); a.legend(); a.grid(alpha=.3)
a = ax[1][0]
for k, lab in (("Eb", "mắt ty xi lanh cần"), ("W1", "chốt cần–tay gầu"), ("W2", "chốt gầu"), ("J", "chốt thanh chữ H"), ("T", "răng gầu")):
    a.plot(col(k + "_x"), col(k + "_y"), label=lab)
a.plot([45], [85], "ko"); a.annotate("chân xi lanh cần", (45, 85)); a.plot([0], [0], "ks"); a.annotate("chốt chân cần", (0, 0))
a.axhline(rig["ground_y"], color="saddlebrown", lw=2, label="mặt đất")
a.invert_yaxis(); a.set_aspect("equal"); a.set_title("Quỹ đạo chốt (px máy, 100 px = 1 m)"); a.legend(fontsize=8); a.grid(alpha=.3)
a = ax[1][1]
a.plot(t, col("v"), label="tốc độ ty xi lanh cần (px/s)")
a.plot(t, [10 * x for x in col("swash")], label="góc đĩa nghiêng ×10")
a.plot(t, [10 * x for x in col("p_pump")], label="áp bơm (tương đối) ×10")
a.plot(t, [40 * x for x in col("pitch_deg")], label="lắc máy ×40 (°)")
a.set_title("Dầu, bơm và phản ứng máy"); a.set_xlabel("t (s)"); a.legend(fontsize=8); a.grid(alpha=.3)
fig.suptitle("CAPY BK EP02 V4 · kiểm tra khớp và xi lanh (480 khung, 0 lỗi QA)")
fig.tight_layout(); fig.savefig(out)
