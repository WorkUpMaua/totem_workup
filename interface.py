import tkinter as tk
import threading
import time
import os
from typing import Optional

from presenter import Presenter
import serial

# ------------------ CONFIG UART ------------------
UART_PORT = os.getenv("UART_PORT", "/dev/serial0").strip()
UART_BAUD = int(os.getenv("UART_BAUD", "9600"))

class UARTManager:
    """
    Gerencia a comunicação UART síncrona (thread-safe) com o Raspberry Pi.
    Abre /dev/serial0 @ 9600 por padrão, similar ao exemplo simples.
    """
    def __init__(self, port: str = UART_PORT, baud: int = UART_BAUD):
        self._port = port
        self._baud = baud
        self._lock = threading.Lock()
        self._ser: Optional[serial.Serial] = None
        self._open_port()

    def _open_port(self):
        try:
            self._ser = serial.Serial(self._port, self._baud, timeout=1)
            time.sleep(2)
        except Exception:
            self._ser = None

    def _ensure_open(self):
        if self._ser is None or not self._ser.is_open:
            self._open_port()

    def send_text(self, text: str) -> bool:
        """
        Envia o texto como bytes (sem terminador). Ex.: 'a' → b'a'
        Retorna True/False conforme sucesso.
        """
        with self._lock:
            try:
                self._ensure_open()
                if self._ser is None:
                    return False
                data = text.encode("utf-8")
                self._ser.write(data)
                self._ser.flush()
                return True
            except Exception:
                return False

# ------------------ UI HELPERS ------------------
def show_toast(message: str, bg: str, duration_ms: int = 2000):
    """Exibe uma notificação flutuante por alguns segundos."""
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes('-topmost', True)

    lbl = tk.Label(
        toast,
        text=message,
        font=("Helvetica", 18, "bold"),
        bg=bg,
        fg="white",
        padx=24,
        pady=12
    )
    lbl.pack()

    def _place_toast():
        root.update_idletasks()
        toast.update_idletasks()
        x = root.winfo_rootx() + (root.winfo_width() - toast.winfo_reqwidth()) // 2
        y = root.winfo_rooty() + 30
        toast.geometry(f"+{x}+{y}")
    root.after(10, _place_toast)

    toast.after(duration_ms, toast.destroy)

def is_success_response(resp) -> bool:
    """
    Tenta inferir se a resposta da API foi sucesso.
    """
    try:
        status_code = getattr(resp, "status_code", None)
        if isinstance(status_code, int):
            return 200 <= status_code < 300

        if isinstance(resp, dict):
            if "ok" in resp: return bool(resp["ok"])
            if "success" in resp: return bool(resp["success"])
            if "status" in resp:
                status = str(resp["status"]).lower()
                return status in ("ok", "success", "opened", "open", "200")
            if "error" in resp or ("message" in resp and "erro" in str(resp["message"]).lower()):
                return False

        if isinstance(resp, str):
            s = resp.lower()
            if any(w in s for w in ("error", "erro", "invalid", "inválido", "denied", "forbidden")):
                return False
            if any(w in s for w in ("ok", "success", "opened", "open", "liberada", "liberado")):
                return True

        if isinstance(resp, bool):
            return resp

        return bool(resp)
    except Exception:
        return False

# ------------------ UI E LÓGICA ------------------
def adicionar_numero(n):
    senha_var.set(senha_var.get() + str(n))

def apagar():
    senha_var.set(senha_var.get()[:-1])

def _confirmar_thread(codigo: str):
    # 1) consulta API
    try:
        resp = Presenter.get_door_open_code(codigo)
        api_ok = is_success_response(resp)
    except Exception:
        resp = None
        api_ok = False

    # 2) se API ok, extrai doorSerial e envia via UART
    sent_ok = False
    door_serial_text = None
    if api_ok:
        try:
            # Esperado: doorSerial é "a"
            door_serial_text = resp.json()['doorSerial']
        except Exception:
            door_serial_text = None

        if isinstance(door_serial_text, str) and len(door_serial_text) > 0:
            # Envia exatamente como no exemplo simples: um único byte ('a' ou o que vier)
            sent_ok = uart.send_text(door_serial_text[0])
            # Se enviou com sucesso, aguarda 5s e envia 'f'
            if sent_ok:
                time.sleep(5)
                uart.send_text('f')
        else:
            sent_ok = False

    # 3) atualiza UI
    def _after_resp():
        senha_var.set("")
        if api_ok and sent_ok:
            show_toast("porta aberta", "#2e7d32")
        else:
            show_toast("código inválido", "#c62828")
        set_buttons_state("normal")

    root.after(0, _after_resp)

def set_buttons_state(state: str):
    for b in all_buttons:
        b.config(state=state)

def confirmar():
    codigo = senha_var.get().strip()
    if not codigo:
        show_toast("código inválido", "#c62828")
        return
    set_buttons_state("disabled")
    threading.Thread(target=_confirmar_thread, args=(codigo,), daemon=True).start()

# ------------------ APP TK ------------------
root = tk.Tk()
root.title("Teclado Numérico")
root.geometry("800x480")
root.resizable(True, True)
root.attributes('-fullscreen', True)

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

numeros = [1, 2, 3, 4, 5, 6, 7, 8, 9]
all_buttons = []

for index, numero in enumerate(numeros):
    row = (index // 3) + 1
    col = index % 3
    btn = tk.Button(
        root,
        text=str(numero),
        font=("Helvetica", 24),
        bg="#555555",
        fg="white",
        activebackground="#777777",
        command=lambda n=numero: adicionar_numero(n),
    )
    btn.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
    all_buttons.append(btn)

btn_apagar = tk.Button(
    root,
    text="Apagar",
    font=("Helvetica", 20),
    bg="#d9534f",
    fg="white",
    activebackground="#e57373",
    command=apagar,
)
btn_apagar.grid(row=4, column=0, sticky="nsew", padx=5, pady=5)
all_buttons.append(btn_apagar)

btn_0 = tk.Button(
    root,
    text="0",
    font=("Helvetica", 24),
    bg="#555555",
    fg="white",
    activebackground="#777777",
    command=lambda: adicionar_numero(0),
)
btn_0.grid(row=4, column=1, sticky="nsew", padx=5, pady=5)
all_buttons.append(btn_0)

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
all_buttons.append(btn_confirmar)

# ------------------ INICIAR UART ------------------
uart = UARTManager()

root.mainloop()
