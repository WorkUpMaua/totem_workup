# send_a_ble.py
# Envia a letra "a" para o HC-08 via BLE quando uma condição for satisfeita.
# Descobre e conecta automaticamente no módulo.

import asyncio
import os
import sys
import time
from typing import Optional

from bleak import BleakClient, BleakScanner, BleakError

# ---- CONFIGURAÇÕES ----
# Se você souber o MAC, defina aqui (formato "AA:BB:CC:DD:EE:FF") ou via env BLE_TARGET_MAC
TARGET_MAC = os.getenv("BLE_TARGET_MAC", "").strip()

# Se preferir descobrir pelo nome de anúncio, ajuste aqui (ou via env BLE_TARGET_NAME)
TARGET_NAME = os.getenv("BLE_TARGET_NAME", "HC-08").strip()

# UUID típico do serviço UART do HC-08 (característica de TX/RX)
UART_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

# Intervalo entre checagens da condição (segundos)
CHECK_INTERVAL = 0.2

# ---- SUA CONDIÇÃO AQUI ----
def condicao_atingida() -> bool:
    """
    Substitua por sua condição real.
    Ex.: checar uma variável global, um GPIO, uma fila, um arquivo etc.
    Neste exemplo, enviamos "a" uma única vez após 5 segundos de execução.
    """
    return (time.monotonic() - START_TIME) > 5.0  # exemplo: depois de 5s


START_TIME = time.monotonic()


async def descobrir_endereco() -> Optional[str]:
    """Descobre o endereço MAC do HC-08 pelo nome de anúncio."""
    print(f"[INFO] Procurando dispositivo BLE com nome '{TARGET_NAME}'...")
    devices = await BleakScanner.discover(timeout=8.0)
    for d in devices:
        # Alguns anúncios trazem 'HC-08' como nome ou no 'metadata'
        if (d.name and TARGET_NAME.lower() in d.name.lower()):
            print(f"[OK] Encontrado: {d.name} ({d.address})")
            return d.address
    print("[WARN] Nenhum dispositivo com esse nome foi encontrado.")
    return None


async def conectar(address: str) -> BleakClient:
    """Conecta e retorna um cliente BLE pronto para uso."""
    print(f"[INFO] Conectando a {address} ...")
    client = BleakClient(address, timeout=10.0)
    await client.connect()
    if not client.is_connected:
        raise BleakError("Falha ao conectar (client.is_connected = False)")
    print("[OK] Conectado!")
    return client


async def enviar_letra_a(client: BleakClient):
    """Envia a letra 'a' (ASCII 0x61) na característica UART."""
    try:
        await client.write_gatt_char(UART_CHAR_UUID, b"a", response=True)
        print("[OK] Enviado: 'a'")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar 'a': {e}")


async def garantir_conexao_e_loop():
    """Mantém conexão e envia 'a' quando a condição for atingida."""
    address = TARGET_MAC

    if not address:
        address = await descobrir_endereco()
        if not address:
            print("[ERRO] Não foi possível descobrir o HC-08. "
                  "Defina BLE_TARGET_MAC ou verifique se o módulo está anunciando.")
            sys.exit(1)

    # Para evitar enviar 'a' repetidas vezes, marque quando já enviou
    enviado = False

    while True:
        client: Optional[BleakClient] = None
        try:
            client = await conectar(address)

            # (Opcional) valida se a característica existe
            # services = await client.get_services()
            # if UART_CHAR_UUID not in [c.uuid for s in services for c in s.characteristics]:
            #     print("[WARN] Característica UART não encontrada; tentando mesmo assim...")

            while client.is_connected:
                if not enviado and condicao_atingida():
                    await enviar_letra_a(client)
                    enviado = True
                    # Se quiser encerrar após enviar, descomente:
                    # await client.disconnect()
                    # return
                await asyncio.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"[WARN] Conexão falhou/interrompida: {e}")
            await asyncio.sleep(2.0)  # espera e tenta reconectar
        finally:
            if client and client.is_connected:
                try:
                    await client.disconnect()
                except Exception:
                    pass
            # Loop continua para tentar reconectar caso necessário


def main():
    try:
        asyncio.run(garantir_conexao_e_loop())
    except KeyboardInterrupt:
        print("\n[INFO] Encerrado pelo usuário.")


if __name__ == "__main__":
    main()
