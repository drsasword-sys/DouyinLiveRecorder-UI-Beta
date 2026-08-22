# DouyinLiveRecorder UI Beta 0.1.0-beta.1

Bản thử nghiệm portable đầu tiên cho Windows 10/11 x64. Gói đã kèm Python
runtime, FFmpeg và Node.js; người dùng chỉ cần giải nén toàn bộ ZIP rồi chạy
`DouyinLiveRecorderBeta.exe`.

## Điểm chính

- UI local tại `http://127.0.0.1:8765`.
- Theo dõi và ghi nhiều phòng Douyin/TikTok mà không chiếm màn hình.
- Dừng và ghi phiên mới theo từng phòng.
- Mở trang live gốc và thư mục video ngay trên UI.
- Cấu hình/cookie/video chỉ nằm trên máy người dùng và không nằm trong gói.

## Kiểm định phát hành

- Unit test: 7/7 đạt.
- Packaged self-test: đạt cho module Python, JavaScript, FFmpeg, Node.js và
  template cấu hình.
- Smoke test API trên một cổng local độc lập: đạt.
- `pip-audit`: không phát hiện lỗ hổng đã biết trong dependency Python khóa cho
  bản build này.

## Lưu ý beta

EXE chưa được ký số nên Windows SmartScreen có thể cảnh báo. Hãy đối chiếu SHA-256
trong `SHA256SUMS.txt`, giải nén toàn bộ thư mục và không chia sẻ
`config/config.ini` sau khi đã nhập cookie.
