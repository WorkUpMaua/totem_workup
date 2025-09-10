# Totem em Tkinter para Raspberry Pi

Este projeto é uma interface gráfica simples e funcional feita em Python com Tkinter que simula um teclado numérico, ideal para sistemas touchscreen, como o Raspberry Pi 3.

---

## Funcionalidades

* Teclado numérico com botões de 0 a 9 dispostos em layout tradicional (3x4).
* Campo de senha que oculta os caracteres digitados (como um campo de senha real).
* Botão **Apagar** para remover o último dígito digitado.
* Botão **Confirmar** que imprime a senha digitada no console e limpa o campo.
* Layout responsivo e flexível que se adapta ao tamanho da janela.
* A janela inicia maximizada para melhor aproveitamento da tela.
* Botões com cores e fontes pensadas para uso em touchscreen, facilitando a interação.

---

## Tecnologias

* Python 3
* Tkinter (biblioteca padrão para interfaces gráficas no Python)

---

## Como usar

1. Certifique-se de ter o Python 3 instalado.
2. Clone este repositório:

   ```bash
   git clone https://github.com/WorkUpMaua/totem_workup.git
   ```
3. Execute o script:

   ```bash
   python interface.py
   ```
5. A interface abrirá maximizada. Use os botões para digitar a senha, apagar e confirmar.

---

## Personalizações

* Você pode modificar a função `confirmar()` para conectar a entrada de senha a um sistema de autenticação real.
* Ajuste cores, tamanhos de fontes e layout conforme sua necessidade.
* Ideal para rodar em Raspberry Pi com touchscreen, mas funciona em qualquer sistema com Python e Tkinter.

---

## Captura de Tela

<img width="1439" height="899" alt="image" src="https://github.com/user-attachments/assets/b54e14a5-7725-4c2e-8951-2ab51df82795" />

