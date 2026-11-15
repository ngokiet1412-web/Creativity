# EP02 V9 · Intro mới và bản xem nhẹ

Capy đeo kính và ngồi bên trái. Anh kỹ sư ngồi bên phải. Hai ly BK nằm hai bên TV. Logo áo Capy dùng chi tiết gốc đặt theo chiều đọc sau khi đổi hướng nhân vật.

TV mở bằng tên kênh và chủ đề tập. Ba nốt âm tổng hợp thay lời xướng cũ. Lời thoại thử bắt đầu từ câu hỏi của Capy. Các mốc thoại tiếp theo đi cùng bản thử V8.

Cảnh mở đầu dùng bờ đất nối ra ngoài khung. Răng gầu hạ vào đất, quét về phía máy, cuộn để giữ đất rồi nâng lên. Cao độ đường đất thay đổi theo đường quét của răng gầu. Kiểm tra giới hạn mặt đất chạy từng khung ở SC01.

`godot/local/studio_show_v9.png` là nền ImageGen tích hợp ngày 2026-11-15, bản chỉnh từ nền studio V8. Yêu cầu dời và thu nhỏ laptop ở góc trái, bổ sung một ly bên phải, giữ tường, đèn, TV động và bàn dùng chung. Ảnh studio lưu cục bộ.

Tái dựng SC01 và SC14 bằng `tools/full/build_full.py` và `tools/full/render_v7.py --version V9`. Dùng `tools/full/export_v9_light.py <thư mục xuất>` để tạo bản 960 × 540, H.264/AAC, có chữ, và ba đoạn nhẹ. Thêm `--nvenc` nếu đã kiểm tra bộ mã hóa NVIDIA trên máy. Bản phụ đề SRT rời tiếp tục dùng để sửa lời đọc trong CapCut.
