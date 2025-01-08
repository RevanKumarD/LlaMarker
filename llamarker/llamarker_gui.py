import streamlit as st
import os
from pathlib import Path
from llamarker import LlaMarker
import tempfile
import shutil

st.title("📝 LlaMarker: Seamless Universal Local Document Parser")

st.write("""
Welcome to **LlaMarker**, your go-to tool for converting documents into clean, well-structured **Markdown** — fast, intuitive, and entirely local! 🖥️

#### Key Features:
- **Multiple formats supported**: Effortlessly upload individual files or entire folders containing **TXT, DOCX, PDF, PPT**, and more.
- **Visual content extraction**: Leverages the power of **Llama 3.2 Vision** to detect and convert images, tables, charts, and diagrams into rich Markdown.
- **Enhanced with Marker**: Built on top of the open-source **Marker** parser, enhanced to handle visual content locally and different document types.
- **Fully local processing**: No cloud, no external servers — everything is processed on your machine for maximum privacy and performance. 🚀

🔄 Simply upload your files, and **LlaMarker** will convert them into clean Markdown, enriched with all visual information!
""")

# Sidebar for file/folder selection
st.sidebar.header("Upload Options")
upload_type = st.sidebar.radio("Select upload type", ["Single File", "Folder"])

if upload_type == "Single File":
    uploaded_file = st.sidebar.file_uploader("Choose a document", type=["docx", "txt", "pdf"])
elif upload_type == "Folder":
    uploaded_folder = st.sidebar.file_uploader("Choose a folder (ZIP format)", type=["zip"])

# Processing button
if st.sidebar.button("Process"):
    if upload_type == "Single File" and uploaded_file:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the uploaded file to the temp directory
            file_path = Path(temp_dir) / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Run LlaMarker on the file
            llamarker = LlaMarker(input_dir=temp_dir)
            llamarker.process_documents()
            llamarker.parse_with_marker()
            llamarker.process_subdirectories()

            # Display results
            st.subheader("Processing Results")
            st.write("Original Document:")
            st.write(file_path.name)
            
            st.write("Parsed Output:")
            with open(Path(temp_dir) / "ParsedFiles" / f"{file_path.stem}.md", "r") as md_file:
                st.markdown(md_file.read())

            st.subheader("Analysis Plot")
            llamarker.plot_analysis(temp_dir)
            st.image(Path(temp_dir) / "page_counts.png")

    elif upload_type == "Folder" and uploaded_folder:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract uploaded ZIP folder
            zip_path = Path(temp_dir) / "uploaded_folder.zip"
            with open(zip_path, "wb") as f:
                f.write(uploaded_folder.getbuffer())
            shutil.unpack_archive(zip_path, temp_dir)

            # Run LlaMarker on the extracted folder
            llamarker = LlaMarker(root_directory=temp_dir)
            llamarker.process_documents()
            llamarker.parse_with_marker()
            llamarker.process_subdirectories()

            # Display summary
            st.subheader("Processing Summary")
            for file_name, page_count in llamarker.generate_summary():
                st.write(f"{file_name}: {page_count} pages")

            st.subheader("Analysis Plot")
            llamarker.plot_analysis(temp_dir)
            st.image(Path(temp_dir) / "page_counts.png")

    else:
        st.error("Please upload a valid file or folder.")

st.sidebar.info("Supported formats: DOCX, TXT, PDF")
