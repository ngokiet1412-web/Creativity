# CAB-01 · Bàn giao CapCut Pro AI

**DRAFT · G1 đang chờ clip CapCut và owner duyệt.** Nhắm 7,50 giây, 225 khung ở 30 fps. Cửa sổ nghiệm thu là 6–8 giây.

## Owner thao tác trong CapCut

1. Duyệt khung nháp `style_candidate/CAB-01_2D_style_test_v01.png` nếu bộ bàn giao có kèm. R03 là ảnh gốc để so mặt, áo, logo và bố trí cabin. Dùng khung 2D làm ảnh đầu vào sau khi chọn hướng đó. Nếu tạo trực tiếp từ R03, đính kèm `references/R03_capy_bk_cabin.png` và dùng hướng 2D trong prompt.
2. Trong Image to Video / Video Studio, dán `CAB-01_prompt_v01.txt`. Chọn dọc 9:16, một cú máy. R01 và R02 dùng để đối chiếu ngoại hình và máy xúc. Kiểm tra model và mức credit trước khi tạo.
3. Dùng câu dưới đây trong Text to Speech hoặc thu âm. Thử giọng nam trẻ miền Nam, gần gũi như nói với bạn. “Ê ê, khoan!” nhanh và bất ngờ, nghỉ một nhịp, rồi nhấn nhẹ “tụt dữ” và lên giọng ở “vậy trời?!”. Nghe và chọn giọng trước khi chạy lip-sync.
4. `audio/CAB-01_guide_vi_v01.wav` là WAV định nhịp tạm, 48 kHz mono, có khoảng trống từ đầu timeline đến lúc Capy nói. Bản này tổng hợp cục bộ với Piper/Điềm Đạm để duyệt timing. Dùng giọng owner chọn cho take trả về và giữ stem thoại khô riêng.
5. Nhập `subtitles/CAB-01_vi_v01.srt` vào Captions, canh lại theo take thật và kiểm tra vùng an toàn. Đặt thoại sau cú liếc và quay lại nhìn camera. Thử lip-sync nếu tính năng hỗ trợ. Soi tiếp xúc tay với joystick, mặt, logo BK và kim đồng hồ.
6. Xuất một take kiểm tra theo tên dưới đây. Ghi model, credit, thời gian, lỗi và chỉnh sửa vào file QA. Owner duyệt G1 trước khi tạo thêm cảnh.

```text
Ê ê, khoan! Sao mới leo cái dốc mà đồng hồ dầu tụt dữ vậy trời?!
```

## Quy tắc tên và tệp trả về

Đặt tất cả tệp của một take trong `returns/v01/`. Tăng đồng bộ lên `v02`, `v03` khi thử lại. Giữ nguyên bản cũ để so sánh. Stem bắt đầu tại 00:00 của clip, có phần lặng trước và sau thoại cùng độ dài timeline.

| File | Nội dung |
|---|---|
| `CAB-01_v01.mp4` | Bản kiểm tra có thoại, H.264, dọc 1080×1920, CFR 30 fps, AAC 48 kHz. Caption để rời. |
| `CAB-01_voice_v01.wav` | Thoại được chọn, PCM 48 kHz, mono/stereo, 16 hoặc 24 bit. |
| `CAB-01_vi_v01.srt` | SRT UTF-8, đã chỉnh theo thoại thật. |
| `CAB-01_prompt_v01.txt` | Nội dung prompt thực tế đã dùng. |
| `CAB-01_qa_v01.md` | Ghi chú CapCut, model, credit, giọng, lip-sync và nhận xét. |
| `CAB-01_motion_v01.mp4` | Tùy chọn, clip chuyển động gốc để Codex ghép lại với stem. |

## Engineering

Chạy từ gốc repo với Python 3.11+ và FFmpeg có libx264, kèm ffprobe. Hai tùy chọn `--ffmpeg` và `--ffprobe` đứng trước tên lệnh khi binary nằm ngoài PATH.

```powershell
python scripts/cab01.py verify-assets
python scripts/cab01.py prepare --guide-wav path/to/timed-guide.wav --out build/CAB-01_v01
python scripts/cab01.py validate --take build/CAB-01_v01/returns/v01
python -m unittest discover -s scripts -p test_cab01.py
```

`prepare` nhận guide WAV đã đặt trên timeline 7,50 giây, chuẩn hóa bản sao và xuất kèm checksum. Có thể thêm `--style-still path/to/CAB-01_2D_style_test_v01.png` để đóng gói bản 2D nháp riêng. [Shot manifest](shot.json) lưu nguồn R03, prompt ImageGen và checksum của bản nháp. `validate` kiểm tra thời lượng, cadence, codec, độ lệch thời điểm đầu luồng, WAV có tín hiệu, phụ đề khớp lời và giải mã toàn bộ video. Khẩu hình, diễn xuất và nhận diện cần người xem kiểm tra theo checklist.

Nếu có clip motion gốc và stem đã canh, tạo bản review H.264/AAC bằng `python scripts/cab01.py review --motion MOTION.mp4 --voice VOICE.wav --captions TAKE.srt --out REVIEW.mp4`. Bản review giữ bố cục 9:16 và phụ đề rời. Lưu clip và stem thật ở thư mục local, cùng ghi chú take. Repo chứa asset tham chiếu và đặc tả.
