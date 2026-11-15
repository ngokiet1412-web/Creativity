# EP02 · So sánh V3 → V4

Ảnh cặp khung: `qa/before_after_V3_V4.jpg` trong gói bàn giao (V3 28.5/13.8/25.5/37.5 s ↔ V4 5.8/8.3/10.5/14.0 s).

| Tiêu chí (theo review 2026-11-12) | V3 | V4 |
|---|---|---|
| Thời lượng mẫu | 42 s | 16 s, đúng khung 12–18 s |
| Studio + ly BK trong mấy giây đầu | Có, 0–4 s | Có, 0–3 s, cel khớp tag |
| Phong cách máy | Ảnh render ImageGen, khá “3D” | Viền mực, chia tông, giảm vân ảnh: minh họa kỹ thuật 2.5D |
| Nhịp nâng cần | Góc cần nội suy ease in/out; ty chạy không đều | Ty theo hồ sơ min-jerk: khởi động, tăng tốc, đi đều, giảm tốc, dừng. Góc giải từ chiều dài ty. |
| Chịu tải | Không có | Võng nhẹ khi van mở, nhún tắt dần khi dừng |
| Phản ứng máy và môi trường | Đất rơi, khói xả | Thêm lắc cứng toàn máy theo phản lực, rung theo tải bơm, bóng gầu/tay gầu, bụi khi đất chạm nền |
| Cuộn gầu | Chỉ có trong đoạn đào | Cuộn sau khi nâng, có vượt nhẹ, đất tràn mép |
| Đường đi của camera | Cắt cảnh giữa các đoạn | Một đường liền: toàn máy → khoang máy → theo ống A → mặt cắt xi lanh → lùi ra |
| Nhãn kỹ thuật | Chung một kiểu | Thẻ K1 ✓ (đã đối chiếu) / NGUYÊN LÝ (giản lược) trên từng nhãn |
| Mờ x-ray, joystick, đầu Capy | Nhảy bậc (lỗi ghi số nguyên) | Mượt |
| Layer chuyển động | Không có | 5 pass: bg, machine, hydraulics, crew, intro |
| Đồ thị chốt | Ảnh chốt 6 khung | Ảnh chốt 6 khung + đồ thị chốt/xi lanh theo thời gian |
| QA hình học | 1.260 khung, 0 lỗi | 480 khung, 0 lỗi |
| Mẫu gần như đứng hình | 9/84 | 2/32 (chỉ ở studio) |
