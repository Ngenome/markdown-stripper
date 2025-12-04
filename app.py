import streamlit as st
import re

# --- Setup Page Config ---
st.set_page_config(
    page_title="Markdown Stripper & Token Saver",
    layout="wide",
    page_icon="🧹"
)

# --- Processing Functions ---

def clean_xml_tags(text):
    """Removes HTML/XML-like tags (e.g., <CodeGroup>, <Tip>) but keeps content."""
    return re.sub(r'<[^>]+>', '', text)

def clean_code_blocks(text):
    """Removes triple backtick code blocks and their content."""
    return re.sub(r'```[\s\S]*?```', '', text)

def clean_markdown_formatting(text):
    """Removes standard markdown symbols to leave plain text."""
    # Remove headings (# Header)
    text = re.sub(r'^\s*#+\s*', '', text, flags=re.MULTILINE)
    # Remove bold/italic (**text**, *text*)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    # Remove blockquotes (>)
    text = re.sub(r'^\s*>\s*', '', text, flags=re.MULTILINE)
    # Remove links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove images ![alt](url) -> ''
    text = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', text)
    # Remove horizontal rules
    text = re.sub(r'^-{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove inline code `text` -> text
    text = text.replace('`', '')
    # Remove list markers
    text = re.sub(r'^\s*[\*\-]\s+', '', text, flags=re.MULTILINE)
    return text

def normalize_whitespace(text):
    """Reduces multiple newlines to single/double newlines."""
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def process_text(text, settings):
    """Master processing function based on settings dictionary."""
    processed = text
    
    # 1. Strip Code Blocks
    if settings.get('strip_code_blocks'):
        processed = clean_code_blocks(processed)
        
    # 2. Strip XML/HTML Components
    if settings.get('strip_xml'):
        processed = clean_xml_tags(processed)
        
    # 3. Strip Standard Markdown
    if settings.get('strip_markdown'):
        processed = clean_markdown_formatting(processed)
        
    # 4. Normalize Whitespace
    processed = normalize_whitespace(processed)
    
    return processed

# --- UI Layout ---

st.title("🧹 Markdown Stripper & Token Saver")
st.markdown("""
Paste your documentation, LLM logs, or mixed Markdown/XML content below. 
Choose a preset to strip formatting and reduce token usage.
""")

# Create two columns: Input (Left) and Output (Right)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Input Text")
    input_text = st.text_area("Paste content here...", height=500, placeholder="# Example Input...")

# --- Sidebar Configuration ---
st.sidebar.header("Configuration")
st.sidebar.info("Select how aggressive the cleaning should be.")

# Mode Selection
mode = st.sidebar.radio(
    "Cleaning Mode",
    ["Plain Text (Default)", "Standard Markdown Only", "Custom"],
    index=0
)

# Settings Logic based on Mode
settings = {
    'strip_code_blocks': False,
    'strip_xml': False,
    'strip_markdown': False
}

if mode == "Plain Text (Default)":
    st.sidebar.markdown("---")
    st.sidebar.write("**Action:** Removes `XML tags`, `Code Blocks`, and `Markdown formatting`. Returns pure text.")
    settings['strip_code_blocks'] = True
    settings['strip_xml'] = True
    settings['strip_markdown'] = True

elif mode == "Standard Markdown Only":
    st.sidebar.markdown("---")
    st.sidebar.write("**Action:** Removes `XML tags` (like `<Tip>`) but **keeps** standard Markdown headers, lists, and links.")
    settings['strip_code_blocks'] = False # Usually keep code in MD, but strip XML wrappers
    settings['strip_xml'] = True
    settings['strip_markdown'] = False

elif mode == "Custom":
    st.sidebar.markdown("---")
    st.sidebar.write("**Custom Filters:**")
    
    settings['strip_xml'] = st.sidebar.checkbox(
        "Strip XML/React Components (<Tag>)", 
        value=True,
        help="Removes tags like <CodeGroup>, <Tip>, but keeps the text inside."
    )
    
    settings['strip_code_blocks'] = st.sidebar.checkbox(
        "Strip Code Blocks (```)", 
        value=True,
        help="Removes code blocks entirely."
    )
    
    settings['strip_markdown'] = st.sidebar.checkbox(
        "Strip Markdown Formatting (**bold**, # Header)", 
        value=True,
        help="Removes visual formatting symbols."
    )

# --- Processing & Output ---

if input_text:
    # Run the cleaner
    output_text = process_text(input_text, settings)
    
    # Calculate crude token estimation (approx 4 chars per token)
    orig_chars = len(input_text)
    new_chars = len(output_text)
    savings = orig_chars - new_chars
    pct_savings = (savings / orig_chars * 100) if orig_chars > 0 else 0
    
    with col2:
        st.subheader("Cleaned Output")
        
        # Stats container
        st.caption(f"📉 **Reduction:** {pct_savings:.1f}% size reduction | **Chars removed:** {savings}")
        
        # Output Area
        st.text_area("Result", value=output_text, height=500, label_visibility="collapsed")
        
else:
    with col2:
        st.subheader("Cleaned Output")
        st.info("Waiting for input text...")
