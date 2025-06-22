@echo off
echo Building Java verification system...

REM Check if Maven is installed
where mvn >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Maven is not installed or not in PATH. Please install Maven first.
    exit /b 1
)

REM Check if Java is installed
where java >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Java is not installed or not in PATH. Please install Java first.
    exit /b 1
)

REM Check if Tesseract is installed
if not exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo Tesseract OCR is not installed. Please install Tesseract OCR first.
    exit /b 1
)

REM Build the project
echo Running Maven build...
mvn clean package

if %ERRORLEVEL% neq 0 (
    echo Build failed. Please check the error messages above.
    exit /b 1
)

echo Build successful!
echo The JAR file has been created in the target directory.
echo You can now run the Python application. 