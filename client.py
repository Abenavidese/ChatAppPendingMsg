import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext
import time

host = 'localhost'
port = 55555

client = None
connected = False
nickname = None

def connect_to_server():
    """Intentar conectar al servidor con reintentos."""
    global client, connected
    while not connected:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, port))
            connected = True
            chat_box_insert("Conectado al servidor.")
            client.send(nickname.encode('ascii'))  # Enviar el nickname al servidor
            threading.Thread(target=receive_messages, daemon=True).start()
        except Exception as e:
            connected = False
            chat_box_insert("Servidor desconectado. Reintentando en 5 segundos...")
            time.sleep(5)

def receive_messages():
    """Recibir mensajes del servidor y manejar desconexiones."""
    global connected
    buffer = ""  # Buffer para manejar mensajes parciales
    while connected:
        try:
            data = client.recv(1024).decode('ascii')
            if not data:
                raise ConnectionResetError
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                chat_box_insert(line.strip())
        except Exception:
            connected = False
            chat_box_insert("Conexión perdida con el servidor. Reintentando...")
            connect_to_server()  # Llamar a la función de reconexión
            break

def chat_box_insert(message):
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, f"{message}\n\n")  # Espacio adicional entre mensajes
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)

def send_message(event=None):
    """Enviar mensaje al servidor."""
    global connected
    message = message_entry.get().strip()
    if not message:
        # Evitar enviar mensajes vacíos
        return
    if connected:
        try:
            chat_box_insert(f"Tú: {message}")  # Mostrar mensaje localmente
            client.send(message.encode('ascii'))
            message_entry.delete(0, tk.END)
        except Exception:
            chat_box_insert("No se pudo enviar el mensaje.")
    else:
        chat_box_insert("No estás conectado al servidor.")

def disconnect():
    """Desconectar del servidor."""
    global connected
    if connected:
        try:
            client.close()
        except Exception:
            pass
    connected = False
    chat_box_insert("Desconectado del servidor.")
    root.quit()

def ask_nickname():
    """Solicitar apodo del usuario."""
    return simpledialog.askstring("Nickname", "Elige un apodo:") or "Anónimo"

root = tk.Tk()
root.title("Chat Cliente")
root.geometry("500x500")
root.configure(bg="#2C3E50")

nickname = ask_nickname()

chat_box_label = tk.Label(root, text=f"Apodo: {nickname}", bg="#2C3E50", fg="#ECF0F1")
chat_box_label.pack(pady=10)

chat_box = scrolledtext.ScrolledText(root, width=50, height=20, state='disabled', bg="#34495E", fg="#ECF0F1")
chat_box.pack(pady=10)

message_entry = tk.Entry(root, width=40, bg="#ECF0F1", font=("Arial", 10))
message_entry.pack(side=tk.LEFT, padx=(20, 10), pady=10)
message_entry.bind("<Return>", send_message)

send_button = tk.Button(root, text="Enviar", command=send_message, bg="#3498DB", fg="#ECF0F1")
send_button.pack(side=tk.LEFT, padx=(0, 10), pady=10)

disconnect_button = tk.Button(root, text="Desconectar", command=disconnect, bg="#E74C3C", fg="#ECF0F1")
disconnect_button.pack(side=tk.LEFT, padx=(10, 20), pady=10)

connect_to_server()

root.mainloop()