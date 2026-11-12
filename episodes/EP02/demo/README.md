# CAPY BK EP02 · Demo nâng cần PC200-8

**Bản nháp duyệt cảnh · 42 giây · 1920 × 1080 · 30 fps.** Demo đi từ động cơ diesel, bơm piston và van phân phối đến một lần nâng cần và giữ vị trí. Hai vai thoại có lời và mốc dựng trong SRT và CSV. Mốc dựng sẽ theo bản thu khi có WAV được duyệt.

## Mở và chỉnh project

1. Mở `godot/project.godot` trong Godot 4.5.1, rồi chạy `demo.tscn` bằng F6.
2. Trong scene tree, `AnimationPlayer → sequence` có keyframe cho `lift_amount` và `pilot_amount`. `Machine/Upper/Boom/Stick/Bucket` là chuỗi khớp cha–con. Hai nút `BoomRam` giữ hai xi lanh nâng cần, theo tọa độ chốt tính trong `machine.gd`.
3. Dự án có bản máy và sơ đồ gốc ngay trong Git. Hình nhân vật EP01 dùng trong bản duyệt nằm ở `godot/local/` trong gói bàn giao. Tên, kích thước atlas, nguồn và cách lấy lại được ghi trong [manifest](ASSET_MANIFEST.md). Tài nguyên cá nhân nằm trong thư mục cục bộ này.

Kiểm thử và quay bằng Movie Maker (chạy tại thư mục demo, dùng đường dẫn tới Godot bản console trên Windows). Dùng phiên đồ họa cho Movie Maker.

```powershell
godot --headless --path godot -- --qa
godot --path godot --resolution 1920x1080 --write-movie EP02-godot.avi --fixed-fps 30 --quit-after 1260
ffmpeg -i EP02-godot.avi -map 0:v -c:v libx264 -pix_fmt yuv420p -movflags +faststart EP02-picture.mp4
```

Xem [storyboard](STORYBOARD.md), [bảng phân vai](audio_timing.csv), [SRT](EP02_demo_vi.srt) và [audit kỹ thuật và QA](TECHNICAL_QA.md). Tài liệu Godot mô tả [Movie Maker](https://docs.godotengine.org/en/4.5/tutorials/animation/creating_movies.html).

## Bàn giao CapCut Pro

1. Tạo project ngang 16:9, 1920 × 1080, 30 fps. Đặt `CAPY-BK-EP02-PC200-8-demo.mp4` vào video track ở 00:00. Đây là bản duyệt có chữ kỹ thuật và intro, có thể tắt tiếng clip để dựng bằng stem riêng.
2. Nhập `EP02_demo_vi.srt` từ mục nhập phụ đề cục bộ. Nhập WAV 48 kHz vào ba track tên `SIGNATURE`, `CAPY` và `ENGINEER`. Đặt stem intro ở 00:00.480. Hai vai còn lại dùng cue trong CSV khi có bản thu. Kiểm tra diacritics, đọc thử và chốt độ dài hình theo lời.
3. Khi cần sửa thời điểm dầu đổi đường hoặc xi lanh dừng, sửa keyframe và render lại trong Godot rồi thay clip trên timeline. Xuất H.264/AAC 1080p30 để owner xem duyệt.

Bản YouTube 10–12 phút và bản TikTok 2–2,5 phút có script V2 riêng ở thư mục EP02. Cả hai qua bước duyệt demo trước khi dựng. Bản dọc sẽ bố trí lại góc máy và đường dầu cho 1080 × 1920.
