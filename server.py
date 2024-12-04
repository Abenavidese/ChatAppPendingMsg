import socket
import threading

host = 'localhost'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen(2)  # Limitar el número de clientes a 2

clients = [None, None]
nicknames = ["", ""]
pending_messages = [[], []]  # Una lista para cada cliente

def handle(client, client_id):
    while True:
        try:
            message = client.recv(1024).decode('ascii').strip()
            if not message:
                raise ConnectionResetError
            full_message = f"{nicknames[client_id]}: {message}"
            send_message_to_other_client(full_message, client_id)
        except (ConnectionResetError, ConnectionAbortedError):
            print(f"{nicknames[client_id]} se ha desconectado.")
            disconnect_client(client_id)
            break

def send_message_to_other_client(message, sender_id):
    """Enviar mensaje al otro cliente o guardarlo si está desconectado."""
    receiver_id = 1 - sender_id  # Si sender_id es 0, receiver_id será 1, y viceversa
    try:
        if clients[receiver_id]:  # Verificar si el otro cliente está conectado
            clients[receiver_id].send((message + "\n").encode('ascii'))  # Agregar un salto de línea explícito
        else:
            pending_messages[receiver_id].append(message)  # Guardar mensaje si el cliente está desconectado
    except Exception as e:
        print(f"Error enviando mensaje al cliente {receiver_id + 1}: {e}")

def send_pending_messages(client, client_id):
    """Enviar mensajes pendientes al cliente cuando se reconecta."""
    for message in pending_messages[client_id]:
        client.send((message + "\n").encode('ascii'))  # Agregar un salto de línea explícito a cada mensaje
    pending_messages[client_id] = []  # Limpiar mensajes pendientes


def send_pending_messages(client, client_id):
    """Enviar mensajes pendientes al cliente cuando se reconecta."""
    for message in pending_messages[client_id]:
        client.send((message + "\n").encode('ascii'))  # Agregar salto de línea para cada mensaje
    pending_messages[client_id] = []  # Limpiar mensajes pendientes

def disconnect_client(client_id):
    """Desconectar al cliente y limpiar su información."""
    if clients[client_id]:
        clients[client_id].close()
        clients[client_id] = None
        nicknames[client_id] = ""
        print(f"Cliente {client_id + 1} desconectado.")

def receive():
    while True:
        for i in range(2):  # Revisión de los dos posibles clientes
            if clients[i] is None:  # Si hay un espacio libre para un cliente
                try:
                    client, address = server.accept()
                    print(f"Conexión establecida con {address}")

                    client.send("NICK\n".encode('ascii'))

                    nickname = client.recv(1024).decode('ascii')

                    nicknames[i] = nickname
                    clients[i] = client
                    print(f"Cliente {i + 1}: {nickname} conectado.")

                    # Enviar mensajes pendientes si existen
                    send_pending_messages(client, i)

                    # Iniciar hilo para manejar al cliente
                    thread = threading.Thread(target=handle, args=(client, i))
                    thread.start()
                except Exception as e:
                    print(f"Error aceptando cliente: {e}")
                    continue

print("Servidor está esperando conexiones...")
receive()
