import asyncio
import threading
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter
import edge_tts
import pygame

# 設定介面風格
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

class TTSApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # 設定視窗
        self.title("個人 AI 語音助理 Pro (TTS)")
        self.geometry("800x650")

        # 初始化音效播放器
        pygame.mixer.init()

        # 支援的語音清單
        self.voices = {
            "台灣-曉臻 (女)": "zh-TW-HsiaoChenNeural",
            "台灣-雲哲 (男)": "zh-TW-YunJheNeural",
            "中國-曉曉 (女)": "zh-CN-XiaoxiaoNeural",
            "中國-雲希 (男)": "zh-CN-YunxiNeural",
            "香港-曉佳 (女)": "zh-HK-HiuGaaiNeural",
            "美國-Guy (男)": "en-US-GuyNeural",
            "美國-Jenny (女)": "en-US-JennyNeural"
        }

        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 標題
        self.label_title = customtkinter.CTkLabel(self, text="AI 文字轉語音 Pro", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 主分頁
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.tab_single = self.tabview.add("單一轉換")
        self.tab_batch = self.tabview.add("批次轉換")

        # --- 單一轉換分頁 ---
        self.tab_single.grid_columnconfigure(0, weight=1)
        self.tab_single.grid_rowconfigure(0, weight=1)
        self.textbox = customtkinter.CTkTextbox(self.tab_single, font=customtkinter.CTkFont(size=14))
        self.textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.textbox.insert("0.0", "請在這裡輸入您想要轉換的文字 (支援長文本自動切分)...")

        # --- 批次轉換分頁 ---
        self.tab_batch.grid_columnconfigure(0, weight=1)
        self.label_batch = customtkinter.CTkLabel(self.tab_batch, text="請選擇多個 .txt 檔案進行批次轉換")
        self.label_batch.grid(row=0, column=0, pady=20)
        self.btn_select_files = customtkinter.CTkButton(self.tab_batch, text="選擇文字檔 (*.txt)", command=self.on_select_batch_files)
        self.btn_select_files.grid(row=1, column=0, pady=10)
        self.file_listbox = customtkinter.CTkTextbox(self.tab_batch, height=150)
        self.file_listbox.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.file_listbox.configure(state="disabled")
        self.selected_files = []

        # --- 設定面板 ---
        self.frame_settings = customtkinter.CTkFrame(self)
        self.frame_settings.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.frame_settings.grid_columnconfigure((0, 1, 2), weight=1)

        self.option_voice = customtkinter.CTkOptionMenu(self.frame_settings, values=list(self.voices.keys()))
        self.option_voice.grid(row=0, column=0, padx=10, pady=10)
        self.option_voice.set("台灣-曉臻 (女)")

        self.slider_rate = customtkinter.CTkSlider(self.frame_settings, from_=-50, to=50)
        self.slider_rate.grid(row=0, column=1, padx=10, pady=10)
        self.slider_rate.set(0)
        
        self.label_slider = customtkinter.CTkLabel(self.frame_settings, text="語速 | 音量")
        self.label_slider.grid(row=1, column=1)

        self.slider_volume = customtkinter.CTkSlider(self.frame_settings, from_=-50, to=50)
        self.slider_volume.grid(row=0, column=2, padx=10, pady=10)
        self.slider_volume.set(0)

        # --- 按鈕區 ---
        self.frame_buttons = customtkinter.CTkFrame(self, fg_color="transparent")
        self.frame_buttons.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.frame_buttons.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_play = customtkinter.CTkButton(self.frame_buttons, text="試聽 (僅限單一)", command=self.on_play_click, fg_color="#2ecc71")
        self.btn_play.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

        self.btn_save = customtkinter.CTkButton(self.frame_buttons, text="轉換並儲存", command=self.on_convert_click)
        self.btn_save.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.btn_stop = customtkinter.CTkButton(self.frame_buttons, text="停止播放", command=lambda: pygame.mixer.music.stop(), fg_color="#e74c3c")
        self.btn_stop.grid(row=0, column=2, padx=5, pady=10, sticky="ew")

        # 狀態列
        self.label_status = customtkinter.CTkLabel(self, text="就緒", font=customtkinter.CTkFont(size=12))
        self.label_status.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="w")

    def split_text(self, text, max_chars=1000):
        """將長文本切分為較短的句子，避免超過 API 限制。"""
        # 使用標點符號切分
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
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = full_sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    async def run_tts_with_splitting(self, text, voice, rate, volume, output_path):
        """處理長文本切分並合併轉換。"""
        try:
            chunks = self.split_text(text)
            temp_files = []
            
            for i, chunk in enumerate(chunks):
                if not chunk.strip(): continue
                temp_path = f"temp_{i}.mp3"
                communicate = edge_tts.Communicate(chunk, voice, rate=rate, volume=volume)
                await communicate.save(temp_path)
                temp_files.append(temp_path)
            
            # 合併檔案 (簡單合併)
            with open(output_path, 'wb') as outfile:
                for f in temp_files:
                    with open(f, 'rb') as infile:
                        outfile.write(infile.read())
                    os.remove(f) # 刪除暫存
            return True
        except Exception as e:
            print(f"TTS Error: {e}")
            return False

    def on_select_batch_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Text files", "*.txt")])
        if files:
            self.selected_files = list(files)
            self.file_listbox.configure(state="normal")
            self.file_listbox.delete("0.0", "end")
            for f in self.selected_files:
                self.file_listbox.insert("end", f"{os.path.basename(f)}\n")
            self.file_listbox.configure(state="disabled")

    def get_settings(self):
        voice_key = self.option_voice.get()
        voice = self.voices[voice_key]
        rate_val = int(self.slider_rate.get())
        rate = f"{'+' if rate_val >= 0 else ''}{rate_val}%"
        vol_val = int(self.slider_volume.get())
        volume = f"{'+' if vol_val >= 0 else ''}{vol_val}%"
        return voice, rate, volume

    def tts_worker(self, tasks, callback):
        """
        tasks: list of (text, output_path)
        """
        voice, rate, volume = self.get_settings()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        results = []
        for i, (text, out) in enumerate(tasks):
            self.after(0, lambda idx=i, total=len(tasks): self.label_status.configure(text=f"處理中 ({idx+1}/{total})..."))
            success = loop.run_until_complete(self.run_tts_with_splitting(text, voice, rate, volume, out))
            results.append(success)
            
        loop.close()
        self.after(0, lambda: callback(results))

    def on_play_click(self):
        text = self.textbox.get("0.0", "end").strip()
        if not text: return
        self.label_status.configure(text="產生試聽中...", text_color="yellow")
        
        def play_callback(results):
            if results[0]:
                self.label_status.configure(text="播放中...", text_color="green")
                pygame.mixer.music.load("temp_preview.mp3")
                pygame.mixer.music.play()
            else:
                self.label_status.configure(text="轉換失敗", text_color="red")

        threading.Thread(target=self.tts_worker, args=([(text, "temp_preview.mp3")], play_callback), daemon=True).start()

    def on_convert_click(self):
        current_tab = self.tabview.get()
        voice, rate, volume = self.get_settings()

        if current_tab == "單一轉換":
            text = self.textbox.get("0.0", "end").strip()
            if not text: return
            out = filedialog.asksaveasfilename(defaultextension=".mp3")
            if not out: return
            tasks = [(text, out)]
        else:
            if not self.selected_files:
                messagebox.showwarning("警告", "請先選擇檔案！")
                return
            folder = filedialog.askdirectory(title="選擇儲存資料夾")
            if not folder: return
            tasks = []
            for f in self.selected_files:
                with open(f, 'r', encoding='utf-8') as file:
                    tasks.append((file.read(), os.path.join(folder, os.path.basename(f).replace('.txt', '.mp3'))))

        self.label_status.configure(text="開始轉換任務...", text_color="yellow")
        self.btn_save.configure(state="disabled")

        def finish_callback(results):
            self.btn_save.configure(state="normal")
            success_count = sum(1 for r in results if r)
            self.label_status.configure(text=f"任務完成！成功: {success_count}/{len(results)}", text_color="green")
            messagebox.showinfo("完成", f"已處理完成 {len(results)} 個任務。")

        threading.Thread(target=self.tts_worker, args=(tasks, finish_callback), daemon=True).start()

if __name__ == "__main__":
    app = TTSApp()
    app.mainloop()
