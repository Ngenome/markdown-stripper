# 🧹 Markdown Stripper & Token Saver

A Streamlit web app that strips Markdown formatting, XML/HTML tags, and code blocks from text to reduce token usage when working with LLMs.

## Features

- **Plain Text Mode**: Removes all formatting (XML tags, code blocks, Markdown)
- **Standard Markdown Mode**: Keeps Markdown but removes XML/React components
- **Custom Mode**: Fine-grained control over what to strip

## Local Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run locally

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Deploy to Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository and branch
5. Set the main file path to `app.py`
6. Click "Deploy"

## Project Structure

```
markdown-stripper/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .streamlit/
    └── config.toml    # Streamlit configuration
```

## License

MIT
