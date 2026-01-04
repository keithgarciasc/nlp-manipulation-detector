# NLP Manipulation Detector - Web UI

A clean, minimal Streamlit web interface for the manipulation detector API.

## Quick Start

### 1. Install Dependencies

```bash
cd ui
pip install -r requirements.txt
```

### 2. Make Sure API is Running

The web UI requires the FastAPI backend to be running. In a separate terminal:

```bash
cd ../api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Run the Streamlit App

```bash
# From the ui directory
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Features

### User Interface
- **Text Input Area**: Enter headlines or text to analyze
- **Example Buttons**: Quick-load sample texts
- **Analyze Button**: Submit text for classification
- **Character Counter**: Track input length
- **Loading Spinner**: Visual feedback during API calls

### Results Display
- **Prediction Label**: Shows "Neutral" or "Manipulative" with emoji
- **Confidence Score**: Displayed as percentage with progress bar
- **Interpretation**: Context-aware messages based on prediction
- **Analyzed Text Viewer**: Expandable section to review input

### Sidebar
- **About Section**: Explanation of how the tool works
- **API Status**: Real-time health check indicator
- **Usage Instructions**: Step-by-step guide

### Error Handling
- API connection errors
- Timeout handling
- Invalid input validation
- Service unavailable detection
- User-friendly error messages

## Configuration

### Environment Variables

Set the API URL via environment variable:

```bash
# Linux/Mac
export API_BASE_URL=http://localhost:8000
streamlit run app.py

# Windows PowerShell
$env:API_BASE_URL="http://localhost:8000"
streamlit run app.py

# Windows Command Prompt
set API_BASE_URL=http://localhost:8000
streamlit run app.py
```

### Default Configuration

If not set, the app defaults to:
- **API URL**: `http://localhost:8000`
- **Request Timeout**: 10 seconds
- **Max Input Length**: 2,000 characters

## Usage Examples

### Basic Usage

1. **Start the API server** (Terminal 1):
   ```bash
   cd api
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Start the web UI** (Terminal 2):
   ```bash
   cd ui
   streamlit run app.py
   ```

3. **Use the interface**:
   - Enter text or click an example button
   - Click "Analyze Text"
   - View results

### Testing Different Scenarios

**Manipulative Text:**
```
SHOCKING: Economy in COMPLETE MELTDOWN!
```

**Neutral Text:**
```
Government announces new infrastructure plan
```

**Edge Cases:**
- Very short text (under 3 characters) - button disabled
- Very long text (over 2,000 characters) - automatically truncated
- Empty input - button disabled

## Screenshot Guide

### Main Interface
```
┌─────────────────────────────────────────┐
│  🔍 NLP Manipulation Detector           │
│                                         │
│  Enter Text to Analyze                  │
│  ┌───────────────────────────────────┐ │
│  │ Paste a headline or text here...  │ │
│  │                                   │ │
│  └───────────────────────────────────┘ │
│                                         │
│  [Example 1] [Example 2] [Example 3]   │
│                                         │
│  [🔍 Analyze Text]                      │
│                                         │
│  ─────────────────────────────────────  │
│  Analysis Results                       │
│  Prediction: ⚠️ Manipulative            │
│  Confidence: 87.3%                      │
│  ████████████████░░░░                   │
└─────────────────────────────────────────┘
```

### Sidebar
```
┌──────────────────┐
│ About            │
│                  │
│ This tool uses   │
│ DistilBERT...    │
│                  │
│ ──────────────── │
│ API Status       │
│ ✓ API Online     │
└──────────────────┘
```

## Troubleshooting

### API Connection Issues

**Problem**: "Cannot connect to API" error

**Solutions**:
1. Verify API is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check API URL in sidebar (should show "API Online")

3. Verify correct port:
   ```bash
   # API should be on port 8000
   # Streamlit should be on port 8501
   ```

4. Set API URL explicitly:
   ```bash
   export API_BASE_URL=http://localhost:8000
   streamlit run app.py
   ```

### Port Already in Use

**Problem**: Streamlit can't start on port 8501

**Solution**:
```bash
# Use different port
streamlit run app.py --server.port 8502

# Or kill existing process
# Windows
netstat -ano | findstr :8501

