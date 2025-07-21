# 📄 Morse Code Learning & Fun App
# Features: Text ↔ Morse conversion, sound playback, challenges, fun facts, session export
# Author: [Your Name] | License: MIT

import csv
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import winsound, threading, random, string, json, time, os

# ====== Morse Code Mappings ======
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.', '0': '-----', ' ': '/'
}
REVERSE_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}
custom_space = '/'  # Custom separator for words

# ====== Fun Facts Loader ======
try:
    with open(os.path.join("docs", "fun_facts.txt"), encoding="utf-8") as f:
        fun_facts = [line.strip("✅ ").strip() for line in f if line.startswith("✅")]
except FileNotFoundError:
    fun_facts = ["🚨 Could not load fun facts. Please check docs/fun_facts.txt"]

# ====== Core Conversion Functions ======
def text_to_morse(text): 
    """Convert English text to Morse code"""
    return ' '.join(MORSE_CODE_DICT.get(c, '?').replace('/', custom_space) for c in text.upper())

def morse_to_text(morse):
    """Convert Morse code to English text"""
    words = morse.strip().split(custom_space)
    return ' '.join(''.join(REVERSE_DICT.get(letter, '?') for letter in word.strip().split()) for word in words)

# ====== Playback Functions ======
def threaded_play(morse):
    """Play Morse code sound & animation in separate thread"""
    draw_morse_pattern(morse)
    threading.Thread(
        target=play_with_visuals, 
        args=(morse, dot_var.get(), dash_var.get(), freq_var.get()), 
        daemon=True
    ).start()

def play_with_visuals(morse, dot_ms, dash_ms, freq):
    """Sound playback with visual feedback"""
    freq = max(37, min(freq, 32767))
    idx = 0
    for symbol in morse:
        if symbol in '.-':
            if idx < len(tag_list): canvas.itemconfig(tag_list[idx], fill="#4CAF50")
            winsound.Beep(freq, dot_ms if symbol == '.' else dash_ms)
            canvas.update(); idx += 1
        elif symbol == ' ': time.sleep(0.2)
        elif symbol == custom_space: time.sleep(0.6)

def draw_morse_pattern(morse):
    """Draw Morse pattern visually on canvas"""
    canvas.delete("all")
    x, tag_list[:] = 10, []
    for symbol in morse:
        if symbol == '.':
            tag_list.append(canvas.create_rectangle(x, 10, x+20, 40, fill="white"))
            x += 30
        elif symbol == '-':
            tag_list.append(canvas.create_rectangle(x, 10, x+50, 40, fill="white"))
            x += 60
        elif symbol == custom_space: x += 30
        elif symbol == ' ': x += 10

# ====== UI Event Handlers ======
def log_history(entry):
    """Append entry to history log"""
    history.config(state="normal")
    history.insert(tk.END, entry + "\n")
    history.config(state="disabled")

def convert_to_morse():
    """Handle Text→Morse conversion"""
    text = text_input.get("1.0", tk.END).strip()
    morse = text_to_morse(text)
    output_label.config(text=morse)
    log_history(f"Text→Morse: {morse}")
    if autoplay_var.get(): threaded_play(morse)

def convert_to_text():
    """Handle Morse→Text conversion"""
    morse = text_input.get("1.0", tk.END).strip()
    text = morse_to_text(morse)
    output_label.config(text=text)
    log_history(f"Morse→Text: {text}")

def auto_convert():
    """Auto-detect input and convert accordingly"""
    data = text_input.get("1.0", tk.END).strip()
    if all(c in ".-/ " for c in data):
        result = morse_to_text(data)
        log_history(f"Auto: Morse→Text: {result}")
    else:
        result = text_to_morse(data)
        log_history(f"Auto: Text→Morse: {result}")
        if autoplay_var.get(): threaded_play(result)
    output_label.config(text=result)

def on_text_change(event=None):
    """Trigger auto-convert on key press if enabled"""
    if autoconvert_var.get():
        auto_convert()

def copy_to_clipboard():
    """Copy output text to clipboard"""
    root.clipboard_clear()
    root.clipboard_append(output_label.cget("text"))
    messagebox.showinfo("Copied", "Output copied to clipboard!")

