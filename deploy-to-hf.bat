@echo off
REM Quick deployment script for Hugging Face Spaces (Windows)
REM Usage: deploy-to-hf.bat YOUR_HF_USERNAME

setlocal enabledelayedexpansion

echo.
echo 🚀 Hugging Face Spaces Deployment Script
echo ========================================
echo.

REM Check if username provided
if "%1"=="" (
    echo Error: Please provide your Hugging Face username
    echo Usage: deploy-to-hf.bat YOUR_HF_USERNAME
    exit /b 1
)

set HF_USERNAME=%1
set SPACE_NAME=NLP-Content-Moderation-Service
set SPACE_URL=https://huggingface.co/spaces/%HF_USERNAME%/%SPACE_NAME%

echo Step 1: Checking prerequisites...

REM Check if Git LFS is installed
git lfs version >nul 2>&1
if errorlevel 1 (
    echo Error: Git LFS not found
    echo Please install from: https://git-lfs.github.com/
    exit /b 1
)
echo ✓ Git LFS installed

REM Check if huggingface-cli is installed
huggingface-cli --version >nul 2>&1
if errorlevel 1 (
    echo Installing huggingface_hub...
    pip install huggingface_hub
)
echo ✓ Hugging Face CLI ready

echo.
echo Step 2: Initializing Git LFS...

git lfs install
git lfs track "*.safetensors"
git lfs track "*.pt"
git lfs track "*.bin"
git add .gitattributes
echo ✓ Git LFS configured

echo.
echo Step 3: Checking model files...

set MODEL_PATH=models\manipulation_detector_model
if not exist "%MODEL_PATH%\config.json" (
    echo Error: Model files not found in %MODEL_PATH%
    exit /b 1
)
if not exist "%MODEL_PATH%\model.safetensors" (
    echo Error: Model files not found in %MODEL_PATH%
    exit /b 1
)
echo ✓ Model files found

echo.
echo Step 4: Adding deployment files...

if not exist "Dockerfile" (
    echo Error: Dockerfile not found
    exit /b 1
)
if not exist "requirements.txt" (
    echo Error: requirements.txt not found
    exit /b 1
)
echo ✓ All deployment files present

git add Dockerfile requirements.txt .gitattributes README.md

echo.
echo Step 5: Adding model files...
git add %MODEL_PATH%\

echo.
echo Step 6: Committing changes...

git commit -m "Add Hugging Face Spaces deployment configuration" -m "- Add Dockerfile for Docker Space" -m "- Add combined requirements.txt" -m "- Configure Git LFS for model files" -m "- Add model files for deployment"
echo ✓ Changes committed

echo.
echo Step 7: Authenticating with Hugging Face...
echo You'll need to login to Hugging Face.
echo Get your token from: https://huggingface.co/settings/tokens
echo.

huggingface-cli login

echo.
echo Step 8: Adding Hugging Face Space as remote...

git remote | findstr "^space$" >nul 2>&1
if not errorlevel 1 (
    echo Remote 'space' already exists. Updating URL...
    git remote set-url space https://huggingface.co/spaces/%HF_USERNAME%/%SPACE_NAME%
) else (
    git remote add space https://huggingface.co/spaces/%HF_USERNAME%/%SPACE_NAME%
)
echo ✓ Remote configured

echo.
echo Step 9: Pushing to Hugging Face Spaces...
echo This may take several minutes...
echo.

git push space main
if errorlevel 1 (
    echo.
    echo Deployment failed. Please check the error above.
    exit /b 1
)

echo.
echo ================================
echo ✓ Deployment successful!
echo ================================
echo.
echo Your Space is deploying at: %SPACE_URL%
echo.
echo Next steps:
echo 1. Visit your Space: %SPACE_URL%
echo 2. Wait for build to complete (3-5 minutes)
echo 3. Check build logs for any errors
echo 4. Test the deployed app
echo.
echo Once deployed, your app will be live at:
echo https://%HF_USERNAME%-%SPACE_NAME%.hf.space
echo.

endlocal