# Linux/Mac
lsof -ti:8501 | xargs kill -9
```

### Model Not Loaded Error

**Problem**: "Model not loaded" message

**Solution**:
- Wait a few seconds after starting the API
- Model loads at startup (takes 2-5 seconds)
- Check API logs for errors

### Slow Response Times

**Problem**: Long wait times for predictions

**Solutions**:
- First request is slower (model warm-up)
- Subsequent requests should be faster (~100-200ms)
- Check API server isn't overloaded
- Verify network connection to API

## Customization

### Changing Examples

Edit the `EXAMPLE_TEXTS` list in [app.py](app.py:30-35):

```python
EXAMPLE_TEXTS = [
    "Your custom example 1",
    "Your custom example 2",
    "Your custom example 3",
    "Your custom example 4"
]
```

### Adjusting Timeouts

Edit the `REQUEST_TIMEOUT` constant in [app.py](app.py:23):

```python
REQUEST_TIMEOUT = 30  # Increase to 30 seconds
```

### Changing Input Limits

Edit the `MAX_INPUT_LENGTH` constant in [app.py](app.py:26):

```python
MAX_INPUT_LENGTH = 5000  # Allow longer inputs
```

### UI Theme

Streamlit uses default theme. To customize, create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## Deployment

### Local Network Access

Allow other devices on your network to access:

```bash
streamlit run app.py --server.address 0.0.0.0
```

Then access from other devices:
```
http://YOUR_IP_ADDRESS:8501
```

### Production Deployment

**Using Docker:**

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8501

ENV API_BASE_URL=http://api:8000

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t manipulation-detector-ui .
docker run -p 8501:8501 -e API_BASE_URL=http://localhost:8000 manipulation-detector-ui
```

**Using Streamlit Cloud:**
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Set `API_BASE_URL` in secrets
5. Deploy

**Note**: Ensure API is publicly accessible or deployed alongside the UI.

## Performance

### Load Times
- **Initial Load**: ~2-3 seconds
- **API Health Check**: <1 second
- **Prediction Request**: ~100-500ms (depends on API)

### Concurrent Users
- Streamlit handles multiple users
- Bottleneck is typically the API server
- Consider scaling API with multiple workers

### Browser Compatibility
- Chrome ✓
- Firefox ✓
- Safari ✓
- Edge ✓

## Development

### Running in Development Mode

```bash
# Auto-reload on file changes
streamlit run app.py

# Custom port
streamlit run app.py --server.port 8502

# Disable CORS (for development)
streamlit run app.py --server.enableCORS false
```

### Debugging

Enable debug mode:
```bash
streamlit run app.py --logger.level=debug
```

View Streamlit config:
```bash
streamlit config show
```

### Code Structure

```
app.py
├── Configuration (lines 17-35)
│   ├── API URLs
│   ├── Timeouts
│   └── UI settings
│
├── API Functions (lines 40-110)
│   ├── check_api_health()
│   └── predict_manipulation()
│
├── UI Helpers (lines 115-140)
│   ├── get_confidence_color()
│   └── get_label_emoji()
│
└── Main App (lines 145-320)
    ├── Page setup
    ├── Sidebar
    ├── Input section
    ├── Results display
    └── Error handling
```

## Testing

### Manual Testing Checklist

- [ ] App loads without errors
- [ ] API status shows "Online" when API running
- [ ] API status shows "Offline" when API stopped
- [ ] Text input accepts text
- [ ] Character counter updates
- [ ] Analyze button disabled for short input
- [ ] Example buttons load text correctly
- [ ] Loading spinner appears during analysis
- [ ] Results display correctly
- [ ] Confidence percentage shows properly
- [ ] Error messages appear for API issues
- [ ] Disclaimer and footer visible

### Test Cases

**Test 1: Normal Operation**
```
Input: "SHOCKING NEWS: Everything is terrible!"
Expected: Manipulative, high confidence
```

**Test 2: Neutral Text**
```
Input: "City council votes on new budget proposal"
Expected: Neutral, high confidence
```

**Test 3: Edge Case - Short Input**
```
Input: "Hi"
Expected: Button disabled
```

**Test 4: API Down**
```
Stop API server
Expected: Connection error with troubleshooting tips
```

## API Integration Details

### Request Format

```python
requests.post(
    "http://localhost:8000/predict",
    json={"text": "input text here"},
    timeout=10
)
```

### Response Format

**Success (200 OK):**
```json
{
  "label": "manipulative",
  "confidence": 0.8734
}
```

**Error (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "Text must be at least 3 characters long",
      "type": "value_error"
    }
  ]
}
```

**Error (503 Service Unavailable):**
```json
{
  "detail": "Model not loaded. Please try again later."
}
```

## FAQ

**Q: Can I use this without the API?**
A: No, the UI requires the FastAPI backend to be running.

**Q: Can I deploy this on Streamlit Cloud?**
A: Yes, but your API must be publicly accessible (deployed on cloud service).

**Q: How do I change the API URL?**
A: Set the `API_BASE_URL` environment variable before running.

**Q: Does this store my data?**
A: No, the UI makes stateless API calls and doesn't persist data.

**Q: Can I add authentication?**
A: This version doesn't include auth. You'd need to modify the code to add API keys or OAuth.

## License

MIT License - See main project LICENSE file.

## Support

For issues:
1. Check API is running: http://localhost:8000/health
2. Check Streamlit logs in terminal
3. Review [main project README](../README.md)
4. Open an issue on GitHub
