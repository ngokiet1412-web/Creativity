# Storyboard demo · 42 giây (V3) & Clip QA Proof 16 giây

## 1. Bản Demo nghiệm thu Giai đoạn 2 (`sequence` · 42,0 giây · 1920 × 1080 · 30 FPS)

| Cảnh | Thời gian | Hình, diễn xuất nhân vật 2D tách lớp và cơ khí PC200-8 | Tiếng & Phụ đề |
|---|---|---|---|
| **D01 · Chào kênh & Màn hình kỹ thuật** | `00:00.000–00:04.200` | Studio EP01, Capy vẫy tay và gọi *“Kĩ Sư Ơiii!”*. Giữ áo polo BK, ly nước, laptop và micro. Bên phải là màn hình blueprint kỹ thuật hiển thị sơ đồ động 5 khâu thủy lực PC200-8, sóng âm thanh trực tiếp và mô hình động học cần–tay gầu–gầu. | `SIGNATURE.wav` ở `00:00.480` (file gốc đã duyệt của owner). |
| **D02 · Công trường & Điểm danh 4 cụm chính** | `00:04.200–00:10.200` | Capy và anh kỹ sư đứng sau hàng rào gỗ công trường bằng rig 2D tách lớp (`Torso`, `Head`, `Hat`, `ArmR`, `ArmL`, `PawL`, `PawR`, `Brows`, `Eyelids`, `Mouth`, không dán khung chữ nhật). Capy vẫy tay đặt câu hỏi (`4.35–7.05s`). Anh kỹ sư trả lời (`7.20–10.05s`) và xoay cánh tay chỉ lần lượt vào 4 vòng sáng trên máy PC200-8: `1. Động cơ SAA6D107E-1`, `2. Bơm piston HPV95`, `3. Van phân phối CLSS`, `4. Xi lanh cần/tay gầu/gầu`. Máy nổ chờ có khói xả và duỗi tay gầu + mở gầu chuẩn bị đào. | `CAPY` hỏi tay máy đào lấy sức từ đâu; `ENGINEER` giới thiệu chuỗi truyền lực. |
| **D03 · Động cơ SAA6D107E-1 & Bơm piston đĩa nghiêng** | `00:10.200–00:17.400` | Mặt cắt động cơ diesel 6 xi lanh `SAA6D107E-1` (`110 kW @ 2000 rpm`, thứ tự nổ `1-5-3-6-2-4`) truyền mô-men qua trục nối sang cụm bơm piston hướng trục (`439 L/phút`). Đĩa nghiêng thay đổi góc nghiêng $\alpha$ theo tín hiệu phản hồi tải `LS` (màu tím), đẩy dầu cao áp `P` (màu đỏ). Nhấn mạnh nguyên lý vật lý: bơm tạo lưu lượng $Q$, áp suất $p$ hình thành theo sức cản của tải. | `ENGINEER` giải thích động cơ quay bơm tạo lưu lượng và áp suất tăng theo tải. |
| **D04 · Tay trang PPC, Van CLSS & Gầu cuộn xúc đất** | `00:17.400–00:24.200` | Tay trang PPC gạt liên tục từ `17.4s` (`pilot_amount: 0 -> 1`), dầu điều khiển pilot màu cam (`3.2 MPa`) đẩy con trượt 6 bậc trong van phân phối CLSS và mở nhánh cảm nhận tải `LS` + van bù áp. Đồng thời ngoài công trường, xi lanh tay gầu thu (`L_arm`) và xi lanh gầu duỗi (`L_bucket: 160 -> 183`) qua cơ cấu 4 khâu làm gầu cuộn xén qua mô đất, đất rơi theo trọng trường $g$ và bụi bốc lên. | `ENGINEER` giải thích mạch pilot, van phân phối CLSS và phối hợp thao tác xúc đất. |
| **D05a · Cắt cảnh cận: Xi lanh nâng cần tác động kép** | `00:24.200–00:28.800` | Cắt máy quay cận vào chân cần và cặp xi lanh nâng cần (`120 × 85 × 1334 mm`) kèm tâm chốt kỹ thuật. Mặt cắt xi lanh tác động kép mở to: dầu đỏ cấp vào khoang đáy ($F = p \cdot A_{\text{đáy}}$, giới hạn `37.3 MPa`), dầu xanh ở khoang ty hồi về thùng ($v \approx Q / A_{\text{đáy}}$), nhánh tím `LS` báo tải về bơm. | `ENGINEER` giải thích dầu vào khoang đáy, dầu khoang ty hồi về thùng và phản hồi tải `LS`. |
| **D05b · Cắt cảnh rộng: Quỹ đạo nâng cần đa khớp** | `00:28.800–00:35.800` | Cắt ra toàn cảnh công trường kèm HUD thông số động học (`L_boom: 289.3 -> 318.2`, `L_arm`, `L_bucket`). Cặp xi lanh nâng cần đẩy cần quay quanh `BOOM_PIN`, nâng gầu đầy đất lên cao. Capy và anh kỹ sư quan sát và chỉ theo quỹ đạo nâng. | `ENGINEER` chốt nguyên lý ty xi lanh vươn ra đẩy cần quay quanh chốt. |
| **D06 · Giữ tải, Mạch hồi – làm mát – lọc & Tổng kết** | `00:35.800–00:42.000` | Tay trang về giữa, van khóa giữ cần đóng kín cổng `A/B` giữ nguyên độ cao cần (`L_boom = 318.2`, không trôi). Bảng kỹ thuật phía trên minh họa dòng dầu hồi đi qua **Két làm mát → Lọc hồi → Thùng dầu** và quét sáng chuỗi 5 khâu năng lượng. Ở tiền cảnh, Capy vẫy tay reo *“Àaa!”* (`36.0–38.8s`) và anh kỹ sư gật đầu xác nhận (`38.9–41.8s`). | `CAPY` tổng kết chuỗi truyền năng lượng từ động cơ đến xi lanh và cần máy đào. |

---

## 2. Clip QA Proof V3 (`proof_16s` · 16,0 giây · 4 Beat kiểm chứng `ANIMATION_QUALITY_V3_BRIEF.md`)

| Beat | Thời gian | Nội dung kiểm chứng chuyển động |
|---|---|---|
| **Beat 1** | `00:00.000–00:03.000` | Máy đào PC200-8 nổ chờ tại công trường (khói xả, mở gầu/tay gầu), Capy và anh kỹ sư đứng sau hàng rào bằng rig 2D tách lớp, Capy vẫy tay đặt câu hỏi. |
| **Beat 2** | `00:03.000–00:09.000` | Kéo tay trang PPC → van CLSS dịch chuyển mở dầu đỏ vào khoang đáy xi lanh → cần và tay gầu chuyển động (`3–6s`), sau đó **cắt máy quay cận cảnh** vào xi lanh, đường dầu và tâm chốt khớp cơ khí (`6–9s`). |
| **Beat 3** | `00:09.000–00:13.000` | Xi lanh gầu duỗi qua cơ cấu 4 khâu làm gầu cuộn xén qua mô đất, hạt đất rơi theo đường parabol trọng trường $g$ kèm bụi đất, đồng thời cần nâng gầu đầy đất lên vị trí giữ tải. |
| **Beat 4** | `00:13.000–00:16.000` | Capy phản ứng hiểu bài (*“Àaa!”*, vẫy tay, mắt cười, miệng mở theo nhịp), anh kỹ sư gật đầu và sơ đồ chuỗi truyền lực thủy lực 5 khâu sáng đồng bộ. |
