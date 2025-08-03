import socket
import threading
import atexit

_running = True  # must be defined at module scope

def is_port_in_use(host="127.0.0.1", port=5678):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        try:
            s.connect((host, port))
            return True
        except (ConnectionRefusedError, OSError):
            return False

def start_log_server(host="127.0.0.1", port=5678):
    global _running

    # 1) If the port is busy, warn and skip
    if is_port_in_use(host, port):
        print(f"⚠️ Fusion log port {host}:{port} is already in use. Skipping log server startup.")
        return

    # 2) Create and bind the socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    #print(f"  Fusion Log Server started at {host}:{port}")

    # 3) Per‑connection handler
    def handle_client(conn):
        with conn:
            while _running:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print(data.decode("utf-8").rstrip())
                except OSError:
                    break

    # 4) Connection‑accept loop
    def accept_loop():
        while _running:
            try:
                conn, _ = server_socket.accept()
            except OSError:
                break  # socket closed
            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

    threading.Thread(target=accept_loop, daemon=True).start()

    # 5) Clean‑up on normal or Ctrl+C exit
    def shutdown():
        nonlocal server_socket  # if Python 3.8+, otherwise use global
        _running = False
        try:
            server_socket.close()
        except OSError:
            pass

    atexit.register(shutdown)