# ====== Session Saving ======
def save_output_with_ext(output, default_ext, filetypes):
    """General save dialog with format options"""
    fp = filedialog.asksaveasfilename(
        defaultextension=default_ext,
        filetypes=filetypes
    )
    if fp:
        with open(fp, 'w', encoding="utf-8") as f:
            f.write(output)
        messagebox.showinfo("Saved", f"Session saved to:\n{fp}")

def save_session():
    save_output_with_ext(
        history.get("1.0", tk.END), ".txt",
        [("Text files", "*.txt"), ("All files", "*.*")]
    )

def save_session_json():
    log_json = json.dumps(history.get("1.0", tk.END).strip().splitlines(), indent=2)
    save_output_with_ext(log_json, ".json", [("JSON files", "*.json"), ("All files", "*.*")])

def save_session_csv():
    log_text = history.get("1.0", tk.END).strip().splitlines()
    fp = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if fp:
        with open(fp, 'w', newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows([[line] for line in log_text])
        messagebox.showinfo("Saved", f"Session saved to:\n{fp}")

def save_session_md():
    log_text = history.get("1.0", tk.END).strip().splitlines()
    md = "\n".join(f"- {line}" for line in log_text)
    save_output_with_ext(md, ".md", [("Markdown files", "*.md"), ("All files", "*.*")])

def load_session():
    """Load a previous session log"""
    fp = filedialog.askopenfilename()
    if fp:
        session = open(fp, encoding="utf-8").read()
        history.config(state="normal")
        history.delete("1.0", tk.END)
        history.insert(tk.END, session)
        history.config(state="disabled")

# ====== Other Tools ======
def show_stats():
    """Show dot/dash count"""
    text = history.get("1.0", tk.END)
    messagebox.showinfo("Stats", f"Dots: {text.count('.')}\nDashes: {text.count('-')}")

def play_reverse():
    """Play Morse in reverse"""
    threaded_play(output_label.cget("text")[::-1])

def random_morse_challenge():
    """Start random challenge with countdown"""
    word = ''.join(random.choice(string.ascii_uppercase) for _ in range(3))
    morse = text_to_morse(word)
    log_history(f"Challenge: {morse}")
    output_label.config(text=morse)
    threaded_play(morse)

    def countdown():
        for i in range(challenge_timer_var.get(), 0, -1):
            output_label.config(text=f"{morse} | Answer in: {i}s")
            time.sleep(1)
        output_label.config(text=f"🎉 Answer: {word} 🎉")
        log_history(f"Answer: {word}")

    threading.Thread(target=countdown, daemon=True).start()

def customize_mapping():
    """Add custom Morse mappings"""
    global custom_space
    key = simpledialog.askstring("Mapping", "Character to map:")
    val = simpledialog.askstring("Mapping", "Morse code to map to:")
    if key and val:
        MORSE_CODE_DICT[key.upper()] = val
        REVERSE_DICT[val] = key.upper()

def set_speed(preset):
    """Set playback speed preset"""
    if preset == "Slow": dot_var.set(300); dash_var.set(900)
    elif preset == "Normal": dot_var.set(200); dash_var.set(600)
    elif preset == "Fast": dot_var.set(100); dash_var.set(300)

def toggle_theme():
    """Toggle light/dark theme"""
    if root["bg"] == "#212121":
        root.config(bg="#f5f5f5")
        output_label.config(bg="#fff", fg="#000")
        history.config(bg="#fff", fg="#000")
        canvas.config(bg="#eee")
    else:
        root.config(bg="#212121")
        output_label.config(bg="#424242", fg="#fff")
        history.config(bg="#424242", fg="#fff")
        canvas.config(bg="#616161")

def show_info_file(title, filename):
    """Display documentation file"""
    path = os.path.join("docs", filename)
    try:
        content = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        content = "🚨 Not found."

    win = tk.Toplevel(root)
    win.title(title)

    txt = tk.Text(win, wrap="word", font=("Consolas", 10))
    txt.insert(tk.END, content)
    txt.config(state="disabled")
    txt.pack(side="left", fill="both", expand=True)
    scrollbar = tk.Scrollbar(win, command=txt.yview)
    scrollbar.pack(side="right", fill="y")
    txt.config(yscrollcommand=scrollbar.set) 

def show_fun_fact():
    """Show a random fun fact"""
    messagebox.showinfo("Fun Fact", random.choice(fun_facts))

# ====== UI Setup ======
root = tk.Tk()
root.title("✨ Morse Mate")
root.configure(bg="#f5f5f5")
root.option_add("*Font", "Arial 10")

menu = tk.Menu(root)
file_menu = tk.Menu(menu, tearoff=0)
for label, cmd in [
    ("Save as Text", save_session), 
    ("Save as JSON", save_session_json), 
    ("Save as CSV", save_session_csv), 
    ("Save as Markdown", save_session_md), 
    ("Load Session", load_session)
]: file_menu.add_command(label=label, command=cmd)
menu.add_cascade(label="File", menu=file_menu)

tools_menu = tk.Menu(menu, tearoff=0)
for label, cmd in [
    ("Show Stats", show_stats), 
    ("Reverse Play", play_reverse), 
    ("Random Challenge", random_morse_challenge), 
    ("Customize Mapping", customize_mapping)
]: tools_menu.add_command(label=label, command=cmd)
menu.add_cascade(label="Tools", menu=tools_menu)

learn_menu = tk.Menu(menu, tearoff=0)
for name, file in [
    ("What is Morse Code?", "what_is_morse.txt"), 
    ("How to Use the App", "how_to_use.txt"),
    ("Feature Guide", "feature_guide.txt"), 
    ("Fun Facts", "fun_facts.txt"),
    ("Python Concepts", "python_concepts.txt")
]: learn_menu.add_command(label=name, command=lambda f=file,n=name: show_info_file(n,f))
menu.add_cascade(label="Learn", menu=learn_menu)

menu.add_command(label="Toggle Theme", command=toggle_theme)
root.config(menu=menu)

text_input = tk.Text(root, height=3, width=50)
text_input.pack(pady=5)
text_input.bind("<KeyRelease>", on_text_change)

output_label = tk.Label(root, text="Output will appear here", bg="#fff", fg="#000", wraplength=400)
output_label.pack(pady=5)

btn_frame = tk.Frame(root, bg="#f5f5f5")
btn_frame.pack(pady=5)
tk.Button(btn_frame, text="Text→Morse", command=convert_to_morse).grid(row=0, column=0, padx=3)
tk.Button(btn_frame, text="Morse→Text", command=convert_to_text).grid(row=0, column=1, padx=3)
tk.Button(btn_frame, text="Copy Output", command=copy_to_clipboard).grid(row=0, column=2, padx=3)
tk.Button(btn_frame, text="Show Fun Fact", command=show_fun_fact).grid(row=0, column=3, padx=3)

opt_frame = tk.Frame(root, bg="#f5f5f5")
opt_frame.pack(pady=5)
dot_var, dash_var, freq_var = tk.IntVar(value=200), tk.IntVar(value=600), tk.IntVar(value=750)
autoplay_var, autoconvert_var, challenge_timer_var = tk.BooleanVar(), tk.BooleanVar(), tk.IntVar(value=10)


tk.Checkbutton(opt_frame, text="Auto-play", variable=autoplay_var, bg="#f5f5f5").grid(row=0, column=0, padx=5)
tk.Checkbutton(opt_frame, text="Auto-convert", variable=autoconvert_var, bg="#f5f5f5").grid(row=0, column=1, padx=5)

tk.Label(opt_frame, text="Speed:").grid(row=0, column=2)
speed_combo = ttk.Combobox(opt_frame, values=["Slow", "Normal", "Fast"], width=7, state="readonly")
speed_combo.set("Normal")  # set default selection
speed_combo.grid(row=0, column=3); speed_combo.bind("<<ComboboxSelected>>", lambda e: set_speed(speed_combo.get()))

tk.Label(opt_frame, text="Challenge (s):").grid(row=1, column=0)
tk.Spinbox(opt_frame, from_=5, to=30, textvariable=challenge_timer_var, width=5).grid(row=1, column=1)


history = tk.Text(root, height=8, width=60, bg="#fff")
history.pack(pady=10)
canvas = tk.Canvas(root, width=500, height=50, bg="#eee")
canvas.pack(pady=5)
tag_list = []
root.mainloop()