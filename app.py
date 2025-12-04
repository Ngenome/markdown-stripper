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
    """Removes HTML/XML-like tags (e.g., <CodeGroup>, <Tip>) but keeps content inside."""
    # Remove self-closing tags like <img ... />
    text = re.sub(r'<[^>]+/>', '', text)
    # Remove opening and closing tags but keep content between them
    text = re.sub(r'<[^>]+>', '', text)
    return text

def clean_code_block_markers(text):
    """Removes triple backtick markers and language hints, but KEEPS the code inside."""
    # Remove opening ``` with optional language identifier (e.g., ```python, ```typescript  theme={null})
    text = re.sub(r'^```[^\n]*\n?', '', text, flags=re.MULTILINE)
    # Remove closing ```
    text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
    return text

def clean_markdown_formatting(text):
    """Removes markdown formatting symbols but keeps the text content."""
    # Remove headings markers (# Header -> Header)
    text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # Remove bold (**text** -> text, __text__ -> text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    
    # Remove italic (*text* -> text, _text_ -> text) - be careful not to match list markers
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', text)
    text = re.sub(r'(?<!_)_([^_]+)_(?!_)', r'\1', text)
    
    # Remove strikethrough (~~text~~ -> text)
    text = re.sub(r'~~([^~]+)~~', r'\1', text)
    
    # Remove blockquote markers (> text -> text)
    text = re.sub(r'^\s*>\s?', '', text, flags=re.MULTILINE)
    
    # Remove links but keep link text ([text](url) -> text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove reference-style links ([text][ref] -> text)
    text = re.sub(r'\[([^\]]+)\]\[[^\]]*\]', r'\1', text)
    
    # Remove link definitions ([ref]: url)
    text = re.sub(r'^\s*\[[^\]]+\]:\s*\S+.*$', '', text, flags=re.MULTILINE)
    
    # Remove images entirely (![alt](url) -> nothing, or keep alt text)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)
    
    # Remove horizontal rules (---, ***, ___)
    text = re.sub(r'^[\-\*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    
    # Remove inline code backticks but keep content (`code` -> code)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove unordered list markers (* item, - item, + item -> item)
    text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
    
    # Remove ordered list markers (1. item -> item)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Remove task list markers (- [ ] or - [x])
    text = re.sub(r'^\s*[\*\-\+]\s*\[[xX ]\]\s*', '', text, flags=re.MULTILINE)
    
    # Remove HTML comments
    text = re.sub(r'<!--[\s\S]*?-->', '', text)
    
    # Remove footnotes
    text = re.sub(r'\[\^[^\]]+\]', '', text)
    
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
    
    # 1. Strip Code Block Markers (keeps code content)
    if settings.get('strip_code_blocks'):
        processed = clean_code_block_markers(processed)
        
    # 2. Strip XML/HTML Tags (keeps content inside)
    if settings.get('strip_xml'):
        processed = clean_xml_tags(processed)
        
    # 3. Strip Standard Markdown Formatting (keeps text content)
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
    input_text = st.text_area("Paste content here...", height=450, placeholder="# Example Input...")
    process_button = st.button("🚀 Process", type="primary", use_container_width=True)

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
    st.sidebar.write("**Action:** Removes `XML tags`, `code block markers`, and `Markdown formatting` while **keeping all content**.")
    settings['strip_code_blocks'] = True
    settings['strip_xml'] = True
    settings['strip_markdown'] = True

elif mode == "Standard Markdown Only":
    st.sidebar.markdown("---")
    st.sidebar.write("**Action:** Removes `XML tags` (like `<Tip>`) but **keeps** Markdown formatting and code blocks.")
    settings['strip_code_blocks'] = False
    settings['strip_xml'] = True
    settings['strip_markdown'] = False

elif mode == "Custom":
    st.sidebar.markdown("---")
    st.sidebar.write("**Custom Filters:**")
    
    settings['strip_xml'] = st.sidebar.checkbox(
        "Strip XML/HTML Tags", 
        value=True,
        help="Removes tags like <CodeGroup>, <Tip>, <Tab> but keeps content inside."
    )
    
    settings['strip_code_blocks'] = st.sidebar.checkbox(
        "Strip Code Block Markers (```)", 
        value=True,
        help="Removes ``` markers and language hints, but KEEPS the code inside."
    )
    
    settings['strip_markdown'] = st.sidebar.checkbox(
        "Strip Markdown Formatting", 
        value=True,
        help="Removes #, **, *, [], (), etc. but keeps the text content."
    )

# --- Processing & Output ---

# Use session state to store output
if 'output_text' not in st.session_state:
    st.session_state.output_text = None
    st.session_state.orig_tokens = 0
    st.session_state.new_tokens = 0

if process_button and input_text:
    # Run the cleaner
    st.session_state.output_text = process_text(input_text, settings)
    st.session_state.orig_tokens = count_tokens(input_text)
    st.session_state.new_tokens = count_tokens(st.session_state.output_text)

if st.session_state.output_text:
    output_text = st.session_state.output_text
    orig_tokens = st.session_state.orig_tokens
    new_tokens = st.session_state.new_tokens
    
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
        st.text_area("Result", value=output_text, height=400, label_visibility="collapsed")
        
        # Copy button
        st.button("📋 Copy to Clipboard", use_container_width=True, 
                  on_click=lambda: st.write("<script>navigator.clipboard.writeText(`" + output_text.replace('`', '\\`') + "`)</script>", unsafe_allow_html=True))
        
else:
    with col2:
        st.subheader("Cleaned Output")
        st.info("Paste content and click **Process** to strip formatting.")
