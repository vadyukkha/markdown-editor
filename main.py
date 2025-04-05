import streamlit as st
import os
from weasyprint import HTML
import io


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_markdown_files():
    return [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".md")]

def load_markdown(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_markdown(filename, content):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def get_unique_filename(filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(UPLOAD_FOLDER, new_filename)):
        new_filename = f"{base}{counter}{ext}"
        counter += 1
    return new_filename

def convert_markdown_to_pdf(markdown_text):
    import markdown
    html_content = markdown.markdown(markdown_text)
    html = HTML(string=html_content)
    pdf_file = io.BytesIO()
    html.write_pdf(pdf_file)
    pdf_file.seek(0)
    return pdf_file

def show_main_interface():
    st.set_page_config(layout="wide", page_title="Markdown Editor")
    st.markdown("# Markdown Editor")
    st.sidebar.title("Markdown Files")
    
    if 'file_processed' not in st.session_state:
        st.session_state.file_processed = False
    
    files = get_markdown_files()
    selected_file = st.sidebar.selectbox("Choose a file", files, index=0 if files else None)
    
    upload_key = "file_uploader_" + str(st.session_state.get("upload_counter", 0))
    uploaded_file = st.sidebar.file_uploader("Upload Markdown File", type=["md"], key=upload_key)
    
    if uploaded_file and not st.session_state.file_processed:
        unique_filename = get_unique_filename(uploaded_file.name)
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state.file_processed = True
        st.session_state.upload_counter = st.session_state.get("upload_counter", 0) + 1
        selected_file = unique_filename
        st.rerun()
    
    if st.session_state.file_processed:
        st.session_state.file_processed = False
    
    if selected_file:
        content = load_markdown(selected_file)
    else:
        content = ""
    
    filename = st.text_input("Filename", selected_file if selected_file else "new_file.md")
    markdown_text = st.text_area("Edit Markdown", content, height=300)
    
    if st.button("Save Markdown"):
        if filename != selected_file:
            filename = get_unique_filename(filename)
        save_markdown(filename, markdown_text)
        st.success(f"Saved {filename}")
        st.rerun()

    st.sidebar.download_button("Download Markdown", markdown_text, file_name=filename, mime="text/markdown")
    
    # PDF Download Button
    pdf_file = convert_markdown_to_pdf(markdown_text)
    if pdf_file:
        st.sidebar.download_button(
            label="Download as PDF",
            data=pdf_file,
            file_name=filename.replace(".md", ".pdf"),
            mime="application/pdf"
        )
    
    st.markdown("# Rendered Markdown")
    st.markdown(markdown_text, unsafe_allow_html=True)

def main():
    show_main_interface()

if __name__ == "__main__":
    main()
