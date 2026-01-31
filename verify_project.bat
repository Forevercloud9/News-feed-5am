@echo off
echo ==========================================
echo Morning 5 MVP - Verification Script
echo ==========================================

echo [1/3] Checking for Flutter SDK...
where flutter >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Flutter SDK not found in PATH.
    echo Please ensure Flutter is installed and added to your system PATH.
    echo You can download it from: https://docs.flutter.dev/get-started/install/windows
    goto :error
)
echo Flutter found!

echo [2/3] Installing Frontend Dependencies...
cd frontend
call flutter pub get
if %errorlevel% neq 0 (
    echo [ERROR] Failed to get dependencies.
    goto :error
)

echo [3/3] Running Flutter Analyze...
call flutter analyze
if %errorlevel% neq 0 (
    echo [WARNING] Analysis found issues. Please review the output above.
) else (
    echo [SUCCESS] No analysis issues found!
)
cd ..

echo ==========================================
echo Verification Complete.
pause
exit /b 0

:error
echo ==========================================
echo Verification Failed.
cd ..
pause
exit /b 1
