import socket
import threading
import json
from datetime import datetime

# 配置文件路径
ACCOUNTS_FILE = "accounts.json"
LOG_FILE = "server.log"
PORT = 2540


class BankServer:
    def __init__(self):
        self.accounts = self.load_accounts()
        self.lock = threading.Lock()

    def load_accounts(self):
        try:
            with open(ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_accounts(self):
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump(self.accounts, f)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")

    def handle_client(self, conn, addr):
        try:
            current_user = None
            while True:
                data = conn.recv(1024).decode().strip()
                if not data:
                    break

                parts = data.split()
                cmd = parts[0]

                if cmd == "HELO":
                    userid = parts[1]
                    if userid in self.accounts:
                        current_user = userid
                        conn.send(b"500 AUTH REQUIRE")
                        self.log(f"{addr} - {userid}: Authentication required")
                    else:
                        conn.send(b"401 ERROR!")

                elif cmd == "PASS":
                    password = parts[1]
                    if current_user and self.accounts[current_user]['password'] == password:
                        conn.send(b"525 OK!")
                        self.log(f"{addr} - {current_user}: Login success")
                    else:
                        conn.send(b"401 ERROR!")

                elif cmd == "BALA":
                    if current_user:
                        balance = self.accounts[current_user]['balance']
                        conn.send(f"AMNT:{balance}".encode())
                        self.log(f"{addr} - {current_user}: Balance checked")

                elif cmd == "WDRA":
                    amount = float(parts[1])
                    with self.lock:
                        if self.accounts[current_user]['balance'] >= amount:
                            self.accounts[current_user]['balance'] -= amount
                            self.save_accounts()
                            conn.send(b"525 OK!")
                            self.log(f"{addr} - {current_user}: Withdraw {amount} OK")
                        else:
                            conn.send(b"401 ERROR!")

                elif cmd == "BYE":
                    conn.send(b"BYE")
                    self.log(f"{addr} - {current_user}: Session ended")
                    break

        finally:
            conn.close()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', PORT))
            s.listen()
            print(f"Server listening on port {PORT}")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()


if __name__ == "__main__":
    server = BankServer()
    server.start()