import streamlit as st
import asyncio
import edge_tts
import os
import re

# 網頁外觀設定
st.set_page_config(page_title="個人 AI 語音助理 Pro", page_icon="🎙️", layout="centered")

st.title("🎙️ AI 文字轉語音網頁版 Pro")

# 語音模型清單
VOICES = {
    "台灣-曉臻 (女)": "zh-TW-HsiaoChenNeural",
    "台灣-雲哲 (男)": "zh-TW-YunJheNeural",
    "中國-曉曉 (女)": "zh-CN-XiaoxiaoNeural",
    "中國-雲希 (男)": "zh-CN-YunxiNeural",
    "香港-曉佳 (女)": "zh-HK-HiuGaaiNeural",
    "美國-Jenny (女)": "en-US-JennyNeural",
    "美國-Guy (男)": "en-US-GuyNeural"
}

# 文本切分邏輯
def split_text(text, max_chars=1000):
    sentences = re.split(r'([。！？；.!?;])', text)
    chunks = []
    current_chunk = ""
    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        punc = sentences[i+1] if i+1 < len(sentences) else ""
        full_sentence = sentence + punc
        if len(current_chunk) + len(full_sentence) <= max_chars:
            current_chunk += full_sentence
        else:
            if current_chunk: chunks.append(current_chunk)
            current_chunk = full_sentence
    if current_chunk: chunks.append(current_chunk)
    return chunks

async def generate_combined_audio(text, v_id, r, v, output_path):
    chunks = split_text(text)
    temp_files = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip(): continue
        temp_path = f"web_temp_{i}.mp3"
        communicate = edge_tts.Communicate(chunk, v_id, rate=r, volume=v)
        await communicate.save(temp_path)
        temp_files.append(temp_path)
    
    with open(output_path, 'wb') as outfile:
        for f in temp_files:
            with open(f, 'rb') as infile:
                outfile.write(infile.read())
            os.remove(f)

# 側邊欄設定
with st.sidebar:
    st.header("⚙️ 設定")
    selected_voice_key = st.selectbox("語音模型", list(VOICES.keys()))
    voice_id = VOICES[selected_voice_key]
    rate_val = st.slider("語速 (%)", -50, 50, 0)
    rate = f"{'+' if rate_val >= 0 else ''}{rate_val}%"
    vol_val = st.slider("音量 (%)", -50, 50, 0)
    volume = f"{'+' if vol_val >= 0 else ''}{vol_val}%"

# 分頁顯示
tab1, tab2 = st.tabs(["單一長文本", "批次檔案處理"])

with tab1:
    text_input = st.text_area("輸入文字 (支援長文自動切分)：", height=300)
    if st.button("✨ 開始轉換", key="single"):
        if text_input:
            with st.spinner("合成中..."):
                asyncio.run(generate_combined_audio(text_input, voice_id, rate, volume, "output_v2.mp3"))
                st.audio("output_v2.mp3")
                with open("output_v2.mp3", "rb") as f:
                    st.download_button("💾 下載音檔", f, "tts_output.mp3")
        else:
            st.warning("請輸入內容")

with tab2:
    uploaded_files = st.file_uploader("上傳多個 .txt 檔案", type="txt", accept_multiple_files=True)
    if st.button("🚀 開始批次處理", key="batch"):
        if uploaded_files:
            for uploaded_file in uploaded_files:
                with st.spinner(f"正在處理 {uploaded_file.name}..."):
                    content = uploaded_file.read().decode("utf-8")
                    out_name = uploaded_file.name.replace(".txt", ".mp3")
                    asyncio.run(generate_combined_audio(content, voice_id, rate, volume, out_name))
                    st.write(f"✅ {uploaded_file.name} 轉換完成")
                    with open(out_name, "rb") as f:
                        st.download_button(f"下載 {out_name}", f, out_name)
        else:
            st.warning("請先上傳檔案")

st.divider()
st.caption("TTS Pro Web V2 - Powered by edge-tts")
