#!/bin/bash
# Quick deployment script for Hugging Face Spaces
# Usage: ./deploy-to-hf.sh YOUR_HF_USERNAME

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Hugging Face Spaces Deployment Script"
echo "========================================"
echo ""

# Check if username provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide your Hugging Face username${NC}"
    echo "Usage: ./deploy-to-hf.sh YOUR_HF_USERNAME"
    exit 1
fi

HF_USERNAME=$1
SPACE_NAME="NLP-Content-Moderation-Service"
SPACE_URL="https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"

echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"

# Check if Git LFS is installed
if ! command -v git-lfs &> /dev/null; then
    echo -e "${RED}Git LFS not found. Installing...${NC}"
    echo "Please install Git LFS from: https://git-lfs.github.com/"
    exit 1
fi
echo -e "${GREEN}✓ Git LFS installed${NC}"

# Check if huggingface-cli is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo -e "${YELLOW}Installing huggingface_hub...${NC}"
    pip install huggingface_hub
fi
echo -e "${GREEN}✓ Hugging Face CLI ready${NC}"

echo ""
echo -e "${YELLOW}Step 2: Initializing Git LFS...${NC}"

# Initialize Git LFS
git lfs install
echo -e "${GREEN}✓ Git LFS initialized${NC}"

# Track model files
git lfs track "*.safetensors"
git lfs track "*.pt"
git lfs track "*.bin"
echo -e "${GREEN}✓ Model files tracked${NC}"

# Add .gitattributes if changes
if ! git diff --quiet .gitattributes 2>/dev/null; then
    git add .gitattributes
    echo -e "${GREEN}✓ .gitattributes updated${NC}"
fi

echo ""
echo -e "${YELLOW}Step 3: Checking model files...${NC}"

MODEL_PATH="models/manipulation_detector_model"
if [ ! -f "${MODEL_PATH}/config.json" ] || [ ! -f "${MODEL_PATH}/model.safetensors" ]; then
    echo -e "${RED}Error: Model files not found in ${MODEL_PATH}${NC}"
    echo "Please ensure your model is trained and saved."
    exit 1
fi
echo -e "${GREEN}✓ Model files found${NC}"

# Check model size
MODEL_SIZE=$(du -sh ${MODEL_PATH} | cut -f1)
echo "  Model size: ${MODEL_SIZE}"

echo ""
echo -e "${YELLOW}Step 4: Adding deployment files...${NC}"

# Check if deployment files exist
MISSING_FILES=()
[ ! -f "Dockerfile" ] && MISSING_FILES+=("Dockerfile")
[ ! -f "requirements.txt" ] && MISSING_FILES+=("requirements.txt")
[ ! -f ".gitattributes" ] && MISSING_FILES+=(".gitattributes")

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo -e "${RED}Error: Missing deployment files: ${MISSING_FILES[*]}${NC}"
    echo "These files should have been created. Please check DEPLOYMENT.md"
    exit 1
fi
echo -e "${GREEN}✓ All deployment files present${NC}"

# Add all deployment files
git add Dockerfile requirements.txt .gitattributes README.md

echo ""
echo -e "${YELLOW}Step 5: Adding model files (this may take a moment)...${NC}"

# Add model files
git add ${MODEL_PATH}/

echo ""
echo -e "${YELLOW}Step 6: Committing changes...${NC}"

# Commit if there are changes
if git diff --staged --quiet; then
    echo -e "${GREEN}✓ No new changes to commit${NC}"
else
    git commit -m "Add Hugging Face Spaces deployment configuration

- Add Dockerfile for Docker Space
- Add combined requirements.txt
- Configure Git LFS for model files
- Add model files for deployment

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
    echo -e "${GREEN}✓ Changes committed${NC}"
fi

echo ""
echo -e "${YELLOW}Step 7: Authenticating with Hugging Face...${NC}"
echo "You'll need to login to Hugging Face."
echo "Get your token from: https://huggingface.co/settings/tokens"
echo ""

# Login to HF
huggingface-cli login

echo ""
echo -e "${YELLOW}Step 8: Adding Hugging Face Space as remote...${NC}"

# Check if space remote already exists
if git remote | grep -q "^space$"; then
    echo -e "${YELLOW}Remote 'space' already exists. Updating URL...${NC}"
    git remote set-url space https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}
else
    git remote add space https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}
fi
echo -e "${GREEN}✓ Remote configured${NC}"

echo ""
echo -e "${YELLOW}Step 9: Pushing to Hugging Face Spaces...${NC}"
echo "This may take several minutes depending on model size..."
echo ""

# Push to space
if git push space main; then
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✓ Deployment successful!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo "Your Space is deploying at: ${SPACE_URL}"
    echo ""
    echo "Next steps:"
    echo "1. Visit your Space: ${SPACE_URL}"
    echo "2. Wait for build to complete (3-5 minutes)"
    echo "3. Check build logs for any errors"
    echo "4. Test the deployed app"
    echo ""
    echo "Once deployed, your app will be live at:"
    echo "https://${HF_USERNAME}-${SPACE_NAME}.hf.space"
    echo ""
else
    echo -e "${RED}Deployment failed. Please check the error above.${NC}"
    echo ""
    echo "Common issues:"
    echo "- Make sure you created the Space on Hugging Face first"
    echo "- Check that the Space name is correct: ${SPACE_NAME}"
    echo "- Verify you have push access to the Space"
    exit 1
fi
