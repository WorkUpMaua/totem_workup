import tkinter as tk
import threading
from presenter import Presenter

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
    Adapte conforme o que seu Presenter realmente retorna.
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
            if "error" in resp or "message" in resp and "erro" in str(resp["message"]).lower():
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

def adicionar_numero(n):
    senha_var.set(senha_var.get() + str(n))

def apagar():
    senha_var.set(senha_var.get()[:-1])

def _confirmar_thread(codigo: str):
    try:
        resp = Presenter.get_door_open_code(codigo)
        ok = is_success_response(resp)
    except Exception:
        ok = False

    def _after_resp():
        senha_var.set("")
        if ok:
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

root.mainloop()
