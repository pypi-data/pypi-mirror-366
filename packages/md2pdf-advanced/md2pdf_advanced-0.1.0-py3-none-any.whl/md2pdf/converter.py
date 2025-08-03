# converter.py

import os
import markdown
from weasyprint import HTML, CSS
from jinja2 import Template
from datetime import datetime

# 任意のCSSスタイルテンプレート
STYLE_MAP = {
    "default": "styles/default.css",
    "zenn": "styles/zenn.css",
    "github": "styles/github.css",
}

def load_style(style: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "styles", f"{style}.css")
    if not os.path.exists(path):
        raise FileNotFoundError(f"スタイルCSSが見つかりません: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def render_html(md_text: str, css_text: str, title="Document") -> str:
    body = markdown.markdown(md_text, extensions=["extra", "codehilite", "tables", "toc"])
    template = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{{ title }}</title>
        <style>{{ css }}</style>
    </head>
    <body>
        {{ body | safe }}
    </body>
    </html>
    """)
    return template.render(title=title, css=css_text, body=body)

def convert_markdown(md_path: str, style: str = "default", summarize: bool = False) -> str:
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"Markdown ファイルが見つかりません: {md_path}")
    
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    if summarize:
        from .ai import summarize_text  # AI要約モジュール（後述予定）
        summary = summarize_text(md_text)
        md_text += f"\n\n---\n\n## 🧠 Summary\n\n{summary}"

    css_text = load_style(style)
    html = render_html(md_text, css_text)
    pdf_path = os.path.splitext(md_path)[0] + ".pdf"
    HTML(string=html).write_pdf(pdf_path)
    
    print(f"✅ PDF出力完了: {pdf_path}")
    return pdf_path