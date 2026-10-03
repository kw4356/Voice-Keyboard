import ctypes
import json
import os
import subprocess
import sys
import tempfile
import time
import threading
import wave
import winreg
import keyboard
import numpy as np
import pyautogui
import pyperclip
import sounddevice as sd
import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as item
import tkinter as tk
from tkinter import simpledialog

# Try loading OpenCC module for Chinese conversion
try:
    from opencc import OpenCC
    OPENCC_AVAILABLE = True
except ImportError:
    OPENCC_AVAILABLE = False
    print("[Warning] opencc package not detected. Run 'pip install opencc-python-reimplemented' to enable Chinese conversion.")

# ==================== Core Settings ====================
APP_NAME = "Voice Keyboard"
CRISP_ASR_BIN = r".\CrispASR\crispasr.exe"
MODELS_DIR = r".\models"
CONFIG_FILE = r".\config.json"
SAMPLE_RATE = 16000
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

LANGUAGES = [
    ("AUTO", "auto"),
    ("Chinese", "zh"),
    ("Cantonese", "yue"),
    ("English", "en"),
    ("Arabic", "ar"),
    ("German", "de"),
    ("French", "fr"),
    ("Spanish", "es"),
    ("Portuguese", "pt"),
    ("Indonesian", "id"),
    ("Italian", "it"),
    ("Japanese", "ja"),
    ("Korean", "ko"),
    ("Russian", "ru"),
    ("Thai", "th"),
    ("Vietnamese", "vi"),
    ("Turkish", "tr"),
    ("Hindi", "hi"),
    ("Malay", "ms"),
    ("Dutch", "nl"),
    ("Swedish", "sv"),
    ("Danish", "da"),
    ("Finnish", "fi"),
    ("Polish", "pl"),
    ("Czech", "cs"),
    ("Filipino", "fil"),
    ("Persian", "fa"),
    ("Greek", "el"),
    ("Hungarian", "hu"),
    ("Macedonian", "mk"),
    ("Romanian", "ro"),
]

ZH_CONVERT_OPTIONS = [
    ("Original Output (No Conversion)", "off"),
    ("Traditional Chinese (s2t)", "s2t"),
    ("Simplified Chinese (t2s)", "t2s"),
]

DEFAULT_CONFIG = {
    "gpu_backend": "vulkan",
    "hotkey": "alt+v",
    "language": "auto",
    "zh_conversion": "s2t",
}

# OpenCC converter cache
OPENCC_CONVERTERS = {}
# =======================================================


def get_opencc_converter(config_name: str):
    """Get or cache OpenCC converter instance"""
    if not OPENCC_AVAILABLE or config_name == "off":
        return None
    if config_name not in OPENCC_CONVERTERS:
        try:
            OPENCC_CONVERTERS[config_name] = OpenCC(config_name)
        except Exception as e:
            print(f"[Error] Failed to initialize OpenCC ({config_name}): {e}")
            return None
    return OPENCC_CONVERTERS[config_name]


def convert_chinese(text: str, mode: str) -> str:
    """Perform Chinese Traditional/Simplified conversion"""
    if mode == "off" or not text:
        return text
    converter = get_opencc_converter(mode)
    if converter:
        return converter.convert(text)
    return text


def disable_cmd_quick_edit():
    """Disable Windows CMD QuickEdit Mode to prevent terminal clicks from freezing Python threads"""
    if sys.platform == "win32":
        try:
            kernel32 = ctypes.windll.kernel32
            hInput = kernel32.GetStdHandle(-10)  # STD_INPUT_HANDLE
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(hInput, ctypes.byref(mode)):
                new_mode = (mode.value & ~0x0040) | 0x0080
                kernel32.SetConsoleMode(hInput, new_mode)
        except Exception:
            pass


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                merged = DEFAULT_CONFIG.copy()
                merged.update(cfg)
                return merged
        except Exception as e:
            print(f"[Warning] Failed to read config file: {e}")
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        print("[System] Configuration updated and saved to config.json")
    except Exception as e:
        print(f"[Error] Failed to save config file: {e}")


def find_gguf_model(models_dir: str) -> str:
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith(".gguf"):
                full_path = os.path.join(models_dir, file)
                print(f"[Model Auto-Detect] Found GGUF model: {full_path}")
                return full_path
    print(f"[Warning] No .gguf files found in '{models_dir}' directory!")
    return os.path.join(models_dir, "model.gguf")


MODEL_PATH = find_gguf_model(MODELS_DIR)


