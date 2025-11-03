import tkinter as tk
import threading
import asyncio
import time
import os
from typing import Optional

from presenter import Presenter
from bleak import BleakClient, BleakScanner, BleakError

# ------------------ CONFIG BLE ------------------
TARGET_NAME = os.getenv("BLE_TARGET_NAME", "HC-08").strip()
UART_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"  # característica UART do HC-08
CONNECT_TIMEOUT = 10.0
RECONNECT_DELAY = 2.0

class BLEManager:
    """
    Gerencia a conexão BLE ao HC-08 em um loop asyncio separado.
    Use ble.send_text("...") para enviar dados. Ele conecta automaticamente.
    """
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._client: Optional[BleakClient] = None
        self._address: Optional[str] = None
        self._connected = False
        self._lock = threading.Lock()
        self._thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _call_soon_threadsafe(self, coro):
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return fut

    async def _discover_address(self) -> Optional[str]:
        # Descobre pelo nome de anúncio (HC-08)
        devices = await BleakScanner.discover(timeout=8.0)
        for d in devices:
            if d.name and TARGET_NAME.lower() in d.name.lower():
                return d.address
        return None

    async def _ensure_connected(self) -> bool:
        if self._client and self._client.is_connected:
            self._connected = True
            return True

        # Descobrir endereço, se necessário
        if not self._address:
            self._address = await self._discover_address()
            if not self._address:
                return False

        # Tentar conectar
        try:
            client = BleakClient("C4:BE:84:ED:F3:A5", timeout=CONNECT_TIMEOUT)
            await client.connect()
            if client.is_connected:
                self._client = client
                self._connected = True
                return True
            return False
        except Exception:
            self._connected = False
            return False

    async def _send_text_async(self, text: str) -> bool:
        ok = await self._ensure_connected()
        if not ok:
            return False

        # Tenta escrever; se falhar, tenta reconectar 1x
        data = text.encode("utf-8")
        try:
            # Linux costuma aceitar response=True
            await self._client.write_gatt_char(UART_CHAR_UUID, data, response=True)
            return True
        except Exception:
            # Tentativa de reconectar e enviar novamente
            try:
                if self._client and self._client.is_connected:
                    try:
                        await self._client.disconnect()
                    except Exception:
                        pass
                self._client = None
                self._connected = False
                await asyncio.sleep(RECONNECT_DELAY)
                if await self._ensure_connected():
                    await self._client.write_gatt_char(UART_CHAR_UUID, data, response=True)
                    return True
            except Exception:
                return False
        return False

    def send_text(self, text: str, timeout: float = 12.0) -> bool:
        """
        Chamada thread-safe: envia texto pela UART BLE.
        Retorna True/False conforme sucesso.
        """
        with self._lock:
            fut = self._call_soon_threadsafe(self._send_text_async(text))
            try:
                return fut.result(timeout=timeout)
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
    Adapte conforme o retorno real do Presenter.
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

    # 2) se API ok, extrai doorSerial e envia via BLE
    sent_ok = False
    door_serial_text = None
    if api_ok:
        door_serial_text = resp.json()['doorSerial']
        if isinstance(door_serial_text, str) and len(door_serial_text) > 0:
            # Envia via BLE
            print(door_serial_text)
            sent_ok = ble.send_text(door_serial_text)
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

# ------------------ INICIAR BLE ------------------
ble = BLEManager()

root.mainloop()
