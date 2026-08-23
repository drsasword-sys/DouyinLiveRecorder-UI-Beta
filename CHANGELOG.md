# Changelog

## 0.1.0-beta.2 - 2026-08-23

### Fixed

- Reconfigure inherited Windows stdout/stderr streams to UTF-8 before importing
  the recorder, preventing `UnicodeEncodeError: charmap` in the packaged EXE.
- Add a regression test covering non-null `cp1252` console streams.
- Prepare runtime config in direct recorder-child mode.
- Make release builds fail fast, version-isolated and resilient to transient
  archive file locks.

## 0.1.0-beta.1 - 2026-08-22

### Added

- Local browser UI bound to `127.0.0.1`.
- Add, resume, stop, open-live and open-output controls.
- Per-user runtime configuration created from sanitized templates.
- Portable Windows build workflow with bundled FFmpeg and Node.js.
- Security headers, URL allowlist and 4 KB API request limit.

### Fixed

- Recorder subprocess now uses UTF-8 output.
- UI and recorder use separate process modes in the packaged executable.
- Repeated launch reuses the existing local UI instead of starting another server.
- Windowed builds provide a safe log sink and avoid privileged multiprocessing
  pipes for Loguru.
- Raw markup, control characters and embedded credentials are rejected in live
  URLs before they reach the local UI or recorder configuration.
