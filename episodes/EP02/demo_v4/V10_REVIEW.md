# EP02 V10 · Kính, logo áo và bản duyệt HD

Mẫu kính gọng tròn và huy hiệu ba khối xanh được vẽ thành lớp riêng để dùng chung cho Capy trong studio, khung thuyết minh và ngoài công trường. Logo ở studio luôn theo chiều đọc dù ảnh nhân vật quay sang hướng khác.

Hai micro trong studio hướng chéo vào miệng từng người, với vòng xanh sáng nhẹ khi có lời. Laptop Dell đặt trước anh kỹ sư. `godot/local/studio_show_v10.png` là bản chỉnh bằng ImageGen tích hợp ngày 2026-11-15 từ nền V9. Yêu cầu gỡ hai micro cũ, để chỗ cho hai lớp rig, thêm Dell ở mép phải và giữ hai ly, bảng hiệu cùng laptop trái. Nền và nhãn hiệu minh họa nằm trong thư mục cục bộ chờ duyệt.

Render lại các cảnh từ Godot với `tools/full/render_v7.py --version V10 --out <thư mục xuất> --jobs 4`. Dùng `tools/full/export_v10_hd.py <thư mục xuất>` để xuất bản duyệt 1920 × 1080 có phụ đề và âm thanh AAC. Sáu phần HD tách ở các khung hình khóa, giữ nguyên chất lượng. Thêm `--nvenc` nếu bộ mã hóa NVIDIA đã được kiểm tra. Bản MP4 sạch, SRT và các WAV vẫn ở thư mục dựng để chỉnh trong CapCut.
