import streamlit as st
import re
import tiktoken

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

# --- Token Counter ---
@st.cache_resource
def get_tokenizer():
    """Cache the tokenizer for performance."""
    return tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    """Count tokens using tiktoken (GPT-4/Claude compatible)."""
    enc = get_tokenizer()
    return len(enc.encode(text))

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
    
    # Calculate token counts using tiktoken
    orig_tokens = count_tokens(input_text)
    new_tokens = count_tokens(output_text)
    tokens_saved = orig_tokens - new_tokens
    pct_savings = (tokens_saved / orig_tokens * 100) if orig_tokens > 0 else 0
    
    with col2:
        st.subheader("Cleaned Output")
        
        # Token stats in metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Original Tokens", f"{orig_tokens:,}")
        m2.metric("Final Tokens", f"{new_tokens:,}")
        m3.metric("Tokens Saved", f"{tokens_saved:,}", f"-{pct_savings:.1f}%")
        
        # Output Area
        st.text_area("Result", value=output_text, height=450, label_visibility="collapsed")
        
else:
    with col2:
        st.subheader("Cleaned Output")
        st.info("Waiting for input text...")
