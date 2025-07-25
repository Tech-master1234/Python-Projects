import secrets

def generate_secret_key():
    # Generate a 32-byte secure random key
    secret_key = secrets.token_hex(32)
    with open('default_dev_key','w') as key:
        key.write(secret_key)
    print(f"Your secure SECRET_KEY: {secret_key}")

if __name__ == "__main__":
    generate_secret_key()