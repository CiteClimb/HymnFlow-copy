@echo off
REM HymnFlow Release Script for Windows
REM Builds three release artifacts and a git tag:
REM   hymnflow-vX-lite.zip  - plugin + default KJV + default hymnal (nnbh)
REM   hymnflow-vX-full.zip  - plugin + all Bibles + all hymn collections
REM   hymnflow-vX-data.zip  - importable Bibles + hymn collections only

setlocal enabledelayedexpansion

REM Get version from package.json
for /f "tokens=2 delims=: " %%a in ('findstr "version" package.json ^| findstr /v "devDependencies"') do (
    set VERSION=%%a
    set VERSION=!VERSION:"=!
    set VERSION=!VERSION:,=!
    goto :found_version
)
:found_version

if "!VERSION!"=="" (
    echo Error: Could not read version from package.json
    exit /b 1
)

echo Creating HymnFlow v!VERSION! release (lite / full / data)...

REM Abort if there are uncommitted changes - tag must point to a clean commit
git diff --quiet >nul 2>&1
if %ERRORLEVEL% NEQ 0 ( echo Error: You have unstaged changes. Commit everything before releasing. & exit /b 1 )
git diff --cached --quiet >nul 2>&1
if %ERRORLEVEL% NEQ 0 ( echo Error: You have staged but uncommitted changes. Commit everything before releasing. & exit /b 1 )

REM ===== 1. LITE bundle: plugin + KJV + nnbh =====
echo Building lite bundle...
set LITE=hymnflow-v!VERSION!-lite
call :stage_plugin "!LITE!"
copy public\data\bible-kjv.js "!LITE!\data\" > nul
copy hymn-bundle\nnbh.json    "!LITE!\data\" > nul
call :make_zip "!LITE!"

REM ===== 2. FULL bundle: plugin + all Bibles + all hymn collections =====
echo Building full bundle...
set FULL=hymnflow-v!VERSION!-full
call :stage_plugin "!FULL!"
call :copy_data "!FULL!\data"

REM ===== 3. DATA bundle: importable Bibles + hymn collections only =====
echo Building data bundle...
set DATA=hymnflow-v!VERSION!-data
if exist "!DATA!" rmdir /s /q "!DATA!"
mkdir "!DATA!\data"
call :copy_data "!DATA!\data"
call :make_zip "!FULL!"
call :make_zip "!DATA!"

REM Create git tag
echo Creating git tag v!VERSION!...
git tag -a "v!VERSION!" -m "Release v!VERSION! - HymnFlow OBS Plugin" 2>nul || echo    (tag v!VERSION! may already exist)

echo.
echo Release artifacts created for v!VERSION!:
echo    hymnflow-v!VERSION!-lite.zip   (plugin + KJV + nnbh)
echo    hymnflow-v!VERSION!-full.zip   (plugin + all Bibles + all hymns)
echo    hymnflow-v!VERSION!-data.zip   (importable Bibles + hymns)
echo.
echo Next steps:
echo    1. Review the ZIP contents
echo    2. Push tag: git push origin v!VERSION!
echo    3. Create the GitHub release and attach all three ZIPs
goto :eof

REM ---- Stage shared plugin (code/UI + core data code) into %1 ----
:stage_plugin
set D=%~1
if exist "!D!" rmdir /s /q "!D!"
mkdir "!D!\data" "!D!\scripts" > nul 2>&1
xcopy public\obs-dock    "!D!\obs-dock\"    /E /Y > nul
xcopy public\obs-overlay "!D!\obs-overlay\" /E /Y > nul
xcopy public\parsers     "!D!\parsers\"     /E /Y > nul
xcopy public\i18n        "!D!\i18n\"        /E /Y > nul
copy public\obs-setup.html "!D!\" > nul
copy public\validation.js  "!D!\" > nul
copy public\data\bible-lookup.js "!D!\data\" > nul
copy public\data\hymns-data.js   "!D!\data\" > nul
copy scripts\hymnflow-obs-hotkeys.py "!D!\scripts\" > nul
copy scripts\convert_bible_txt.py    "!D!\scripts\" > nul
copy scripts\convert_yoruba_bible.py "!D!\scripts\" > nul
copy README.md              "!D!\" > nul
copy doc\SETUP.md           "!D!\" > nul
copy doc\TROUBLESHOOTING.md "!D!\" > nul
copy doc\SECURITY.md        "!D!\" > nul
if exist "doc\RELEASE_NOTES_v!VERSION!.md" copy "doc\RELEASE_NOTES_v!VERSION!.md" "!D!\" > nul
goto :eof

REM ---- Copy all importable Bibles + hymn collections into %1 ----
:copy_data
set DD=%~1
copy public\data\bible-kjv.js "!DD!\" > nul
copy public\data\en_bbe.json  "!DD!\" > nul
copy public\data\bible-yor.js "!DD!\" > nul
copy hymn-bundle\cac_ghb.json "!DD!\" > nul
copy hymn-bundle\cac_yhb.json "!DD!\" > nul
copy hymn-bundle\fws.json     "!DD!\" > nul
copy hymn-bundle\nnbh.json    "!DD!\" > nul
copy hymn-bundle\umh.json     "!DD!\" > nul
copy hymn-bundle\ybh.json     "!DD!\" > nul
copy hymn-bundle\metadata.json "!DD!\" > nul
goto :eof

REM ---- Zip folder %1 into %1.zip (PowerShell Compress-Archive) ----
:make_zip
set Z=%~1
if exist "!Z!.zip" del /q "!Z!.zip"
powershell -NoProfile -Command "Compress-Archive -Path '!Z!' -DestinationPath '!Z!.zip' -Force"
goto :eof
