# EP02 V7 · Hydraulic Reveal · bàn giao G0/G1 (DRAFT)

**Ngày kiểm tra:** 2026-11-16. **Phạm vi:** kiểm kê V6 và môi trường, đề xuất duyệt bộ máy 2.5D và một clip kiểm chứng 17 giây. Bốn khung cần owner duyệt trước khi chốt thiết kế cho các cảnh khác. [Master plan đã đọc trên main, `00191ca`](https://github.com/ngokiet1412-web/Creativity/blob/00191ca258a6e53fb74a5fd194a97bf9ca790cf7/episodes/EP02/V7_ENGINEERING_CINEMATIC_MASTERPLAN.md).

## G0 · Asset và môi trường

| Nguồn | Phát hiện và quyết định |
|---|---|
| V6 giao cục bộ | `EP02_FULL_V6_DRAFT.mp4` 522,088 giây, 1920 × 1080, 30 fps, H.264. Giải mã toàn bộ hình không lỗi. Tệp có luồng AAC nhưng đo gần sàn đo ffmpeg (−91 dBFS cả trung bình và cực đại). SRT có 123 cue từ 00:00,800 đến 08:37,874 và `VOICE_SHEET.csv` gắn thoại. V6 là nguồn hình, nội dung và nhịp tham khảo. |
| Nguồn dựng V6 | Bundle `ep02-full-v6.bundle`, ref cục bộ `handoff/ep02-full-v6` tại `95d7f591e84276c0773402f9dadf55b0e306a677`, tên ref trong gói vẫn là `claude/ep02-full-v5`. Có Godot 4 project, 14 cảnh, script tạo timeline và asset kỹ thuật. SC03–SC05 ở `segments/`; SC05 V4.2 là biến thể kỹ thuật. Có thể dùng lại nhịp pilot/van/xi lanh và cách khoanh chốt ở SC06–SC07. |
| Hình và rig dùng cho V7 | Tái dùng sáu PNG của demo V4, `rig.json` và rig Blender proof `952a807`. Atlas và phông là ImageGen do dự án tạo 2026-11-12, theo nét EP01, trạng thái DRAFT. `host_capy.png` là hình cục bộ đã dùng trong EP02, giữ mặt và áo. Cảnh V7 thêm mặt cắt, đèn và lớp chú thích bằng Blender Python ngày 2026-11-16. File đầu ra đóng gói hình Capy và font hệ thống, chỉ để bàn giao cục bộ. [Manifest V4](../demo_v4/ASSET_MANIFEST.md) · [Nguồn và prompt ảnh](../demo_v4/godot/art/source/PROVENANCE_codex_v2.md). |
| CAD, bản thu, mô phỏng | Chưa tìm được bộ CAD PC200-8 đủ quyền, shop drawing định vị tai chốt theo serial, bản thu đã duyệt hoặc dự án FEA của máy trong gói V6/workspace được kiểm. Hình gầu nguồn đã vẽ đất nên cảnh bắt đầu với gầu có tải. |
| Siemens NX | NX 12.0.0.27 và `NXBIN/run_journal.exe` có sẵn. Journal VB kiểm tra mở NXOpen session và tạo được part đơn vị mm. Journal Python báo lỗi khởi tạo interpreter. Windows Application Control chặn DLL sinh ra cho journal xuất CAD nên chưa có mẫu STEP/STL thật từ NX. Đây là kết quả kiểm tra chức năng cục bộ, chưa xác nhận quyền phát hành CAD. |
| MATLAB / Simulink | R2026b 26.2, MATLAB chạy batch; `license('checkout','SIMULINK')` thành công và mở library Simulink. Máy thông báo license Trial chỉ dùng đánh giá. Dùng MATLAB để kiểm chứng mô hình động học và CSV. Simscape và Simscape Multibody được phát hiện, chưa dùng cho demo. [MathWorks về test và checkout license](https://www.mathworks.com/help/matlab/ref/license.html?s_tid=doc_ta). |
| ANSYS | Workbench/Mechanical APDL 2024 R1 (24.1) được cài. MAPDL batch lấy license và chạy lệnh kiểm tra, exit 0. Chưa có vật liệu, khe hở, tiếp xúc, tải và điều kiện biên được duyệt cho tai chốt, nên chưa chạy FEA. [Ansys MAPDL batch](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/ans_ope/Hlp_G_OPE3_4.html). |
| Blender | Blender 5.3.0 (`02f0899d78e3`) tại `C:\Program Files\Blender Foundation\Blender 5.3\blender.exe`, Python 3.13.13. Scene và render EEVEE chạy trên Dell 7560. Blender mở lại file, kiểm tra đủ 7 ảnh và 2 font đã nhúng. [Định dạng nhập Blender](https://docs.blender.org/manual/en/5.3/files/import_export/index.html). |

Đã đối chiếu checksum MP4 và SRT V6 trong thư mục handoff với bản OneDrive. Hai cặp trùng nhau. Dùng SHA-256 sau để xác định đúng nguồn.

| Tệp | SHA-256 |
|---|---|
| `EP02_FULL_V6_DRAFT.mp4` | `53a665b8fb0ef361bde84c08aa7d65437dfbbe61a444904e8b2175cbeb0c1bf0` |
| `EP02_FULL_V6_vi.srt` | `58913d7ac5abf3dc9b8270f145a416c826f5452187dbaa3fcc48ba6fe4e858d3` |
| `ep02-full-v6.bundle` | `1ab3be9e4244dcca41f10a8523f928218d8d6c921535c8615ef00c60a8712d1` |

## G1 · Máy, hệ tọa độ và quan hệ chốt

Khung thuận tay phải: +X tiến về gầu, +Y về trái theo chiều tiến của máy, +Z lên. Gốc đặt trên nền, ngay dưới chốt chân cần. Ba trục chốt song song +Y. NX và CSV dùng mm, Blender dùng m với hệ số **0,001 đúng một lần**. `joint_map.csv` lưu vị trí giữa máy (Y=0) của từng chốt ở khung 1. Hai xi lanh cần có cùng tọa độ X/Z nhưng tại hai lớp Y riêng của rig. `motion_trace.csv` ghi t_s, góc local theo +Y, chiều dài chốt–chốt và hành trình từng xi lanh, cùng tọa độ X/Z mọi khung. Góc cần tính từ thân, tay gầu tính từ cần, gầu tính từ tay gầu. Để tránh nhầm quy ước ảnh Godot, CSV đã chuyển sang góc thực nhập Blender.

| Khâu | Cha → chốt/điểm cuối | Quan hệ |
|---|---|---|
| Cần | Thân → `boom_pivot` → `stick_pivot` | Khoảng cách hai chốt 5.700 mm |
| Tay gầu | Cần → `stick_pivot` → `bucket_pivot` | Khoảng cách hai chốt 2.925 mm |
| Gầu | Tay gầu → `bucket_pivot` | Hai thanh qua `bucket_side–bucket_b–bucket_boss` dài 650 và 750 mm, vòng khép dùng một nhánh giao hai đường tròn |
| Xi lanh cần/tay/gầu | Từng cặp `*_a`, `*_b` | Trục theo A→B, chiều dài giữa tâm hai chốt là `norm(B-A)`. Vỏ, ty và thanh dẫn là chi tiết riêng có kích thước cố định. |

Chiều dài 5.700 mm và tùy chọn 2.925 mm theo brochure đúng họ PC200-8. Các tọa độ lắp và kích thước chi tiết còn lại dùng thông số minh họa của rig cũ. Các giá trị dưới đây chỉ kiểm tra tính nhất quán của mô hình. [Komatsu PC200-8/PC200LC-8, CEN00049-08](https://d3is8fue1tbsks.cloudfront.net/PDF/Komatsu/PC200-8_PC200LC-8.pdf).

### Đường trao đổi CAD

`nx_calibration.vb` định nghĩa chi tiết hiệu chuẩn bất đối xứng 1.000 × 200 × 300 mm và ba dấu chuẩn tại chốt lấy từ CSV. Khi journal được phê duyệt trên máy, nó tạo PRT và xuất STEP AP214 để lưu hình học gốc, cùng STL để Blender nhập bằng trình tích hợp sẵn. Quy trình giữ hệ trục, đối chiếu ba dấu chuẩn sau nhập và kiểm tra STEP khai báo mm. STL chưa đủ cho assembly sản xuất vì không giữ cây chi tiết, vật liệu và pivot. Khi có CAD đủ quyền, xuất mesh từng chi tiết theo tên, giữ STEP gốc cục bộ và gắn pivot từ CSV riêng. Hình máy trong demo này dùng rig Blender và PNG V4, không phụ thuộc NX. [Siemens CAD interoperability](https://www.siemens.com/en-us/products/designcenter/cad-software/cad-interoperability/).

Đã chạy phép đo ở đầu Blender bằng fixture STL tổng hợp, với cả ba dấu chuẩn từ CSV. Blender nhập đúng hộp 1,000 × 0,200 × 0,300 m và sai số ba dấu chuẩn tối đa 0,000504 mm. Kết quả này kiểm chứng trình nhập và phép đổi đơn vị. Phép thử tài liệu STEP dùng chuỗi khai báo đơn vị mẫu. Xuất STEP/STL từ NX và kiểm tra lại trên chính file NX vẫn đang chờ.

## Kiểm chứng demo Hydraulic Reveal

- MATLAB dựng 510 mẫu 30 fps, kiểm thêm 2.037 mẫu 120 Hz. Blender so các mốc MATLAB với transform đã tính của rig tại 510 khung và 509 điểm giữa khung. Ngưỡng đối chiếu hình học là 0,1 mm. Sai lệch lớn nhất ở chốt 0,00152 mm, ở trục xi lanh 0,00461 mm. Khoảng hở gầu với nền thấp nhất 289,68 mm. Gầm cố định, không có animation di chuyển xích.
- Hành trình ty từ vị trí đóng trong shot: cần 564,14–886,60 mm, tay gầu 529,42–602,39 mm, gầu 1.070,64–1.092,42 mm. Tệp `actuator_strokes.png` vẽ ba đường hành trình. Không có giá trị áp suất/lưu lượng định lượng trong trace. Mũi tên trên mặt cắt biểu diễn cấp vào khoang đáy và hồi ra khoang ty khi xi lanh nâng cần đang kéo dài.
- EEVEE render 510 PNG trong 194,34 giây. MP4 H.264 1920 × 1080 @ 30 fps dài đúng 17,000 giây và giải mã hết. Clip kỹ thuật im tiếng, câu Capy hiển thị dạng chữ duyệt. Các khung 52, 118, 272 và 464 cho thấy vào cảnh, lộ mặt cắt, ty đang kéo dài và Capy chốt ý.
- Giữ góc ngang để đọc chốt từ asset nguyên bản. Hướng máy 3/4 và X-ray xuyên thân thật cần mesh có độ dày hoặc artwork đã duyệt từ góc tương ứng. Mặt cắt hiện là lớp kỹ thuật đặt cạnh máy và dùng cùng hành trình với rig. Ảnh `EP02_V6_V7_DOI_CHIEU.jpg` đặt hai cặp khung cùng nội dung cạnh nhau, ghi timecode gốc của từng bản.

## Những nguồn cần bổ sung

1. Ảnh đối chiếu hoặc bản vẽ có phép dùng của đúng cấu hình PC200-8: khoảng cách từ khung đến chốt, bề rộng và độ dày khâu, hai lớp tai xi lanh, offset ngang và kích thước lúc đóng/mở. Cần cho góc 3/4 và kiểm chứng hình dáng.
2. Shop manual được phép dùng, đúng serial và cấu hình, để xác định cổng, thứ tự đường hồi, bố trí đường ống cũng như logic pilot/CLSS. Cần xác nhận bore/rod, dữ liệu tải, lưu lượng, ma sát và tổn thất nếu muốn mô phỏng áp suất. Demo chỉ dạy nguyên lý.
3. Để làm ANSYS cho một tai chốt: cần bản vẽ, thép và đường cong vật liệu, chốt/gối, tiếp xúc, điều kiện biên, nguồn tải/hướng tải. Sau đó mới chọn phần tử, chạy phân tích độ nhạy lưới và báo cáo ứng suất/chuyển vị dưới giả định rõ ràng.
4. Bản thu được owner duyệt và quyền sử dụng artwork/font cho bản phát hành. Bản nhìn thử chỉ để review cục bộ.

## Dựng và sửa

Chạy từ gốc repo với đường dẫn local của Capy và FFmpeg. Thêm `-PreviewOnly` để chạy thử MATLAB → Blender và xuất 4 ảnh, hoặc bỏ tùy chọn đó để render MP4. Dùng `-IncludeNX` ở một thư mục output mới khi hệ thống cho phép journal NX. Có thể nạp lại `EP02_hero.blend` để chỉnh đèn, camera và mặt cắt. Nếu đổi góc/nhịp máy, sửa waypoint trong `export_motion.m`, chạy lại pipeline và đối chiếu mốc mở mặt cắt.

```powershell
$ff = (Resolve-Path '../.capy-tools/python/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe').Path
.\episodes\EP02\engineering_v7\build.ps1 -Out 'build/EP02_v7_hydraulic_reveal' `
    -Capy 'episodes/EP02/demo_v4/godot/local/host_capy.png' -FFmpeg $ff
```

Đầu ra chính: `EP02_hero.blend`, `EP02_V7_HYDRAULIC_REVEAL_DRAFT.mp4`, `joint_map.csv`, `motion_trace.csv`, `blender_geometry.csv`, `actuator_strokes.png`, `preview_*.png`. Mã và tài liệu mới nằm trên branch của demo, file nguồn V6 và file dựng thử được giữ tại máy.
