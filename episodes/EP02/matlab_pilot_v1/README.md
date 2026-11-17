# EP02 V7 — MATLAB và ANSYS Engineering Validation

DRAFT · 17/11/2026 · [Issue #17](https://github.com/ngokiet1412-web/Creativity/issues/17)

| Hạng mục | Kết quả thực thi |
| --- | --- |
| MATLAB R2026b `26.2.0.3386108` | **PASS** cho động học và mô hình lưu lượng lý tưởng. Tái chạy Argon V3 cho sai khác số bằng 0 trên toàn bảng 540 frame. Bản sửa giữ ba tư thế NX và 2.161 mẫu ở 120 Hz qua các kiểm tra hành trình, độ ăn ty, vòng bốn khâu, khoảng cách với nền và hãm cuối. |
| NX 12.0 | **PASS** cho bản CAD đã chọn trong phạm vi 26 cặp cụm tại mỗi tư thế LOW, REACH và HIGH. Chạy lại 6.243 phép Boolean, 0 giao khối và 0 lỗi. Lượt quét va chạm liên tục và giao thoa phần cứng chốt nằm ngoài các cặp đã thử. |
| Ansys Mechanical 2024 R1 và MAPDL 24.1 | **PASS** cho phản lực và hai chỉ số hội tụ đã định. Static Structural hoàn tất ở ba cỡ lưới và một trường hợp đổi gối đỡ. **FAIL** nếu dùng ứng suất đỉnh làm chỉ số hội tụ. |
| Blender | Kiểm tra hàm đọc khoang dầu trùng MATLAB trên 3.240 thể tích. Phần rig, đường đi của tải và bản đồ ứng suất ở giai đoạn đề xuất. |

## Nguồn mô hình và phạm vi xác minh

NX GUI ghi nhận file đang xem là `PC2008_ARGON_V3_NX_FIT_DRAFT/PC2008_HIGH_PLACED_SOLIDS.prt`, SHA-256 `491edb470e2963273a0130ecd16d567f85633df1dab2f6cd9329c751f43973d7`. Bản này chứa thay đổi fit của [PR #14](https://github.com/ngokiet1412-web/Creativity/pull/14) tại `a46bcb08f03e5fedb1898e93d650e7365c5d3ead`. Mã và bảng đối chứng Argon lấy từng byte từ [PR #15](https://github.com/ngokiet1412-web/Creativity/pull/15) tại `51f10d630fe32b40d1501500c4a989ac8259a959`. [PR #16](https://github.com/ngokiet1412-web/Creativity/pull/16) tại `462e89d27c787116d0336d5dc87447d8e920b345` cung cấp audit đối chứng và ghi nhận giao thoa trên CAD V2.

Brochure [Komatsu CEN00049-08](https://d3is8fue1tbsks.cloudfront.net/PDF/Komatsu/PC200-8_PC200LC-8.pdf) cho lựa chọn cần 5.700 mm, tay gầu 2.925 mm và bộ kích thước bore × stroke × rod 120 × 1.334 × 85 mm (hai xi lanh cần), 135 × 1.490 × 95 mm (tay gầu), 115 × 1.120 × 80 mm (gầu). Các chốt, chiều dài co, dung sai lắp, mô hình khoang dầu và kích thước chốt FEA mang nhãn `ASSUMED-PARAM`. Tính nhất quán giữa CAD, bảng chốt và mô hình là tiêu chí của pilot.

## MATLAB và khoang dầu

- Giữ spline Argon đến 14,2 s. Đoạn quintic 14,2–16,8 s nối vị trí, vận tốc, gia tốc ở đầu và cho vận tốc, gia tốc bằng 0 ở cuối. Thay đổi góc tối đa 0,088°. Gia tốc góc cần trước điểm dừng từ −0,5624 deg/s² ở Argon về 0. Kiểm tra hai phía ở điểm nối và dừng cho sai khác gia tốc dưới 2,5×10⁻⁸ deg/s². Jerk có thể đổi bậc tại chỗ nối. Gia tốc khởi động kế thừa Argon.
- Toạ độ chốt và chiều dài xi lanh tại ba tư thế khớp các CSV NX đến 6,72×10⁻⁷ mm và 4,26×10⁻⁷ mm. Đây là độ khớp số của cùng mô hình. Độ ăn ty nhỏ nhất theo công thức concept 405,38 mm, khoảng hở bao gầu với nền 83,38 mm, sai số khép vòng dưới 10⁻⁹ mm. Khoảng hở dùng tập điểm bao, không suy ra khoảng cách mặt lưới hay va chạm chi tiết ở các tư thế trung gian.
- Hành trình sử dụng trong pilot lần lượt 572,05–859,81 mm (cần), 323,65–519,93 mm (tay gầu) và 863,71–974,62 mm (gầu). Dịch tai chân xi lanh tay gầu +230 mm và chân xi lanh gầu +195 mm theo khung cục bộ của CAD sửa, nên chiều dài hai xi lanh này có thể đổi khoảng 51,18 mm và 14,59 mm so với trace cũ, kể cả ảnh hưởng đổi easing.
- `shared_model.json` chứa các mốc khoang từ CAD. Ở xi lanh cần, đầu lòng nằm tại 172 mm từ mắt thân, đầu trong gland tại 2.038 mm, hai mặt hiệu dụng của cụm piston cách mắt ty 2.000 và 1.918 mm. Với chiều dài chốt `L` tính bằng mm, cột dầu là `L−2172` và `3956−L`. So với MATLAB Argon, cột cap ngắn hơn 272 mm và cột rod dài hơn 196 mm trong vùng xét. Công thức axial khớp script Blender V3. Adapter `chamber_geometry.py` trả khoảng phủ axial và bán kính theo mét, sai khác thể tích tối đa 9,77×10⁻¹⁴ L khi đối chiếu 540 frame ở cả ba xi lanh. Mô hình bỏ qua dầu trong ống và cổng, khe nhỏ, độ nén và rò.
- Lực lý tưởng theo `F = p_cap·A_cap − p_rod·A_annulus`. Tình huống minh họa dùng 100 bar cap và 10 bar rod. Kết quả một xi lanh nâng cần là 107,462 kN, cả cặp là 214,924 kN. `Q_cap = A_cap·v` và `Q_rod = −A_annulus·v` theo quy ước dương là dòng vào khoang. Lúc thu ty, khoang cấp/hồi đảo vai. Lưu lượng cấp cao nhất cho cặp cần là 29,43 L/min. Có đối chiếu đơn vị, dấu và `p·Q = F·v`. Áp suất và chuyển động được đặt độc lập để minh họa, chưa có mô hình động lực, tổn hao và điều khiển thực.

## Ansys Mechanical Static Structural

Journal NX xuất duy nhất solid `Pin_shank` từ `pin_R42_L170.prt` của cùng bộ CAD, SHA-256 `2c0441ba6780d51d836e4523226a58d355c87046fabac64701cfabdeb3e3a6df`. STEP AP214 là một solid có bán kính 42 mm, chiều dài 170 mm, trục Y và đơn vị mm. Shaft đối xứng qua Y = 0, bản dựng được chọn lấy một chốt ứng với **một** xi lanh nâng cần. Lược hai vành giữ và keeper tab khỏi trường hợp tải, nên đây là bài toán thân chốt. Không dùng assembly nhiều solid lồng nhau làm mô hình contact. Mechanical đọc STEP, kiểm tra ba mặt và quy mô, áp điều kiện biên vào lưới tetra bậc hai SOLID187 và giải bằng MAPDL. Log ghi bản phát hành, checkout Mechanical Enterprise, điều kiện biên và kết quả. [Hướng dẫn Static Structural của Ansys](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/ans_str/Hlp_G_STR2_5.html)

Thép đàn hồi đẳng hướng lấy từ vật liệu Structural Steel mặc định của Mechanical, `E = 200 GPa`, `ν = 0,30`, xác nhận trong `ds.dat`. Chốt được bỏ qua biến dạng dẻo và chỉ giải tĩnh tuyến tính. Tải hướng `+X` của hệ chốt từ lực một xi lanh với 100/10 bar. Trên nửa bên `X < 0`, các nút mặt nhận lực phân bố theo diện tích bao quanh và trọng số `max(−X/R,0)²·max(1−(Y/38)²,0)`. Chuẩn hóa tổng tải về 107,462 kN. Mô hình này xấp xỉ áp lực từ mắt ty, chưa mô phỏng độ hở, ma sát và trượt giữa lỗ, tai và chốt.

```text
Trục chốt Y [mm], tải theo hướng +X
   -85    -72  -46  -38         0         +38  +46 +72    +85
    |------[ đỡ ]----[ vùng tải phân bố  ↑  ]----[ đỡ ]------|
            UX=UZ=0                          UX=UZ=0
                               Một nút trên gối dương giữ UY
Nhạy điều kiện biên    Hai gối đổi bề rộng từ |Y|=46–72 thành 52–72
```

| Case | Cỡ đặt [mm] | Phần tử | Ứng suất tại điểm giữa [MPa] | Ứng suất đỉnh [MPa] | Dịch chuyển đỉnh [mm] |
| --- | ---: | ---: | ---: | ---: | ---: |
| Coarse | 8 | 3.458 | 25,694 | 51,795 | 0,012127 |
| Medium | 5 | 10.652 | 25,992 | 70,552 | 0,011945 |
| Fine | 3 | 32.544 | 26,008 | 106,660 | 0,011929 |
| Fine, dời mép gối 6 mm | 3 | 32.544 | 31,773 | 96,847 | 0,014132 |

Nút đọc ứng suất mục tiêu gần `(42,0,0)` mm, cách vị trí mục tiêu 0,22 mm ở lưới mịn. Từ vừa sang mịn, ứng suất ở điểm này đổi +0,062% và dịch chuyển lớn nhất −0,134%. Tổng phản lực `PRRSOL` theo X là −107.460 N sau làm tròn theo log. Sai lệch chuẩn vector 0,00196%, nhỏ hơn ngưỡng 0,2%. Sai lệch này bị chi phối bởi số chữ số in trong bảng. Đỉnh ứng suất tăng 51,18% từ lưới vừa sang mịn. Nút đỉnh lưới mịn có Y = −45,71 mm, ngay sát mép gối −46 mm. Khi dời mép đến −52 mm, nút đỉnh dịch đến −52,11 mm, ứng suất điểm giữa tăng 22,17% và dịch chuyển đỉnh tăng 18,47%. Kết quả nhạy với gối đỡ và chưa đủ để kết luận độ bền của chốt Komatsu.

## Chạy lại và dùng kết quả

Trong PowerShell ở checkout, lấy ref nếu thiếu commit Argon, rồi chạy với bộ CAD chủ dự án đã chọn và một thư mục mới. Yêu cầu Python, MATLAB, NX và Mechanical có thể chạy trên máy. Thêm `-MatlabOnly` nếu chỉ chạy phần động học.

```powershell
git fetch origin refs/pull/15/head:refs/remotes/origin/pr-15
./episodes/EP02/matlab_pilot_v1/reproduce.ps1 -Cad '<PC2008_ARGON_V3_NX_FIT_DRAFT>' -Out '<thu-muc-ket-qua-moi>'
```

- `source_manifest.json` ghim đầu vào. `matlab/` có `summary.json`, bảng đối chiếu ba tư thế NX, dấu vết 120 Hz và 540 frame, tọa độ chốt mỗi frame, đồ thị PNG và bản FIG chỉnh sửa được.
- `nx_verify/` chứa CSV Boolean và log. `ansys/` chứa STEP, báo cáo hội tụ, file `.mechdat`, thư mục dữ liệu đi cùng mỗi project, `.rst`, deck, log, trường vô hướng và ảnh gốc Mechanical. Giữ `.mechdat` cạnh thư mục `_Mech_Files` khi di chuyển để mở kết quả. Ảnh Mechanical có scale biến dạng hiển thị. Sử dụng legend và giá trị số khi đọc độ võng.
- Kết quả chạy trên máy nằm dưới `CODEX_MATLAB_ANSYS_20261117` cùng cấp thư mục CAD. Repo lưu mã và báo cáo để tái chạy. File CAD và kết quả native giữ tại máy.

## Nối sang Blender

Chốt phiên bản hình và rig theo CAD fit ở PR #14 trước khi thay trace. Dùng `pins_540_frames.csv` để kiểm tra vị trí theo `(X,Y,Z)/1000` và trục quay ngang Y. Không dời mesh bằng nội suy phi tuyến. Dùng `motion_540_frames.csv` để xác định vị trí piston, lấy khoảng dầu từ `chamber_geometry.py` và dùng lưu lượng có dấu để chọn chiều animation. Dựng một mũi tên lực theo hai đầu chốt của một xi lanh, gắn nhãn tải giả định. Không gán độ lớn này cho tải chốt thực hay áp suất biến thiên theo thời gian.

Để trình bày kết quả Ansys, dùng node ID, `nodes_mm.csv` và các trường vô hướng xuất từ đúng một case. Nếu cần tạo bề mặt cong để ánh xạ, xuất mặt lưới kết quả tương ứng từ `.rst` rồi kiểm tra bán kính và trục trước khi gắn trường. Giữ thang MPa cố định và đưa con trỏ đến điểm đọc giữa chốt. Minh họa tách biệt ảnh hưởng của việc dịch vùng gối. Dữ liệu còn thiếu cho bài toán ngoài phạm vi pilot gồm bản vẽ cơ cấu theo đúng cấu hình, độ hở và lớp lắp chốt, vật liệu thực, độ cứng tai, áp suất hai khoang đồng bộ theo pose và lịch tải đã xác nhận.
