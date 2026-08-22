# ADR-0001: Local browser UI over the upstream recorder

## Status

Accepted

## Date

2026-08-22

## Context

The upstream recorder is a mature console application with multi-platform stream
resolution, FFmpeg orchestration and config-file based per-room stop behavior.
The beta needs simple Windows controls without rewriting that recording engine.

## Decision

Run a standard-library HTTP UI on `127.0.0.1` and control the unchanged recorder
through `config/URL_config.ini`. The packaged executable has two modes: UI server
and recorder child (`--recorder`). Runtime config and recordings live beside the
executable, while bundled read-only resources live under PyInstaller `_internal`.

## Consequences

- The upstream recording flow remains intact and rollback is additive.
- The UI has no external web framework dependency.
- The application is Windows-first and requires a writable extracted directory.
- Closing the UI process also terminates the recorder child; users should stop
  active rooms first so FFmpeg can finalize files.
