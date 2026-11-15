# EP02 V7 · Bản duyệt hình và thoại

V7 dùng bản bàn giao V6 ở commit `95d7f59`. Nội dung vẫn theo kịch bản YouTube PC200-8. Bản dựng cần chủ kênh nghe và duyệt chất giọng trước khi dùng để phát hành.

- SC08 và SC09 dùng ảnh máy nhìn từ trên mới. Gầu úp miệng xuống đất và nhìn thấy lưng gầu. Trong SC08, thân trên giữ tư thế cần, tay gầu, gầu rồi quay quanh chốt giữa. Bánh xích giữ nguyên vị trí, ô bánh răng nằm riêng ở góc. Cảnh này minh họa chuyển động quay toa nên không bổ sung động tác gầu.
- SC04 giữ trọn bơm, van LS và hai nhánh chấp hành trong khung hình. SC09 vẽ hai đường A và B của cùng một mô tơ di chuyển. Màu cấp và hồi tương ứng với một chiều đang minh họa. Mặt cắt khớp quay thể hiện nguyên lý, chưa xác nhận được bố trí cổng của từng máy.
- Voice thử dùng một mẫu nam tiếng Việt với nhịp đọc khác nhau nhẹ cho hai vai. Giữ đoạn signature đã chọn từ EP01. Miệng bám theo mức âm của câu thật. Các mốc trong một câu dài được chia theo chữ để đưa ra SRT dễ đọc. Mỗi đoạn thoại đầu vào là WAV mono 48 kHz.

## Tài nguyên mới

| Tệp | Nguồn và yêu cầu hình | Cảnh |
| --- | --- | --- |
| `godot/art/top_upper_v7.png` | ImageGen tích hợp, 2026-11-15. Dựa vào hình thân máy V4, vẽ từ trên với vỏ kim loại, cabin, ống dầu, cần và tay gầu. Chỉnh riêng gầu tại chốt để lộ mặt lưng lồi, gân chịu mòn và một phần đầu răng. Nền trong suốt. Hình minh họa dự án, đang chờ duyệt. | SC08, SC09 |
| `godot/art/top_ground_v7.png` | ImageGen tích hợp, 2026-11-15. Nền công trường 2D từ trên, đất nén màu vàng nâu với dấu xích và mép cây. Hình minh họa dự án, đang chờ duyệt. | SC08, SC09 |
| `godot/local/` | Cel studio và ảnh hai nhân vật gốc EP01, giọng thử, và phần thu signature có sẵn. Tệp bàn giao cục bộ. | Các cảnh có nhân vật |

Thông số và giới hạn của sơ đồ tiếp tục lấy từ nguồn K1/K2 đã ghi trong `TECHNICAL_QA_V4.md` và `FULL_V5_REPORT.md`.

## Dựng lại

1. Mở `godot/project.godot` bằng Godot 4.5.1. Cảnh ở `godot/full/`, riêng SC03, SC04 và SC05 ở `godot/segments/` (SC05 dùng `sc05_v42.tscn`).
2. Đặt tệp thoại theo bảng `full_v5/VOICE_SHEET.csv` trong `godot/local/voice/`. Bản thử đã có WAV và JSON theo câu. Chuẩn bị ảnh nhân vật với `tools/full/prepare_local_v7.py` từ ảnh EP01, chép `studio-cels.png` vào `godot/local/` và chạy `tools/full/bake_studio_plate.py`.
3. Đặt `FFMPEG`, `FFPROBE` và `GODOT` tới các chương trình tương ứng nếu chúng chưa có trong PATH. Với WAV và các tệp mốc câu đã chuẩn bị, chạy `python tools/full/build_full.py` rồi `python tools/full/render_v7.py`. Nếu chỉ chỉnh một cảnh, dùng `--parts-only --shots SC08`, rồi `--assemble-only` để ghép đủ tập theo thứ tự. Xóa hoặc cất riêng đoạn xuất cũ nếu dùng `--resume` sau khi thay đổi cảnh đó.
4. Trong CapCut Pro, tạo timeline 1920 × 1080, 30 FPS. Nhập MP4 và SRT rời từ thư mục xuất. MP4 đã có bản mix. Nếu chỉnh giọng, nhập ba WAV trong thư mục `stems` cùng mốc 00:00 và tắt tiếng track MP4 để tránh chồng lời. Nghe lại intro và chỗ cắt trước khi xuất.
