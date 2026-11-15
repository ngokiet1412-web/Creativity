# EP02 · SC05 V4.2: xi lanh nâng cần (bản thử 8 giây, DRAFT, chờ owner duyệt)

Ngày 2026-11-13. Nhánh `claude/ep02-v42-sc05-cylinder`, tách từ `b5ae650`, là bản SC03–SC05 owner đã duyệt.
Bản V4.1 (nhánh `claude/ep02-v41-polish`) **bị owner trả lại** vì đổi góc máy, bố cục và phong cách. V4.2 không dùng gì từ V4.1.

## 1. Nguyên tắc của bản này

- **Không ghi đè bản đã duyệt.** `segments/sc05.gd` và `sc05.tscn` giữ nguyên từng byte. Bản mới là file riêng:
  - `segments/sc05_v42.gd`: bản sao của `sc05.gd`, chỉ đổi phần vẽ xi lanh và tỉ lệ dòng hồi.
  - `segments/sc05_v42.tscn`: cùng node, cùng key, chỉ trỏ sang script mới.
  - `cutaway/cyl_v42.gd`: hình xi lanh mới.
- **Giữ nguyên:** bố cục, góc máy, key camera, nhịp, tay gạt, van PPC, con trượt, bơm, đường ống, nhãn, nhân vật. Xi lanh vẽ trong **đúng khung cũ**: vị trí (980, −130), vỏ dài 520 px, cao 120 px, lòng 84 px, ty 44 px, piston ở `a0.x + 40 + ext`. Hành trình `ext` tính đúng như bản cũ.
- **Kiểm chứng bằng so pixel** giữa hai bản cùng khung hình:

| Thời điểm (s) | Trạng thái | Pixel khác ngoài khung xi lanh |
|---|---|---|
| 25,4 | Ty đã dừng | 0 |
| 17,5 / 20 / 23 | Đang chạy | Chỉ vạch dầu ở đường hồi B→T và trong thân van, do sửa lỗi 3 bên dưới |

## 2. Lỗi kỹ thuật trong bản đã duyệt và cách sửa

1. **Cửa A nằm dưới piston khi ty co hết.** Ở bản cũ, cửa A ở x+40, trùng mặt piston khi `ext = 0`, nên dầu không có đường vào khoang đáy.
   → Cửa A khoan xuyên nắp đáy, mở vào một hốc trên mặt nắp. Dầu tới được piston ở mọi vị trí.
2. **Chốt đáy lơ lửng, không nối với xi lanh, và ty không có mắt.**
   → Thêm chạc ở nắp đáy, chốt nằm trong tai cố định trên khung (có ký hiệu gối cố định). Đầu ty có mắt ty và chốt nằm trong tai cần, vẽ cắt rời bằng nét gãy.
3. **Dòng hồi sai tỉ lệ.** Bản cũ cho dòng hồi bằng 0,5 lần dòng cấp. Với lòng 84 px và ty 44 px đã vẽ, tỉ lệ diện tích là 1 − (44/84)² = **0,726**.
   → Vạch dầu ở đường B, trong thân van và về thùng chạy đúng 0,726 lần tốc độ phía A.

## 3. Nâng chất lượng hình (giữ phong cách 2D/2.5D technical cartoon)

- Vỏ và nắp đáy vẽ mặt cắt có gạch chéo, giữ màu cam của bản đã duyệt. Có viền sáng ở mép trên (nguồn sáng trên-trái) và bóng mềm dưới cụm xi lanh và ty.
- Piston có 2 phớt (đen), vòng dẫn hướng (đồng) và đai ốc. Ty chrome có dải sáng.
- Đầu dẫn hướng: bạc dẫn hướng, phớt ty, gạt bụi, bu lông mặt bích.
- Chốt có vòng bóng quanh bạc, có điểm sáng. Nét viền đồng đều 2,2 px.
- **Dầu trong xi lanh** đi theo đúng dòng chảy:
  - Phía cấp: dầu tỏa từ cửa A vào khoang đáy.
  - Phía hồi: dầu dồn về cửa B.
  - Tốc độ vạch lấy từ cùng giá trị tích phân với đường ống. Khi con trượt đóng, vạch dừng; khoang đáy vẫn đỏ vì giữ áp tải.

## 4. Đoạn 8 giây (17,5–25,5 s)

| Thời gian (s) | Tay gạt | Độ mở P→A (px) | Hành trình ty (px) | Q phía đáy (tương đối) | Q phía ty (tương đối) |
|---|---|---|---|---|---|
| 17,5 | 1,00 | 48,0 | 42,6 | 1,000 | 0,726 |
| 21,0 | 1,00 | 48,0 | 143,4 | 1,000 | 0,726 |
| 24,5 | 0,68 | 35,2 | 243,6 | 0,734 | 0,532 |
| 25,0 | 0,02 | 0 | 247,0 | 0 | 0 |
| 25,5 | 0 | 0 | 247,0 | 0 | 0 |

**QA** chạy trên toàn bộ SC05 V4.2: 1.058 khung, 0 lỗi. Các điểm kiểm:
- Không mở van khi tay gạt nằm trong vùng chết.
- Ty không lùi khi P→A đang mở.
- Piston không qua mặt nắp và cách đầu dẫn hướng ít nhất 100 px.

## 5. Điều cần owner quyết

- **Cơ cấu nâng cần:** bố cục SC05 đã duyệt chỉ có xi lanh, không có cần máy. Để giữ đúng bố cục, V4.2 chỉ vẽ tai cần cắt rời ở mắt ty. Nếu owner muốn **thấy cần nâng lên** cùng lúc với ty, cần thêm một khung cơ cấu (chốt chân cần, xi lanh xoay quanh chốt đáy), tức là đổi bố cục. Tôi chờ owner quyết trước khi làm.
- Các cảnh khác chưa đụng tới. Không render hàng loạt.

## 6. File

- `EP02_SC05_V42_cylinder_17.5-25.5s_DRAFT.mp4`: đoạn 8 giây bản sạch, không chia đôi.
- `EP02_SC05_V42_full_DRAFT.mp4`: toàn cảnh SC05 V4.2 (35,3 s). Vẫn là một cảnh, không phải render hàng loạt.
- `EP02_SC05_V4_vs_V42_AB_DRAFT.mp4`: A/B 8 giây, cùng vùng cắt, cùng khung hình (trên: V4 đã duyệt, dưới: V4.2), phóng 1,4 lần như nhau.
- `SC05_t{18.0,21.0,24.5}_V4.jpg` và `_V42.jpg`: ảnh nguyên khung cùng thời điểm.
- Âm thanh: chỉ tiếng máy tổng hợp. Thoại chờ file ElevenLabs owner duyệt.
