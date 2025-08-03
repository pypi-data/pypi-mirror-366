# md2pdf

📄 **Markdown to PDF Converter with CLI & GUI**

`md2pdf` は、Markdown ファイルを美しくカスタマイズされた PDF に変換できる Python パッケージです。CLI と GUI の両方に対応し、以下のような特徴を備えています。

---

## ✨ 特徴

- ✅ **Markdown → PDF** 変換（HTML + CSS + WeasyPrint）
- 🎨 **3種類のデザインテンプレート**（default / zenn / github）
- 🧠 **AI要約機能（オプション）**
- 🖥 **Streamlit ベースの GUI 操作**
- 🔧 CLI からの高速変換も可能

---

## 🔧 インストール

```bash
git clone https://github.com/yut0takagi/md2pdf.git
cd md2pdf
pip install -r requirements.txt
```

---

## 🚀 使い方

### CLI（コマンドライン）

```bash
python -m md2pdf .cli convert example.md --style github
```

オプション:

- `--style`: 使用するCSSテンプレート（default, zenn, github）
- `--summarize`: AIによる要約を最後に追加（※APIキー必要）

### GUI（Streamlit）

```bash
PYTHONPATH=. streamlit run md2pdf/gui.py
```

ブラウザが開き、アップロード＆変換が可能です。

---

## 📁 ディレクトリ構成

```
md2pdf/
├── md2pdf/
│   ├── converter.py
│   ├── cli.py
│   ├── gui.py
│   └── styles/
│       ├── default.css
│       ├── zenn.css
│       └── github.css
├── example.md
├── requirements.txt
├── README.md
└── pyproject.toml
```

---

## 📄 ライセンス

MIT License
