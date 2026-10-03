[中文](https://github.com/kw4356/Voice-Keyboard/blob/main/readme-zh.md)

# Voice-Keyboard
A lightweight offline voice input tool for Windows. Powered by `CrispASR` and `Qwen 3 ASR`.
The windows built in voice input is not good in Cantonese, so i made one with AI.

> *Note: This project was mostly vibe-coded using Gemini 3.6 Flash and Qwen3.8-Flash-Next*

---

## 📜 Credits

Thanks [CrispStrobe](https://github.com/CrispStrobe/CrispASR) making [CrispASR (Vulkan)](https://github.com/CrispStrobe/CrispASR/releases)

Thanks Qwen team (Alibaba) for [Qwen 3 ASR](https://github.com/QwenLM/Qwen3-ASR)

## ✨ Key Features
- 🚀 **Fast and fully Offline Recognition**: Powered by the [CrispASR](https://github.com/CrispStrobe/CrispASR) runtime and Qwen3-ASR GGUF models. Requires no internet connection, keeping your data safe and private.
- 🎯 **Hold-to-Talk Mode**: Press and hold the hotkey to record, and release to auto-transcribe and simulate `Ctrl + V` to paste.
- ⚡ **Vulkan GPU / CPU Acceleration**: Supports NVIDIA/AMD GPU Vulkan hardware acceleration or pure CPU computation, easily switchable.
- 🔤 **Multilingual & Traditional/Simplified Chinese Conversion**: Supports recognition for over 28 languages (including Cantonese, Mandarin, English, etc.); features built-in OpenCC for automatic Chinese script conversion (`s2t` / `t2s`).
- 🔔 **System Tray & Status Indicators**: Dynamic system tray icon (🟢 Ready / 🔴 Recording / 🟠 Processing).
- ⚙️ **Custom Configuration & Auto-Start**: Automatically scans for `.gguf` models, supports Windows startup auto-run, and custom persistent settings (`config.json`).

---

## ⚙️ Tech
System Microphone input → Qwen3-ASR → paste the text

---

## 📁 File Structure
```text
VoiceKeyboard/
├── VoiceKeyboard.exe          # Main application executable
├── config.json                # Configuration file
├── CrispASR/
│   └── crispasr.exe           # CrispASR executable
└── models/
  └── Qwen3-ASR-0.6B-Q4_K_M.gguf  # Qwen3-ASR model file
```
---

## 🚀 Get Started
1,Download and Unzip
2,Run VoiceKeyboard.exe (EN for English UI ; ZH for Chinese UI)
3,Start Using:
-Press and hold the hotkey(default:alt+caps lock) to speak.
-Release hotkey , it will automatically convert your voice to text and paste it into the active cursor location.

---

## ⚙️ Context Menu & Settings
Right-click the system tray icon to change setting:

| Menu Option | Description | 
| :--- | :--- | 
| **Model** | show what model is using |
| **Hardware Acceleration** | Switch between `Vulkan (GPU)` or `CPU`| 
| **Recognition Language** | 30 languages (default is `Auto`) | 
| **Chinese Conversion** | Switch between Traditional /Simplified Chinese when the output is Chinese | 
| **Change Hotkey** | Custom trigger hotkey |
| **Start on Boot** | Toggle Windows auto-start on/off |

---

## 📜 License & Copyright

- **Third-Party Libraries**: Individual components (e.g., `CrispASR`, `opencc`, and respective dependencies) are governed by their original project licenses.
- **Project License**: Distributed under the **[MIT License](https://opensource.org/license/MIT)**.

Copyright © 2026 **kw4356**
