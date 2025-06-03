import tkinter as tk
from tkinter import ttk, font
import threading, requests, json, sys
from datetime import datetime

# --- CONFIG ---
LM_ENDPOINT = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "deepseek-r1"
API_HEADERS = {"Content-Type": "application/json"}
SYSTEM_PROMPT = "You are DeepSeek-R1, a helpful AI assistant developed by DeepSeek. Respond helpfully and professionally in English."
chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

# --- Optimized Model Query ---
def query_model(user_input):
    chat_history.append({"role": "user", "content": user_input})
    payload = {
        "model": MODEL_NAME,
        "messages": chat_history,
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        response = requests.post(
            LM_ENDPOINT, 
            headers=API_HEADERS, 
            data=json.dumps(payload),
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        reply = data['choices'][0]['message']['content'].strip()
        
        if not reply:
            reply = "⚠️ Response generation failed. Please try again."
        
        chat_history.append({"role": "assistant", "content": reply})
        return reply
        
    except requests.exceptions.RequestException as e:
        return f"🚨 Network Error: {str(e)}"
    except (KeyError, json.JSONDecodeError):
        return "⚠️ Invalid response format from API"
    except Exception as e:
        return f"❌ Unexpected Error: {str(e)}"

# --- UI Utilities ---
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

def create_message_bubble(parent, text, is_user=False):
    canvas = tk.Canvas(parent, bg="#f0f0f0", bd=0, highlightthickness=0)
    
    # Colors based on speaker
    bubble_color = "#e6f7ff" if not is_user else "#f0f0f0"
    text_color = "#1f1f1f"
    
    # Create bubble with padding
    text_id = canvas.create_text(
        15, 15, 
        text=text, 
        anchor="nw", 
        fill=text_color,
        font=("Segoe UI", 12),
        width=380
    )
    
    # Get text dimensions
    bbox = canvas.bbox(text_id)
    text_width = bbox[2] - bbox[0] + 30
    text_height = bbox[3] - bbox[1] + 20
    
    # Create rounded rectangle
    bubble = create_rounded_rectangle(
        canvas, 
        5, 5, 
        text_width, text_height,
        radius=18,
        fill=bubble_color,
        outline="#ddd" if is_user else "#b3e0ff"
    )
    
    # Ensure text is above bubble
    canvas.tag_raise(text_id)
    
    # Configure canvas size
    canvas.configure(width=text_width+10, height=text_height+10)
    return canvas

# --- Thread-safe message handling ---
def respond(user_input):
    response = query_model(user_input)
    root.after(0, lambda: add_message("DeepSeek-R1", response, is_user=False))

def send_prompt(event=None):
    user_input = input_box.get("1.0", "end-1c").strip()
    if not user_input:
        return
    
    input_box.delete("1.0", tk.END)
    add_message("You", user_input, is_user=True)
    threading.Thread(target=respond, args=(user_input,), daemon=True).start()

# --- Enhanced UI Components ---
def add_message(sender, text, is_user=False):
    # Create container frame
    container = tk.Frame(chat_frame, bg="#f0f0f0")
    container.pack(fill="x", padx=10, pady=8)
    
    # Create header with timestamp
    header_frame = tk.Frame(container, bg="#f0f0f0")
    header_frame.pack(fill="x", side="right" if is_user else "left")
    
    timestamp = datetime.now().strftime("%H:%M")
    tk.Label(
        header_frame, 
        text=f"{sender} • {timestamp}", 
        font=("Segoe UI", 9), 
        fg="#666",
        bg="#f0f0f0"
    ).pack(side="right" if is_user else "left")
    
    # Create message bubble
    bubble_frame = tk.Frame(container, bg="#f0f0f0")
    bubble_frame.pack(fill="x", pady=4, side="right" if is_user else "left")
    
    bubble = create_message_bubble(bubble_frame, text, is_user)
    bubble.pack()
    
    # Auto-scroll to bottom
    chat_canvas.yview_moveto(1)

# --- Modern GUI Setup ---
root = tk.Tk()
root.title("CATR1.0.A.X [C] Team Flames 20XX [C]")
root.geometry("900x720")
root.configure(bg="#f0f0f0")

# Set application icon (replace with actual icon path)
try:
    root.iconbitmap("deepseek_icon.ico")
except:
    pass

# Configure styles
style = ttk.Style()
style.configure("TScrollbar", background="#e0e0e0")

# Create chat container
chat_container = tk.Frame(root, bg="#f0f0f0")
chat_container.pack(fill="both", expand=True, padx=10, pady=(10, 0))

# Chat canvas with scrollbar
chat_canvas = tk.Canvas(chat_container, bg="#f0f0f0", bd=0, highlightthickness=0)
chat_scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=chat_canvas.yview)

chat_frame = tk.Frame(chat_canvas, bg="#f0f0f0")
chat_frame.bind(
    "<Configure>", 
    lambda e: chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))
)

chat_canvas.create_window((0, 0), window=chat_frame, anchor="nw")
chat_canvas.configure(yscrollcommand=chat_scrollbar.set)

chat_canvas.pack(side="left", fill="both", expand=True)
chat_scrollbar.pack(side="right", fill="y")

# Input area
input_frame = tk.Frame(root, bg="#f0f0f0")
input_frame.pack(fill="x", padx=10, pady=10)

input_box = tk.Text(
    input_frame, 
    height=3, 
    font=("Segoe UI", 12), 
    bg="white", 
    wrap=tk.WORD,
    padx=12,
    pady=10,
    relief="flat",
    highlightbackground="#ddd",
    highlightthickness=1
)
input_box.pack(fill="x", pady=(0, 8), side="left", expand=True)
input_box.focus_set()

# Send button with modern style
send_btn = tk.Button(
    input_frame,
    text="➤",
    font=("Segoe UI", 12, "bold"),
    command=send_prompt,
    bg="#1890ff",
    fg="white",
    activebackground="#40a9ff",
    relief="flat",
    padx=15,
    cursor="hand2",
    bd=0
)
send_btn.pack(side="right", padx=(5, 0))

# Bind Enter key (without Shift)
input_box.bind("<Return>", lambda e: "break" if e.state == 0 else None)
input_box.bind("<Shift-Return>", lambda e: None)
root.bind("<Control-Return>", send_prompt)

# Status bar
status_bar = tk.Label(
    root, 
    text="DeepSeek-R1 • Ready • Model: deepseek-r1", 
    anchor="w",
    font=("Segoe UI", 9),
    fg="#666",
    bg="#eaeaea",
    padx=10
)
status_bar.pack(fill="x", side="bottom", ipady=3)

# Start-up sequence
def intro_message():
    greeting = "Hello! I'm DeepSeek-R1, an AI assistant developed by DeepSeek. How can I help you today?"
    chat_history.append({"role": "assistant", "content": greeting})
    add_message("DeepSeek-R1", greeting, is_user=False)

root.after(300, intro_message)
print("CATR1.0.A.X Engine LIVE - Ready for interaction")
root.mainloop()
