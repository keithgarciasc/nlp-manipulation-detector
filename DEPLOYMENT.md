# Deployment Guide - Hugging Face Spaces

## Recommended Approach: **Docker Space** (Streamlit + FastAPI Combined)

### Why Docker Space?

**Not Streamlit Space** because:
- ❌ Streamlit Spaces only run one Streamlit app
- ❌ Cannot run FastAPI alongside Streamlit
- ❌ Would require deploying API separately (more complex)

**Docker Space is the right choice** because:
- ✅ Runs both FastAPI and Streamlit in one container
- ✅ Internal networking (no external API calls)
- ✅ Simple configuration with one Dockerfile
- ✅ Free tier includes 16GB RAM (enough for DistilBERT)
- ✅ Automatic HTTPS and public URL
- ✅ Git-based deployment (just push to update)

---

## Architecture

```
┌─────────────────────────────────────┐
│   Hugging Face Docker Space         │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │  Streamlit   │→ │  FastAPI    │ │
│  │  (Port 7860) │  │(Port 8000)  │ │
│  │              │  │             │ │
│  │  Public UI   │  │ Internal    │ │
│  └──────────────┘  └─────────────┘ │
│         ↓               ↓           │
│    ┌────────────────────────┐      │
│    │  DistilBERT Model      │      │
│    │  (Loaded once)         │      │
│    └────────────────────────┘      │
└─────────────────────────────────────┘
         ↓
    Public URL: https://username-space-name.hf.space
```

**Key Points:**
- Streamlit exposed on port 7860 (HF Spaces requirement)
- FastAPI runs internally on port 8000
- Streamlit calls `http://localhost:8000` (same container)
- Model loaded once at container startup

---

## Step 1: Prepare Your Repository

### Required File Structure

```
NLP-Content-Moderation-Service/
├── api/
│   ├── main.py                    # FastAPI app
│   └── requirements.txt
├── ui/
│   ├── app.py                     # Streamlit app
│   └── requirements.txt
├── models/
│   └── manipulation_detector_model/
│       ├── config.json            # Must be committed!
│       └── model.safetensors      # Must be committed!
├── Dockerfile                     # NEW - for HF Spaces
├── requirements.txt               # NEW - combined dependencies
├── README.md                      # Will be shown on Space
└── .gitattributes                 # NEW - for Git LFS
```

### Critical: Model Files Must Be in Git

Your model files are currently ignored by `.gitignore`. You need to:

**Option A: Use Git LFS (Recommended)**
```bash
# Install Git LFS
git lfs install

# Track model files
git lfs track "*.safetensors"
git lfs track "models/manipulation_detector_model/*"

# Add .gitattributes
git add .gitattributes

# Add model files
git add models/manipulation_detector_model/
git commit -m "Add trained model with Git LFS"
```

**Option B: Remove from .gitignore**
```bash
# Edit .gitignore and remove these lines:
# *.safetensors
# *.pt

# Then add and commit
git add models/manipulation_detector_model/
git commit -m "Add trained model files"
```

---

## Step 2: Create Deployment Files

### File 1: `.gitattributes` (for Git LFS)

```gitattributes
*.safetensors filter=lfs diff=lfs merge=lfs -text
*.pt filter=lfs diff=lfs merge=lfs -text
*.bin filter=lfs diff=lfs merge=lfs -text
```

### File 2: `Dockerfile`

```dockerfile
# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY ui/ ./ui/
COPY models/ ./models/

# Create startup script
RUN echo '#!/bin/bash\n\
# Start FastAPI in background\n\
cd /app/api && uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
\n\
# Wait for API to start\n\
sleep 5\n\
\n\
# Start Streamlit on port 7860 (HF Spaces requirement)\n\
cd /app/ui && streamlit run app.py --server.port 7860 --server.address 0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port 7860 (Hugging Face Spaces requirement)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:7860/_stcore/health || exit 1

# Run startup script
CMD ["/app/start.sh"]
```

### File 3: `requirements.txt` (combined)

```txt
# FastAPI dependencies
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.0

# Streamlit dependencies
streamlit==1.40.0
requests==2.32.3

# ML dependencies
torch==2.7.1
transformers==4.56.2

# Shared utilities
python-multipart==0.0.9
```

### File 4: Update `ui/app.py` API URL

Find this line in `ui/app.py`:
```python
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
```

Keep it as-is! In Docker Space, both services run in the same container, so `localhost:8000` is correct.

---

## Step 3: Create Hugging Face Space

### 3.1 Create Space on Hugging Face

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in:
   - **Space name**: `NLP-Content-Moderation-Service` (or your choice)
   - **License**: MIT
   - **Select SDK**: **Docker** ⚠️ (NOT Streamlit!)
   - **Space hardware**: CPU basic (free tier)
   - **Visibility**: Public

4. Click **"Create Space"**

### 3.2 Push Your Code to the Space

HF Spaces are Git repositories. You'll push to them like GitHub:

```bash
# Add HF Space as remote
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/NLP-Content-Moderation-Service

# Push to Space
git push space main
```

**First-time setup:**
```bash
# You'll need HF CLI for authentication
pip install huggingface_hub

# Login to HF
huggingface-cli login
# (Enter your HF token - get it from https://huggingface.co/settings/tokens)

# Now push
git push space main
```

---

## Step 4: Wait for Build & Deployment

### What Happens:

1. **Build Phase** (3-5 minutes):
   - HF downloads your repo
   - Builds Docker image
   - Installs dependencies (~2GB download)
   - Downloads model files via Git LFS

2. **Startup Phase** (20-40 seconds):
   - Container starts
   - FastAPI loads model (~5 seconds)
   - Streamlit starts (~2 seconds)
   - Health check passes

3. **Running**:
   - Space status shows "Running"
   - Public URL active: `https://YOUR_USERNAME-NLP-Content-Moderation-Service.hf.space`

### Monitoring Build:

Go to your Space page and click **"Build logs"** to see:
```
Building Docker image...
Installing dependencies...
Starting container...
✓ Application running on port 7860
```

---

## Step 5: Configure Space (Optional)

### Add README Card

Edit `README.md` to add Space metadata:

```yaml
---
title: NLP Manipulation Detector
emoji: 🔍
colorFrom: red
colorTo: orange
sdk: docker
pinned: false
license: mit
---

# NLP Manipulation Detector

Detect manipulative language in text using fine-tuned DistilBERT.

[Rest of your README content...]
```

This creates a nice card on the Space page.

---

## Common Issues & Solutions

### Issue 1: "Application didn't start on port 7860"

**Cause**: Streamlit not exposing port 7860

**Fix**: Ensure `Dockerfile` has:
```dockerfile
EXPOSE 7860
CMD streamlit run app.py --server.port 7860 --server.address 0.0.0.0
```

### Issue 2: "Out of memory" during build/runtime

**Cause**: Model + dependencies too large for free tier (16GB limit)

**Solutions**:
1. Check model size: `du -sh models/` (should be ~250MB)
2. Reduce dependencies in `requirements.txt`
3. Upgrade to paid hardware (unlikely needed for DistilBERT)

**Memory breakdown:**
- Base image: ~1GB
- Dependencies: ~2GB
- Model: ~250MB
- Runtime: ~500MB
- **Total: ~3.75GB** ✅ Fits in 16GB

### Issue 3: "Model files not found"

**Cause**: Model files not committed or Git LFS not configured

**Fix**:
```bash
# Verify files are tracked
git lfs ls-files

# Should show:
# models/manipulation_detector_model/model.safetensors

# If not, track them
git lfs track "models/**/*.safetensors"
git add .gitattributes models/
git commit -m "Track model with Git LFS"
git push space main
```

### Issue 4: Slow cold starts (30+ seconds)

**Cause**: Model loading at startup

**Expected**: First request takes 20-40 seconds (normal)

**Optimization**: Models loads at container start (already implemented in Dockerfile startup script)

**Note**: HF Spaces sleep after 48h inactivity. First visit after sleep = cold start.

### Issue 5: API returns 503 "Model not loaded"

**Cause**: FastAPI started but model not loaded yet

**Fix**: Increase sleep time in startup script:
```bash
# In Dockerfile start.sh
sleep 10  # Increase from 5 to 10 seconds
```

### Issue 6: Streamlit can't connect to API

**Cause**: Wrong API URL or API not running

**Debug**:
1. Check API is running:
   - In Space logs, look for: `Uvicorn running on http://0.0.0.0:8000`
2. Check Streamlit API URL:
   - Should be `http://localhost:8000` (not external URL)
3. Check API health:
   - Logs should show: `Model loaded successfully`

**Fix**: Ensure `ui/app.py` has:
```python
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
```

---

## Resource Limits (Free Tier)

| Resource | Limit | Your Usage | Status |
|----------|-------|------------|--------|
| RAM | 16 GB | ~4 GB | ✅ OK |
| CPU | 2 vCPU | Variable | ✅ OK |
| Storage | 50 GB | ~3 GB | ✅ OK |
| Disk I/O | Moderate | Low | ✅ OK |

**Performance Expectations (Free Tier):**
- Cold start: 30-40 seconds
- Inference latency: 200-500ms per request
- Concurrent users: 5-10 (CPU-bound)
- Auto-sleep: After 48h inactivity

---

## Updating Your Deployment

### Make Changes Locally

```bash
# Edit code
vim ui/app.py

# Test locally
streamlit run ui/app.py

# Commit
git add ui/app.py
git commit -m "Update UI styling"
```

### Push to HF Space

```bash
# Push to GitHub (optional)
git push origin main

# Push to HF Space (triggers rebuild)
git push space main
```

### Deployment Process:
1. HF detects new commit
2. Rebuilds Docker image (~3 minutes)
3. Restarts container (~30 seconds)
4. Space automatically updates

