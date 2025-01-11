import streamlit as st
from streamlit import session_state as ss
import os
import ollama
import base64
from pathlib import Path
from llamarker import LlaMarker
import tempfile
import shutil
import time
import html


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to a base64 string.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64 encoded string of the image.
    """
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


# Encode and store the logo image for display in the sidebar
encoded_logo = encode_image_to_base64("llamarker/assets/Llamarker_logo.png")

# Define paths for GUI output
cwd = os.getcwd()
gui_out = f"{cwd}/OutDir"
parsed_pdf_folder = f"{gui_out}/PDFs"
parsed_markdown_folder = f"{gui_out}/ParsedFiles"

container_height = "700px"

# Ensure output directory exists
if not os.path.exists(gui_out):
    os.makedirs(gui_out)

# Initialize session state variables for tracking upload and processing
if "uploaded_item" not in ss:
    ss.uploaded_item = False

if "uploaded_file" not in ss:
    ss.uploaded_file = None

if "files_parsed" not in ss:
    ss.files_parsed = False

# Set up the page configuration for Streamlit
st.set_page_config(
    page_title="LlaMarker",
    page_icon="🖍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Header for the main application
st.header("🖍 LlaMarker: Seamless Local Document Parser")

# Introduction section with key features of the app
st.write(
    """
    <style>
    .small-font { font-size: 14px; }
    </style>
    <div class="small-font">
    
    Welcome to **LlaMarker**, your go-to tool for converting documents into clean, structured **Markdown** — fast, intuitive, and entirely local! 🖥️

    </div>
    """,
    unsafe_allow_html=True,
)

# Display key features if no file has been uploaded
if not ss.uploaded_item:
    st.write(
        """
        <style>
        .small-font { font-size: 14px; }
        </style>
        <div class="small-font">
        
        🎉 **Key Features**:
        - 🔄 **Supports multiple formats**: Upload single files or entire folders — including **DOCX**, **TXT**, **PDF**, **RTF**, **ODT**, **XLS**, **XLSX**, **CSV**, **ODS**, **PPT**, **PPTX**, and **ODP**.
        - 🖼️ **Visual content extraction**: Leverage the power of **Llama 3.2 Vision** to convert images, tables, and charts into clean, rich **Markdown**.
        - 🚀 **Powered by Marker**: Built on top of **Marker**, now enhanced for processing various document types locally, including complex visuals.
        - 🔐 **Local processing only**: Everything runs directly on your machine — ensuring complete **privacy**, **speed**, and **control** over your data.

        📁 Simply upload your files, and **LlaMarker** will instantly transform them into beautifully formatted Markdown with all key visual content! ✨
        
        </div>
        """,
        unsafe_allow_html=True,
    )


# Sidebar section for displaying the logo
st.sidebar.markdown(
    f"""
    <style>
    .logo-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 125px;
        margin-bottom: 50px;
    }}
    .logo-container img {{
        max-width: 90%;
        height: auto;
    }}
    </style>
    <div class="logo-container">
        <img src="data:image/png;base64,{encoded_logo}" alt="LlaMarker Logo">
    </div>
    """,
    unsafe_allow_html=True,
)

if not ss.files_parsed:
    # Marker settings
    st.sidebar.subheader("Marker Settings")
    force_ocr = st.sidebar.toggle("Force OCR", help="Enable this to force OCR processing even if text is extractable.")
    selected_languages = st.sidebar.multiselect(
        "OCR Languages",
        ["en", "fr", "de"],
        default=["en"],
        help="Specify which languages to use for OCR processing."
    )

    # Image processing settings
    st.sidebar.subheader("Image Processing Settings")
    qa_evaluator_flag = st.sidebar.toggle("Enable QA Evaluator", value=True, help="Enable or disable the QA evaluator for selecting the best response.")

    # Fetch and display available models from Ollama
    try:
        response = ollama.list()  # Fetch the list of installed models
        vision_models = ollama_vision_models = [ "llama3.2-vision", "llama3.2-vision-90B", "llava", "llava-13B", 
        "llava-34B", "llava-llama3", "bakllava", "moondream", "minicpm-v", "llava-phi3",
        ]
        models = response.models  # Extract the models from the ListResponse object
        model_names = [model.model for model in models if any(vm in model.model.lower() for vm in vision_models)]

        selected_model = st.sidebar.selectbox("Select LLM model", model_names)

    except Exception as e:
        st.sidebar.error(f"Error listing models: {e}")
        

    # Save selected settings to session state
    ss.selected_model = selected_model
    ss.force_ocr = force_ocr
    ss.selected_languages = selected_languages
    ss.qa_evaluator_flag = qa_evaluator_flag

# Styling for the file upload container
st.markdown(
    """
    <style>
    .file-upload-container {
        border: 2px dashed #007BFF; /* Dashed border */
        padding: 20px;             /* Inner padding for spacing */
        border-radius: 10px;       /* Rounded corners */
        background-color: #f9f9f9; /* Light gray background */
        text-align: center;        /* Center text */
    }
    .file-upload-container > div {
        margin-top: 10px;          /* Space above the file uploader */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# Layout for file uploader section
col1, col2, col3 = st.columns([1, 5, 1], gap="large")

with col2:
    if not ss.uploaded_item:
        uploaded_file = st.file_uploader("Upload a document or folder", type=["docx", "txt", "pdf", "rtf", "odt", "xls", "xlsx", "csv", "ods", "ppt", "pptx", "odp", "zip"])
        st.info("Supported formats: .docx, .txt, .pdf, .rtf, .odt, .xls, .xlsx, .csv, .ods, .ppt, .pptx, .odp")
        if uploaded_file:
            ss.uploaded_item = True
            ss.uploaded_file = uploaded_file
            st.rerun()

# Main logic for processing uploaded files
if ss.uploaded_item:
    start_time = time.time()  # Start the timer to measure processing time

    if not ss.files_parsed:
        with tempfile.TemporaryDirectory() as upload_folder:
            # Save uploaded file to a temporary folder
            file_path = Path(upload_folder) / ss.uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(ss.uploaded_file.getbuffer())

            # If the uploaded file is a ZIP, unpack it
            if file_path.suffix == ".zip":
                shutil.unpack_archive(file_path, upload_folder)
                ss.uploaded_file_list = [
                    str(p) for p in Path(upload_folder).rglob("*") if p.suffix in [".pdf", ".txt", ".docx"]
                ]
            else:
                ss.uploaded_file_list = [str(file_path)]

            # Initialize LlaMarker and process the documents
            llamarker = LlaMarker(input_dir=upload_folder, output_dir=gui_out, save_pdfs=True, verbose=1)
            with st.spinner("Converting your documents..."):
                llamarker.process_documents()
            with st.spinner("Parsing using Marker OCR ..."):
                llamarker.parse_with_marker(force_ocr=ss.force_ocr, languages=",".join(ss.selected_languages))
            with st.spinner("Extracting necessary info from images using Llama3.2-Vision ..."):
                llamarker.process_subdirectories(model=ss.selected_model, qa_evaluator=ss.qa_evaluator_flag)
                llamarker.plot_analysis(parsed_markdown_folder)

            ss.files_parsed = True
        end_time = time.time()  # End the timer
        ss.processing_time = round(end_time - start_time, 2)

    # Display processing time and parsed files
    if ss.uploaded_file_list and ss.files_parsed:

        st.sidebar.success(f"Processing completed in {ss.processing_time} seconds.")

        # Sidebar for selecting a parsed file to view
        with st.sidebar:
            if len(ss.uploaded_file_list) > 1:
                st.markdown("### Choose a file to view:")
                ss.selected_file = st.radio(
                    "Files:",
                    options=ss.uploaded_file_list,
                    index=0,
                    format_func=lambda x: Path(x).name,
                )
            else:
                ss.selected_file = ss.uploaded_file_list[0]

        # Columns for displaying uploaded and parsed files
        uploaded_file_col, parsed_file_col = st.columns(2, gap="medium", border=True)

        with uploaded_file_col:
            
            with st.spinner("Displaying selected file..."):
                pdf_file = Path(parsed_pdf_folder) / Path(ss.selected_file).with_suffix(".pdf").name
                col1_, col2_, col3_ = st.columns([5,5,2], gap='large', vertical_alignment="center")
                with col1_:
                    st.markdown("### Uploaded File")
                with col3_:
                    # Button to reset the app for a new upload
                    if st.button("X"):
                        ss.uploaded_item = False
                        ss.uploaded_file = None
                        ss.uploaded_file_list = []
                        ss.selected_file = None
                        ss.files_parsed = False
                        ss.processing_time = 0
                        st.rerun()
                st.divider()
                if pdf_file.exists():
                    pdf_data = pdf_file.read_bytes()
                    pdf_base64 = base64.b64encode(pdf_data).decode("utf-8")
                    st.markdown(
                        f"<iframe src=\"data:application/pdf;base64,{pdf_base64}\" width=\"100%\" height=\"{container_height}\"></iframe>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.error(f"PDF File Not Found : {pdf_file}", icon="🚨")

        with parsed_file_col:
            with st.spinner("Displaying parsed file..."):
                md_file_path = Path(parsed_markdown_folder) / Path(ss.selected_file).with_suffix(".md").name
                
                col1_, col2_, col3_ = st.columns([5,3,5], gap='large', vertical_alignment="center")
                with col1_:
                    st.markdown("### Parsed Content")
                with col3_:
                    # Add a toggle switch for raw or rendered view
                    show_raw = st.toggle("Show Raw Markdown")
                    
                st.divider()
                if md_file_path.exists():
                    
                    with open(md_file_path, "r") as md_file:
                        md_content = md_file.read()
                    
                    if show_raw:
                        # Show raw markdown content in a text area
                        st.text_area("Raw Markdown Content", md_content, height=650)
                    else:
                        # Show rendered markdown content in a scrollable container
                        st.markdown(
                            f"""
                            <div style="overflow-y: scroll; height: {container_height}; border: 1px solid #ccc; padding: 10px;">
                                {html.escape(md_content)}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Add a download button for the markdown content
                    st.download_button(
                        label="Download Markdown File",
                        data=md_content,
                        file_name=os.path.basename(md_file_path),
                        mime="text/markdown",
                        icon=":material/download:"
                    )

                else:
                    st.error(f"Parsed File Not Found : {md_file_path}", icon="🚨")
                    
        # Sidebar for displaying analysis plot
        with st.sidebar:
            if len(ss.uploaded_file_list) > 1:
                st.subheader("Analysis Plot")
                st.image(Path(parsed_markdown_folder) / "page_counts.png")

            if st.button("Upload New", type="primary", icon=":material/upload:"):
                ss.uploaded_item = False
                ss.uploaded_file = None
                ss.uploaded_file_list = []
                ss.selected_file = None
                ss.files_parsed = False
                ss.processing_time = 0
                st.rerun()
