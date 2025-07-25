import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

# Generate a random AES key (32 bytes for 256-bit encryption)
key = get_random_bytes(32)
with open("aes_key.key", "wb") as key_file:
    key_file.write(key)

# Define paths
input_folder = "files_to_encrypt"  # Folder containing files to encrypt
output_folder = "encrypted"       # Folder to store encrypted files

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Encrypt each file in the input folder
for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    if os.path.isfile(file_path):  # Process only files
        with open(file_path, "rb") as file:
            file_data = file.read()
        
        # Initialize AES cipher in CBC mode
        cipher = AES.new(key, AES.MODE_CBC)
        iv = cipher.iv  # Initialization vector

        # Encrypt the data
        encrypted_data = cipher.encrypt(pad(file_data, AES.block_size))

        # Save the encrypted file with IV prepended
        encrypted_file_path = os.path.join(output_folder, filename)
        with open(encrypted_file_path, "wb") as encrypted_file:
            encrypted_file.write(iv + encrypted_data)

print("All files have been encrypted using AES 256-bit and saved in the 'encrypted' folder.")
