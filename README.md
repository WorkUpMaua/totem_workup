# Totem para Raspberry Pi - Projeto WorkUp

Este projeto é uma interface gráfica simples e funcional feita em Python com Tkinter que simula um teclado numérico, ideal para sistemas touchscreen, como o Raspberry Pi 3.

A ideia é simular o comportamento do totem de abertura da fechadura eletrônica, que utiliza a API de reservas do WorkUp para pegar o código de entrada da porta e abrir a fechadura se o código for válido.

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
3. Ative o ambiente virtual (Linux/MacOS)

      ```bash
   python -m venv venv
   source venv/bin/activate
   ```

4. Baixe as dependências (Linux/MacOS)

      ```bash
   pip install -r requirements.txt
   ```

5. Abra a aplicação

   ```bash
   python interface.py
   ```

---

## Captura de Tela

<img width="1439" height="899" alt="image" src="https://github.com/user-attachments/assets/b54e14a5-7725-4c2e-8951-2ab51df82795" />

## Vídeo Demonstrativo do projeto

[Clique aqui para ver](https://youtube.com/shorts/3AmJxlv6VCY?feature=share)


## 🤝 Integrantes

- [João Paulo Bonagurio Ramirez](https://github.com/yJony)           | 22.01247-8
- [Lucas Milani Thomsen Galhardo](https://github.com/LucasKiller)    | 22.00818-7  
- [Lucas Olivares Borges da Silva](https://github.com/lvcasolivares) | 22.00889-6
- [Luis Gustavo Gonçalves Machado](https://github.com/luisgmachado)  | 21.00322-0
- [Tiago Tadeu de Azevedo](https://github.com/tiagooazevedo)         | 22.00856-0
- [Victor Augusto de Gasperi](https://github.com/VictorGasperi)      | 22.00765-2 