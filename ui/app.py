"""
Streamlit Web UI for NLP Manipulation Detector

A simple web interface that calls the FastAPI inference service
to detect manipulative language in text.

Usage:
    streamlit run app.py
"""

import os
from typing import Optional, Dict, Any

import streamlit as st
import requests
from requests.exceptions import RequestException, ConnectionError, Timeout

# ============================================================================
# CONFIGURATION
# ============================================================================

# API configuration - can be overridden via environment variable
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
PREDICT_ENDPOINT = f"{API_BASE_URL}/predict"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

# Request timeout in seconds
REQUEST_TIMEOUT = 10

# UI configuration
MAX_INPUT_LENGTH = 2000  # Character limit for input

# Example texts with labels
EXAMPLE_TEXTS = {
    "😱 Sensational": "SHOCKING: Economy in COMPLETE MELTDOWN!",
    "📰 Neutral": "Government announces new infrastructure plan",
    "🚨 Clickbait": "URGENT: You WON'T BELIEVE what happened next!",
    "📊 Factual": "Study shows moderate increase in unemployment rates"
}

# ============================================================================
# API INTERACTION FUNCTIONS
# ============================================================================

def check_api_health() -> bool:
    """
    Check if the API is running and healthy.

    Returns:
        bool: True if API is healthy, False otherwise
    """
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "healthy"
        return False
    except Exception:
        return False


def predict_manipulation(text: str) -> Optional[Dict[str, Any]]:
    """
    Call the FastAPI predict endpoint to classify text.

    Args:
        text: Input text to classify

    Returns:
        Dict with 'label' and 'confidence' if successful, None otherwise

    Raises:
        RequestException: If API request fails
    """
    try:
        # Make POST request to API
        response = requests.post(
            PREDICT_ENDPOINT,
            json={"text": text},
            timeout=REQUEST_TIMEOUT
        )

        # Raise exception for bad status codes
        response.raise_for_status()

        # Parse and return JSON response
        return response.json()

    except ConnectionError:
        raise RequestException(
            f"Cannot connect to API at {API_BASE_URL}. "
            "Make sure the FastAPI server is running."
        )
    except Timeout:
        raise RequestException(
            f"Request timed out after {REQUEST_TIMEOUT} seconds. "
            "The API might be overloaded."
        )
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            raise RequestException(
                "Invalid input. Text must be between 3-512 tokens."
            )
        elif e.response.status_code == 503:
            raise RequestException(
                "Model not loaded. The API server is still starting up."
            )
        else:
            raise RequestException(
                f"API error ({e.response.status_code}): {e.response.text}"
            )
    except Exception as e:
        raise RequestException(f"Unexpected error: {str(e)}")


# ============================================================================
# UI HELPER FUNCTIONS
# ============================================================================

def get_confidence_color(confidence: float) -> str:
    """
    Return color based on confidence level.

    Args:
        confidence: Confidence score between 0 and 1

    Returns:
        Color string for Streamlit
    """
    if confidence >= 0.8:
        return "green"
    elif confidence >= 0.6:
        return "orange"
    else:
        return "red"