**Zero-downtime**: No - brief downtime during restart (acceptable for demos)

---

## Testing Your Deployment

### 1. Check Space Status

Visit: `https://huggingface.co/spaces/YOUR_USERNAME/NLP-Content-Moderation-Service`

Should show: **"Running"** with green indicator

### 2. Test UI

Visit: `https://YOUR_USERNAME-NLP-Content-Moderation-Service.hf.space`

Should see:
- Streamlit interface loads
- API status shows "✓ API Online"
- Example buttons work
- Analysis returns results

### 3. Test API Directly

From your Space's "App" view, you can't access the API directly (not exposed publicly), but you can verify it's working via Streamlit's API status indicator.

### 4. Check Logs

In Space page → "Logs" tab:

Should see:
```
INFO:     Started server process [12]
INFO:     Waiting for application startup.
INFO:     Loading model and tokenizer...
INFO:     Model loaded successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000

  You can now view your Streamlit app in your browser.
  URL: http://0.0.0.0:7860
```

---

## Cost Analysis

### Free Tier (CPU Basic)
- **Cost**: $0/month
- **Limits**: See table above
- **Suitable for**: Demos, portfolios, low traffic

### Paid Tiers (if needed)
- **CPU Upgrade**: $0.05/hour (~$36/month)
- **GPU T4**: $0.60/hour (~$432/month) - NOT NEEDED for inference

**Recommendation**: Start with free tier. Only upgrade if you get consistent high traffic.

---

## Alternative: Separate Deployments (Not Recommended)

If you really want to deploy separately:

### Option 1: Two Spaces
1. **FastAPI on Gradio Space** (has API mode)
2. **Streamlit on Streamlit Space**
3. Update `API_BASE_URL` in UI to point to FastAPI Space URL

**Drawbacks**:
- ❌ More complex
- ❌ Two spaces to manage
- ❌ External API calls (slower)
- ❌ Need to keep both running

### Option 2: FastAPI on HF Inference Endpoints
1. Deploy model as HF Inference Endpoint
2. Deploy Streamlit on Streamlit Space
3. Call Inference Endpoint API

**Drawbacks**:
- ❌ Costs money (no free tier for Inference Endpoints)
- ❌ Requires API key management

**Verdict**: Stick with Docker Space (one container) for simplicity.

---

## Security Considerations

### What's Public:
- ✅ Streamlit UI (intended)
- ✅ Model predictions (intended)
- ✅ Model files in repo (intended - open source)

### What's Private:
- ✅ FastAPI not directly accessible (internal only)
- ✅ No authentication needed (as per requirements)
- ✅ No user data stored (stateless)

### Potential Abuse:
- ⚠️ Anyone can use your Space (costs you nothing on free tier)
- ⚠️ Rate limiting not implemented (HF has some built-in)
- ⚠️ No CAPTCHA (acceptable for demo)

**Mitigation**:
- HF Spaces has built-in DDoS protection
- Can enable "Duplicate this Space" button so others run their own copy
- Can pause/delete Space if needed

---

## Summary Checklist

Before deploying:

- [ ] Model files committed with Git LFS
- [ ] `Dockerfile` created in repo root
- [ ] `requirements.txt` (combined) created
- [ ] `.gitattributes` created
- [ ] README.md has Space metadata
- [ ] Tested locally that API + UI work together
- [ ] HF account created and CLI authenticated

Deploy:

- [ ] Create Docker Space on HF
- [ ] Add HF Space as git remote
- [ ] Push code to Space
- [ ] Wait for build (check logs)
- [ ] Test deployed app
- [ ] Share public URL

Post-deployment:

- [ ] Monitor first few days for issues
- [ ] Check memory/CPU usage in Space settings
- [ ] Add example screenshots to README
- [ ] Share on social media / portfolio

---

## Next Steps

1. **Commit deployment files**:
   ```bash
   git add Dockerfile requirements.txt .gitattributes
   git commit -m "Add Hugging Face Spaces deployment config"
   ```

2. **Setup Git LFS and commit model**:
   ```bash
   git lfs install
   git lfs track "*.safetensors"
   git add .gitattributes models/
   git commit -m "Add model files with Git LFS"
   ```

3. **Create HF Space** (follow Step 3 above)

4. **Push and deploy**:
   ```bash
   git push space main
   ```

5. **Monitor and test** (follow Step 4-5 above)

---

## Getting Help

If you encounter issues:

1. **Check Space logs** - Most issues visible here
2. **HF Discord** - https://discord.gg/huggingface
3. **HF Forums** - https://discuss.huggingface.co/
4. **Documentation** - https://huggingface.co/docs/hub/spaces-overview

Common searches:
- "HF Spaces Docker deployment"
- "HF Spaces multi-service Docker"
- "HF Spaces port 7860"

---

**You're ready to deploy! Follow the steps above and your app will be live in ~10 minutes.** 🚀
