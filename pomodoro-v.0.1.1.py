import tkinter as tk
import math
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image as PILImage, ImageDraw
import time

# ---------------------- НАСТРОЙКИ -----------------------
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 15

# ---------------------- ГЛОБАЛЬНЫЕ -----------------------
reps = 0
timer = None
current_theme = "light"
tray_icon = None
tray_updater_thread = None
remaining_seconds = 0
tray_running = True

# ---------------------- ТЕМЫ -----------------------------
themes = {
    "light": {
        "bg": "white",
        "fg": "black",
        "highlight": "green",
    },
    "dark": {
        "bg": "#1e1e1e",
        "fg": "white",
        "highlight": "#00ff88",
    }
}

# ---------------------- UI FUNCTIONS ---------------------
def apply_theme():
    theme = themes[current_theme]
    window.config(bg=theme["bg"])
    title_label.config(bg=theme["bg"], fg=theme["highlight"])
    timer_label.config(bg=theme["bg"], fg=theme["fg"])
    check_marks.config(bg=theme["bg"], fg=theme["highlight"])
    for btn in (start_button, reset_button, theme_button, hide_button):
        btn.config(bg=theme["bg"], fg=theme["fg"])

def toggle_theme():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    apply_theme()

def hide_to_tray():
    window.withdraw()
    start_tray_icon()

def show_window():
    window.deiconify()
    stop_tray_icon()

def quit_app():
    global tray_running
    tray_running = False
    stop_tray_icon()
    window.destroy()

# ---------------------- ТРЕЙ ----------------------------
def start_tray_icon():
    def create_icon():
        icon_img = PILImage.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(icon_img)
        draw.ellipse((16, 16, 48, 48), fill='red')
        return icon_img

    def update_tray_title():
        while tray_running:
            if tray_icon:
                mins = remaining_seconds // 60
                secs = remaining_seconds % 60
                tray_icon.title = f"Pomodoro — {mins:02d}:{secs:02d}"
            time.sleep(1)

    global tray_icon, tray_updater_thread
    tray_icon = pystray.Icon("Pomodoro", create_icon(), menu=pystray.Menu(
        item("Показать", show_window),
        item("Выход", quit_app)
    ))

    tray_updater_thread = threading.Thread(target=update_tray_title, daemon=True)
    tray_updater_thread.start()

    threading.Thread(target=tray_icon.run, daemon=True).start()

def stop_tray_icon():
    if tray_icon:
        tray_icon.stop()

# ---------------------- ТАЙМЕР ---------------------------
def start_timer():
    global reps
    reps += 1

    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60

    if reps % 8 == 0:
        count_down(long_break_sec)
        title_label.config(text="Длинный\nперерыв")
    elif reps % 2 == 0:
        count_down(short_break_sec)
        title_label.config(text="Короткий\nперерыв")
    else:
        count_down(work_sec)
        title_label.config(text="Работа!")

def count_down(count):
    global timer, remaining_seconds
    remaining_seconds = count
    mins = math.floor(count / 60)
    secs = count % 60
    timer_label.config(text=f"{mins:02d}:{secs:02d}")
    if count > 0:
        timer = window.after(1000, count_down, count - 1)
    else:
        start_timer()
        check_marks.config(text="✔" * (reps // 2))

def reset_timer():
    global reps, remaining_seconds
    if timer:
        window.after_cancel(timer)
    reps = 0
    remaining_seconds = 0
    title_label.config(text="Таймер")
    timer_label.config(text="00:00")
    check_marks.config(text="")

# ---------------------- UI SETUP ------------------------

window = tk.Tk()
window.title("Pomodoro by jTroi")
window.geometry("300x220")
window.attributes('-topmost', True)
window.resizable(True, True)

window.columnconfigure(0, weight=1)
window.rowconfigure([0, 1, 2, 3], weight=1)

title_label = tk.Label(window, text="Таймер", font=("Arial", 20, "bold"))
title_label.grid(row=0, column=0, sticky="n", pady=5)

timer_label = tk.Label(window, text="00:00", font=("Arial", 36, "bold"))
timer_label.grid(row=1, column=0, sticky="n")

check_marks = tk.Label(window, font=("Arial", 14))
check_marks.grid(row=2, column=0, sticky="n")

btn_frame = tk.Frame(window)
btn_frame.grid(row=3, column=0, pady=10, sticky="s")

start_button = tk.Button(btn_frame, text="Старт", command=start_timer, width=7)
start_button.grid(row=0, column=0, padx=5)

reset_button = tk.Button(btn_frame, text="Сброс", command=reset_timer, width=7)
reset_button.grid(row=0, column=1, padx=5)

theme_button = tk.Button(btn_frame, text="Тема", command=toggle_theme, width=7)
theme_button.grid(row=1, column=0, padx=5, pady=5)

hide_button = tk.Button(btn_frame, text="Скрыть", command=hide_to_tray, width=7)
hide_button.grid(row=1, column=1, padx=5, pady=5)

apply_theme()
window.protocol("WM_DELETE_WINDOW", quit_app)
window.mainloop()
