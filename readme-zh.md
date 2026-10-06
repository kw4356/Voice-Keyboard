# Voice-Keyboard
一款專為 Windows 設計的輕量級離線語音輸入工具，由 `CrispASR` 與 `Qwen 3 ASR` 驅動。  
由於 Windows 內建的語音輸入對廣東話支援不佳，因此我利用 AI 開發了這款工具。

> *注意：本專案主要使用 Gemini 3.6 Flash & Qwen3.8-Flash-Next 以 vibe-coding 方式開發。*

---

## 📜 致謝

感謝 [CrispStrobe](https://github.com/CrispStrobe/CrispASR) 開發 [CrispASR (Vulkan)](https://github.com/CrispStrobe/CrispASR/releases)

感謝通義千問團隊（阿里巴巴）開發 [Qwen 3 ASR](https://github.com/QwenLM/Qwen3-ASR)

## ✨ 主要特色
- 🚀 **快速且完全離線識別**：採用 [CrispASR](https://github.com/CrispStrobe/CrispASR) 執行階段與 Qwen3-ASR GGUF 模型，完全無需連接網路，保障你的數據安全與個人隱私。
- 🎯 **按住說話模式（Hold-to-Talk）**：按住快捷鍵開始錄音，鬆開後自動轉寫並模擬 `Ctrl + V` 自動貼上文字。
- ⚡ **Vulkan GPU / CPU 加速**：支援 NVIDIA/AMD GPU 的 Vulkan 硬體加速或純 CPU 運算，可隨時輕鬆切換。
- 🔤 **多語言識別與繁簡轉換**：支援超過 28 種語言識別（包含粵語/廣東話、國語/普通話、英語等）；內建 OpenCC 支援自動繁簡體中文轉換（`s2t` / `t2s`）。
- 🔔 **系統托盤與狀態指示**：動態系統托盤圖示（🟢 就緒 / 🔴 錄音中 / 🟠 處理中）。
- ⚙️ **自訂設定與開機自啟**：自動掃描 `.gguf` 模型，支援 Windows 開機自動啟動，並可持久化儲存自訂設定（`config.json`）。

---

## ⚙️ 工作原理
系統麥克風輸入 → Qwen3-ASR 識別 → 自動貼上文字

---

## 📁 檔案結構
```text
VoiceKeyboard/
├── VoiceKeyboard.exe          # 主程式執行檔
├── config.json                # 設定檔
├── CrispASR/
│   └── crispasr.exe           # CrispASR 執行檔
└── models/
  └── Qwen3-ASR-0.6B-Q4_K_M.gguf  # Qwen3-ASR 模型檔案
```
---

## 🚀 快速上手
1. [下載](https://github.com/kw4356/Voice-Keyboard/releases)並解壓縮檔案
2. 執行 `VoiceKeyboard.exe`（EN 為英文介面，ZH 為中文介面）
3. 開始使用：
   - 按住快捷鍵（預設：`Alt + Caps Lock`）開始說話。
   - 鬆開快捷鍵後，系統會自動將語音轉換為文字並貼上至目前游標所在位置。

---

## ⚙️ 右鍵選單與設定
右鍵點擊系統托盤圖示即可更改設定：

| 選單選項 | 說明 | 
| :--- | :--- | 
| **模型 (Model)** | 顯示目前正在使用的模型 |
| **硬體加速 (Hardware Acceleration)** | 在 `Vulkan (GPU)` 或 `CPU` 之間切換 | 
| **識別語言 (Recognition Language)** | 支援約 30 種語言（預設為 `Auto` 自動識別） | 
| **繁簡轉換 (Chinese Conversion)** | 輸出中文時可切換繁體／簡體中文 | 
| **修改快捷鍵 (Change Hotkey)** | 自訂觸發快捷鍵 |
| **開機自啟 (Start on Boot)** | 開啟或關閉 Windows 開機自動啟動 |

---

## 📜 開源許可與版權

- **第三方函式庫**：各獨立組件（如 `CrispASR`、`OpenCC` 及相關依賴項）均遵循其原始專案的授權條款。
- **本專案許可**：採用 **[MIT 許可證](https://opensource.org/license/MIT)** 發布。

Copyright © 2026 **kw4356**
