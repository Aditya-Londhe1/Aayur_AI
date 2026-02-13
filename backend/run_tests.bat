@echo off
echo ============================================================
echo Voice Assistant Testing Suite
echo ============================================================
echo.

echo Step 1: Verifying Setup...
echo ------------------------------------------------------------
python verify_setup.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Please install missing packages first!
    pause
    exit /b 1
)

echo.
echo.
echo Step 2: Testing Gemini API...
echo ------------------------------------------------------------
python test_gemini.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Gemini API test failed!
    pause
    exit /b 1
)

echo.
echo.
echo Step 3: Testing Translation System...
echo ------------------------------------------------------------
python test_translation.py

echo.
echo.
echo ============================================================
echo All Tests Completed!
echo ============================================================
echo.
echo Next: Proceed to Option B - Minimal Working Version
echo.
pause
