# AI 文字轉語音 (TTS) Pro 助理

這是一個基於 Python 開發的文字轉語音桌面應用程式與網頁工具。
是透過Gemini Cli開發的小工具

## 功能特點
- **桌面版 (my_tts_app.py)**:
  - 支援多種語音模型（台語、國語、粵語、英語）。
  - **批次轉換**: 一次處理多個 .txt 檔案。
  - **長文本切分**: 自動處理超過字數限制的文章並合併。
  - 現代化 Dark Mode 介面。
- **網頁版 (app.py)**:
  - 可部署於 Streamlit Cloud，隨處可用。

## 安裝需求
```bash
pip install -r requirements.txt
```

## 使用方式
- 執行桌面版: `python TTS/my_tts_app.py`
- 執行網頁版: `streamlit run TTS/app.py`

## 技術棧
- [edge-tts](https://github.com/rany2/edge-tts)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [Streamlit](https://streamlit.io/)
