import os
import json
import base64
from getpass import getpass
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- Key Derivation ---
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    return kdf.derive(password.encode())

# --- Encryption ---
def encrypt_entry(entry: dict, key: bytes) -> dict:
    iv = os.urandom(12)
    aesgcm = AESGCM(key)
    plaintext = json.dumps(entry).encode()
    ciphertext = aesgcm.encrypt(iv, plaintext, None)

    return {
        "iv": base64.b64encode(iv).decode(),
        "data": base64.b64encode(ciphertext).decode()
    }

# --- Decryption ---
def decrypt_entry(encrypted_entry: dict, key: bytes) -> dict:
    iv = base64.b64decode(encrypted_entry['iv'])
    ciphertext = base64.b64decode(encrypted_entry['data'])
    aesgcm = AESGCM(key)
    
    plaintext = aesgcm.decrypt(iv, ciphertext, None)
    return json.loads(plaintext.decode())

# --- Save encrypted entry to file ---
def save_encrypted_entry(encrypted_entry: dict, filename='passwords.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            entries = json.load(f)
    else:
        entries = []

    entries.append(encrypted_entry)

    with open(filename, 'w') as f:
        json.dump(entries, f, indent=4)

# --- Load and search passwords ---
def load_passwords(filename='passwords.json') -> list:
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        return json.load(f)

def search_passwords(key: bytes, search_term: str) -> list:
    entries = load_passwords()
    results = []
    
    for entry in entries:
        try:
            decrypted = decrypt_entry(entry, key)
            # Search in website, username, and email
            if (search_term.lower() in decrypted['website'].lower() or
                search_term.lower() in decrypted['username'].lower() or
                search_term.lower() in decrypted['email'].lower()):
                results.append(decrypted)
        except Exception:
            continue  # Skip entries that can't be decrypted
    
    return results

def display_entry(entry: dict):
    print("\n=== Password Entry ===")
    print(f"Website: {entry['website']}")
    print(f"Username: {entry['username']}")
    print(f"Email: {entry['email']}")
    print(f"Password: {entry['password']}")
    print(f"Recovery: {entry['recovery']}")
    print("===================\n")

# --- Handle salt storage ---
def get_or_create_salt(meta_file='meta.json'):
    if os.path.exists(meta_file):
        with open(meta_file, 'r') as f:
            meta = json.load(f)
            return base64.b64decode(meta['salt'])
    else:
        salt = os.urandom(16)
        with open(meta_file, 'w') as f:
            json.dump({"salt": base64.b64encode(salt).decode()}, f)
        return salt

# --- Main program ---
def main():
    print("🔐 Password Manager")
    master_password = getpass("Enter master password: ")
    salt = get_or_create_salt()
    key = derive_key(master_password, salt)

    while True:
        print("\nOptions:")
        print("1. Store new password")
        print("2. Search passwords")
        print("3. View all passwords")
        print("4. Export passwords to text file")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            print("\nEnter the details for the new password entry:")
            entry = {
                "website": input("Website URL: "),
                "username": input("Username: "),
                "email": input("Email: "),
                "password": getpass("Password: "),
                "recovery": input("Recovery email or phone: ")
            }
            
            encrypted_entry = encrypt_entry(entry, key)
            save_encrypted_entry(encrypted_entry)
            print("\n✅ Entry encrypted and saved!")

        elif choice == "2":
            search_term = input("\nEnter search term (website/username/email): ")
            results = search_passwords(key, search_term)
            
            if not results:
                print("\n❌ No matching entries found.")
            else:
                print(f"\n✅ Found {len(results)} matching entries:")
                for entry in results:
                    display_entry(entry)
        
        elif choice == "3":
            entries = load_passwords()
            if not entries:
                print("\n❌ No entries found.")
            else:
                print(f"\n✅ Found {len(entries)} entries:")
                for entry in entries:
                    try:
                        decrypted = decrypt_entry(entry, key)
                        display_entry(decrypted)
                    except Exception:
                        print("❌ Failed to decrypt an entry")
        
        elif choice == "4":
            entries = load_passwords()
            if not entries:
                print("\n❌ No entries found to export.")
                continue
            
            try:
                filename = input("\nEnter filename to export (e.g., passwords.txt): ")
                with open(filename, 'w', encoding='utf-8') as f:
                    for entry in entries:
                        try:
                            decrypted = decrypt_entry(entry, key)
                            f.write("=== Password Entry ===\n")
                            f.write(f"Website: {decrypted['website']}\n")
                            f.write(f"Username: {decrypted['username']}\n")
                            f.write(f"Email: {decrypted['email']}\n")
                            f.write(f"Password: {decrypted['password']}\n")
                            f.write(f"Recovery: {decrypted['recovery']}\n")
                            f.write("===================\n\n")
                        except Exception:
                            f.write("Failed to decrypt an entry\n\n")
                print(f"\nPasswords exported to {filename}")
            except Exception as e:
                print(f"\nFailed to export passwords: {str(e)}")
            
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
