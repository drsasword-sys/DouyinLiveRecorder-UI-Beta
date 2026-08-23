# DouyinLiveRecorder UI Beta 0.1.0-beta.3

Bản beta khuyến nghị cho Windows 10/11 x64.

## Sửa lỗi

- Bao gồm toàn bộ hotfix UTF-8/config/build của beta.2.
- Tắt address reuse của HTTP server local, ngăn nhiều tiến trình UI cùng giữ
  cổng 8765 và tránh nguy cơ khởi động nhiều recorder khi bấm EXE lặp lại.

## Kiểm định

- Unit/release test: 14/14 đạt.
- Packaged self-test: đạt.
- Recorder-child UTF-8 smoke test: đạt.
- Duplicate-instance port test: tiến trình thứ hai phải thoát và mở lại UI đang
  chạy, không tạo listener thứ hai.

EXE chưa ký số nên Windows SmartScreen có thể cảnh báo. Giải nén toàn bộ ZIP và
đối chiếu SHA-256 trong `SHA256SUMS.txt`.