def create_icon(color_code: str) -> Image.Image:
    image = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)

    # 1. Draw a rounded rectangle base (#0F172A dark background)
    dc.rounded_rectangle((1, 1, 30, 30), radius=6, fill="#0F172A", outline="#334155", width=1)

    # 2. Draw small sound waves on both sides
    dc.rounded_rectangle((5, 13, 7, 19), radius=1, fill="#475569")
    dc.rounded_rectangle((24, 13, 26, 19), radius=1, fill="#475569")

    # 3. Draw the microphone core head (status colors: green/red/orange)
    dc.rounded_rectangle((13, 7, 18, 17), radius=3, fill=color_code)

    # 4. Draw the microphone U-shaped metal ring and base
    dc.arc((10, 11, 21, 20), start=0, end=180, fill="#F8FAFC", width=2)
    dc.line((16, 20, 16, 24), fill="#F8FAFC", width=2)
    dc.line((12, 24, 20, 24), fill="#F8FAFC", width=2)

    return image


def is_autostart_enabled() -> bool:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ
        )
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False


def set_autostart(enable: bool):
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE
    )
    if enable:
        if getattr(sys, "frozen", False):
            cmd = f'"{sys.executable}"'
        else:
            cmd = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
    else:
        try:
            winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass
    winreg.CloseKey(key)


class VoiceKeyboardApp:

    def __init__(self):
        self.running = True
        self.is_recording = False
        self.recording_data = []
        self.icon = None
        self.config = load_config()

    def audio_callback(self, indata, frames, time_info, status):
        if self.is_recording:
            self.recording_data.append(indata.copy())

    def inject_text(self, text: str):
        orig = pyperclip.paste()
        pyperclip.copy(text)
        time.sleep(0.05)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.1)
        pyperclip.copy(orig)

    def process_asr(self):
        if not self.recording_data:
            print("[Diagnostics] No audio data captured")
            return

        audio_np = np.concatenate(self.recording_data, axis=0)
        max_amplitude = np.max(np.abs(audio_np))
        print(f"\n[Diagnostics] Peak audio amplitude: {max_amplitude} / 32767")

        if max_amplitude < 500:
            print("[Warning] Audio volume too low, please check microphone input!")

        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ) as temp_wav:
            wav_path = temp_wav.name

        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_np.tobytes())

        try:
            gpu_backend = self.config.get("gpu_backend", "vulkan")
            language = self.config.get("language", "auto")
            zh_conv_mode = self.config.get("zh_conversion", "s2t")

            print(
                f"[Progress] Running CrispASR (Backend: {gpu_backend.upper()}, Lang: {language}, Conv: {zh_conv_mode})..."
            )
            start_time = time.time()

            cmd = [
                CRISP_ASR_BIN,
                "-m",
                MODEL_PATH,
                "--backend",
                "qwen3",
                "--gpu-backend",
                gpu_backend,
                "-f",
                wav_path,
                "--no-timestamps",
                "-np",
            ]

            if language != "auto":
                cmd.extend(["-l", language])

            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=30,
                creationflags=creation_flags
            )

            elapsed = time.time() - start_time
            print(f"[Progress] Inference completed in {elapsed:.2f} seconds")

            recognized_text = result.stdout.strip()

            if recognized_text:
                final_text = convert_chinese(recognized_text, zh_conv_mode)
                print(f"[Recognition Success]: {final_text}")
                self.inject_text(final_text)
            else:
                stderr_msg = result.stderr.strip()
                print(f"[Voice Input] No valid text recognized (STDERR: {stderr_msg})")

        except subprocess.TimeoutExpired:
            print("[ERROR] CrispASR execution timed out (30s) and was terminated!")
        except Exception as e:
            print(f"[ERROR] CrispASR execution exception: {e}")
        finally:
            if os.path.exists(wav_path):
                os.remove(wav_path)

    def run_hotkey_loop(self):
        while self.running:
            current_hotkey = self.config.get("hotkey", "alt+v")
            try:
                if keyboard.is_pressed(current_hotkey):
                    self.is_recording = True
                    self.recording_data = []
                    if self.icon:
                        self.icon.icon = create_icon("#E63232")

                    stream = sd.InputStream(
                        samplerate=SAMPLE_RATE,
                        channels=1,
                        dtype="int16",
                        callback=self.audio_callback,
                    )
                    stream.start()

                    while keyboard.is_pressed(current_hotkey) and self.running:
                        time.sleep(0.02)

                    self.is_recording = False
                    stream.stop()
                    stream.close()

                    if self.icon:
                        self.icon.icon = create_icon("#F0A014")

                    self.process_asr()

                    if self.icon:
                        self.icon.icon = create_icon("#28B450")
            except Exception as e:
                print(f"[Hotkey Error] Current hotkey '{current_hotkey}' is invalid: {e}")
                time.sleep(1)
            time.sleep(0.05)


def update_tooltip(icon, app):
    model_name = os.path.basename(MODEL_PATH)
    hk = app.config.get("hotkey", "alt+v").upper()
    lang = app.config.get("language", "auto")
    backend = app.config.get("gpu_backend", "vulkan").upper()
    zh_mode = app.config.get("zh_conversion", "s2t")
    icon.tooltip = f"{APP_NAME}\nModel: {model_name}\nBackend: {backend} | Lang: {lang} | Conv: {zh_mode}\nHold [{hk}] to speak"


