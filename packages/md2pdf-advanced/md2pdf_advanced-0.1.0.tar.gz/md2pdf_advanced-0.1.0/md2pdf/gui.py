# gui.py
import streamlit as st
from converter import convert_markdown

def launch_gui():
    st.title("Markdown to PDF Converter")
    uploaded = st.file_uploader("Upload your .md file")
    style = st.selectbox("Choose a style", ["default", "zenn", "github"])
    summarize = st.checkbox("Summarize content with AI")
    
    if st.button("Convert to PDF"):
        if uploaded:
            with open("temp.md", "wb") as f:
                f.write(uploaded.read())
            pdf_path = convert_markdown("temp.md", style=style, summarize=summarize)
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF", f, file_name="output.pdf")

if __name__ == "__main__":
    launch_gui()