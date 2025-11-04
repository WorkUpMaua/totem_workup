import tkinter as tk
import time
import os
from presenter import Presenter
import serial

# UART configuração básica
UART_PORT = os.getenv("UART_PORT", "/dev/serial0")
UART_BAUD = 9600

# Abre UART uma vez
ser = serial.Serial(UART_PORT, UART_BAUD, timeout=1)
time.sleep(0.2)

def show_toast(message, bg):
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.configure(bg=bg)
    toast.attributes('-topmost', True)

    label = tk.Label(toast, text=message, bg=bg, fg="white", font=("Helvetica", 18, "bold"), padx=20, pady=10)
    label.pack()

    root.update_idletasks()
    x = root.winfo_x() + (root.winfo_width()//2) - (toast.winfo_reqwidth()//2)
    y = root.winfo_y() + 30
    toast.geometry(f"+{x}+{y}")

    toast.after(2000, toast.destroy)

def confirmar_codigo():
    codigo = senha_var.get().strip()
    if not codigo:
        show_toast("Código inválido", "#c62828")
        return

    # 1) Chama API (bloqueia a UI — versão simples!)
    resp = Presenter.get_door_open_code(codigo)

    try:
        door_serial = resp.json().get("doorSerial")
    except:
        door_serial = None

    # 2) Se OK → envia caractere pela UART
    if door_serial and isinstance(door_serial, str) and len(door_serial) > 0:
        ser.write(door_serial[0].encode())
        ser.flush()

        show_toast("Porta aberta", "#2e7d32")

        # Espera 5 segundos (UI congela — simples!)
        time.sleep(5)

        ser.write(b'f')
        ser.flush()
    else:
        show_toast("Código inválido", "#c62828")

    senha_var.set("")

# ---------------- UI Simples ----------------
root = tk.Tk()
root.title("Teclado")
root.geometry("400x500")
root.configure(bg="#222222")

senha_var = tk.StringVar()

entry = tk.Entry(root, textvariable=senha_var, font=("Helvetica", 32), justify="center")
entry.pack(pady=20, fill="x", padx=20)

frame = tk.Frame(root, bg="#222222")
frame.pack()

def add_num(n):
    senha_var.set(senha_var.get() + str(n))

for num in range(1, 10):
    btn = tk.Button(frame, text=str(num), font=("Helvetica", 24),
                    width=4, height=2, command=lambda n=num: add_num(n))
    btn.grid(row=(num-1)//3, column=(num-1)%3, padx=5, pady=5)

btn_zero = tk.Button(frame, text="0", font=("Helvetica", 24),
                     width=4, height=2, command=lambda: add_num(0))
btn_zero.grid(row=3, column=1, padx=5, pady=5)

btn_conf = tk.Button(root, text="Confirmar", font=("Helvetica", 24), bg="#4caf50", fg="white",
                     command=confirmar_codigo)
btn_conf.pack(pady=20, ipadx=20, ipady=10)

btn_clear = tk.Button(root, text="Apagar", font=("Helvetica", 18), bg="#d9534f", fg="white",
                      command=lambda: senha_var.set(""))
btn_clear.pack(ipadx=10, ipady=5)

root.mainloop()
