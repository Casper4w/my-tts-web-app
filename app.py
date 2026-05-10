import streamlit as st
import asyncio
import edge_tts
import os

# 網頁外觀設定
st.set_page_config(page_title="個人 AI 語音助理", page_icon="🎙️", layout="centered")

st.title("🎙️ AI 文字轉語音網頁工具")
st.markdown("輸入文字，選擇語音模型，即可產生高品質 MP3。")

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

# 側邊欄設定區
with st.sidebar:
    st.header("⚙️ 參數設定")
    selected_voice_key = st.selectbox("選擇語音模型", list(VOICES.keys()))
    voice_id = VOICES[selected_voice_key]
    
    rate_val = st.slider("語速調整 (%)", -50, 50, 0)
    rate = f"{'+' if rate_val >= 0 else ''}{rate_val}%"
    
    vol_val = st.slider("音量調整 (%)", -50, 50, 0)
    volume = f"{'+' if vol_val >= 0 else ''}{vol_val}%"

# 文字輸入區
text = st.text_area("請輸入想要轉換的文字：", placeholder="例如：你好，今天天氣真不錯！", height=250)

# 非同步轉換函式
async def generate_audio(text, v_id, r, v):
    communicate = edge_tts.Communicate(text, v_id, rate=r, volume=v)
    await communicate.save("temp_output.mp3")

# 轉換按鈕
if st.button("✨ 立即轉換語音", use_container_width=True):
    if not text.strip():
        st.warning("⚠️ 請先輸入文字內容。")
    else:
        with st.spinner("正在合成語音中..."):
            try:
                # 執行非同步任務
                asyncio.run(generate_audio(text, voice_id, rate, volume))
                
                # 顯示結果
                st.success("✅ 轉換成功！")
                
                # 播放器
                audio_file = open("temp_output.mp3", "rb")
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mp3")
                
                # 下載按鈕
                st.download_button(
                    label="💾 下載 MP3 檔案",
                    data=audio_bytes,
                    file_name="tts_output.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                audio_file.close()
            except Exception as e:
                st.error(f"❌ 發生錯誤：{e}")

st.divider()
st.caption("Powered by edge-tts & Streamlit")
