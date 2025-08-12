import sys
import time
import tkinter as tk
import os
import winsound
import threading
from tkinter import messagebox
from typing import List

# ==========================
# Configurazione iniziale
# ==========================
PLAYER_NAMES = ["Rosso", "Blu", "Verde", "Giallo"]
PLAYER_COLORS = ["#ff3b30", "#007aff", "#34c759", "#ffcc00"]
PLAYER_SOUNDS = [
    "buzzer_rosso.wav",
    "buzzer_blu.wav",
    "buzzer_verde.wav",
    "buzzer_giallo.wav",
]

POLL_MS = 5
MAX_READS_PER_TICK = 16
DEBUG_PRINT = False

# ==========================
# Import HID
# ==========================
try:
    import hid  # pip install hidapi
except ModuleNotFoundError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Dipendenza mancante",
        "Modulo 'hid' non trovato.\n\nInstalla hidapi eseguendo:\n"
        "py -m pip install --upgrade pip\n"
        "py -m pip install hidapi"
    )
    sys.exit(1)

# ==========================
# HID helpers
# ==========================
def find_buzz_device():
    for d in hid.enumerate():
        prod = (d.get('product_string') or '').lower()
        manu = (d.get('manufacturer_string') or '').lower()
        if 'buzz' in prod or 'buzz' in manu:
            return d
    return None

def open_buzz():
    info = find_buzz_device()
    if not info:
        return None
    dev = hid.device()
    dev.open(info['vendor_id'], info['product_id'], info.get('serial_number') or None)
    dev.set_nonblocking(True)
    return dev

# ==========================
# Audio
# ==========================
def play_sound_for(idx: int):
    def play():
        path = os.path.abspath(PLAYER_SOUNDS[idx]) if 0 <= idx < len(PLAYER_SOUNDS) else None
        if path and os.path.exists(path):
            winsound.PlaySound(path, winsound.SND_FILENAME)
        else:
            try:
                freq = 1000 + idx * 150
                winsound.Beep(freq, 1000)
            except Exception:
                winsound.MessageBeep(winsound.MB_OK)
    threading.Thread(target=play, daemon=True).start()

# ==========================
# Decodifica pulsanti
# ==========================
def get_pressed_players(report: bytes) -> List[int]:
    if len(report) < 4:
        return []
    mapping = [
        (2, 0x01, 0),  # Rosso
        (2, 0x20, 1),  # Blu
        (3, 0x80, 2),  # Verde
        (3, 0x04, 3),  # Giallo
    ]
    return [idx for byte_idx, mask, idx in mapping if report[byte_idx] & mask]

# ==========================
# Stato round
# ==========================
class RoundState:
    def __init__(self):
        self.active = False
        self.winner_index = None

    def start(self):
        self.active = True
        self.winner_index = None

    def lockout(self, idx: int):
        self.active = False
        self.winner_index = idx

    def reset(self):
        self.active = False
        self.winner_index = None

# ==========================
# App principale
# ==========================
class BuzzApp:
    def __init__(self):
        self.dev = open_buzz()
        self.round = RoundState()

        self.root = tk.Tk()
        self.root.title("Buzz! - Primo istantaneo")
        self.root.configure(bg="black")
        self.root.geometry("1000x480")

        self.label = tk.Label(self.root, text="Premi SPAZIO per iniziare il round",
                              fg="white", bg="black", font=("Segoe UI", 56, "bold"))
        self.label.pack(expand=True, fill="both")

        self.info = tk.Label(self.root,
                             text="Spazio/Invio: Inizia • F11: Schermo intero • ESC: Esci",
                             fg="#cccccc", bg="black", font=("Segoe UI", 16))
        self.info.pack()

        self.config_btn = tk.Button(self.root, text="🎛 Imposta nomi",
                                    command=self.open_name_config,
                                    font=("Segoe UI", 12),
                                    bg="#333", fg="#ffffff")
        self.config_btn.pack(pady=(5, 10))

        self.fullscreen = False

        self.root.bind("<Escape>", self.on_exit)
        self.root.bind("<F11>", self.on_toggle_fullscreen)
        self.root.bind("<space>", self.on_start_round)
        self.root.bind("<Return>", self.on_start_round)
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

        if not self.dev:
            self.show_error("Controller Buzz! non trovato.\nCollegalo e riavvia il programma.")
        else:
            self.update_status("Premi SPAZIO per iniziare il round", "white", "black")
            self.poll()

    # --------------------------
    # UI helpers
    def update_status(self, text: str, fg: str, bg: str):
        self.label.config(text=text, fg=fg, bg=bg)
        self.root.config(bg=bg)
        self.info.config(bg=bg)
        self.config_btn.config(bg=bg)

    def show_error(self, msg: str):
        self.update_status(msg, "#ff3b30", "black")

    # --------------------------
    # GUI per modifica nomi
    def open_name_config(self):
        win = tk.Toplevel(self.root)
        win.title("Imposta nomi giocatori")
        win.configure(bg="black")
        win.geometry("400x300")
        entries = []

        for i, name in enumerate(PLAYER_NAMES):
            lbl = tk.Label(win, text=f"Giocatore {i+1}:", fg="white", bg="black", font=("Segoe UI", 14))
            lbl.pack(pady=(15,0))
            entry = tk.Entry(win, font=("Segoe UI", 14), justify="center")
            entry.insert(0, name)
            entry.pack(pady=5)
            entries.append(entry)

        def save():
            for i, entry in enumerate(entries):
                PLAYER_NAMES[i] = entry.get()
            win.destroy()
            self.update_status("Premi SPAZIO per iniziare il round", "white", "black")

        btn = tk.Button(win, text="💾 Salva", command=save, font=("Segoe UI", 12), bg="#007aff", fg="white")
        btn.pack(pady=20)

    # --------------------------
    # Loop HID
    def poll(self):
        if self.dev:
            try:
                for _ in range(MAX_READS_PER_TICK):
                    data = self.dev.read(32)
                    if not data:
                        break
                    report = bytes(data)
                    if DEBUG_PRINT:
                        print("HID:", report)
                    if not self.round.active or self.round.winner_index is not None:
                        continue
                    pressed = get_pressed_players(report)
                    if not pressed:
                        continue
                    idx = pressed[0]
                    self.declare_winner(idx)
                    self.round.lockout(idx)
                    break
            except Exception as e:
                self.show_error(f"Errore HID: {e}")
        self.root.after(POLL_MS, self.poll)

    def declare_winner(self, idx: int):
        name = PLAYER_NAMES[idx] if idx < len(PLAYER_NAMES) else f"Giocatore {idx+1}"
        color = PLAYER_COLORS[idx] if idx < len(PLAYER_COLORS) else "white"
        self.update_status(f"🏆 Vince: {name}", "black", color)
        play_sound_for(idx)

    def on_start_round(self, event=None):
        self.round.start()
        self.update_status("⏳ Round attivo... premi per rispondere!", "white", "black")

    def on_toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def on_exit(self, event=None):
        try:
            if self.dev:
                self.dev.close()
        except Exception:
            pass
        self.root.destroy()
        sys.exit(0)

# ==========================
# Main
# ==========================
def main():
    app = BuzzApp()
    app.root.mainloop()

if __name__ == "__main__":
    main()
