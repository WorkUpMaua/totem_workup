import tkinter as tk

def adicionar_numero(n):
    senha_var.set(senha_var.get() + str(n))

def apagar():
    senha_var.set(senha_var.get()[:-1])

def confirmar():
    print("Senha digitada:", senha_var.get())
    senha_var.set("")

root = tk.Tk()
root.title("Teclado Numérico")
root.geometry("800x480")
root.resizable(True, True)

root.attributes('-fullscreen', True)

# Aumentando o tamanho da fonte e o padding do Entry
senha_var = tk.StringVar()
entrada_senha = tk.Entry(
    root,
    textvariable=senha_var,
    font=("Helvetica", 48),    # Fonte maior para mais altura
    justify="center",
    bd=4,
    relief="ridge",
)
entrada_senha.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=10, pady=15)

# Configurando o peso da linha 0 para dar mais altura ao Entry
root.rowconfigure(0, weight=2)  # dobrando o peso da linha 0
for i in range(1, 5):
    root.rowconfigure(i, weight=1)
for j in range(3):
    root.columnconfigure(j, weight=1)

numeros = [1, 2, 3, 4, 5, 6, 7, 8, 9]

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
