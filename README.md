---
title: NLP Content Moderation Service
emoji: 🔍
colorFrom: red
colorTo: orange
sdk: docker
pinned: false
license: mit
---

# NLP Content Moderation Service

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.7.1-red.svg)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/🤗%20Transformers-4.56.2-yellow.svg)](https://huggingface.co/transformers/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A machine learning system that detects emotionally manipulative language in news headlines using a fine-tuned DistilBERT transformer model.

> **🚀 [Try the Live Demo on Hugging Face Spaces](https://huggingface.co/spaces/keithgarciasc/NLP-Content-Moderation-Service)** (update after deployment)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Model Performance](#model-performance)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Dataset](#dataset)
- [Model Architecture](#model-architecture)
- [Training](#training)
- [Model Interpretation](#model-interpretation)
- [Use Cases](#use-cases)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project implements an end-to-end NLP pipeline for detecting manipulative language patterns in news headlines. The system scrapes headlines from major news sources, trains a binary classifier to distinguish between neutral and emotionally manipulative content, and provides interpretability features to understand model predictions.

## Features

- **Binary Classification**: Distinguishes between `neutral` and `manipulative` headlines
- **Pre-trained Transformer**: Built on `distilbert-base-uncased` architecture
- **Model Interpretability**: Token attribution analysis using transformers-interpret
- **Automated Data Collection**: Web scraping pipeline for major news sources
- **Comprehensive Evaluation**: Precision, recall, F1-score metrics on held-out test set
- **Production-Ready Model**: Saved model artifacts ready for deployment

## Model Performance

| Metric | Score |
|--------|-------|
| **Accuracy** | ~89% |
| **F1 Score** | 0.88 |
| **Training Examples** | 2,473 |
| **Test Examples** | 619 |
| **Total Dataset** | 3,092 headlines |

Evaluated on a balanced test set with robust cross-validation.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/keithgarciasc/NLP-Content-Moderation-Service.git
cd NLP-Content-Moderation-Service
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Getting the Trained Model

**Important**: The trained model files are not included in this repository due to their size (~250MB).

You have three options:

#### Option 1: Train Your Own Model (Recommended for Learning)
Follow the training pipeline in the notebooks:
```bash
jupyter notebook notebooks/train_model.ipynb
```

#### Option 2: Download Pre-trained Model
Download the pre-trained model from [Hugging Face Hub](https://huggingface.co/) or [Google Drive](https://drive.google.com) (link to be added) and place it in:
```
models/manipulation_detector_model/
├── config.json
└── model.safetensors
```

#### Option 3: Use Git LFS (For Contributors)
If you have access to the model via Git LFS:
```bash
git lfs install
git lfs pull
```

### Required Packages

```
torch>=2.7.1
transformers>=4.56.2
pandas>=2.3.2
scikit-learn
feedparser
selenium
transformers-interpret
nltk
jupyter
```

## Usage

### Quick Start - Using Pre-trained Model

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load the trained model
model = AutoModelForSequenceClassification.from_pretrained("./models/manipulation_detector_model")
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

# Classify a headline
headline = "SHOCKING: Economy in COMPLETE MELTDOWN!"
inputs = tokenizer(headline, return_tensors="pt", truncation=True, padding=True)

with torch.no_grad():
    outputs = model(**inputs)
    prediction = torch.argmax(outputs.logits, dim=-1)

# 0 = neutral, 1 = manipulative
print(f"Prediction: {'Manipulative' if prediction.item() == 1 else 'Neutral'}")
```

### Training from Scratch

1. **Collect Data**:
```bash
# Run RSS feed scraper
jupyter notebook notebooks/rss_headlines.ipynb

# Or use dynamic web scraper
python scripts/html_scraper_dynamic.py
```

2. **Prepare Data**:
```bash
# Clean and explore data
jupyter notebook notebooks/explore_data.ipynb

# Tokenize and create datasets
jupyter notebook notebooks/prepare_for_training.ipynb
```

3. **Train Model**:
```bash
jupyter notebook notebooks/train_model.ipynb
```

4. **Inspect Predictions**:
```bash
jupyter notebook notebooks/inspect_predictions.ipynb
```

## Project Structure

```
NLP-Content-Moderation-Service/
│
├── data/
│   ├── raw/                          # Raw scraped headlines
│   ├── processed/
│   │   ├── cleaned/                  # Cleaned and labeled data
│   │   └── tokenized/                # Tokenized PyTorch datasets
│   └── inspection_outputs/           # Model interpretation results
│
├── models/
│   └── manipulation_detector_model/  # Trained model artifacts
│       ├── config.json
│       └── model.safetensors
│
├── notebooks/
│   ├── rss_headlines.ipynb          # RSS feed data collection
│   ├── explore_data.ipynb           # Data exploration and cleaning
│   ├── prepare_for_training.ipynb   # Tokenization and dataset prep
│   ├── train_model.ipynb            # Model training pipeline
│   ├── inspect_predictions.ipynb    # Model interpretation
│   └── results/                     # Training checkpoints
│
├── scripts/
│   └── html_scraper_dynamic.py      # Selenium-based web scraper
│
├── requirements.txt                  # Python dependencies
├── LICENSE                           # MIT License
└── README.md                         # This file
```

## Dataset

### Data Sources

Headlines collected from:
- **RSS Feeds**: NPR, New York Times, Washington Post, Bloomberg, CNN
- **Web Scraping**: MSN, Yahoo News, Fox News

### Data Statistics

- **Total Headlines**: 3,092
- **Training Set**: 2,473 (80%)
- **Test Set**: 619 (20%)
- **Label Distribution**: Balanced between neutral and manipulative

### Labeling Methodology

Headlines are manually labeled based on:
- Emotional language intensity
- Fear-mongering tactics
- Sensationalism
- Clickbait patterns
- Loaded terminology

## Model Architecture

### Base Model
- **Architecture**: DistilBERT (distilbert-base-uncased)
- **Parameters**: 66M
- **Layers**: 6 transformer blocks
- **Hidden Size**: 768
- **Attention Heads**: 12

### Training Configuration

```python
{
    "learning_rate": 2e-5,
    "batch_size": 16,
    "num_epochs": 3,
    "optimizer": "AdamW",
    "weight_decay": 0.01,
    "warmup_steps": 500,
    "scheduler": "linear"
}
```

## Training

The model is fine-tuned using Hugging Face's `Trainer` API with:

- **Loss Function**: Cross-entropy loss
- **Optimizer**: AdamW with weight decay
- **Learning Rate Schedule**: Linear decay with warmup
- **Evaluation Strategy**: End of each epoch
- **Early Stopping**: Based on F1 score

Training takes approximately 15-30 minutes on a modern GPU.

## Model Interpretation

The project includes interpretability features using `transformers-interpret`:

### Token Attribution

Identifies words that most strongly influence predictions:

**Manipulative Indicators**:
- "shutdown", "crisis", "bizarre", "stunned"
- "shocking", "outrage", "disaster", "meltdown"
- ALL CAPS words, excessive punctuation

**Neutral Indicators**:
- Factual reporting verbs (reported, announced, stated)
- Specific numbers and dates
- Named entities without emotional framing

### Visualization

Run [notebooks/inspect_predictions.ipynb](notebooks/inspect_predictions.ipynb) to generate token attribution scores and visualizations.

## Use Cases

### Potential Applications

1. **Browser Extensions**: Real-time headline analysis while browsing news sites
2. **Editorial Review Tools**: Assist journalists in identifying emotionally charged language
3. **Media Literacy Education**: Teach users to recognize manipulative content
4. **Social Media Filtering**: Flag potentially manipulative shared content
5. **News Aggregators**: Provide transparency scores for headlines
6. **Research Tools**: Analyze trends in media manipulation over time

### API Integration Example

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Headline(BaseModel):
    text: str

@app.post("/classify")
def classify_headline(headline: Headline):
    # Load model and tokenizer (do this once at startup)
    inputs = tokenizer(headline.text, return_tensors="pt")
    outputs = model(**inputs)
    prediction = torch.argmax(outputs.logits, dim=-1)

    return {
        "headline": headline.text,
        "classification": "manipulative" if prediction.item() == 1 else "neutral",
        "confidence": torch.softmax(outputs.logits, dim=-1).max().item()
    }
```

## Future Work

- [ ] Expand to multi-class classification (fear, anger, urgency, etc.)
- [ ] Increase dataset size to 10,000+ headlines
- [ ] Add explanation generation module
- [ ] Implement headline rewriting suggestions
- [ ] Deploy as REST API service
- [ ] Create web demo interface
- [ ] Support multiple languages
- [ ] Add real-time news feed monitoring
- [ ] Integrate with fact-checking databases

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add unit tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Hugging Face Transformers](https://huggingface.co/transformers/)
- Pre-trained model: [DistilBERT](https://huggingface.co/distilbert-base-uncased)
- Interpretability: [transformers-interpret](https://github.com/cdpierse/transformers-interpret)

## Citation

If you use this project in your research, please cite:

```bibtex
@software{nlp_content_moderation_service,
  title = {NLP Content Moderation Service},
  author = {Keith Garcia},
  year = {2026},
  url = {https://github.com/keithgarciasc/NLP-Content-Moderation-Service}
}
```

## Contact

For questions, feedback, or collaboration opportunities, please open an issue or reach out via [your contact method].

---

**Disclaimer**: This tool is designed for educational and research purposes. It should be used as one of many factors in evaluating news content, not as the sole arbiter of truth or bias.
