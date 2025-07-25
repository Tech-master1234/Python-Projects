import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Load the AES key
with open("aes_key.key", "rb") as key_file:
    key = key_file.read()

# Define paths
input_folder = "encrypted"          # Folder containing encrypted files
output_folder = "decrypted_files"   # Folder to store decrypted files

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Decrypt each file in the input folder
for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    if os.path.isfile(file_path):  # Process only files
        with open(file_path, "rb") as encrypted_file:
            encrypted_data = encrypted_file.read()
        
        # Extract the IV (first 16 bytes) and the actual encrypted data
        iv = encrypted_data[:16]
        actual_encrypted_data = encrypted_data[16:]
        
        # Initialize AES cipher for decryption
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Decrypt and unpad the data
        decrypted_data = unpad(cipher.decrypt(actual_encrypted_data), AES.block_size)

        # Save the decrypted file to the output folder
        decrypted_file_path = os.path.join(output_folder, filename)
        with open(decrypted_file_path, "wb") as decrypted_file:
            decrypted_file.write(decrypted_data)

print("All files have been decrypted and saved in the 'decrypted_files' folder.")
