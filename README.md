# NLP Manipulation Detector

This project features a fine-tuned **DistilBERT** model designed to detect emotionally manipulative language in news headlines.

## 🧠 Model Overview
- Built on the `distilbert-base-uncased` transformer architecture.
- Fine-tuned using Hugging Face's `Trainer` API.
- Trained on a custom dataset of **3,000 news headlines**:
  - 1,500 labeled as **neutral**
  - 1,500 labeled as **manipulative**

## 📊 Performance
- **Accuracy**: ~89%
- **F1 Score**: 0.88
- Evaluated using precision, recall, and F1 metrics on a held-out test set.

## 🔧 Features
- Binary classification: `manipulative` vs `neutral`
- Easily integrable into real-time applications:
  - Browser extensions
  - Editorial review tools
  - Media transparency platforms
## 📁 Outputs
- Trained model saved to `../models/manipulation_detector_model`
- Evaluation metrics printed after training

## 🚀 Future Work
- Expand dataset to include more nuanced emotional categories
- Integrate explanation and rewrite modules
---

Feel free to fork, contribute, or reach out with feedback!