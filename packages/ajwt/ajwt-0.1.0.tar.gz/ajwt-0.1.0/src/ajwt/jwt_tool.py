import base64


def main():
    while True:
        try:
            token = input("Enter a JWT Token: ")
            message, signature = token.rsplit(".", 1)
            header, payload = message.split(".")
            header = header + "=" * (-len(header) % 4)
            header = base64.urlsafe_b64decode(header).decode()
            payload = payload + "=" * (-len(payload) % 4)
            payload = base64.urlsafe_b64decode(payload).decode()
            print(header)
            print(payload)

            signature = signature + "=" * -(len(signature) % -4)
            signature = base64.urlsafe_b64decode(signature)
            print(len(signature) * 8)
        except:
            pass


if __name__ == "__main__":
    main()
