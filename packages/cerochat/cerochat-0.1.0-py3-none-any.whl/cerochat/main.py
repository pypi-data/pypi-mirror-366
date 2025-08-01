def main():
    from cerochat.chat import Chat
    from cerochat.database import reserve_username
    
    print("Welcome to CeroChat - Terminal based chat application")
    print("Follow us on Telegram: https://t.me/cerochat")
    
    while True:
        username = input("Enter your username: ").strip()
        if not username:
            continue
            
        chat = Chat()
        try:
            chat.connect(username)
            break
        except SystemExit:
            continue

if __name__ == "__main__":
    main()