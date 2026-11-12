#!/usr/bin/env python3
"""Subtitle + VO-slot timing for the SC03/SC04/SC05 segment clips.

Text is copied word for word from episodes/EP02/SCRIPT_YOUTUBE_PC200_8_FULL_V2.md.
Long lines are split into subtitle cues only at punctuation; no words are changed.

The approved ElevenLabs voices are not recorded yet, so every cue gets an
ESTIMATED spoken length (Vietnamese syllables / 4.2 per s + 0.25 s). The check
flags any cue whose estimate does not fit before the next cue/window end, so the
editor knows where the picture needs a hold frame instead of speeding up the voice.

usage: make_segment_srt.py <out_dir>
"""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from segment_timing import warp, extra  # noqa: E402

RATE = 4.2  # syllables per second, calm explainer pace (estimate only)

# (speaker, start_s, window_end_s, text)
SEG = {  # times on the BASE timeline; shifted by segment_timing.warp
    "SC03": (41.0, [
        ("ANH KỸ SƯ", 0.6, 4.6, "Động cơ diesel cấp công suất cơ học cho bơm."),
        ("ANH KỸ SƯ", 4.8, 9.6, "Dữ liệu PC200-8 cho thấy động cơ Komatsu SAA6D107E-1;"),
        ("ANH KỸ SƯ", 9.8, 16.4, "phần bơm chính là loại piston thay đổi lưu lượng, có hai phần bơm để điều phối các nhu cầu làm việc."),
        ("ANH KỸ SƯ", 16.6, 20.6, "Bên trong bơm piston hướng trục, khi góc đĩa nghiêng thay đổi, hành trình piston thay đổi theo."),
        ("ANH KỸ SƯ", 20.8, 24.6, "Góc lớn hơn thường cho lưu lượng lớn hơn ở cùng tốc độ quay; góc nhỏ hơn thì lưu lượng giảm."),
        ("CAPY", 25.4, 29.8, "Vậy ga máy tăng chưa chắc gầu lúc nào cũng chạy nhanh nhất?"),
        ("ANH KỸ SƯ", 30.4, 35.5, "Đúng. Lưu lượng đến cơ cấu còn tùy bơm đang được điều khiển ra sao, van đang mở thế nào,"),
        ("ANH KỸ SƯ", 35.6, 40.8, "tải và các giới hạn công suất. Đó mới là điều thú vị."),
    ]),
    "SC04": (39.0, [
        ("CAPY", 0.8, 4.0, "Thế cái tên CLSS nghe như mật mã là gì anh?"),
        ("ANH KỸ SƯ", 4.4, 7.55, "Đó là hệ thống thủy lực tâm kín có cảm nhận tải."),
        ("ANH KỸ SƯ", 7.65, 11.4, "Nói đơn giản: khi các tay điều khiển ở trung gian, máy không cần cấp lưu lượng lớn tới mọi cơ cấu."),
        ("ANH KỸ SƯ", 11.5, 17.2, "Khi một cơ cấu cần làm việc, tín hiệu cảm nhận tải — gọi là LS — cùng các bộ điều chỉnh trên bơm giúp thay đổi lưu lượng phù hợp."),
        ("ANH KỸ SƯ", 17.4, 24.2, "Van bù áp còn hỗ trợ phân chia dòng dầu khi nhiều cơ cấu làm việc cùng lúc."),
        ("CAPY", 24.8, 27.6, "À! Không phải cứ nổ máy là bơm xả hết công suất đi khắp nơi."),
        ("CAPY", 27.7, 30.2, "Nó phải nghe xem ai đang cần dầu!"),
        ("ANH KỸ SƯ", 31.0, 33.0, "Hiểu theo mức nhập môn thì đúng."),
        ("ANH KỸ SƯ", 33.1, 38.6, "Nhưng điều khiển thực tế có cả giới hạn công suất của động cơ và các điều kiện vận hành."),
    ]),
    "SC05": (29.0, [
        ("CAPY", 0.8, 4.4, "Tui gạt cái cần nhỏ xíu trong cabin, sao điều khiển nổi một cái xi lanh bự vậy?"),
        ("ANH KỸ SƯ", 5.4, 9.0, "Tay điều khiển không tự đưa toàn bộ lưu lượng của bơm chính."),
        ("ANH KỸ SƯ", 9.1, 13.8, "Trên PC200-8, mạch điều khiển pilot và cụm van chính thực hiện việc phân phối dầu đến các cơ cấu."),
        ("ANH KỸ SƯ", 13.9, 16.4, "Gạt joystick làm thay đổi tín hiệu điều khiển,"),
        ("ANH KỸ SƯ", 16.5, 19.6, "từ đó dịch chuyển phần tử van tương ứng để cho dầu đi đến khoang thích hợp của xi lanh hoặc mô tơ."),
        ("CAPY", 19.9, 23.0, "Tức là một tín hiệu nhỏ có thể điều khiển cả dòng năng lượng lớn?"),
        ("ANH KỸ SƯ", 24.0, 28.8, "Đúng, nhưng phải có nguồn năng lượng từ động cơ và bơm phía sau."),
    ]),
}

SPOKEN = {"PC200-8": "pê xê hai trăm tám", "SAA6D107E-1": "ét a a sáu đê một trăm lẻ bảy e một",
          "CLSS": "xê eo ét ét", "LS": "eo ét"}


def syllables(text):
    for k, v in SPOKEN.items():
        text = text.replace(k, v)
    return len(re.findall(r"[\wÀ-ỹ]+", text))


def ts(t):
    ms = int(round(t * 1000))
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


def main(out):
    os.makedirs(out, exist_ok=True)
    rows = []
    for seg, (length, cues) in SEG.items():
        with open(os.path.join(out, "EP02_%s_vi.srt" % seg), "w", encoding="utf-8") as f:
            key = seg.lower()
            length = length + extra(key)
            for i, (who, b0, b1, text) in enumerate(cues, 1):
                t0, t1 = warp(key, b0), warp(key, b1)
                est = syllables(text) / RATE + 0.25
                fits = t0 + est <= t1 + 1e-6
                assert t1 <= length
                f.write("%d\n%s --> %s\n%s: %s\n\n" % (i, ts(t0), ts(t1), who, text))
                rows.append([seg, i, who, "%.2f" % t0, "%.2f" % t1, "%.2f" % (t1 - t0), "%.2f" % est,
                             "OK" if fits else "CẦN GIỮ HÌNH +%.1fs" % (t0 + est - t1),
                             "pending ElevenLabs (owner-approved voice)", text])
    with open(os.path.join(out, "audio_timing_segments.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["segment", "cue", "speaker", "start_s", "end_s", "slot_s", "est_speech_s", "fit", "voice_file", "line"])
        w.writerows(rows)
    bad = [r for r in rows if r[7] != "OK"]
    print("%d cues, %d need hold" % (len(rows), len(bad)))
    for r in bad:
        print("  ", r[0], r[1], r[7], r[9][:60])


if __name__ == "__main__":
    main(sys.argv[1])
