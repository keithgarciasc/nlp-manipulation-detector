# 🧠 NLP Manipulation Scoring & Reframing Engine

## 📌 Project Overview

This project aims to build an NLP-powered engine that detects emotionally manipulative language in headlines and media posts, scores its intensity, and either highlights or rewrites it to neutral phrasing. The system will be deployed as a browser extension to help users critically engage with content on aggregator sites like Yahoo, Reddit, and YouTube.

---

## 🔧 Core Features

- **Manipulation Detection**  
  Classifies text as manipulative or neutral using fine-tuned NLP models.

- **Scoring System**  
  Outputs a manipulation score from 0–100, categorized into:
  - Low (0–30)
  - Medium (31–70)
  - High (71–100)

- **Explanation Engine**  
  Provides 2–3 reasons for each flagged item (e.g., “fear language,” “clickbait phrasing”).

- **Browser Extension Modes**  
  - **Highlight Mode**: Flags emotionally charged words inline (e.g., “threatens”).  
  - **Rewrite Mode**: Replaces manipulative phrasing with neutral alternatives (e.g., “threatens” → “considers declaring”).

---

## 🗂️ Data Strategy

- Utilize public datasets:
  - Kaggle Clickbait Dataset
  - LIAR Dataset
  - Twitter Sentiment Corpus
- Manually label 500–1,000 examples to improve model accuracy and explainability.
- Balance dataset with neutral examples to reduce bias.
- Optional: Scrape headlines from Yahoo and other aggregators for real-world testing.

---

## 🧠 Modeling Approach

- Fine-tune a small transformer model (e.g., DistilBERT or RoBERTa) for binary classification.
- Combine model output with:
  - Rule-based heuristics
  - Sentiment and emotion scoring
- Calibrate manipulation score using weighted logic.
- Build a lightweight rewrite engine using:
  - Masked language modeling
  - Curated phrase maps

---

## 🖥️ Deployment Plan

- **Local MVP**: API endpoint for scoring and rewriting.
- **Browser Extension**:
  - Injects scores and tooltips into live pages.
  - Toggle between highlight and rewrite modes.
  - Supports Yahoo, Reddit, YouTube, and other headline-rich platforms.
- **Feedback Loop**:
  - Users can flag false positives/negatives to improve model performance.

---

## 🧪 Use Cases

- Media literacy tool for everyday consumers.
- Diagnostic engine for journalists and watchdog organizations.
- Real-time detox layer for emotionally manipulative content.
