# DouyinLiveRecorder UI Beta 0.1.0-beta.2

Hotfix cho bản Windows portable.

## Sửa lỗi

- Sửa `UnicodeEncodeError: 'charmap' codec can't encode characters` khi tiến
  trình recorder in chữ Trung/Vietnamese trên một số máy Windows.
- Ép stdout/stderr hiện hữu sang UTF-8 trước khi import recording engine; nếu
  stream không hỗ trợ đổi encoding, ứng dụng fallback sang file log UTF-8.
- Thêm regression test cho trường hợp stream Windows `cp1252` không phải `None`.
- Recorder child tự tạo config runtime nếu được chạy trực tiếp.
- Build fail-fast khi PyInstaller lỗi, tách output theo phiên bản và retry khóa
  file tạm thời khi nén.

## Kiểm định

- Unit test: 13/13 đạt.
- Packaged self-test: đạt.
- Recorder child smoke test: phải khởi động qua phần banner Unicode mà không
  xuất hiện traceback `charmap`.

EXE chưa ký số nên Windows SmartScreen có thể cảnh báo. Hãy tải ZIP beta.2,
giải nén toàn bộ và đối chiếu SHA-256 trong asset `SHA256SUMS.txt`.
