# Issue #13 · Siemens NX CAD pilot · Codex và Argon V2

Ngày kiểm tra 2026-11-16. Nhánh Codex tách từ `main` tại `2cce44c`, theo [task NX](../NX_PILOT_CAD_BUILD_TASK_V1.md), [source register](../CAD_SOURCE_REGISTER_PC2008.md) và [master plan](../V7_ENGINEERING_CINEMATIC_MASTERPLAN.md). Các file CAD và ảnh bàn giao nằm cục bộ.

## Môi trường và nguồn

- NX 12.0.0.27 ở `C:\Program Files\Siemens\NX 12.0\NXBIN\ugraf.exe`. Journal Player (Alt+F8) chạy Python 3.6.1. `run_journal.exe` chạy được khi thư mục làm việc là `NXBIN`. Modeling và STEP đã thực thi bằng phần mềm cài sẵn. Windows Application Control chặn một số Python extension của NX khi import trực tiếp, có `NXOpen_Assemblies.pyd`, `NXOpen_UF.pyd` và Drafting. Phiên NX vẫn mở được các part và đọc được cây assembly của Argon qua đối tượng part. Kết quả chỉ xác nhận chức năng đang chạy trên máy.
- Gói V6 cục bộ dưới `CAPY_BK_EP02_FULL_V6_Claude_handoff`. Hash bundle `1ab3be9e4244dcca41f10a8523f928218d8d6c921535c8615ef00c60a8712d1`. Hash MP4 `53a665b8fb0ef361bde84c08aa7d65437dfbbe61a444904e8b2175cbeb0c1bf0`. Hash SRT `58913d7ac5abf3dc9b8270f145a416c826f5452187dbaa3fcc48ba6fe4e858d3`. Cây nguồn Godot ở ref V6 `95d7f59` chứa `episodes/EP02/demo_v4/godot/art/rig.json`. Pilot kế thừa hệ chốt minh họa của rig đó và vẽ biên dạng NX mới. Không có CAD OEM được xác minh trong bộ V6.
- Cấu hình brochure chọn boom 5.700 mm và arm 2.925 mm. Hai xi lanh cần có bore/stroke/ty 120/1.334/85 mm, tay gầu 135/1.490/95 mm và gầu 115/1.120/80 mm. Tất cả tâm chốt, chiều dài lắp khi đóng, bán kính lỗ, biên dạng thép và giá trị ngang Y ghi `ASSUMED-PARAM`. Kích thước lựa chọn 5.700/2.925 mm và khoảng cách chốt concept được để ở các dòng riêng. [Komatsu CEN00049-08](https://d3is8fue1tbsks.cloudfront.net/PDF/Komatsu/PC200-8_PC200LC-8.pdf).

## Pilot Codex đã chạy

NX lưu 13 part chi tiết, ba tư thế low/reach/high và một part tách cụm xi lanh để quan sát. Mỗi tư thế có 76 solid. Boom và stick có web côn, tấm bọc trên/dưới, lỗ chốt và tai. Gầu có sàn cung tròn, má bên và năm răng. Các xi lanh có vỏ, ty, đầu piston, bạc dẫn và tai lắp. Feature NX chỉnh sửa được. Một số chiều rộng và chiều dài Extrude nối expression. Biên dạng tham số và quan hệ vị trí được cập nhật bằng journal. Các part tư thế là multibody. Bản Codex không có assembly component chịu ràng buộc.

Gốc đặt tại chốt chân cần, +X hướng gầu, +Y về trái máy, +Z lên, đơn vị mm. Bốn khâu gầu khép theo giao hai đường tròn và một nhánh cố định. Chiều dài xi lanh là khoảng cách A–B, hành trình từ vị trí đóng giả định và ty giữ nguyên chiều dài. `pose_check.csv` kiểm ba trạng thái trên mô hình giải tích. Hành trình lớn nhất tại ba trạng thái: cần 859,808 mm, tay gầu 471,214 mm, gầu 981,657 mm. Bảng vị trí tâm chốt không dùng để xác nhận va chạm, độ bền hay lắp vừa ngoài thực tế.

Chạy lại `nx_pilot.py` và `geometry.py` từ một thư mục dữ liệu cục bộ. Trong PowerShell, vào `$env:UGII_BASE_DIR\NXBIN` và gọi `run_journal.exe <đường dẫn nx_pilot.py>`. Script tạo một thư mục NX mới theo thời gian. `nx_review.py` mở lại các part đã lưu và kiểm số solid, datum cùng STEP. Đầu ra NX có log và CSV cục bộ. Phiên xuất ảnh tự động của Codex qua UF bị chặn nên không có bộ bốn ảnh giao diện do journal Codex xuất.

Bản bàn giao Codex ở thư mục `NX_NATIVE_20261116_191809`. Khi mở lại bằng NX, cả ba tư thế giữ đủ 13 datum và 76 solid. Sai lệch datum tối đa 0,000000672 mm so với CSV đã làm tròn. `PC2008_REACH_AP214.step` chứa 76 `MANIFOLD_SOLID_BREP` và khai báo đơn vị mm. Đây là STEP của part nhiều solid ở tư thế reach.

## Review gói Argon V2 do owner cung cấp

- Tệp `NX_NATIVE_V2_ARGON_20261116.zip`, SHA-256 `99f886563247f17366c31005ae4a02cbc6e5232b61c0c9ed1e5a443337b591dd`, vượt qua kiểm tra CRC. `joint_map.csv`, `assembly_params.csv` và `pose_check.csv` trùng byte với pilot Codex. So sánh hình và cây lắp ráp trên cùng các giả định này.
- Kiểm độc lập bằng NX 12: mở part `PC2008_REACH_PLACED_SOLIDS.prt` có 181 solid. Mở `PC2008_WORK_EQUIPMENT_CONCEPT_ASSY_REACH.prt` có 27 component, 11 constraint và 0 part báo chưa nạp. Các file STEP AP214 low/reach/high đóng dấu cuối tệp và chứa 181 `MANIFOLD_SOLID_BREP` mỗi file. STEP reach khai báo mm.
- Bốn tấm trong ZIP là các bảng trình bày có chú thích, với hình lấy từ solid NX qua luồng xuất. Chúng cho thấy ống xi lanh, đầu ty, gầu cong, tai chốt và các tư thế. Gói ZIP có log và phần kiểm feature tree, chưa chứa journal `.py` tạo bản Argon. Giữ kèm journal đúng phiên bản nếu muốn dựng lại từ nguồn.
- Argon V2 phù hợp hơn làm bản CAD concept để owner duyệt vì đã đóng gói part, assembly, STEP và bảng pin riêng. Kiểm tra tiếp trong NX là đổi một tư thế bằng constraint và chạy kiểm giao thoa trên đường đi, tập trung khu vực tai chân cần, đầu ty và bốn khâu gầu. Ba snapshot hợp lệ theo bảng hành trình là mốc để so. Chưa có kích thước OEM đủ cho shop model hay dữ liệu tải/vật liệu cho FEA.
