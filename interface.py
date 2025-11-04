import tkinter as tk
import time
from presenter import Presenter
import serial

# ------------------ UART ------------------
ser = serial.Serial("/dev/serial0", 9600, timeout=1)
time.sleep(0.2)  # pequena espera para estabilizar a porta

# ------------------ FUNÇÕES UI ------------------
def show_toast(message: str, bg: str, duration_ms: int = 2000):
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.configure(bg=bg)
    toast.attributes('-topmost', True)

    lbl = tk.Label(
        toast,
        text=message,
        font=("Helvetica", 18, "bold"),
        bg=bg,
        fg="white",
        padx=24,
        pady=12,
    )
    lbl.pack()

    root.update_idletasks()
    x = root.winfo_rootx() + (root.winfo_width() - toast.winfo_reqwidth()) // 2
    y = root.winfo_rooty() + 30
    toast.geometry(f"+{x}+{y}")

    toast.after(duration_ms, toast.destroy)


def confirmar():
    codigo = senha_var.get().strip()

    if not codigo:
        show_toast("código inválido", "#c62828")
        return

    btn_confirmar.config(state="disabled")

    # 1) Consulta API (simples e direto)
    try:
        resp = Presenter.get_door_open_code(codigo)
        data = resp.json()
        door_serial = data.get("doorSerial")
    except:
        door_serial = None

    # 2) Se falhou a API
    if not door_serial:
        show_toast("código inválido", "#c62828")
        btn_confirmar.config(state="normal")
        senha_var.set("")
        return

    # 3) Envia primeiro comando (ex.: "a")
    ser.write(door_serial[0].encode())
    ser.flush()

    show_toast("porta aberta", "#2e7d32")
    senha_var.set("")

    # 4) Após 5s enviar "f" sem travar UI
    def enviar_f():
        ser.write(b"f")
        ser.flush()
        btn_confirmar.config(state="normal")

    root.after(5000, enviar_f)


# ------------------ UI ------------------
root = tk.Tk()
root.title("Teclado Numérico")
root.attributes('-fullscreen', True)
root.configure(bg="#222222")

senha_var = tk.StringVar()

entrada_senha = tk.Entry(
    root,
    textvariable=senha_var,
    font=("Helvetica", 48),
    justify="center",
    bd=4,
    relief="ridge",
)
entrada_senha.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=10, pady=15)

root.rowconfigure(0, weight=2)
for i in range(1, 5):
    root.rowconfigure(i, weight=1)
for j in range(3):
    root.columnconfigure(j, weight=1)


def add_num(n):
    senha_var.set(senha_var.get() + str(n))


# Números 1 a 9
numeros = [1, 2, 3, 4, 5, 6, 7, 8, 9]
for index, numero in enumerate(numeros):
    row = (index // 3) + 1
    col = index % 3
    tk.Button(
        root,
        text=str(numero),
        font=("Helvetica", 24),
        bg="#555555",
        fg="white",
        activebackground="#777777",
        command=lambda n=numero: add_num(n),
    ).grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

# Botão Apagar
tk.Button(
    root,
    text="Apagar",
    font=("Helvetica", 20),
    bg="#d9534f",
    fg="white",
    activebackground="#e57373",
    command=lambda: senha_var.set(""),
).grid(row=4, column=0, sticky="nsew", padx=5, pady=5)

# Botão 0
tk.Button(
    root,
    text="0",
    font=("Helvetica", 24),
    bg="#555555",
    fg="white",
    activebackground="#777777",
    command=lambda: add_num(0),
).grid(row=4, column=1, sticky="nsew", padx=5, pady=5)

# Botão Confirmar
btn_confirmar = tk.Button(
    root,
    text="Confirmar",
    font=("Helvetica", 20),
    bg="#5cb85c",
    fg="white",
    activebackground="#81c784",
    command=confirmar,
)
btn_confirmar.grid(row=4, column=2, sticky="nsew", padx=5, pady=5)

root.mainloop()
