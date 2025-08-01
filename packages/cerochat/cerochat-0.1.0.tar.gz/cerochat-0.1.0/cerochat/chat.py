import time
import threading
import sys
from datetime import datetime
from cerochat.database import insert_message, get_messages, delete_messages_by_username, get_last_message_id, reserve_username

class Chat:
    def __init__(self):
        self.username = None
        self.last_id = 0
        self.running = False
        self.message_lock = threading.Lock()
        self.new_message_event = threading.Event()
        self.has_sent_message = False

    def connect(self, username: str):
        if not reserve_username(username):
            print(f"Username '{username}' is already taken. Please choose another one.")
            sys.exit(1)
            
        self.username = username
        self.running = True
        self.last_id = get_last_message_id()
        
        with self.message_lock:
            print(f"Welcome to Cerochat, {username}. Follow us on Telegram: https://t.me/cerochat")
            self._print_input_prompt()
        
        threading.Thread(target=self.listen_messages, daemon=True).start()
        self.input_loop()

    def _print_input_prompt(self):
        prompt = f"[{self.username}]: " if self.has_sent_message else "Your message: "
        print(prompt, end="", flush=True)

    def listen_messages(self):
        while self.running:
            messages = get_messages(after_id=self.last_id)
            if messages:
                with self.message_lock:
                    print("\r", end="")
                    for msg in messages:
                        # Игнорируем служебные сообщения о подключении
                        if msg["message"] != "USER_JOINED_SIGNAL":
                            current_time = datetime.now().strftime("%H:%M")
                            print(f"{current_time} [{msg['username']}] {msg['message']}")
                    self.last_id = messages[-1]["id"]
                    self._print_input_prompt()

    def input_loop(self):
            try:
                while True:
                    msg = input()
                    if msg.strip():
                        current_time = datetime.now().strftime("%H:%M")
                        formatted_msg = f"{msg.strip()}"
                        insert_message(self.username, formatted_msg)
                        self.has_sent_message = True
                        with self.message_lock:
                            self._print_input_prompt()
            except KeyboardInterrupt:
                self.disconnect()

    def disconnect(self):
        print("\nDisconnecting...")
        self.running = False
        delete_messages_by_username(self.username)