@echo off
REM HymnFlow release — thin wrapper around the cross-platform Python script.
REM Usage: scripts\release.bat [version] [--publish] [--rebuild] [--dry-run]
REM See scripts\release.py and doc\RELEASING.md for details.
python "%~dp0release.py" %*
