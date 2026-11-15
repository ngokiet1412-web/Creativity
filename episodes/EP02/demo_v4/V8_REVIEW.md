# EP02 V8 · Studio hai người và bản nghe thử

SC01 và SC14 dùng cùng một bàn. Anh kỹ sư ở bên trái, Capy ở bên phải và TV nằm giữa. Capy giữ sẵn cả hai tay trên bàn. Khi nghe, Capy chớp mắt và gật nhẹ. Hình máy chạy trên TV được dựng trong Godot, với chuyển cảnh vào công trường cuối đoạn mở đầu và kéo ngược về studio ở đoạn kết.

SC02 bỏ biểu tượng lọc dầu hồi trên thân máy vì tài liệu đã đối chiếu chưa đủ để xác nhận tọa độ của cụm này. SC10 minh họa lọc ở mạch dầu hồi theo chức năng. Đường dầu trong các sơ đồ dùng viền tối, lõi màu và vệt sáng chạy theo dòng. Màu, chiều và các kết nối dùng cùng dữ liệu như bản trước. Nhãn chính xuất hiện từng mục, còn nguồn thông số nằm trong báo cáo kỹ thuật.

Lời tham khảo dùng lại 39 đoạn thử của V7. Tiếng động cơ, cần điều khiển, thủy lực và xích được tổng hợp và đặt theo các mốc của cảnh. Câu signature dùng đoạn âm thanh chủ kênh đã chọn. Ba track thoại và một track hiệu ứng bắt đầu từ mốc 00:00 để thay giọng bằng bản thu riêng. Phụ đề duyệt có kiểu chữ và nền đậm cố định ở dưới. SRT lẫn tệp kiểu phụ đề ASS đi kèm.

| Tài nguyên | Cách tạo | Phạm vi |
| --- | --- | --- |
| `godot/local/studio_show_v8.png` | ImageGen tích hợp, 2026-11-15. Tham chiếu studio V7, tạo một mảng tường xanh đậm liền, bàn gỗ xuyên khung, laptop, ly BK và hai micro. Để trống phần giữa cho TV và hai bên cho ảnh nhân vật. Giữ trong thư mục cục bộ để duyệt hình và nhãn hiệu. | SC01, SC14 |
| `godot/local/host_capy.png` và `host_eng.png` | Tách lớp từ ảnh gốc EP01. Biên bàn tay Capy giữ theo đường nét gốc. Godot ghép hai vai vào bàn và animate đầu, mí mắt và miệng. | Studio và các sơ đồ có nhân vật |
| `tools/full/foley_v8.py` | Âm tổng hợp, hạt giống cố định, không dùng bản thu máy thật. | Mở đầu và cảnh thao tác |

Dựng lại với `python tools/full/render_v7.py --version V8 --out build/EP02_v8_show --jobs 4 --review`. Chạy từ vị trí có đường dẫn phù hợp cho thư mục xuất và dùng các tài nguyên cục bộ từ hướng dẫn V7. Với video đã render, `--remix-only --review` dùng lại hình và trộn âm thanh mới.

Trong CapCut, dùng MP4 sạch và SRT để tự chỉnh chữ. Khi thay giọng, tắt audio của MP4, dùng track hiệu ứng và signature ở mốc 00:00 rồi đặt lời Capy và anh kỹ sư theo bảng timing. Bản có phụ đề đã đóng chữ để duyệt.