def get_label_emoji(label: str) -> str:
    """
    Return emoji based on prediction label.

    Args:
        label: Predicted label ('manipulative' or 'neutral')

    Returns:
        Emoji string
    """
    return "⚠️" if label == "manipulative" else "✅"


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main Streamlit application."""

    # Page configuration
    st.set_page_config(
        page_title="Manipulation Detector",
        page_icon="🔍",
        layout="centered"
    )

    # Header
    st.title("🔍 NLP Manipulation Detector")
    st.markdown(
        "Analyze text for emotionally manipulative language using AI. "
        "Enter a headline or text below to get started."
    )

    # Sidebar with info
    with st.sidebar:
        st.header("About")
        st.markdown(
            """
            This tool uses a fine-tuned **DistilBERT** model to detect
            manipulative language patterns in text.

            **Labels:**
            - ✅ **Neutral**: Factual, balanced language
            - ⚠️ **Manipulative**: Emotionally charged, sensational language

            **How it works:**
            1. Enter text in the input box
            2. Click "Analyze Text"
            3. View the prediction and confidence score
            """
        )

        # API status indicator
        st.divider()
        st.subheader("API Status")
        if check_api_health():
            st.success("✓ API Online")
        else:
            st.error("✗ API Offline")
            st.caption(f"Expected at: {API_BASE_URL}")

    # Main input section
    st.subheader("Enter Text to Analyze")

    # Initialize session state for text input if not exists
    if "text_input" not in st.session_state:
        st.session_state.text_input = ""

    # Check if example button was clicked (before rendering text area)
    for idx, (label, text) in enumerate(EXAMPLE_TEXTS.items()):
        if st.session_state.get(f"example_clicked_{idx}", False):
            st.session_state.text_input = text
            st.session_state[f"example_clicked_{idx}"] = False

    # Text input area (using session state as default value)
    user_input = st.text_area(
        label="Input Text",
        value=st.session_state.text_input,
        placeholder="Paste a headline or text here...",
        height=150,
        max_chars=MAX_INPUT_LENGTH,
        help=f"Maximum {MAX_INPUT_LENGTH} characters"
    )

    # Update session state when user types
    if user_input != st.session_state.text_input:
        st.session_state.text_input = user_input

    # Example buttons (below text input)
    st.caption("Or try an example:")
    cols = st.columns(4)
    for idx, (label, text) in enumerate(EXAMPLE_TEXTS.items()):
        with cols[idx]:
            if st.button(label, key=f"example_{idx}", use_container_width=True):
                st.session_state.text_input = text
                st.rerun()

    # Character count
    char_count = len(user_input)
    st.caption(f"Characters: {char_count}/{MAX_INPUT_LENGTH}")

    # Analyze button
    analyze_button = st.button(
        "🔍 Analyze Text",
        type="primary",
        use_container_width=True,
        disabled=len(user_input.strip()) < 3
    )

    # Results section
    if analyze_button and user_input.strip():
        # Show loading spinner while making API call
        with st.spinner("Analyzing text..."):
            try:
                # Call API
                result = predict_manipulation(user_input)

                if result:
                    # Extract results
                    label = result.get("label", "unknown")
                    confidence = result.get("confidence", 0.0)

                    # Display results
                    st.divider()
                    st.subheader("Analysis Results")

                    # Create two columns for results
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            label="Prediction",
                            value=f"{get_label_emoji(label)} {label.capitalize()}"
                        )

                    with col2:
                        st.metric(
                            label="Confidence",
                            value=f"{confidence * 100:.1f}%"
                        )

                    # Confidence bar
                    st.progress(confidence)

                    # Interpretation message
                    if label == "manipulative":
                        if confidence >= 0.8:
                            st.warning(
                                "⚠️ **High confidence** that this text contains "
                                "manipulative language patterns."
                            )
                        else:
                            st.info(
                                "⚠️ The model detected some manipulative language, "
                                "but confidence is moderate."
                            )
                    else:
                        if confidence >= 0.8:
                            st.success(
                                "✅ **High confidence** that this text uses "
                                "neutral, factual language."
                            )
                        else:
                            st.info(
                                "✅ The text appears mostly neutral, "
                                "but confidence is moderate."
                            )

                    # Show analyzed text in expander
                    with st.expander("View Analyzed Text"):
                        st.text(user_input)

            except RequestException as e:
                # Display API error
                st.error(f"❌ **Error**: {str(e)}")
                st.info(
                    "**Troubleshooting:**\n"
                    "1. Make sure the FastAPI server is running\n"
                    "2. Check that the API URL is correct\n"
                    f"3. Current API URL: `{API_BASE_URL}`"
                )

            except Exception as e:
                # Display unexpected error
                st.error(f"❌ **Unexpected error**: {str(e)}")

    # Disclaimer
    st.divider()
    st.caption(
        "⚠️ **Disclaimer**: This tool provides probabilistic predictions and may not always be accurate. "
        "Use it as one of many factors when evaluating content, not as the sole arbiter of truth. "
        "Results should be interpreted with human judgment and domain expertise."
    )

    # Footer
    st.caption(
        f"Powered by DistilBERT | API: {API_BASE_URL}"
    )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