def change_backend(app, backend_type):

    def handler(icon, item):
        def _task():
            app.config["gpu_backend"] = backend_type
            save_config(app.config)
            update_tooltip(icon, app)

        threading.Thread(target=_task, daemon=True).start()

    return handler


def change_language(app, lang_code):

    def handler(icon, item):
        def _task():
            app.config["language"] = lang_code
            save_config(app.config)
            update_tooltip(icon, app)

        threading.Thread(target=_task, daemon=True).start()

    return handler


def change_zh_conversion(app, mode):

    def handler(icon, item):
        def _task():
            app.config["zh_conversion"] = mode
            save_config(app.config)
            update_tooltip(icon, app)

        threading.Thread(target=_task, daemon=True).start()

    return handler


def change_hotkey_thread(icon, app):

    def _gui():
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        current_hk = app.config.get("hotkey", "alt+v")
        new_hk = simpledialog.askstring(
            "Custom Hotkey Settings",
            "Enter hotkey combination (e.g., alt+v, caps lock, f2, ctrl+shift+v):",
            initialvalue=current_hk,
            parent=root,
        )
        root.destroy()

        if new_hk and new_hk.strip():
            clean_hk = new_hk.strip().lower()
            try:
                keyboard.is_pressed(clean_hk)
                app.config["hotkey"] = clean_hk
                save_config(app.config)
                update_tooltip(icon, app)
                print(f"[System] Hotkey successfully changed to: {clean_hk}")
            except Exception as e:
                print(f"[Error] Invalid hotkey combination '{clean_hk}': {e}")

    threading.Thread(target=_gui, daemon=True).start()


def main():
    disable_cmd_quick_edit()

    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model file not found: {MODEL_PATH}")

    app = VoiceKeyboardApp()

    def on_quit(icon, item):
        app.running = False
        icon.stop()

    def toggle_autostart(icon, item):
        new_state = not is_autostart_enabled()
        set_autostart(new_state)

    model_name = os.path.basename(MODEL_PATH)

    # 1. Hardware acceleration menu
    backend_menu = pystray.Menu(
        item(
            "Vulkan (GPU)",
            change_backend(app, "vulkan"),
            checked=lambda item: app.config.get("gpu_backend") == "vulkan",
            radio=True,
        ),
        item(
            "CPU",
            change_backend(app, "cpu"),
            checked=lambda item: app.config.get("gpu_backend") == "cpu",
            radio=True,
        ),
    )

    # 2. Recognition language menu
    lang_items = []
    for label, code in LANGUAGES:
        lang_items.append(
            item(
                f"{label} ({code})",
                change_language(app, code),
                checked=lambda item, c=code: app.config.get("language") == c,
                radio=True,
            )
        )
    lang_menu = pystray.Menu(*lang_items)

    # 3. Chinese conversion menu
    zh_conv_items = []
    for label, mode in ZH_CONVERT_OPTIONS:
        zh_conv_items.append(
            item(
                label,
                change_zh_conversion(app, mode),
                checked=lambda item, m=mode: app.config.get("zh_conversion")
                == m,
                radio=True,
            )
        )
    zh_conv_menu = pystray.Menu(*zh_conv_items)

    # 4. Main tray menu
    menu = pystray.Menu(
        item(f"Model: {model_name}", lambda item: None, enabled=False),
        pystray.Menu.SEPARATOR,
        item("Hardware Acceleration", backend_menu),
        item("Recognition Language", lang_menu),
        item("Chinese Trad/Simp Conversion", zh_conv_menu),
        item(
            lambda item: f"Change Hotkey (Current: {app.config.get('hotkey', 'alt+v').upper()})",
            lambda icon, item: change_hotkey_thread(icon, app),
        ),
        pystray.Menu.SEPARATOR,
        item(
            "Start on Boot",
            toggle_autostart,
            checked=lambda item: is_autostart_enabled(),
        ),
        pystray.Menu.SEPARATOR,
        item("Exit Voice Keyboard", on_quit),
    )

    icon = pystray.Icon("VoiceKeyboard", create_icon("#28B450"), "", menu)
    app.icon = icon
    update_tooltip(icon, app)

    threading.Thread(target=app.run_hotkey_loop, daemon=True).start()

    print(f"=== Voice Keyboard Started Successfully ===")
    print(f"Model: {model_name}")
    print(f"Compute Device: {app.config.get('gpu_backend').upper()}")
    print(f"Language: {app.config.get('language')}")
    print(f"Chinese Conv: {app.config.get('zh_conversion')}")
    print(
        f"Hotkey: [{app.config.get('hotkey').upper()}] (Hold to speak, release to paste)\n"
    )

    icon.run()


if __name__ == "__main__":
    main()