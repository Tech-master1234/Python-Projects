
import os
import binascii

def generate_secret_key():
    return binascii.hexlify(os.urandom(24)).decode()

if __name__ == "__main__":
    secret_key = generate_secret_key()
    with open("API_SECRET_KEY", "w") as f:
        f.write(secret_key)
    print("Secret key generated and saved to 'API_SECRET_KEY' file.")
